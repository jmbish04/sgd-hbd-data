import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Play, Sparkles } from 'lucide-react';

export default function SQLRunner() {
    const [query, setQuery] = useState('SELECT * FROM logs ORDER BY timestamp DESC LIMIT 20');
    const [results, setResults] = useState<any[]>([]);
    const [columns, setColumns] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [nlQuery, setNlQuery] = useState('');
    const [explanation, setExplanation] = useState('');

    const runQuery = async () => {
        setLoading(true);
        setError('');
        try {
            const res = await fetch('/api/sql', {
                method: 'POST',
                body: JSON.stringify({ query }),
                headers: { 'Content-Type': 'application/json' }
            });

            if (!res.ok) {
                const text = await res.text();
                try {
                    // Try to parse as JSON first in case it's a structured error
                    const jsonErr = JSON.parse(text);
                    throw new Error(jsonErr.error || text);
                } catch (e) {
                    // If not JSON, throw text
                    throw new Error(text || res.statusText);
                }
            }

            const json = await res.json();

            if (json.error) {
                setError(json.error);
                setResults([]);
            } else {
                if (json.results && Array.isArray(json.results)) {
                    setResults(json.results);
                    if (json.results.length > 0) {
                        setColumns(Object.keys(json.results[0]));
                    }
                } else {
                    // Handle case where it might be just an array
                    if (Array.isArray(json)) {
                        setResults(json);
                        if (json.length > 0) setColumns(Object.keys(json[0]));
                    } else {
                        // D1 result object structure: { results: [], success: true, ... }
                        // The worker returns whatever D1 returns.
                        // If using .all(), it returns { results: [], ... }
                        setResults(json.results || []);
                        if (json.results && json.results.length > 0) {
                            setColumns(Object.keys(json.results[0]));
                        }
                    }
                }
            }
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };



    const generateSql = async () => {
        if (!nlQuery.trim()) return;
        setLoading(true);
        setError('');
        setExplanation('');

        try {
            const res = await fetch('/api/nl-to-sql', {
                method: 'POST',
                body: JSON.stringify({ query: nlQuery }),
                headers: { 'Content-Type': 'application/json' }
            });
            const json = await res.json();

            if (json.error) {
                setError(json.error);
            } else {
                setQuery(json.sql_query);
                setExplanation(json.explanation);
            }
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col gap-6 h-[calc(100vh-100px)]">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">SQL Runner</h1>
            </div>

            <div className="grid gap-6 md:grid-cols-3 h-full">
                <div className="flex flex-col gap-4 md:col-span-1">
                    <Card className="flex-1 flex flex-col">
                        <CardHeader>
                            <CardTitle>Query Editor</CardTitle>
                        </CardHeader>
                        <CardContent className="flex-1 flex flex-col gap-4">
                            <div className="flex flex-col gap-2">
                                <label className="text-sm font-medium">Natural Language (AI)</label>
                                <div className="flex gap-2">
                                    <Textarea
                                        placeholder="Show me recent logs..."
                                        value={nlQuery}
                                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNlQuery(e.target.value)}
                                        className="resize-none h-20"
                                    />
                                    <Button variant="secondary" className="h-20 w-12 flex flex-col gap-1" onClick={generateSql}>
                                        <Sparkles className="h-4 w-4" />
                                    </Button>
                                </div>
                                {explanation && (
                                    <div className="text-xs text-muted-foreground mt-1 bg-muted p-2 rounded border">
                                        <span className="font-semibold">AI Explanation:</span> {explanation}
                                    </div>
                                )}
                            </div>

                            <div className="flex flex-col gap-2 flex-1">
                                <label className="text-sm font-medium">SQL</label>
                                <Textarea
                                    className="font-mono flex-1 resize-none p-4"
                                    value={query}
                                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setQuery(e.target.value)}
                                />
                            </div>

                            <Button onClick={runQuery} disabled={loading}>
                                {loading ? 'Running...' : <><Play className="mr-2 h-4 w-4" /> Run Query</>}
                            </Button>
                        </CardContent>
                    </Card>
                </div>

                <div className="md:col-span-2 h-full overflow-hidden">
                    <Card className="h-full flex flex-col">
                        <CardHeader>
                            <CardTitle>Results {results.length > 0 && `(${results.length} rows)`}</CardTitle>
                        </CardHeader>
                        <CardContent className="flex-1 overflow-auto p-0">
                            {error ? (
                                <div className="p-6 text-red-500 font-mono text-sm whitespace-pre-wrap">{error}</div>
                            ) : results.length === 0 ? (
                                <div className="p-6 text-muted-foreground">No results to display.</div>
                            ) : (
                                <div className="relative w-full overflow-auto">
                                    <Table>
                                        <TableHeader className="sticky top-0 bg-secondary">
                                            <TableRow>
                                                {columns.map(col => (
                                                    <TableHead key={col} className="whitespace-nowrap">{col}</TableHead>
                                                ))}
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {results.map((row, i) => (
                                                <TableRow key={i}>
                                                    {columns.map(col => (
                                                        <TableCell key={col} className="whitespace-nowrap max-w-[300px] truncate">
                                                            {row[col] !== null ? String(row[col]) : <span className="text-muted-foreground italic">null</span>}
                                                        </TableCell>
                                                    ))}
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
