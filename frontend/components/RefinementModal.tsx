'use client';

import React, { useState } from 'react';
import { X, Sparkles, Check, RefreshCw, Layers, Zap, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RefinementModalProps {
    isOpen: boolean;
    onClose: () => void;
    originalImage: string | null; // Base64 snapshot from Canvas
    refinedImage: string | null;  // Base64 from AI
    isRefining: boolean;
    onApply: () => void;
    onRegenerate: () => void;
}

export default function RefinementModal({
    isOpen,
    onClose,
    originalImage,
    refinedImage,
    isRefining,
    onApply,
    onRegenerate
}: RefinementModalProps) {
    const [viewMode, setViewMode] = useState<'side-by-side' | 'overlay'>('side-by-side');
    const [overlayProgress, setOverlayProgress] = useState(50);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-xl p-4 animate-in fade-in duration-300">
            <div className="bg-[#0f0f1a] text-white w-full max-w-6xl rounded-[2.5rem] border border-white/10 shadow-[0_0_100px_rgba(168,85,247,0.15)] flex flex-col overflow-hidden max-h-[95vh] relative">
                
                {/* Header Decoration */}
                <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-transparent via-accent-purple to-transparent opacity-50" />
                
                {/* Close Button */}
                <button 
                    onClick={onClose} 
                    className="absolute top-8 right-8 p-3 bg-white/5 hover:bg-white/10 rounded-2xl transition-all border border-white/5 z-50 group"
                >
                    <X className="w-5 h-5 text-white/40 group-hover:text-white group-hover:rotate-90 transition-all" />
                </button>

                {/* Main Content */}
                <div className="p-10 flex flex-col h-full overflow-y-auto">
                    
                    <header className="mb-10 text-center relative">
                        <div className="flex items-center justify-center gap-3 mb-4">
                            <div className="h-[1px] w-12 bg-white/10" />
                            <div className="px-4 py-1 bg-accent-purple/10 border border-accent-purple/30 rounded-full flex items-center gap-2">
                                <Sparkles className="w-3.5 h-3.5 text-accent-purple animate-pulse" />
                                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-accent-purple">Flux.1 Hyper-Realism</span>
                            </div>
                            <div className="h-[1px] w-12 bg-white/10" />
                        </div>
                        <h2 className="text-3xl font-black tracking-tight mb-2 uppercase">REFINAMIENTO DE IDENTIDAD</h2>
                        <p className="text-white/40 text-xs font-bold uppercase tracking-widest">Transformando Geometría 3D en Textura Fotográfica</p>
                    </header>

                    <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-10 min-h-[500px]">
                        
                        {/* Comparison View Area */}
                        <div className="lg:col-span-8 flex flex-col gap-6">
                            <div className="relative flex-1 rounded-3xl overflow-hidden border border-white/5 bg-black/40 group">
                                {isRefining ? (
                                    <div className="absolute inset-0 flex flex-col items-center justify-center z-20 bg-black/40 backdrop-blur-md">
                                        <div className="relative">
                                            <div className="w-24 h-24 border-t-2 border-accent-purple rounded-full animate-spin" />
                                            <Sparkles className="w-8 h-8 text-accent-purple absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
                                        </div>
                                        <div className="mt-8 text-center">
                                            <h3 className="text-xl font-black uppercase tracking-widest mb-2">Sintetizando Poros y Micro-Detalle...</h3>
                                            <div className="flex gap-2 justify-center">
                                                {['Estructura facial fijada', 'Generando piel', 'Renderizando iluminación'].map((msg, i) => (
                                                    <div key={i} className="px-3 py-1 bg-white/5 rounded-lg text-[9px] font-bold text-white/30 animate-pulse" style={{ animationDelay: `${i * 0.5}s` }}>
                                                        {msg}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                ) : viewMode === 'side-by-side' ? (
                                    <div className="flex w-full h-full gap-1 p-1">
                                        <div className="flex-1 relative group/original">
                                            <img src={originalImage || ''} alt="Original" className="w-full h-full object-cover" />
                                            <div className="absolute bottom-6 left-6 px-4 py-2 bg-black/60 backdrop-blur-xl border border-white/10 rounded-xl">
                                                <span className="text-[10px] font-black uppercase tracking-widest text-white/40">3D Mannequin Base</span>
                                            </div>
                                        </div>
                                        <div className="flex-1 relative group/refined">
                                            <img src={refinedImage || ''} alt="Refined" className="w-full h-full object-cover" />
                                            <div className="absolute bottom-6 left-6 px-4 py-2 bg-accent-purple/80 backdrop-blur-xl border border-white/20 rounded-xl shadow-[0_0_20px_rgba(168,85,247,0.4)]">
                                                <span className="text-[10px] font-black uppercase tracking-widest text-white">AI Hyper-Realism</span>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="relative w-full h-full cursor-col-resize select-none overflow-hidden">
                                        <img src={originalImage || ''} alt="Original" className="absolute inset-0 w-full h-full object-cover" />
                                        <div 
                                            className="absolute inset-0 overflow-hidden" 
                                            style={{ clipPath: `inset(0 ${100 - overlayProgress}% 0 0)` }}
                                        >
                                            <img src={refinedImage || ''} alt="Refined" className="w-full h-full object-cover" />
                                        </div>
                                        {/* Slider Line */}
                                        <div 
                                            className="absolute top-0 bottom-0 w-1 bg-accent-purple shadow-[0_0_15px_rgba(168,85,247,0.8)] z-10"
                                            style={{ left: `${overlayProgress}%` }}
                                        >
                                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 bg-accent-purple rounded-full flex items-center justify-center border-4 border-[#0f0f1a] shadow-2xl">
                                                <Layers className="w-4 h-4 text-white" />
                                            </div>
                                        </div>
                                        {/* Interaction Area */}
                                        <input 
                                            type="range" min="0" max="100" value={overlayProgress} 
                                            onChange={(e) => setOverlayProgress(parseInt(e.target.value))}
                                            className="absolute inset-0 w-full h-full opacity-0 z-30 cursor-col-resize"
                                        />
                                    </div>
                                )}
                            </div>

                            {/* View Controls */}
                            <div className="flex justify-center gap-4">
                                <button 
                                    onClick={() => setViewMode('side-by-side')}
                                    className={cn(
                                        "px-6 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-2 border",
                                        viewMode === 'side-by-side' ? "bg-white text-black border-white" : "bg-white/5 text-white/40 border-white/10 hover:bg-white/10"
                                    )}
                                >
                                    <Layers className="w-3.5 h-3.5" />
                                    Lado a Lado
                                </button>
                                <button 
                                    onClick={() => setViewMode('overlay')}
                                    className={cn(
                                        "px-6 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-2 border",
                                        viewMode === 'overlay' ? "bg-white text-black border-white" : "bg-white/5 text-white/40 border-white/10 hover:bg-white/10"
                                    )}
                                >
                                    <Zap className="w-3.5 h-3.5" />
                                    Slider Interactiva
                                </button>
                            </div>
                        </div>

                        {/* Actions Sidebar Area */}
                        <div className="lg:col-span-4 flex flex-col justify-center border-l border-white/5 pl-10 space-y-10">
                            
                            <div className="space-y-4">
                                <h4 className="text-[11px] font-black uppercase tracking-[0.2em] text-white/30 flex items-center gap-2">
                                    <Info className="w-3.5 h-3.5" />
                                    Diagnóstico de IA
                                </h4>
                                <div className="p-6 bg-white/5 rounded-3xl border border-white/5 space-y-4">
                                    <div className="flex justify-between items-center">
                                        <span className="text-[10px] font-bold text-white/40">Consistencia Estructural</span>
                                        <span className="text-[10px] font-black text-green-400">98.2%</span>
                                    </div>
                                    <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                                        <div className="h-full bg-green-400 w-[98%]" />
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-[10px] font-bold text-white/40">Fidelidad de Piel</span>
                                        <span className="text-[10px] font-black text-accent-purple">8K Ultra</span>
                                    </div>
                                    <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                                        <div className="h-full bg-accent-purple w-[100%]" />
                                    </div>
                                    <p className="text-[9px] text-white/20 italic leading-relaxed">
                                        * ControlNet Depth mantiene las proporciones exactas de tu modelo 3D mientras sintetiza texturas realistas.
                                    </p>
                                </div>
                            </div>

                            <div className="flex flex-col gap-4">
                                <button 
                                    onClick={onRegenerate}
                                    disabled={isRefining}
                                    className="w-full py-5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl flex items-center justify-center gap-3 transition-all font-black uppercase text-xs tracking-widest disabled:opacity-50"
                                >
                                    <RefreshCw className={cn("w-4 h-4", isRefining && "animate-spin")} />
                                    Regenerar Variación
                                </button>
                                <button 
                                    onClick={onApply}
                                    disabled={isRefining || !refinedImage}
                                    className="w-full py-6 bg-accent-purple hover:scale-[1.02] active:scale-[0.98] rounded-3xl flex items-center justify-center gap-3 transition-all font-black uppercase text-sm tracking-[0.2em] text-white shadow-[0_0_30px_rgba(168,85,247,0.4)] disabled:opacity-50 disabled:hover:scale-100"
                                >
                                    <Check className="w-5 h-5" />
                                    Aplicar & Finalizar
                                </button>
                                <p className="text-center text-[9px] font-bold text-white/20 uppercase tracking-widest">
                                    Costo de Refinamiento: 25 Créditos Pro
                                </p>
                            </div>

                        </div>
                    </div>
                </div>

                {/* Footer Message */}
                <div className="bg-black/40 p-4 border-t border-white/5 text-center">
                    <p className="text-[9px] font-black uppercase tracking-[0.3em] text-white/10">Velora Director - Engine v4.0 Cinematic Skin Pipeline</p>
                </div>
            </div>
        </div>
    );
}
