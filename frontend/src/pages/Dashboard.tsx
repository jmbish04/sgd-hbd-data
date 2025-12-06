import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Activity, Database, Server, AlertCircle, Search, RefreshCw } from 'lucide-react';
import { HealthCheckLog } from '@/components/HealthCheckLog';

export default function Dashboard() {
    const [health, setHealth] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/health')
            .then(res => res.json())
            .then(data => setHealth(data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return <div className="p-8">Loading system status...</div>;
    }

    const statusColor = health?.status === 'healthy' ? 'text-green-500' : 'text-red-500';

    return (
        <div className="flex flex-col gap-6">
            <h1 className="text-3xl font-bold tracking-tight">System Overview</h1>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">System Status</CardTitle>
                        <Activity className={`h-4 w-4 ${statusColor}`} />
                    </CardHeader>
                    <CardContent>
                        <div className={`text-2xl font-bold ${statusColor}`}>{health?.status || 'Unknown'}</div>
                        <p className="text-xs text-muted-foreground">
                            Last checked: {new Date().toLocaleTimeString()}
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Worker</CardTitle>
                        <Server className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{health?.worker || 'Unknown'}</div>
                        <p className="text-xs text-muted-foreground">
                            Cloudflare Worker
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Database (D1)</CardTitle>
                        <Database className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{health?.d1 || 'Unknown'}</div>
                        <p className="text-xs text-muted-foreground">
                            SQLite Storage
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Python Engine</CardTitle>
                        <AlertCircle className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{health?.python || 'Unknown'}</div>
                        <p className="text-xs text-muted-foreground">
                            Data Processing Container
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 transition-all hover:shadow-md">
                    <CardHeader>
                        <CardTitle>System Diagnostics</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <HealthCheckLog />
                    </CardContent>
                </Card>
                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>Quick Actions</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex flex-col gap-2">
                            <Button asChild variant="outline" className="w-full justify-start">
                                <Link to="/catalog">
                                    <Database className="mr-2 h-4 w-4" />
                                    Manage Datasets
                                </Link>
                            </Button>
                            <Button asChild variant="outline" className="w-full justify-start">
                                <Link to="/sql">
                                    <Search className="mr-2 h-4 w-4" />
                                    SQL Runner
                                </Link>
                            </Button>
                            <Button variant="outline" className="w-full justify-start" onClick={() => window.location.reload()}>
                                <RefreshCw className="mr-2 h-4 w-4" />
                                Refresh Dashboard
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
