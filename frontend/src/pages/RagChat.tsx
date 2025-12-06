import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, User, Bot, Loader2, FileText, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    sources?: Array<{
        url: string;
        title?: string;
        relevance?: number;
    }>;
    warnings?: string[];
    timestamp: Date;
}

export default function RagChat() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "welcome",
            role: "assistant",
            content: "Hello! I am your Policy Assistant. Ask me anything about HDB policies, grants, or regulations.",
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: "user",
            content: input,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setLoading(true);

        try {
            // Using the vector search endpoint for now, or the specific chat agent endpoint if available
            // Assuming /api/agent/query or similar. Based on codebase, we have /api/agent/query in routes/agent.py
            const res = await fetch("/api/agent/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    query: userMsg.content,
                    user_id: "demo-user" // Fixed for demo
                })
            });

            if (!res.ok) throw new Error(await res.text());

            const data = await res.json();
            
            const botMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: data.answer || data.response || "No response generated.",
                sources: data.sources || [],
                warnings: data.warnings || [],
                timestamp: new Date()
            };

            setMessages(prev => [...prev, botMsg]);
        } catch (error: any) {
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: `Error: ${error.message || "Something went wrong."}`,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setLoading(false);
            // Focus input after response
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-100px)] gap-4">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Policy Chat</h1>
                    <p className="text-muted-foreground">AI-powered answers grounded in official HDB policies.</p>
                </div>
                <Badge variant="outline" className="text-sm">
                    RAG Enabled
                </Badge>
            </div>

            <Card className="flex-1 flex flex-col overflow-hidden">
                <CardHeader className="pb-4 border-b">
                    <CardTitle className="text-lg">Chat Session</CardTitle>
                    <CardDescription>Ask questions like "Can I buy an HDB flat if I own a condo?"</CardDescription>
                </CardHeader>
                
                <div className="flex-1 overflow-hidden relative">
                    <ScrollArea className="h-full p-4" ref={scrollRef}>
                        <div className="flex flex-col gap-6 pb-4">
                            {messages.map((msg) => (
                                <div
                                    key={msg.id}
                                    className={cn(
                                        "flex gap-3 max-w-[80%]",
                                        msg.role === "user" ? "self-end flex-row-reverse" : "self-start"
                                    )}
                                >
                                    <div className={cn(
                                        "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                                        msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                                    )}>
                                        {msg.role === "user" ? <User size={16} /> : <Bot size={16} />}
                                    </div>
                                    
                                    <div className="flex flex-col gap-2">
                                        <div className={cn(
                                            "p-3 rounded-lg text-sm",
                                            msg.role === "user" 
                                                ? "bg-primary text-primary-foreground" 
                                                : "bg-muted text-foreground"
                                        )}>
                                            <p className="whitespace-pre-wrap">{msg.content}</p>
                                        </div>

                                        {/* Sources Section */}
                                        {msg.sources && msg.sources.length > 0 && (
                                            <div className="flex flex-col gap-1 mt-1">
                                                <span className="text-xs font-semibold text-muted-foreground flex items-center gap-1">
                                                    <FileText size={12} /> Sources:
                                                </span>
                                                <div className="flex flex-wrap gap-2">
                                                    {msg.sources.map((source, idx) => (
                                                        <a 
                                                            key={idx} 
                                                            href={source.url} 
                                                            target="_blank" 
                                                            rel="noopener noreferrer"
                                                            className="text-xs bg-secondary/50 hover:bg-secondary px-2 py-1 rounded border transition-colors truncate max-w-[200px]"
                                                        >
                                                            {source.title || new URL(source.url).hostname}
                                                        </a>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Warnings Section */}
                                        {msg.warnings && msg.warnings.length > 0 && (
                                            <div className="flex flex-col gap-1 mt-1 p-2 bg-yellow-500/10 border border-yellow-500/20 rounded">
                                                <span className="text-xs font-semibold text-yellow-600 flex items-center gap-1">
                                                    <AlertTriangle size={12} /> Considerations:
                                                </span>
                                                <ul className="list-disc list-inside text-xs text-muted-foreground">
                                                    {msg.warnings.map((warn, idx) => (
                                                        <li key={idx}>{warn}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        
                                        <span className="text-[10px] text-muted-foreground opacity-50 px-1">
                                            {msg.timestamp.toLocaleTimeString()}
                                        </span>
                                    </div>
                                </div>
                            ))}
                            {loading && (
                                <div className="flex gap-3 max-w-[80%] self-start">
                                    <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center shrink-0">
                                        <Loader2 size={16} className="animate-spin" />
                                    </div>
                                    <div className="p-3 rounded-lg bg-muted text-sm text-foreground">
                                        <span className="animate-pulse">Thinking...</span>
                                    </div>
                                </div>
                            )}
                        </div>
                    </ScrollArea>
                </div>

                <CardFooter className="p-4 border-t bg-background/50 backdrop-blur-sm">
                    <div className="flex w-full gap-2">
                        <Input
                            ref={inputRef}
                            placeholder="Ask a question..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            disabled={loading}
                            className="flex-1"
                        />
                        <Button onClick={handleSend} disabled={loading || !input.trim()}>
                            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                        </Button>
                    </div>
                </CardFooter>
            </Card>
        </div>
    );
}

