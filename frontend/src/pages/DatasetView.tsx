import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

export default function DatasetView() {
    const { datasetId } = useParams();
    const [data, setData] = useState<any[]>([]);
    const [columns, setColumns] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [tableName, setTableName] = useState<string>('');

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            setError('');
            try {
                // 1. Get the real table name from the registry API
                const regRes = await fetch('/api/datasets');
                const regJson = await regRes.json();
                
                const datasetInfo = regJson.datasets?.find((d: any) => d.id === datasetId);
                const realTableName = datasetInfo?.tableName;

                if (!realTableName) {
                    throw new Error(`Could not find table name for dataset ${datasetId}`);
                }
                setTableName(realTableName);

                // 2. Fetch Data using the real table name
                const query = `SELECT * FROM ${realTableName} LIMIT 50`;
                const res = await fetch('/api/sql', {
                    method: 'POST',
                    body: JSON.stringify({ query })
                });
                
                const json = await res.json();
                
                if (json.error) {
                    throw new Error(json.error);
                }

                if (json.results && Array.isArray(json.results) && json.results.length > 0) {
                    setData(json.results);
                    setColumns(Object.keys(json.results[0]));
                } else if (json.results && Array.isArray(json.results)) {
                    setData([]);
                } else {
                    // D1 generic response handling
                    setData(json || []);
                }

            } catch (e: any) {
                console.error(e);
                setError(e.message);
            } finally {
                setLoading(false);
            }
        };

        if (datasetId) {
            loadData();
        }
    }, [datasetId]);

    return (
        <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Dataset View</h1>
                    <p className="text-muted-foreground">{datasetId}</p>
                    {tableName && <p className="text-xs font-mono text-muted-foreground">Table: {tableName}</p>}
                </div>
                <Button variant="outline" onClick={() => window.location.reload()}>Refresh</Button>
            </div>

            {error && (
                <div className="p-4 bg-red-50 text-red-500 rounded-md border border-red-200">
                    Error: {error}
                </div>
            )}

            <Card>
                <CardHeader>
                    <CardTitle>Preview (First 50 Rows)</CardTitle>
                </CardHeader>
                <CardContent className="overflow-auto min-h-[300px]">
                    {loading ? (
                        <div className="flex items-center justify-center h-40">
                            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                        </div>
                    ) : data.length === 0 ? (
                        <div className="text-center text-muted-foreground py-8">No data found in table.</div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    {columns.map(col => (
                                        <TableHead key={col} className="whitespace-nowrap bg-muted/50">{col}</TableHead>
                                    ))}
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data.map((row, i) => (
                                    <TableRow key={i}>
                                        {columns.map(col => (
                                            <TableCell key={col} className="whitespace-nowrap max-w-[300px] truncate">
                                                {row[col] !== null && row[col] !== undefined ? String(row[col]) : <span className="text-muted-foreground italic">null</span>}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
