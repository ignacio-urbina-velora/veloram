'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import Navbar from '@/components/Navbar';
import { api, API_BASE } from '@/lib/api';
import { 
    Download, 
    Trash2, 
    Clock, 
    AlertCircle, 
    CheckCircle2, 
    Loader2, 
    Film, 
    Sparkles,
    Calendar,
    ChevronRight,
    RefreshCw,
    Plus,
    User2,
    PlayCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface Project {
    id: number;
    title: string;
    tier: number;
    status: string;
    final_video_url: string | null;
    total_cost_usd: number;
    created_at: string;
}

interface AvatarRecord {
    id: number;
    name: string;
    texture_url: string;
    status: string;
    created_at: string;
    styles?: Record<string, string>;
}

const TIER_NAMES: Record<number, { name: string; emoji: string; color: string }> = {
    1: { name: 'Quick', emoji: '⚡', color: 'var(--tier1-color)' },
    2: { name: 'Pro', emoji: '🎬', color: 'var(--tier2-color)' },
    3: { name: 'Cinematic', emoji: '🎥', color: 'var(--tier3-color)' },
};

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
    draft: { label: 'Borrador', color: 'var(--text-muted)' },
    queued: { label: 'En cola', color: '#f59e0b' },
    generating: { label: 'Generando...', color: '#22d3ee' },
    postprocessing: { label: 'Post-producción', color: '#a78bfa' },
    completed: { label: 'Completado', color: '#22c55e' },
    failed: { label: 'Error', color: '#ef4444' }
};

export default function CollectionPage() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [avatars, setAvatars] = useState<AvatarRecord[]>([]);
    const [user, setUser] = useState<{ username: string; credits: number } | null>(null);
    const [loading, setLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [activeTab, setActiveTab] = useState<'videos' | 'avatars'>('videos');

    const loadData = useCallback(async (silent = false) => {
        if (!silent) setLoading(true);
        else setIsRefreshing(true);
        try {
            const [userData, projectsData, avatarsData] = await Promise.all([
                api.getMe(),
                api.getProjects(),
                api.listAvatars().catch(() => []),
            ]);
            setUser(userData);
            setProjects(projectsData.sort((a: Project, b: Project) => b.id - a.id));
            setAvatars(avatarsData);
        } catch (err) {
            console.error("Failed to load collection:", err);
        } finally {
            setLoading(false);
            setIsRefreshing(false);
        }
    }, []);

    useEffect(() => {
        loadData();
    }, [loadData]);

    // Auto-polling for active generations
    useEffect(() => {
        const hasActiveProjects = projects.some(p =>
            ['generating', 'postprocessing', 'queued'].includes(p.status)
        );
        if (!hasActiveProjects) return;
        const interval = setInterval(() => { loadData(true); }, 8000);
        return () => clearInterval(interval);
    }, [projects, loadData]);

    const handleDelete = async (id: number) => {
        if (!confirm('¿Estás seguro de que quieres eliminar este proyecto?')) return;
        try {
            await fetch(`${API_BASE}/projects/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${api.getToken() ?? ''}` } });
            setProjects(prev => prev.filter(p => p.id !== id));
        } catch {
            alert('Error al eliminar el proyecto');
        }
    };

    const handleDeleteAvatar = async (id: number) => {
        if (!confirm('¿Eliminar este avatar de tu colección?')) return;
        try {
            await api.deleteAvatar(id);
            setAvatars(prev => prev.filter(a => a.id !== id));
        } catch {
            alert('Error al eliminar el avatar');
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0c0c0c] flex flex-col items-center justify-center">
                <Loader2 className="w-10 h-10 text-accent-purple animate-spin mb-4" />
                <p className="text-white/40 text-sm font-medium animate-pulse">Cargando tu colección...</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#0c0c0c] text-white">
            <Navbar />
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb-20">
                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
                    <div className="space-y-2">
                        <div className="flex items-center gap-3">
                            <h1 className="text-4xl font-black uppercase tracking-tighter italic text-white flex items-center gap-3">
                                Mi Colección
                            </h1>
                            {isRefreshing && <RefreshCw className="w-4 h-4 text-accent-purple animate-spin" />}
                        </div>
                        <p className="text-white/40 text-sm flex items-center gap-2">
                            <Clock className="w-4 h-4" />
                            Créditos: <span className="text-accent-secondary font-bold">${user?.credits.toFixed(2)}</span>
                        </p>
                    </div>
                    <div className="flex gap-3">
                        <Link href="/avatar" className="group flex items-center gap-2 bg-white/5 border border-white/10 hover:bg-white/10 text-white px-5 py-3 rounded-full font-bold text-sm tracking-wide transition-all">
                            <User2 className="w-4 h-4 text-pink-400" />
                            <span>Nuevo Avatar</span>
                        </Link>
                        <Link href="/studio" className="group flex items-center gap-2 bg-accent-purple hover:bg-purple-500 text-white px-6 py-3 rounded-full font-bold text-sm tracking-wide transition-all shadow-lg shadow-purple-500/20 active:scale-95">
                            <Plus className="w-4 h-4" />
                            <span>Nuevo Video</span>
                            <ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                        </Link>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-1 p-1 bg-white/5 rounded-xl w-fit mb-10">
                    {[
                        { key: 'videos', icon: Film, label: `Videos (${projects.length})` },
                        { key: 'avatars', icon: User2, label: `Avatares (${avatars.length})` },
                    ].map(({ key, icon: Icon, label }) => (
                        <button
                            key={key}
                            onClick={() => setActiveTab(key as 'videos' | 'avatars')}
                            className={cn(
                                'flex items-center gap-2 px-5 py-2.5 rounded-lg font-bold text-sm transition-all',
                                activeTab === key
                                    ? 'bg-white text-black shadow'
                                    : 'text-white/40 hover:text-white/70'
                            )}
                        >
                            <Icon className="w-4 h-4" />
                            {label}
                        </button>
                    ))}
                </div>

                {/* VIDEO PROJECTS TAB */}
                {activeTab === 'videos' && (
                    projects.length === 0 ? (
                        <div className="rounded-3xl border border-white/5 bg-white/[0.02] p-20 flex flex-col items-center justify-center text-center">
                            <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6">
                                <Film className="w-10 h-10 text-white/20" />
                            </div>
                            <h3 className="text-2xl font-bold mb-2">Tu colección está vacía</h3>
                            <p className="text-white/40 max-w-md mb-8 leading-relaxed">
                                Aún no has creado ningún video. Empieza ahora y genera contenido de alta calidad en minutos.
                            </p>
                            <Link href="/studio" className="bg-white text-black px-8 py-4 rounded-full font-bold hover:bg-white/90 transition-colors">
                                Crear mi primer video
                            </Link>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {projects.map((project) => {
                                const tierInfo = TIER_NAMES[project.tier] || TIER_NAMES[1];
                                const statusInfo = STATUS_LABELS[project.status] || STATUS_LABELS.draft;
                                const isGenerating = ['generating', 'postprocessing', 'queued'].includes(project.status);

                                return (
                                    <div key={project.id} className="group relative rounded-3xl border border-white/5 bg-[#111118] hover:border-white/10 transition-all duration-300 overflow-hidden flex flex-col">
                                        
                                        {/* Video preview / thumbnail area */}
                                        {project.final_video_url ? (
                                            <div className="relative w-full aspect-video bg-black overflow-hidden">
                                                <video
                                                    src={project.final_video_url.startsWith('http') ? project.final_video_url : `${API_BASE}${project.final_video_url}`}
                                                    className="w-full h-full object-cover opacity-90 group-hover:opacity-100 transition-opacity"
                                                    muted
                                                    loop
                                                    playsInline
                                                    onMouseEnter={e => (e.target as HTMLVideoElement).play()}
                                                    onMouseLeave={e => { (e.target as HTMLVideoElement).pause(); (e.target as HTMLVideoElement).currentTime = 0; }}
                                                />
                                                {/* Play hint overlay */}
                                                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                                    <div className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                                                        <PlayCircle className="w-6 h-6 text-white" />
                                                    </div>
                                                </div>
                                            </div>
                                        ) : isGenerating ? (
                                            <div className="w-full aspect-video bg-accent-purple/5 flex items-center justify-center border-b border-white/5">
                                                <div className="flex flex-col items-center gap-2">
                                                    <Loader2 className="w-8 h-8 text-accent-purple animate-spin" />
                                                    <span className="text-[10px] text-accent-purple/70 font-medium">{statusInfo.label}</span>
                                                </div>
                                            </div>
                                        ) : null}

                                        <div className="p-6 flex-1">
                                            <div className="flex items-start justify-between mb-4">
                                                <div className="space-y-1 overflow-hidden">
                                                    {/* ID badge */}
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-[9px] font-mono font-bold text-white/40 tracking-widest">
                                                            # {project.id}
                                                        </span>
                                                        <span className="text-[10px] font-bold uppercase tracking-widest text-[#aaa]">
                                                            {tierInfo.emoji} {tierInfo.name}
                                                        </span>
                                                    </div>
                                                    <h3 className="text-lg font-bold text-white truncate pr-2" title={project.title}>
                                                        {project.title}
                                                    </h3>
                                                </div>
                                                <div className={cn(
                                                    "shrink-0 flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold border",
                                                    project.status === 'completed' ? "bg-green-500/10 text-green-400 border-green-500/20" :
                                                    project.status === 'failed' ? "bg-red-500/10 text-red-400 border-red-500/20" :
                                                    "bg-accent-purple/10 text-accent-purple border-accent-purple/20"
                                                )}>
                                                    {isGenerating && <Loader2 className="w-2.5 h-2.5 animate-spin" />}
                                                    {project.status === 'completed' && <CheckCircle2 className="w-2.5 h-2.5" />}
                                                    {project.status === 'failed' && <AlertCircle className="w-2.5 h-2.5" />}
                                                    {statusInfo.label}
                                                </div>
                                            </div>

                                            {isGenerating && (
                                                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden mb-6">
                                                    <div className={cn(
                                                        "h-full bg-accent-purple transition-all duration-1000",
                                                        project.status === 'queued' ? "w-[15%]" :
                                                        project.status === 'generating' ? "w-[45%]" : "w-[85%]"
                                                    )} />
                                                </div>
                                            )}

                                            <div className="flex items-center justify-between text-[11px] text-white/30 pt-4 border-t border-white/[0.04]">
                                                <div className="flex items-center gap-1.5">
                                                    <Calendar className="w-3.5 h-3.5" />
                                                    <span>{new Date(project.created_at).toLocaleDateString()}</span>
                                                </div>
                                                <div className="flex items-center gap-1.5 font-mono text-accent-secondary">
                                                    <span>${project.total_cost_usd.toFixed(2)}</span>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="p-4 bg-white/[0.02] border-t border-white/[0.04] grid grid-cols-2 gap-3">
                                            {project.final_video_url ? (
                                                <a
                                                    href={project.final_video_url.startsWith('http') ? project.final_video_url : `${API_BASE}${project.final_video_url}`}
                                                    className="col-span-1 flex items-center justify-center gap-2 bg-white text-black py-2.5 rounded-xl font-bold text-xs hover:bg-white/90 transition-all"
                                                    download target="_blank" rel="noopener noreferrer"
                                                >
                                                    <Download className="w-3.5 h-3.5" />
                                                    Descargar
                                                </a>
                                            ) : (
                                                <button className="col-span-1 border border-white/5 text-white/20 py-2.5 rounded-xl font-bold text-xs cursor-not-allowed">
                                                    Procesando...
                                                </button>
                                            )}
                                            <button
                                                onClick={() => handleDelete(project.id)}
                                                className="col-span-1 flex items-center justify-center gap-2 bg-white/5 text-white/40 py-2.5 rounded-xl font-bold text-xs hover:bg-red-500/10 hover:text-red-400 transition-all"
                                            >
                                                <Trash2 className="w-3.5 h-3.5" />
                                                Eliminar
                                            </button>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )
                )}

                {/* AVATARS TAB */}
                {activeTab === 'avatars' && (
                    avatars.length === 0 ? (
                        <div className="rounded-3xl border border-white/5 bg-white/[0.02] p-20 flex flex-col items-center justify-center text-center">
                            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-pink-500/20 to-violet-500/20 flex items-center justify-center mb-6">
                                <User2 className="w-10 h-10 text-white/20" />
                            </div>
                            <h3 className="text-2xl font-bold mb-2">Sin avatares guardados</h3>
                            <p className="text-white/40 max-w-md mb-8 leading-relaxed">
                                Crea tu primer avatar 3D ultrarrealista personalizado con el Motor Humano Interactivo.
                            </p>
                            <Link href="/avatar" className="bg-gradient-to-r from-pink-500 to-violet-500 text-white px-8 py-4 rounded-full font-bold hover:opacity-90 transition-opacity flex items-center gap-2">
                                <Sparkles className="w-4 h-4" />
                                Crear mi Avatar
                            </Link>
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
                            {avatars.map((avatar) => {
                                const fullUrl = avatar.texture_url.startsWith('http')
                                    ? avatar.texture_url
                                    : `${API_BASE}${avatar.texture_url}`;

                                 return (
                                    <div key={avatar.id} className="group relative rounded-2xl overflow-hidden border border-white/5 bg-[#111118] hover:border-pink-500/30 transition-all duration-300">
                                        {/* Avatar Thumbnail */}
                                        <div className="aspect-[3/4] relative bg-gradient-to-b from-white/5 to-black overflow-hidden">
                                            {/* Debugging: console.log("Avatar URL:", fullUrl) */}
                                            <Image
                                                src={fullUrl}
                                                alt={avatar.name}
                                                fill
                                                unoptimized
                                                className="object-cover object-top group-hover:scale-105 transition-transform duration-500"
                                                onError={(e) => { 
                                                    console.error("Failed to load avatar image:", fullUrl);
                                                }}
                                            />
                                            {/* Overlay buttons on hover */}
                                            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4 gap-2">
                                                <Link
                                                    href={`/dashboard/avatars/new?avatar_id=${avatar.id}`}
                                                    className="flex items-center justify-center gap-2 bg-pink-500 text-white px-4 py-2 rounded-xl font-bold text-xs hover:bg-pink-600 transition-all shadow-lg shadow-pink-500/20"
                                                >
                                                    <Sparkles className="w-3.5 h-3.5" />
                                                    Revisar en 3D
                                                </Link>
                                                <Link
                                                    href={`/studio?avatar_id=${avatar.id}`}
                                                    className="flex items-center justify-center gap-2 bg-white text-black px-4 py-2 rounded-xl font-bold text-xs hover:bg-white/90 transition-all"
                                                >
                                                    <PlayCircle className="w-3.5 h-3.5" />
                                                    Usar en Video
                                                </Link>
                                                <button
                                                    onClick={() => handleDeleteAvatar(avatar.id)}
                                                    className="flex items-center justify-center gap-2 bg-red-500/20 text-red-300 border border-red-500/30 px-4 py-2 rounded-xl font-bold text-xs hover:bg-red-500/30 transition-all"
                                                >
                                                    <Trash2 className="w-3.5 h-3.5" />
                                                    Eliminar
                                                </button>
                                            </div>
                                        </div>

                                        {/* Avatar Info */}
                                        <div className="p-3">
                                            <p className="text-xs font-bold text-white truncate">{avatar.name}</p>
                                            <p className="text-[10px] text-white/30 mt-0.5">
                                                {new Date(avatar.created_at).toLocaleDateString('es-CL')}
                                            </p>
                                            {avatar.styles?.clothing && (
                                                <span className="mt-1.5 inline-block text-[9px] font-bold uppercase tracking-widest bg-pink-500/10 text-pink-400 border border-pink-500/20 px-2 py-0.5 rounded-full">
                                                    {avatar.styles.clothing}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )
                )}
            </main>
        </div>
    );
}
