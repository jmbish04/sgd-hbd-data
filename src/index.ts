import { Container } from './lib/container';

// Export the Durable Object class
import { drizzle } from 'drizzle-orm/d1';
import { logs } from './schema';
import { HDBEnrichmentService } from './services/enrichment';

// Export the Durable Object class
export class DataProcessor extends Container {
  private conn?: WebSocket;
  private resolveResolve?: (s: string) => void;

  constructor(ctx: DurableObjectState<any>, env: Env) {
    super(ctx, env);
    this.defaultPort = parseInt(env.PORT || "8080"); // Dynamic Port

    // Explicitly pass secrets and env vars to the Container environment
    // The Container runtime (via super.start) relies on this.envVars.
    this.envVars = {
      CLOUDFLARE_ACCOUNT_ID: env.CLOUDFLARE_ACCOUNT_ID,
      CLOUDFLARE_API_TOKEN: env.CLOUDFLARE_API_TOKEN,
      CLOUDFLARE_D1_DATABASE_ID: env.CLOUDFLARE_D1_DATABASE_ID,
      R2_BUCKET_NAME: env.R2_BUCKET_NAME,
      R2_ACCOUNT_ID: env.R2_ACCOUNT_ID,
      AWS_ACCESS_KEY_ID: env.AWS_ACCESS_KEY_ID,
      AWS_SECRET_ACCESS_KEY: env.AWS_SECRET_ACCESS_KEY,

      // Optional/Defaults
      WORKER_LOG_URL: env.WORKER_LOG_URL || "",
      GOOGLE_API_KEY: env.GOOGLE_API_KEY || "",
      GOOGLE_MAPS_API_KEY: env.GOOGLE_MAPS_API_KEY || "",
      PORT: env.PORT || "8080", // Pass PORT to container

      // Ensure Python output is unbuffered
      PYTHONUNBUFFERED: "1"
    };

    // Initialize websocket connection to container
    this.initWebsocket();
  }

  private async blockConcurrencyRetry(cb: () => Promise<unknown>) {
    await this.ctx.blockConcurrencyWhile(async () => {
      let lastErr;
      for (let i = 0; i < 10; i++) {
        try {
          return await cb();
        } catch (err) {
          lastErr = err;
          continue;
        }
      }
      throw lastErr;
    });
  }

  private async initWebsocket() {
    await this.blockConcurrencyRetry(async () => {
      // Use containerFetch to establish websocket connection to container
      // containerFetch handles ensuring the container is running and healthy
      const res = await this.containerFetch(new Request('http://container/api/health/stream', {
        headers: { Upgrade: 'websocket' }
      }));

      if (res.webSocket === null) {
        // If we get a 503 or similar because container is starting, throw to retry
        if (res.status === 503) throw new Error('Container starting');
        throw new Error('websocket server is faulty');
      }

      // Accept the websocket and listen to messages
      res.webSocket.accept();
      res.webSocket.addEventListener('message', (msg: MessageEvent) => {
        if (this.resolveResolve !== undefined) {
          this.resolveResolve(typeof msg.data === 'string' ? msg.data : new TextDecoder().decode(msg.data));
        }
      });
      res.webSocket.addEventListener('close', () => {
        this.ctx.abort();
      });

      this.conn = res.webSocket;
    });
  }


  // Override fetch to handle websocket upgrades
  override async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    // Handle websocket upgrade for health streaming
    if (url.pathname === '/api/health/stream') {
      const upgradeHeader = request.headers.get('Upgrade');
      if (upgradeHeader === 'websocket') {
        const webSocketPair = new WebSocketPair();
        const [client, server] = Object.values(webSocketPair);

        server.accept();

        // Connect server websocket to container websocket
        if (this.conn) {
          // Forward messages from client to container
          server.addEventListener('message', (event) => {
            if (this.conn && this.conn.readyState === WebSocket.OPEN) {
              this.conn.send(event.data);
            }
          });

          // Forward messages from container to client
          this.conn.addEventListener('message', (event) => {
            if (server.readyState === WebSocket.OPEN) {
              server.send(event.data);
            }
          });

          // Handle websocket close
          server.addEventListener('close', () => {
            if (this.conn) {
              this.conn.close();
            }
          });

          // Start the health test by sending a trigger message
          if (this.conn.readyState === WebSocket.OPEN) {
            this.conn.send(JSON.stringify({ action: 'START' }));
          }
        } else {
          server.send(JSON.stringify({ type: 'ERROR', error: 'Container websocket not available' }));
          server.close(1011, 'Internal Error');
        }

        return new Response(null, {
          status: 101,
          webSocket: client,
        });
      }
    }

    // For non-websocket requests, forward to container
    return await super.fetch(request);
  }
}

// Default export for the Worker (ES Module format)
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    // 1. Internal Logging Endpoint (called by Python)
    if (url.pathname === '/_internal/log' && request.method === 'POST') {
      try {
        const db = drizzle(env.DB);
        const payload = await request.json() as any;

        await db.insert(logs).values({
          timestamp: payload.timestamp || new Date().toISOString(),
          level: payload.level || 'INFO',
          component: payload.component || 'unknown',
          message: payload.message || '',
          traceId: payload.traceId,
          error: payload.error,
          metadata: payload.metadata
        });

        return new Response('Logged', { status: 200 });
      } catch (e) {
        console.error('Failed to write log to D1:', e);
        return new Response(`Log Failed: ${e}`, { status: 500 });
      }
    }

    // 2. Health Check (Worker + D1 + Python)
    if (url.pathname === '/api/health') {
      const health = await checkHealth(env, request.url);
      return new Response(JSON.stringify(health), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // 3. SQL Runner API
    if (url.pathname === '/api/sql' && request.method === 'POST') {
      try {
        const payload = await request.json() as any;
        const query = payload.query;

        if (!query) {
          return new Response('Missing query', { status: 400 });
        }

        console.log(`[SQL] Executing: ${query.substring(0, 200)}${query.length > 200 ? '...' : ''}`);

        // Execute raw SQL
        // Note: In production, this should be restricted/authenticated!
        const result = await env.DB.prepare(query).all();

        return new Response(JSON.stringify(result), {
          headers: { 'Content-Type': 'application/json' }
        });
      } catch (e) {
        console.error(`[SQL] Error executing query: ${e}`);
        return new Response(JSON.stringify({ error: String(e) }), {
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }

    // 4. Manual Enrichment Trigger (Internal)
    if (url.pathname === '/api/enrich' && request.method === 'POST') {
      try {
        const payload = await request.json() as any;
        const blockId = payload.blockId;

        if (!blockId) return new Response('Missing blockId', { status: 400 });

        const service = new HDBEnrichmentService(env);
        // Run in background to avoid timeout
        ctx.waitUntil(service.enrichBlock(blockId));

        return new Response(`Enrichment started for Block ${blockId}`, { status: 202 });
      } catch (e) {
        return new Response(`Enrichment Failed: ${e}`, { status: 500 });
      }
    }

    // 5. Route everything else to the DataProcessor DO
    if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/ingest/')) {
      const id = env.DataProcessor.idFromName('main');
      const stub = env.DataProcessor.get(id);
      return stub.fetch(request);
    }

    // 6. Health Stream (WebSocket) - Routes to container via Durable Object
    if (url.pathname === '/api/health/stream') {
      const upgradeHeader = request.headers.get('Upgrade');
      if (!upgradeHeader || upgradeHeader !== 'websocket') {
        return new Response('Expected Upgrade: websocket', { status: 426 });
      }

      // Route websocket requests to the DataProcessor DO
      const id = env.DataProcessor.idFromName('main');
      const stub = env.DataProcessor.get(id);
      return stub.fetch(request);
    }

    // 7. Health History API
    if (url.pathname === '/api/health/history') {
      const db = drizzle(env.DB);
      const { systemHealthTests } = await import('./schema');
      // Import desc if needed or use sql desc
      const { desc } = await import('drizzle-orm');

      const history = await db.select()
        .from(systemHealthTests)
        .orderBy(desc(systemHealthTests.executedAt))
        .limit(50)
        .all();

      return new Response(JSON.stringify(history), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // If we are here, it's likely a frontend asset request (SPA route) or 404.
    // We forward to the ASSETS binding, which handles SPA routing (serving index.html)
    // thanks to `not_found_handling: "single_page_application"` in wrangler.jsonc.
    return env.ASSETS.fetch(request);
  },

  async scheduled(_event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    ctx.waitUntil((async () => {
      const health = await checkHealth(env, 'http://localhost'); // URL doesn't matter for internal check
      const db = drizzle(env.DB);

      await db.insert(logs).values({
        timestamp: new Date().toISOString(),
        level: health.status === 'healthy' ? 'INFO' : 'WARN',
        component: 'HealthCheck',
        message: `Scheduled Health Check: ${health.status}`,
        metadata: JSON.stringify(health)
      });

      // Run Historical Portfolio Analysis (Weekly)
      try {
        const service = new HDBEnrichmentService(env);
        console.log('Starting Scheduled Portfolio Analysis...');
        await service.runHistoricalPortfolioAnalysis();
        console.log('Completed Portfolio Analysis.');
      } catch (e) {
        console.error('Portfolio Analysis Failed:', e);
        await db.insert(logs).values({
          timestamp: new Date().toISOString(),
          level: 'ERROR',
          component: 'PortfolioAnalysis',
          message: `Cron Job Failed: ${e}`,
          error: String(e)
        });
      }

      // Run System Self-Tests (Cron Health Check)
      try {
        const { SystemSelfTestService } = await import('./services/self_test');
        const tester = new SystemSelfTestService(env);
        console.log('Starting System Self-Tests...');
        await tester.runAllTests('SCHEDULED'); // No callback needed for cron
        console.log(`Completed System Self-Tests.`);
      } catch (e) {
        console.error('System Self-Test Failed:', e);
        await db.insert(logs).values({
          timestamp: new Date().toISOString(),
          level: 'ERROR',
          component: 'SystemSelfTest',
          message: `Self-Test Execution Failed: ${e}`,
          error: String(e)
        });
      }
    })());
  }
};

async function checkHealth(env: Env, baseUrl: string): Promise<any> {
  const db = drizzle(env.DB);
  let d1Status = 'unknown';
  try {
    // Simple query to check D1 connectivity
    await db.select().from(logs).limit(1);
    d1Status = 'connected';
  } catch (e) {
    d1Status = `error: ${e}`;
  }

  // Check Python Container
  let pythonStatus = 'unknown';
  try {
    const id = env.DataProcessor.idFromName('main');
    const stub = env.DataProcessor.get(id);
    // Use a dummy request to the DO, which forwards to Python
    const pyRes = await stub.fetch(new Request(new URL('/api/health', baseUrl).toString()));
    if (pyRes.ok) {
      const pyJson = await pyRes.json() as any;
      pythonStatus = pyJson.status || 'active';
    } else {
      pythonStatus = `error: ${pyRes.status}`;
    }
  } catch (e) {
    pythonStatus = `unreachable: ${e}`;
  }

  return {
    status: (d1Status === 'connected' && pythonStatus === 'healthy') ? 'healthy' : 'degraded',
    worker: 'active',
    d1: d1Status,
    python: pythonStatus,
    timestamp: new Date().toISOString()
  };
}

