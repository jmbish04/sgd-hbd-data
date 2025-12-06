import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, XCircle, RefreshCw, Play, Layers } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Dataset {
    id: string;
    module: string;
    collection_mode: string;
    count: number;
    last_updated: string | null;
    status: string;
}

export default function Catalog() {
    const [datasets, setDatasets] = useState<Dataset[]>([]);
    const [loading, setLoading] = useState(true);
    const [selected, setSelected] = useState<Set<string>>(new Set());
    const [processing, setProcessing] = useState<Set<string>>(new Set());

    const fetchDatasets = () => {
        fetch('/api/datasets')
            .then(async res => {
                if (!res.ok) {
                    const text = await res.text();
                    throw new Error(text || res.statusText);
                }
                return res.json();
            })
            .then(data => {
                if (data.datasets) {
                    setDatasets(data.datasets);
                }
            })
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        fetchDatasets();
    }, []);

    const toggleSelection = (id: string) => {
        const newSelected = new Set(selected);
        if (newSelected.has(id)) {
            newSelected.delete(id);
        } else {
            newSelected.add(id);
        }
        setSelected(newSelected);
    };

    const toggleAll = () => {
        if (selected.size === datasets.length) {
            setSelected(new Set());
        } else {
            setSelected(new Set(datasets.map(d => d.id)));
        }
    };

    const triggerIngest = async (ids: string[]) => {
        const newProcessing = new Set(processing);
        ids.forEach(id => newProcessing.add(id));
        setProcessing(newProcessing);

        // Process sequentially or parallel? Parallel is fine for async backend.
        for (const id of ids) {
            try {
                await fetch(`/ingest/${id}`, { method: 'POST' });
            } catch (e) {
                console.error(`Failed to trigger ${id}`, e);
            }
        }

        // Wait a bit then refresh to show updated status/counts (though processing is async)
        setTimeout(() => {
            const doneProcessing = new Set(processing);
            ids.forEach(id => doneProcessing.delete(id));
            setProcessing(doneProcessing);
            fetchDatasets(); // Refresh to see if counts changed (unlikely immediately, but maybe status)
        }, 2000);
    };

    if (loading && datasets.length === 0) return <div className="p-8">Loading catalog...</div>;

    return (
        <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Data Catalog</h1>
                    <p className="text-muted-foreground">Manage and monitor data ingestion pipelines.</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={fetchDatasets} disabled={loading}>
                        <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                        Refresh
                    </Button>
                    {selected.size > 0 && (
                        <Button onClick={() => triggerIngest(Array.from(selected))}>
                            <Layers className="mr-2 h-4 w-4" />
                            Process Selected ({selected.size})
                        </Button>
                    )}
                    <Button variant="default" onClick={() => triggerIngest(datasets.map(d => d.id))}>
                        <Play className="mr-2 h-4 w-4" />
                        Process All
                    </Button>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Registered Datasets</CardTitle>
                    <CardDescription>
                        {datasets.length} datasets available. Select to batch process.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead className="w-[50px]">
                                    <Checkbox
                                        checked={datasets.length > 0 && selected.size === datasets.length}
                                        onCheckedChange={toggleAll}
                                    />
                                </TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Dataset ID</TableHead>
                                <TableHead>Rows</TableHead>
                                <TableHead>Last Updated</TableHead>
                                <TableHead>Mode</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {datasets.map((dataset) => (
                                <TableRow key={dataset.id}>
                                    <TableCell>
                                        <Checkbox
                                            checked={selected.has(dataset.id)}
                                            onCheckedChange={() => toggleSelection(dataset.id)}
                                        />
                                    </TableCell>
                                    <TableCell>
                                        {dataset.status === 'active' ? (
                                            <div className="flex items-center text-green-600" title="Active">
                                                <CheckCircle2 className="h-5 w-5" />
                                            </div>
                                        ) : (
                                            <div className="flex items-center text-muted-foreground" title={dataset.status}>
                                                <XCircle className="h-5 w-5" />
                                            </div>
                                        )}
                                    </TableCell>
                                    <TableCell className="font-medium">
                                        {dataset.id}
                                        {processing.has(dataset.id) && <span className="ml-2 text-xs text-blue-500 animate-pulse">(Processing...)</span>}
                                    </TableCell>
                                    <TableCell>{dataset.count.toLocaleString()}</TableCell>
                                    <TableCell className="text-xs text-muted-foreground">
                                        {dataset.last_updated ? new Date(dataset.last_updated).toLocaleString() : '-'}
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant={dataset.collection_mode === 'complex' ? 'secondary' : 'outline'}>
                                            {dataset.collection_mode}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <div className="flex justify-end gap-2">
                                            <Link to={`/catalog/${dataset.id}`}>
                                                <Button variant="ghost" size="sm">View</Button>
                                            </Link>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => triggerIngest([dataset.id])}
                                                disabled={processing.has(dataset.id)}
                                            >
                                                <RefreshCw className={cn("h-3 w-3 mr-1", processing.has(dataset.id) && "animate-spin")} />
                                                Rerun
                                            </Button>
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
