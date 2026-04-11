'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Home, Compass, MessageSquare, Image as ImageIcon, Users, FolderHeart, Film, CreditCard } from 'lucide-react';
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

const navItems = [
    { label: 'Inicio', href: '/dashboard', icon: Home },
    { label: 'Descubre', href: '/dashboard/discover', icon: Compass },
    { label: 'Chat', href: '/dashboard/chat', icon: MessageSquare },
    { label: 'Colección', href: '/dashboard/collection', icon: FolderHeart },
    { label: 'Generar Imagen', href: '/dashboard/generate', icon: ImageIcon },
    { label: 'Crear Personaje', href: '/dashboard/avatars/new', icon: Users, isPrimary: true },
    { label: 'Video Workflow', href: '/dashboard/studio', icon: Film, isPrimary: true },
];

export default function DashboardSidebar() {
    const pathname = usePathname();
    const [credits, setCredits] = useState<number>(0);

    useEffect(() => {
        if (api.isLoggedIn()) {
            api.getMe().then(user => {
                setCredits(user.credits || 0);
            }).catch(() => { });
        }
    }, [pathname]);

    return (
        <aside className="w-64 shrink-0 h-full border-r border-white/5 bg-[#050505] hidden md:flex flex-col">
            {/* Logo Area */}
            <div className="h-16 flex items-center px-6 border-b border-white/5 shrink-0">
                <Link href="/dashboard" className="flex items-center gap-2 group">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-accent-purple to-pink-500 flex items-center justify-center text-white font-black text-xs shadow-lg shadow-purple-500/20 group-hover:scale-105 transition-transform uppercase">
                        VS
                    </div>
                    <span className="font-bold text-lg tracking-tight text-white/90 uppercase notranslate" translate="no" suppressHydrationWarning>Velora <span className="text-accent-purple notranslate" translate="no" suppressHydrationWarning>Studio</span></span>
                </Link>
            </div>

            {/* Navigation Links */}
            <nav className="flex-1 overflow-y-auto py-6 px-4 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    const Icon = item.icon;

                    if (item.isPrimary) {
                        return (
                            <Link key={item.href} href={item.href} className="block mt-6 mb-2">
                                <div className="bg-gradient-to-r from-accent-purple to-pink-600 p-[1px] rounded-xl hover:shadow-[0_0_20px_rgba(236,72,153,0.3)] transition-all">
                                    <div className="bg-black/80 backdrop-blur-sm rounded-[11px] px-4 py-3 pb-3 flex items-center gap-3 w-full group/btn relative overflow-hidden">
                                        <div className="absolute inset-0 bg-gradient-to-r from-accent-purple/20 to-pink-600/20 translate-x-[-100%] group-hover/btn:translate-x-0 transition-transform duration-500" />
                                        <Icon className="w-5 h-5 text-accent-purple relative z-10" />
                                        <span className="font-bold text-sm text-white relative z-10 notranslate" translate="no">{item.label}</span>
                                    </div>
                                </div>
                            </Link>
                        );
                    }

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all group relative overflow-hidden",
                                isActive
                                    ? "bg-white/10 text-white"
                                    : "text-white/60 hover:text-white hover:bg-white/5"
                            )}
                        >
                            {isActive && <div className="absolute left-0 top-1/4 bottom-1/4 w-1 bg-accent-purple rounded-r-full" />}
                            <Icon className={cn("w-5 h-5 transition-transform group-hover:scale-110", isActive ? "text-accent-purple" : "opacity-80")} />
                            <span className="notranslate" translate="no">{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Bottom Tools */}
            <div className="p-4 border-t border-white/5 shrink-0">
                <div className="bg-gradient-to-br from-[#111] to-[#0a0a0a] border border-white/5 rounded-2xl p-4 flex flex-col gap-3">
                    <div className="flex justify-between items-center text-xs font-bold text-white/50 uppercase tracking-widest">
                        <span>Créditos</span>
                        <span className="text-accent-gold">{credits.toLocaleString()}</span>
                    </div>
                    <div className="w-full h-1.5 bg-black rounded-full overflow-hidden">
                        <div 
                            className="h-full bg-accent-gold transition-all duration-500" 
                            style={{ width: `${Math.min(100, (credits / 100) * 100)}%` }} 
                        />
                    </div>
                </div>
            </div>
        </aside>
    );
}
