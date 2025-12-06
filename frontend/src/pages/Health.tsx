import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Activity, Database, Server, AlertCircle, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { HealthCheckLog } from '@/components/HealthCheckLog';

interface HealthHistoryItem {
    id: number;
    testName: string;
    status: 'PASS' | 'FAIL';
    executedAt: string;
    durationMs: number;
    error?: string;
}

export default function HealthPage() {
    const [health, setHealth] = useState<any>(null);
    const [history, setHistory] = useState<HealthHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                const [healthRes, historyRes] = await Promise.all([
                    fetch('/api/health'),
                    fetch('/api/health/history')
                ]);

                const healthData = await healthRes.json();
                setHealth(healthData);

                if (historyRes.ok) {
                    const historyData = await historyRes.json();
                    setHistory(historyData);
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    if (loading) {
        return <div className="p-8">Loading system diagnostics...</div>;
    }

    const statusColor = health?.status === 'healthy' ? 'text-green-500' : 'text-red-500';

    return (
        <div className="flex flex-col gap-6">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight">System Health</h1>
                <p className="text-muted-foreground">
                    Real-time status, diagnostics, and historical performance.
                </p>
            </div>

            {/* Top Status Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Overall Status</CardTitle>
                        <Activity className={`h-4 w-4 ${statusColor}`} />
                    </CardHeader>
                    <CardContent>
                        <div className={`text-2xl font-bold ${statusColor}`}>{health?.status?.toUpperCase() || 'UNKNOWN'}</div>
                        <p className="text-xs text-muted-foreground">
                            Checked: {new Date().toLocaleTimeString()}
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Worker Node</CardTitle>
                        <Server className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{health?.worker || 'Unknown'}</div>
                        <div className="flex items-center pt-1">
                             <Badge variant="outline" className="text-xs">Cloudflare</Badge>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Database</CardTitle>
                        <Database className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{health?.d1 || 'Unknown'}</div>
                        <div className="flex items-center pt-1">
                             <Badge variant="outline" className="text-xs">D1 SQLite</Badge>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Compute Engine</CardTitle>
                        <AlertCircle className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{health?.python || 'Unknown'}</div>
                        <div className="flex items-center pt-1">
                             <Badge variant="outline" className="text-xs">Python Container</Badge>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Interactive Diagnostics */}
                <Card className="h-full">
                    <CardHeader>
                        <CardTitle>Interactive Diagnostics</CardTitle>
                        <CardDescription>
                            Run a full suite of self-tests on the backend infrastructure.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <HealthCheckLog />
                    </CardContent>
                </Card>

                {/* History Log */}
                <Card className="h-full flex flex-col">
                    <CardHeader>
                        <CardTitle>Recent Test History</CardTitle>
                        <CardDescription>
                            Results from scheduled cron jobs and manual triggers.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-hidden p-0">
                        <ScrollArea className="h-[350px] px-6">
                            <div className="space-y-4 pb-6">
                                {history.length === 0 ? (
                                    <div className="text-center text-muted-foreground py-8">
                                        No history available.
                                    </div>
                                ) : (
                                    history.map((item) => (
                                        <div key={item.id} className="flex items-start justify-between border-b pb-4 last:border-0">
                                            <div className="flex items-start gap-3">
                                                {item.status === 'PASS' ? (
                                                    <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5" />
                                                ) : (
                                                    <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
                                                )}
                                                <div>
                                                    <p className="font-medium text-sm">{item.testName}</p>
                                                    <p className="text-xs text-muted-foreground flex items-center gap-1">
                                                        <Clock className="h-3 w-3" />
                                                        {new Date(item.executedAt).toLocaleString()}
                                                    </p>
                                                    {item.error && (
                                                        <p className="text-xs text-red-500 mt-1 font-mono bg-red-500/10 p-1 rounded">
                                                            {item.error}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <Badge variant={item.status === 'PASS' ? 'secondary' : 'destructive'}>
                                                    {item.status}
                                                </Badge>
                                                <p className="text-xs text-muted-foreground mt-1">
                                                    {item.durationMs}ms
                                                </p>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </ScrollArea>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

