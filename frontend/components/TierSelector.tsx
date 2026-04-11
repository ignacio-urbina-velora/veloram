'use client';

import { useState } from 'react';
import {
    CheckCircle2,
    XCircle,
    Info
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface TierSelectorProps {
    selectedTier: number;
    onSelect: (tier: number) => void;
    isAdmin?: boolean;
}

const TIERS_DATA = [
    {
        title: "Tier 1 — Rápido (LTX-2 fp8)",
        color: 'border-purple-500',
        textColor: 'text-purple-500',
        shadowColor: 'shadow-purple-500/20',
        buttonClass: 'border-purple-500 text-purple-500 hover:bg-purple-500/10',
        featuresBase: [
            { text: 'IA LTX-2 fp8', included: true },
            { text: 'Resolución 720p', included: true },
            { text: 'Clonación facial básica', included: true },
            { text: 'Anatomía ultra-realista', included: false },
        ],
        plans: [
            { id: 11, name: 'Basic', price: 50, videos: 5 },
            { id: 12, name: 'Medium', price: 85, videos: 10 },
            { id: 13, name: 'Full', price: 150, videos: 20 },
        ]
    },
    {
        title: "Tier 2 — Profesional (Wan 2.2 FP8 + NSFW LoRA)",
        color: 'border-yellow-500',
        textColor: 'text-yellow-500',
        shadowColor: 'shadow-yellow-500/20',
        buttonClass: 'border-yellow-500 text-yellow-500 hover:bg-yellow-500/10',
        featuresBase: [
            { text: 'IA Wan 2.2 FP8', included: true },
            { text: 'Resolución Full HD', included: true },
            { text: 'Clonación facial avanzada', included: true },
            { text: 'Anatomía ultra-realista', included: true },
            { text: 'Interpolación 60 FPS', included: true },
        ],
        plans: [
            { id: 21, name: 'Basic Pro', price: 90, videos: 5, tag: 'RECOMMENDED' },
            { id: 22, name: 'Medium Pro', price: 159, videos: 10 },
            { id: 23, name: 'Full Pro', price: 299, videos: 20 },
        ]
    },
    {
        title: "Tier 3 — Cinematográfico (HunyuanVideo bf16 + Post Pesado)",
        color: 'border-cyan-500',
        textColor: 'text-cyan-500',
        shadowColor: 'shadow-cyan-500/20',
        buttonClass: 'border-cyan-500 text-cyan-500 hover:bg-cyan-500/10',
        featuresBase: [
            { text: 'IA HunyuanVideo bf16', included: true },
            { text: 'Resolución 4K Cinema', included: true },
            { text: 'Clonación facial perfecta', included: true },
            { text: 'Anatomía ultra-realista', included: true },
            { text: 'Control total de cámara', included: true },
            { text: 'Upscaling avanzado + Post', included: true }
        ],
        plans: [
            { id: 31, name: 'Basic Cinematic', price: 350, videos: 5, tag: 'BEST VALUE' },
            { id: 32, name: 'Medium Cinematic', price: 680, videos: 10 },
            { id: 33, name: 'Full Cinematic', price: 1350, videos: 20 },
        ]
    }
];

export default function TierSelector({ selectedTier, onSelect, isAdmin }: TierSelectorProps) {
    const [coupon, setCoupon] = useState('');

    const isDiscountActive = coupon.trim().length > 0;

    return (
        <div className="space-y-20 max-w-7xl mx-auto">

            {/* Cupón / Descuento Arriba */}
            <div className="max-w-md mx-auto relative group">
                <input
                    type="text"
                    placeholder="Código de Afiliado / Influencer..."
                    className="w-full bg-[#121212] border border-white/10 hover:border-white/20 rounded-2xl px-6 py-5 text-sm focus:outline-none focus:border-accent-gold/40 transition-all font-medium tracking-wide pr-32 text-center shadow-lg"
                    value={coupon}
                    onChange={(e) => setCoupon(e.target.value)}
                />
                <button className="absolute right-2 top-2 bottom-2 bg-white/10 text-white hover:bg-white hover:text-black px-6 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all">
                    {isDiscountActive ? 'Aplicado ✔️' : 'Aplicar'}
                </button>
            </div>

            {TIERS_DATA.map((tierGroup, groupIdx) => (
                <div key={groupIdx} className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">

                    {/* Banner / Letrero del Tier */}
                    <div className="text-center space-y-2">
                        <div className={cn("inline-block px-4 py-1.5 rounded-full border bg-opacity-10 text-xs font-black uppercase tracking-[0.2em] mb-2", tierGroup.color, tierGroup.textColor)}>
                            Categoría {groupIdx + 1}
                        </div>
                        <h2 className={cn("text-3xl md:text-4xl font-black tracking-tighter", tierGroup.textColor)}>
                            {tierGroup.title.split('—')[1] || tierGroup.title}
                        </h2>
                    </div>

                    {/* Planes dentro de este Tier */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {tierGroup.plans.map((plan) => {
                            const inflatedPrice = Math.round(plan.price * 1.4);
                            const finalPrice = isDiscountActive ? plan.price : inflatedPrice;
                            const isSelected = selectedTier === plan.id;

                            return (
                                <div
                                    key={plan.id}
                                    onClick={() => onSelect(plan.id)}
                                    className={cn(
                                        "relative bg-[#111] rounded-2xl border p-8 cursor-pointer transition-all duration-300 flex flex-col",
                                        tierGroup.color,
                                        isSelected ? `shadow-2xl ${tierGroup.shadowColor} scale-105 z-10` : "hover:border-opacity-70 border-opacity-30 hover:shadow-lg"
                                    )}
                                >
                                    {/* Top Tags */}
                                    <div className="flex justify-between items-start mb-6">
                                        <h3 className={cn("text-2xl font-bold tracking-tight", tierGroup.textColor)}>
                                            {plan.name}
                                        </h3>
                                        {plan.tag && (
                                            <div className="bg-white/10 text-white/80 text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-full border border-white/10">
                                                {plan.tag}
                                            </div>
                                        )}
                                    </div>

                                    {/* Price */}
                                    <div className="mb-6 flex flex-col gap-1">
                                        <div className="flex items-end gap-2">
                                            {isAdmin ? (
                                                <div className="text-4xl font-black text-white">$0</div>
                                            ) : (
                                                <>
                                                    {isDiscountActive && (
                                                        <span className="text-xl text-gray-500 line-through mb-1">${inflatedPrice}</span>
                                                    )}
                                                    <div className="text-4xl font-black text-white">
                                                        ${finalPrice}
                                                    </div>
                                                </>
                                            )}
                                            <div className="text-sm text-gray-500 mb-1">
                                                / mes
                                            </div>
                                        </div>

                                        {/* Mensaje de código de afiliado */}
                                        {!isAdmin && !isDiscountActive && (
                                            <div className="text-sm font-bold tracking-wide">
                                                <span className="text-accent-gold">Cód. de afiliado:</span> <span className="text-white">${plan.price}</span>
                                            </div>
                                        )}
                                        {!isAdmin && isDiscountActive && (
                                            <div className="text-sm font-bold tracking-wide text-green-400">
                                                Descuento de afiliado aplicado
                                            </div>
                                        )}
                                    </div>

                                    {/* Action Button */}
                                    <button className={cn(
                                        "w-full py-3 rounded-full text-sm font-bold transition-all border border-solid mb-8",
                                        tierGroup.buttonClass,
                                        isSelected && "bg-opacity-20 bg-current"
                                    )}>
                                        {isSelected ? 'Selected' : 'Subscribe now'}
                                    </button>

                                    {/* Features List */}
                                    <ul className="space-y-4 flex-1">
                                        <li className="flex items-center gap-3 text-sm font-bold text-white">
                                            <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0" />
                                            <span>{plan.videos} Videos / Month</span>
                                        </li>
                                        {tierGroup.featuresBase.map((f, i) => (
                                            <li key={i} className="flex items-center gap-3 text-sm">
                                                {f.included ? (
                                                    <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0" />
                                                ) : (
                                                    <XCircle className="w-5 h-5 text-gray-600 shrink-0" />
                                                )}
                                                <span className={f.included ? 'text-gray-300' : 'text-gray-600'}>
                                                    {f.text}
                                                </span>
                                                {f.included && <Info className="w-4 h-4 text-gray-600 ml-auto shrink-0 opacity-50" />}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            );
                        })}
                    </div>
                </div>
            ))}
        </div>
    );
}
