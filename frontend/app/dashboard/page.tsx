'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
    Download,
    Sparkles,
    Play,
    Users,
    ChevronDown
} from 'lucide-react';
import { cn } from '@/lib/utils';
import Image from 'next/image';

const CATEGORIES = [
    { id: 'girls', label: 'Chicas' },
    { id: 'anime', label: 'Anime' },
    { id: 'boys', label: 'Chicos' }
];

const MOCK_AVATARS = [
    {
        id: '1',
        name: 'Olivia',
        age: 28,
        tagline: 'De espíritu alternativo que trabaja de asistente en una...',
        image: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=400',
    },
    {
        id: '2',
        name: 'Natalia',
        age: 19,
        tagline: 'Estudiante de primer año, intentando descubrir su camino...',
        image: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&q=80&w=400',
    },
    {
        id: '3',
        name: 'Isabella',
        age: 25,
        tagline: 'Tu novia española está  locamente enamorada de ti...',
        image: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&q=80&w=400',
    },
    {
        id: '4',
        name: 'Verónica',
        age: 55,
        tagline: 'La madre de tu mejor amigo. Está casada, es dominante...',
        image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=400',
    },
    {
        id: '5',
        name: 'Emma',
        age: 22,
        tagline: 'Gamer competitiva y amante de los gatos. Se frustra...',
        image: 'https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?auto=format&fit=crop&q=80&w=400',
    },
    {
        id: '6',
        name: 'Sophia',
        age: 31,
        tagline: 'Directora de marketing. Muy seria en el trabajo pero...',
        image: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&q=80&w=400',
    },
    {
        id: '7',
        name: 'Mia',
        age: 20,
        tagline: 'Vecina de al lado. Le gusta espiar cuando no le...',
        image: 'https://images.unsplash.com/photo-1554151228-14d9def656e4?auto=format&fit=crop&q=80&w=400',
    }
];

export default function DashboardPage() {
    const [activeCategory, setActiveCategory] = useState(CATEGORIES[0].id);

    return (
        <div className="min-h-full pb-20 pt-8 px-4 md:px-8 max-w-7xl mx-auto">

            {/* Header Flotante / Filtros */}
            <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-10 pb-4 border-b border-white/5 sticky top-0 bg-[#050505]/90 backdrop-blur-md z-10">
                <div className="flex items-center gap-6 overflow-x-auto w-full sm:w-auto pb-2 sm:pb-0">
                    {CATEGORIES.map(category => (
                        <button
                            key={category.id}
                            onClick={() => setActiveCategory(category.id)}
                            className={cn(
                                "text-sm font-bold tracking-wider relative whitespace-nowrap px-1 py-2 transition-colors",
                                activeCategory === category.id
                                    ? "text-accent-purple"
                                    : "text-white/60 hover:text-white"
                            )}
                        >
                            {/* Un tab visualmente minimalista estilo Candy.ai */}
                            {category.label}
                            {activeCategory === category.id && (
                                <span className="absolute bottom-0 left-0 w-full h-[2px] bg-accent-purple rounded-t-full" />
                            )}
                        </button>
                    ))}
                </div>

                <div className="flex items-center gap-4 ml-auto">
                    <button className="flex items-center gap-2 bg-gradient-to-r from-accent-purple/20 to-transparent border border-accent-purple/30 text-accent-purple px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider hover:border-accent-purple/60 transition-colors">
                        <Sparkles className="w-3 h-3 fill-current" />
                        Prémium 70% DESCT
                    </button>

                    <button className="flex items-center gap-2 text-white/80 hover:text-white transition-colors bg-white/5 border border-white/10 px-4 py-2 rounded-full text-sm font-medium">
                        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-pink-500 to-orange-400"></div>
                        <span>Mi perfil</span>
                        <ChevronDown className="w-4 h-4 ml-1 opacity-50" />
                    </button>
                </div>
            </header>

            {/* Grid de Contenido */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-4 gap-6">

                {/* 1. Tarjeta: Crear Avatar IA (Rápido) */}
                <Link href="/dashboard/avatars/new?type=ai">
                    <div className="group relative rounded-2xl overflow-hidden aspect-[3/4] border-2 border-dashed border-pink-500/30 hover:border-pink-500/80 bg-gradient-to-b from-pink-500/5 to-transparent transition-all duration-300 flex flex-col items-center justify-center p-6 text-center cursor-pointer h-full hover:bg-pink-500/10">
                        <div className="absolute inset-0 bg-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                        <div className="w-16 h-16 rounded-full bg-pink-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                            <Sparkles className="w-8 h-8 text-pink-400" />
                        </div>
                        <h3 className="text-xl font-bold tracking-tight mb-2 text-white">Avatar IA</h3>
                        <p className="text-sm text-white/50 mb-6">Generación rápida con IA en segundos</p>
                        <div className="bg-gradient-to-r from-pink-500 to-violet-500 text-white px-6 py-3 rounded-full text-xs font-black uppercase tracking-wider shadow-[0_0_15px_rgba(236,72,153,0.3)] w-fit">
                            Crear Rápido
                        </div>
                    </div>
                </Link>

                {/* 2. Tarjeta: Crear Avatar 3D (Avanzado) */}
                <Link href="/dashboard/avatars/new?type=professional">
                    <div className="group relative rounded-2xl overflow-hidden aspect-[3/4] border-2 border-dashed border-blue-500/30 hover:border-blue-500/80 bg-gradient-to-b from-blue-500/5 to-transparent transition-all duration-300 flex flex-col items-center justify-center p-6 text-center cursor-pointer h-full hover:bg-blue-500/10">
                        <div className="absolute inset-0 bg-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                        <div className="w-16 h-16 rounded-full bg-blue-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                            <Users className="w-8 h-8 text-blue-400" />
                        </div>
                        <h3 className="text-xl font-bold tracking-tight mb-2 text-white">Avatar 3D</h3>
                        <p className="text-sm text-white/50 mb-6">Personalizado con esculpido de maniquí</p>
                        <div className="bg-white/10 border border-white/20 text-white px-6 py-3 rounded-full text-xs font-black uppercase tracking-wider shadow-lg hover:bg-white/20 w-fit transition-colors">
                            Crear 3D
                        </div>
                    </div>
                </Link>

                {/* 2. Tarjetas de Modelos/Avatares */}
                {MOCK_AVATARS.map((avatar) => (
                    <div
                        key={avatar.id}
                        className="group relative rounded-3xl overflow-hidden aspect-[3/4] bg-[#111] cursor-pointer"
                    >
                        {/* Imagen de fondo cover */}
                        <div className="absolute inset-0">
                            {/*eslint-disable-next-line @next/next/no-img-element*/}
                            <img
                                src={avatar.image}
                                alt={avatar.name}
                                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                            />
                            {/* Gradiente oscuro inferior para legibilidad del texto */}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
                        </div>

                        {/* Contenido flotante inferior */}
                        <div className="absolute inset-x-0 bottom-0 p-5 flex flex-col items-start translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
                            <div className="flex items-baseline gap-2 mb-1">
                                <h3 className="text-2xl font-bold text-white tracking-tight drop-shadow-md">
                                    {avatar.name}
                                </h3>
                                <span className="text-lg font-medium text-white/80 drop-shadow-md">{avatar.age}</span>
                            </div>

                            <p className="text-sm text-white/80 line-clamp-2 leading-snug mb-4 drop-shadow-sm">
                                {avatar.tagline}
                            </p>

                            {/* CTA Action - Reveal on hover or always visible, Candy.ai style */}
                            <button className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-accent-purple to-purple-500 hover:from-purple-500 hover:to-accent-purple text-white py-3 rounded-full text-sm font-bold shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40 transition-all opacity-90 group-hover:opacity-100">
                                <Download className="w-4 h-4" />
                                <span>Juega conmigo</span>
                            </button>
                        </div>
                    </div>
                ))}

            </div>
        </div>
    );
}
