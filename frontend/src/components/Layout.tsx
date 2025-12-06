import { Link, Outlet, useLocation } from 'react-router-dom';
import { LayoutDashboard, Database, Search, MessageSquare, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Layout() {
    const location = useLocation();

    const navItems = [
        { href: '/', label: 'Dashboard', icon: LayoutDashboard },
        { href: '/catalog', label: 'Data Catalog', icon: Database },
        { href: '/chat', label: 'Policy Chat', icon: MessageSquare },
        { href: '/sql', label: 'SQL Runner', icon: Search },
        { href: '/health', label: 'System Health', icon: Activity },
    ];

    return (
        <div className="min-h-screen bg-background font-sans antialiased">
            <div className="flex min-h-screen">
                {/* Sidebar */}
                <aside className="w-64 border-r bg-muted/40 hidden md:block">
                    <div className="flex h-14 items-center border-b px-4 lg:h-[60px] lg:px-6">
                        <Link to="/" className="flex items-center gap-2 font-semibold">
                            <Database className="h-6 w-6" />
                            <span className="">Data Refinery</span>
                        </Link>
                    </div>
                    <nav className="grid items-start px-2 text-sm font-medium lg:px-4 mt-4">
                        {navItems.map((item) => (
                            <Link
                                key={item.href}
                                to={item.href}
                                className={cn(
                                    "flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:text-primary",
                                    location.pathname === item.href
                                        ? "bg-muted text-primary"
                                        : "text-muted-foreground"
                                )}
                            >
                                <item.icon className="h-4 w-4" />
                                {item.label}
                            </Link>
                        ))}
                    </nav>
                </aside>

                {/* Main Content */}
                <div className="flex flex-col flex-1">
                    <header className="flex h-14 items-center gap-4 border-b bg-muted/40 px-4 lg:h-[60px] lg:px-6">
                        <div className="w-full flex-1">
                            {/* Breadcrumbs or Search could go here */}
                        </div>
                        <div className="flex items-center gap-4">
                            {/* User menu or settings */}
                        </div>
                    </header>
                    <main className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">
                        <Outlet />
                    </main>
                </div>
            </div>
        </div>
    );
}
