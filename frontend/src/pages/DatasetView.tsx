import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';

export default function DatasetView() {
    const { datasetId } = useParams();
    const [data, setData] = useState<any[]>([]);
    const [columns, setColumns] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        // We don't have a direct "get table name from dataset id" API exposed to frontend easily yet without mapping.
        // For now, we'll try to guess the table name or use a generic SQL query if we knew the table.
        // Actually, the user wants to see data.
        // Let's assume the table name matches the dataset ID with some transformation, or we just query `raw_hdb_resale_prices` as a test if ID matches.
        // A better way: The Catalog should pass the table name, or we fetch metadata.
        // For this MVP, let's just run a SQL query that tries to find the table.
        // Or simpler: Just allow the user to run SQL.

        // Let's try to query a table named after the dataset_id (replacing - with _).
        const tableName = datasetId?.replace(/-/g, '_');

        // This is a guess. Real implementation needs a mapping.
        // Let's try to fetch from /api/sql

        const fetchTable = async () => {
            try {
                // First, list tables to find a match?
                // Or just try SELECT * FROM tableName LIMIT 50
                // We'll try a few common prefixes if it fails?
                // Actually, let's just try `raw_{tableName}` which is the convention in `schema.ts` (mostly).

                const query = `SELECT * 
                FROM raw_${tableName} 
                LIMIT 50`;
                const res = await fetch('/api/sql', {
                    method: 'POST',
                    body: JSON.stringify({ query })
                });
                const json = await res.json();

                if (json.error) {
                    // Try without raw_ prefix
                    const query2 = `SELECT * 
                    FROM ${tableName} 
                    LIMIT 50`;

                    const res2 = await fetch('/api/sql', {
                        method: 'POST',
                        body: JSON.stringify({ query: query2 })
                    });
                    const json2 = await res2.json();
                    if (json2.error) throw new Error(json.error + " | " + json2.error);

                    if (json2.results && json2.results.length > 0) {
                        setData(json2.results);
                        setColumns(Object.keys(json2.results[0]));
                    }
                } else {
                    if (json.results && json.results.length > 0) {
                        setData(json.results);
                        setColumns(Object.keys(json.results[0]));
                    }
                }
            } catch (e: any) {
                setError(e.message);
            } finally {
                setLoading(false);
            }
        };

        fetchTable();
    }, [datasetId]);

    return (
        <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">Dataset: {datasetId}</h1>
                <Button variant="outline" onClick={() => window.location.reload()}>Refresh</Button>
            </div>

            {error && (
                <div className="p-4 bg-red-50 text-red-500 rounded-md">
                    Could not load data (Table might not exist or name mismatch): {error}
                </div>
            )}

            <Card>
                <CardHeader>
                    <CardTitle>Preview (First 50 Rows)</CardTitle>
                </CardHeader>
                <CardContent className="overflow-auto">
                    {loading ? (
                        <div>Loading data...</div>
                    ) : data.length === 0 ? (
                        <div>No data found or table empty.</div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    {columns.map(col => (
                                        <TableHead key={col} className="whitespace-nowrap">{col}</TableHead>
                                    ))}
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data.map((row, i) => (
                                    <TableRow key={i}>
                                        {columns.map(col => (
                                            <TableCell key={col} className="whitespace-nowrap max-w-[200px] truncate">
                                                {row[col] !== null ? String(row[col]) : <span className="text-muted-foreground italic">null</span>}
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
