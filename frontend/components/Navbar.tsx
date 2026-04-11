'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    Menu,
    X,
    Video,
    User,
    BarChart3,
    ShieldCheck,
    LogOut,
    CreditCard,
    ChevronRight,
    Zap as ZapIcon,
    Layers,
    Globe,
    ChevronDown
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';

interface NavbarProps {
    studioStep?: 'tier' | 'avatar' | 'workflow';
    setStudioStep?: (step: any) => void;
    projectTitle?: string;
    setProjectTitle?: (val: string) => void;
    isSubmitting?: boolean;
    handleGenerateAll?: () => void;
}

export default function Navbar({
    studioStep,
    setStudioStep,
    projectTitle,
    setProjectTitle,
    isSubmitting,
    handleGenerateAll
}: NavbarProps) {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);
    const [credits, setCredits] = useState<number>(0);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const pathname = usePathname();

    useEffect(() => {
        setIsLoggedIn(api.isLoggedIn());
        if (api.isLoggedIn()) {
            api.getMe().then(user => {
                // Only show admin for the specific master email
                setIsAdmin(user.is_admin && user.email === 'admin@ai-video.com');
                setCredits(user.credits || 0);
            }).catch(() => { });
        }
    }, [pathname]);

    const handleLogout = () => {
        api.clearTokens();
        window.location.href = '/login';
    };

    const navLinks = [
        { name: 'Avatar', href: '/studio?step=avatar', icon: <User className="w-4 h-4" /> },
        { name: 'Generar Vídeo', href: '/studio', icon: <Video className="w-4 h-4" /> },
        { name: 'Mis Vídeos', href: '/dashboard', icon: <BarChart3 className="w-4 h-4" /> },
        { name: 'Precios', href: 'http://localhost:3004', icon: <CreditCard className="w-4 h-4" /> },
    ];

    const isStudio = pathname === '/studio';

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0c0c0c]/80 backdrop-blur-2xl border-b border-white/[0.06] px-6 h-14 flex items-center justify-between">
            <div className="flex items-center gap-6">
                <Link href="/" className="flex items-center gap-2.5 group shrink-0">
                    <div className="w-7 h-7 bg-gradient-to-tr from-accent-purple to-purple-400 rounded-lg flex items-center justify-center group-hover:scale-105 transition-transform shadow-lg shadow-accent-purple/20">
                        <ZapIcon className="w-4 h-4 text-white fill-current" />
                    </div>
                    <span className="text-[13px] font-bold tracking-tight text-white/90 hidden sm:block">AI Video</span>
                    <ChevronRight className="w-3 h-3 text-white/15 hidden sm:block" />
                </Link>

                {isStudio && setStudioStep ? (
                    <div className="hidden lg:flex items-center gap-0.5 bg-white/[0.04] p-1 rounded-lg border border-white/[0.06]">
                        {[
                            { id: 'tier', label: 'Tier', icon: <ZapIcon className="w-3 h-3" /> },
                            { id: 'avatar', label: 'Avatar', icon: <User className="w-3 h-3" /> },
                            { id: 'workflow', label: 'Workflow', icon: <Layers className="w-3 h-3" /> },
                        ].map((s, idx) => (
                            <div key={s.id} className="flex items-center">
                                <button
                                    onClick={() => (studioStep === 'workflow' || idx < 2) && setStudioStep(s.id)}
                                    className={cn(
                                        "flex items-center gap-2 px-3.5 py-1.5 rounded-md text-[10px] font-semibold transition-all",
                                        studioStep === s.id ? "bg-accent-purple text-white shadow-lg shadow-accent-purple/20" : "text-white/40 hover:text-white/70 hover:bg-white/[0.04]"
                                    )}
                                >
                                    {s.icon} {s.label}
                                </button>
                                {idx < 2 && <ChevronRight className="w-3 h-3 text-white/10 mx-0.5" />}
                            </div>
                        ))}
                    </div>
                ) : pathname !== '/' ? (
                    <div className="hidden md:flex items-center gap-1">
                        {navLinks.filter(link => isLoggedIn || link.name === 'Precios').map((link) => (
                            <Link
                                key={link.name}
                                href={link.href}
                                className={cn(
                                    "flex items-center gap-2 px-4 py-2 rounded-full text-[11px] font-bold uppercase tracking-wider transition-all",
                                    pathname && pathname.startsWith(link.href.split('?')[0])
                                        ? "text-accent-gold bg-white/5"
                                        : "text-white/40 hover:text-white hover:bg-white/5"
                                )}
                            >
                                {link.icon} {link.name}
                            </Link>
                        ))}
                    </div>
                ) : null}
            </div>

            <div className="flex items-center gap-4">
                {isStudio && studioStep === 'workflow' && setProjectTitle && (
                    <div className="hidden min-[1100px]:block">
                        <input
                            className="bg-white/5 border border-white/10 rounded-full px-6 py-2 text-[10px] font-bold focus:outline-none focus:border-accent-gold/40 w-48 transition-all focus:w-64"
                            placeholder="Nombre Producción..."
                            value={projectTitle}
                            onChange={(e) => setProjectTitle(e.target.value)}
                        />
                    </div>
                )}

                {isStudio && handleGenerateAll && (
                    <button
                        onClick={() => {
                            if (studioStep === 'workflow') handleGenerateAll();
                            else if (setStudioStep) setStudioStep(studioStep === 'tier' ? 'avatar' : 'workflow');
                        }}
                        disabled={isSubmitting}
                        className="bg-accent-purple text-white px-5 py-2 rounded-lg text-[10px] font-bold shadow-lg shadow-accent-purple/20 hover:bg-accent-purple/90 active:scale-95 transition-all flex items-center gap-2"
                    >
                        {isSubmitting ? 'Iniciando...' : (studioStep === 'workflow' ? 'Producción Final' : 'Continuar')}
                        {!isSubmitting && <kbd className="px-1.5 py-0.5 rounded bg-white/15 text-[7px] font-mono">⇧↵</kbd>}
                    </button>
                )}

                {/* User Controls - Only for internal pages */}
                {pathname !== '/' ? (
                    isLoggedIn ? (
                        <div className="flex items-center gap-4">
                            <div className="hidden xl:flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-full">
                                <CreditCard className="w-3 h-3 text-accent-gold" />
                                <span className="text-[9px] font-black italic">{credits.toFixed(2)} Créditos</span>
                            </div>

                            {isAdmin && (
                                <Link
                                    href="/admin"
                                    className="flex items-center gap-2 px-4 py-2 rounded-full text-[10px] font-bold uppercase text-accent-purple bg-accent-purple/5 border border-accent-purple/20 hover:bg-accent-purple/10 transition-all"
                                >
                                    <ShieldCheck className="w-4 h-4" /> Admin
                                </Link>
                            )}

                            <button
                                onClick={handleLogout}
                                className="p-2 text-white/40 hover:text-red-500 transition-colors"
                            >
                                <LogOut className="w-5 h-5" />
                            </button>
                        </div>
                    ) : (
                        <div className="flex items-center gap-3">
                            <Link href="/login" className="text-xs font-bold uppercase tracking-widest text-white/60 hover:text-white px-4 py-2">
                                Entrar
                            </Link>
                            <Link href="/register" className="bg-white text-black text-xs font-black uppercase tracking-widest px-6 py-2.5 rounded-full hover:bg-accent-gold transition-all shadow-xl shadow-white/5">
                                Suscribirse
                            </Link>
                        </div>
                    )
                ) : (
                    <div className="flex items-center gap-4">
                        <div className="relative group">
                            <button className="flex items-center gap-1.5 text-white/60 hover:text-white transition-colors p-2">
                                <Globe className="w-4 h-4" />
                                <span className="text-[10px] font-bold uppercase">ES</span>
                                <ChevronDown className="w-3 h-3" />
                            </button>
                            <div className="absolute right-0 top-full mt-2 w-32 bg-[#1a1a1a] border border-white/10 rounded-lg shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all flex flex-col overflow-hidden">
                                {['Español (ES)', 'English (EN)', '中文 (ZH)', 'Français (FR)'].map((lang) => (
                                    <button key={lang} className="text-left px-4 py-2 text-[11px] font-medium text-white/70 hover:text-white hover:bg-white/5 transition-colors">
                                        {lang}
                                    </button>
                                ))}
                            </div>
                        </div>
                        
                        <div className="flex items-center gap-3 border-l border-white/10 pl-4">
                            <Link href="/login" className="text-xs font-bold uppercase tracking-widest text-white/60 hover:text-white px-4 py-2">
                                Entrar
                            </Link>
                            <Link href="/register" className="bg-white text-black text-xs font-black uppercase tracking-widest px-6 py-2.5 rounded-full hover:bg-accent-gold transition-all shadow-xl shadow-white/5">
                                Suscribirse
                            </Link>
                        </div>
                    </div>
                )}
            </div>
        </nav>
    );
}

function Zap(props: any) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M4 14.71 13 3.5v9h7L11 20.5v-9z" />
        </svg>
    )
}
