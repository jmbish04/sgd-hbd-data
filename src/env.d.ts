interface Env {
    // Secrets
    CLOUDFLARE_ACCOUNT_ID: string;
    CLOUDFLARE_API_TOKEN: string;
    GOOGLE_API_KEY?: string;
    GOOGLE_MAPS_API_KEY?: string;

    // Environment Variables (Vars)
    CLOUDFLARE_D1_DATABASE_ID: string;
    WORKER_LOG_URL?: string;
    PORT?: string;

    // R2 Configuration (needed for startup.sh)
    R2_BUCKET_NAME: string;
    R2_ACCOUNT_ID: string;
    AWS_ACCESS_KEY_ID: string;
    AWS_SECRET_ACCESS_KEY: string;

    // Bindings
    DB: D1Database;
    DataProcessor: DurableObjectNamespace;
    ASSETS: Fetcher;
}
