'use client';

import { useState, Suspense } from 'react';
import AIAvatarBuilder from '@/components/AIAvatarBuilder';
import ProfessionalAvatarBuilder from '@/components/ProfessionalAvatarBuilder';
import { Sparkles, Box } from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

function NewAvatarContent() {
    const searchParams = useSearchParams();
    const typeParam = searchParams.get('type');
    const defaultTab = typeParam === 'professional' ? 'professional' : 'ai';
    const [activeTab, setActiveTab] = useState<'ai' | 'professional'>(defaultTab);

    return (
        <div className="min-h-screen bg-[#050505] text-white overflow-hidden flex flex-col">
            {/* Header minimalista para la página con Opciones de Pestañas integradas */}
            <header className="h-16 border-b border-white/5 flex flex-col md:flex-row items-center justify-between px-6 bg-black/80 backdrop-blur-md sticky top-0 z-50">
                <Link href="/dashboard" className="text-sm font-bold tracking-wider hover:text-accent-purple transition-colors flex items-center gap-2">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 12H5M12 19l-7-7 7-7" /></svg>
                    Volver a Creadores
                </Link>

                <div className="flex bg-white/5 p-1 rounded-xl border border-white/10 mt-2 md:mt-0">
                    <button
                        onClick={() => setActiveTab('ai')}
                        className={cn(
                            "flex items-center gap-2 px-6 py-2 rounded-lg text-xs font-black uppercase tracking-widest transition-all",
                            activeTab === 'ai' 
                                ? "bg-gradient-to-r from-pink-500 to-violet-500 text-white shadow-[0_0_15px_rgba(236,72,153,0.3)]" 
                                : "text-white/40 hover:text-white/80 hover:bg-white/5"
                        )}
                    >
                        <Sparkles className="w-3.5 h-3.5" />
                        Imagen IA (Rápido)
                    </button>
                    <button
                        onClick={() => setActiveTab('professional')}
                        className={cn(
                            "flex items-center gap-2 px-6 py-2 rounded-lg text-xs font-black uppercase tracking-widest transition-all",
                            activeTab === 'professional' 
                                ? "bg-white/10 text-white shadow-inner" 
                                : "text-white/40 hover:text-white/80 hover:bg-white/5"
                        )}
                    >
                        <Box className="w-3.5 h-3.5" />
                        Profesional (3D)
                    </button>
                </div>
                
                <div className="w-32 hidden md:block"></div> {/* Spacer to keep tabs centered */}
            </header>

            <main className="flex-1 relative overflow-hidden">
                {activeTab === 'ai' ? (
                    <AIAvatarBuilder />
                ) : (
                    <ProfessionalAvatarBuilder />
                )}
            </main>
        </div>
    );
}

export default function NewAvatarPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-[#050505] flex items-center justify-center text-white/50">Cargando constructor...</div>}>
            <NewAvatarContent />
        </Suspense>
    );
}
