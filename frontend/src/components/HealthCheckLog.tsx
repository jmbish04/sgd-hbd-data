import { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Play, CheckCircle, XCircle } from 'lucide-react';

interface LogEntry {
    type: 'STARTED' | 'TEST_START' | 'TEST_END' | 'ALL_COMPLETED' | 'ERROR';
    testName?: string;
    status?: string;
    durationMs?: number;
    error?: string;
    runId?: string;
    result?: any;
    timestamp?: string;
}

export function HealthCheckLog() {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [status, setStatus] = useState<'IDLE' | 'RUNNING' | 'COMPLETED'>('IDLE');
    const wsRef = useRef<WebSocket | null>(null);
    const scrollRef = useRef<HTMLDivElement>(null);

    const startHealthCheck = () => {
        setLogs([]);
        setStatus('RUNNING');

        const viteWorkerUrl = import.meta.env.VITE_WORKER_URL;
        let url;

        if (viteWorkerUrl) {
            // If explicit URL provided (e.g. keying off remote worker), use it.
            // Strip scheme and path to get host for WS.
            // Expected format: https://host.com or https://host.com/some/path
            try {
                const targetObj = new URL(viteWorkerUrl);
                const protocol = targetObj.protocol === 'https:' ? 'wss:' : 'ws:';
                url = `${protocol}//${targetObj.host}/api/health/stream`;
            } catch (e) {
                console.error("Invalid VITE_WORKER_URL:", viteWorkerUrl, e);
                // Fallback
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const host = window.location.host;
                url = `${protocol}//${host}/api/health/stream`;
            }
        } else {
            // Default relative path (proxied)
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            url = `${protocol}//${host}/api/health/stream`;
        }

        console.log("Connecting to WebSocket:", url);
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log("Connected to Health Stream");
            ws.send(JSON.stringify({ action: 'START' }));
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                setLogs(prev => [...prev, { ...msg, timestamp: new Date().toLocaleTimeString() }]);

                if (msg.type === 'ALL_COMPLETED') {
                    setStatus('COMPLETED');
                    ws.close();
                }
            } catch (e) {
                console.error("Failed to parse WebSocket message:", event.data);
            }
        };

        ws.onerror = (e) => {
            console.error("WebSocket Error:", e);
            setLogs(prev => [...prev, { type: 'ERROR', error: "WebSocket connection failed." }]);
            setStatus('IDLE');
        };

        ws.onclose = () => {
            if (status === 'RUNNING') {
                // If closed unexpectedly
            }
        };
    };

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs]);

    return (
        <div className="flex flex-col h-[300px] gap-4">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium">Live Health Logs</h3>
                <Button
                    size="sm"
                    variant={status === 'RUNNING' ? "secondary" : "default"}
                    onClick={startHealthCheck}
                    disabled={status === 'RUNNING'}
                >
                    <Play className="mr-2 h-4 w-4" />
                    {status === 'RUNNING' ? 'Running...' : 'Run Diagnostics'}
                </Button>
            </div>

            <div className="flex-1 border rounded-md bg-zinc-950 p-4 font-mono text-xs overflow-hidden relative">
                <div className="h-full w-full overflow-y-auto">
                    {logs.length === 0 && status === 'IDLE' && (
                        <div className="text-zinc-500 italic">Ready to run system health diagnostics...</div>
                    )}
                    {logs.map((log, idx) => (
                        <div key={idx} className="mb-2 flex gap-2 items-start text-zinc-300">
                            <span className="text-zinc-600">[{log.timestamp}]</span>
                            {renderLogContent(log)}
                        </div>
                    ))}
                    <div ref={scrollRef} />
                </div>
            </div>
        </div>
    );
}

function renderLogContent(log: LogEntry) {
    switch (log.type) {
        case 'STARTED':
            return <span className="text-blue-400">Values Initialization (RunID: {log.runId})</span>;
        case 'TEST_START':
            return <span>Starting test: <span className="font-bold text-yellow-500">{log.testName}</span>...</span>;
        case 'TEST_END':
            // The result structure depends on our backend. 
            // In self_test.ts: result is expected to be nested under 'result' field in message?
            // Actually the message IS the HealthTestResult (or contains it).
            // Let's assume log.result IS the HealthTestResult object or log itself is.
            // Backend sends: onProgress({ type: 'TEST_END', result: aiResult });
            const res = log.result;
            const isPass = res?.status === 'PASS';
            return (
                <span className="flex items-center gap-2">
                    Finished {res?.testName}:
                    {isPass ?
                        <span className="text-green-500 flex items-center"><CheckCircle className="h-3 w-3 mr-1" /> PASS</span> :
                        <span className="text-red-500 flex items-center"><XCircle className="h-3 w-3 mr-1" /> FAIL</span>
                    }
                    <span className="text-zinc-500">({res?.durationMs}ms)</span>
                </span>
            );
        case 'ALL_COMPLETED':
            return <span className="text-green-400 font-bold">Diagnostic Run Completed Successfully.</span>;
        case 'ERROR':
            return <span className="text-red-500 font-bold">Error: {log.error}</span>;
        default:
            return <span>{JSON.stringify(log)}</span>;
    }
}
