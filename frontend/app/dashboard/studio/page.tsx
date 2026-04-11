'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import TierSelector from '@/components/TierSelector';
import AutoDirector from '@/components/AutoDirector';
import { api, API_BASE } from '@/lib/api';
import {
    Zap,
    Trash2,
    Sparkles,
    Users,
    ChevronRight,
    PlusCircle,
    CheckCircle2,
    Crown,
    ImageOff,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';

interface SavedAvatar {
    id: number;
    name: string;
    texture_url: string;
    status: string;
    created_at: string;
    is_hd?: boolean;
}

export interface Shot {
    id?: number;
    order: number;
    prompt: string;
    motion_prompt?: string;
    camera_movement: string;
    lighting: string;
    mood: string;
    dialogue: string;
    negative_prompt: string;
    duration_target_sec: number;
    status?: 'pending' | 'generating' | 'done';
    preview_url?: string;
    project_id?: number;
}

type Step = 'tier' | 'avatar' | 'workflow';

const TIER_SHOTS: Record<number, { min: number; max: number }> = {
    1: { min: 3, max: 8 },
    2: { min: 5, max: 15 },
    3: { min: 8, max: 40 },
    11: { min: 3, max: 8 }, 12: { min: 3, max: 8 }, 13: { min: 3, max: 8 },
    21: { min: 5, max: 15 }, 22: { min: 5, max: 15 }, 23: { min: 5, max: 15 },
    31: { min: 8, max: 40 }, 32: { min: 8, max: 40 }, 33: { min: 8, max: 40 },
};

const getBaseTier = (id: number): number => {
    if (id >= 10 && id < 20) return 1;
    if (id >= 20 && id < 30) return 2;
    if (id >= 30 && id < 40) return 3;
    return id;
};

// Avatar skeleton card
function AvatarSkeleton() {
    return (
        <div className="rounded-3xl overflow-hidden aspect-[3/4] bg-white/5 animate-pulse">
            <div className="w-full h-full bg-gradient-to-b from-white/10 to-white/5" />
        </div>
    );
}

function createDefaultShots(count: number): Shot[] {
    return Array.from({ length: count }, (_, i) => ({
        order: i,
        prompt: '',
        camera_movement: 'dolly_in',
        lighting: 'warm_golden',
        mood: 'intense',
        dialogue: '',
        negative_prompt: '',
        duration_target_sec: 10,
        status: 'pending'
    }));
}

function StudioContent() {
    const [step, setStep] = useState<Step>('tier');
    const [selectedTier, setSelectedTier] = useState(2);
    const [projectTitle, setProjectTitle] = useState('');
    const [globalPrompt, setGlobalPrompt] = useState('');
    const [stylePreset] = useState('hyper-realistic');
    const [targetDurationSec, setTargetDurationSec] = useState(60); // 1 min default
    const [shots, setShots] = useState<Shot[]>(createDefaultShots(5));
    const [avatarPrompt, setAvatarPrompt] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');
    const [isMasterAdmin, setIsMasterAdmin] = useState(false);
    const [isMock, setIsMock] = useState(false);
    const [videoEngine, setVideoEngine] = useState('mock');
    const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
    const [savedAvatars, setSavedAvatars] = useState<SavedAvatar[]>([]);
    const [avatarsLoading, setAvatarsLoading] = useState(true);
    const [hoveredAvatarId, setHoveredAvatarId] = useState<number | null>(null);
    
    const searchParams = useSearchParams();
    const avatarIdParam = searchParams?.get('avatar_id');
    const [selectedAvatarId, setSelectedAvatarId] = useState<number | null>(null);

    // Load real avatars from backend
    useEffect(() => {
        if (!api.isLoggedIn()) { setAvatarsLoading(false); return; }
        api.listAvatars()
            .then(list => {
                // Extend each item to carry the is_hd flag from metadata
                setSavedAvatars(list as SavedAvatar[]);
            })
            .catch(() => setSavedAvatars([]))
            .finally(() => setAvatarsLoading(false));
    }, []);

    useEffect(() => {
        if (avatarIdParam) {
            const id = parseInt(avatarIdParam);
            setSelectedAvatarId(id);
            setStep('workflow');
            // Try to find avatar name in the loaded list
            const found = savedAvatars.find(a => a.id === id);
            const label = found ? found.name : `Avatar #${id}`;
            setGlobalPrompt(`Modelo: ${label}, estilo hiperrealista. `);
            setAvatarPrompt(`Seleccionaste: ${label}`);
        }
    }, [avatarIdParam, savedAvatars]);

    useEffect(() => {
        if (api.isLoggedIn()) {
            api.getMe().then(u => {
                setIsMasterAdmin(u.is_admin && u.email === 'admin@ai-video.com');
            }).catch(() => { });
        }
    }, []);

    const handleSelectAvatar = (avatar: SavedAvatar) => {
        setSelectedAvatarId(avatar.id);
        setGlobalPrompt(`Modelo: ${avatar.name}, estilo hiperrealista de alta fidelidad. `);
        setAvatarPrompt(`Avatar seleccionado: ${avatar.name}`);
        setStep('workflow');
    };

    const handleTierSelect = (tier: number) => {
        setSelectedTier(tier);
        const cfg = TIER_SHOTS[tier] || TIER_SHOTS[1];
        if (shots.length < cfg.min) {
            setShots(createDefaultShots(cfg.min));
        } else if (shots.length > cfg.max) {
            setShots(shots.slice(0, cfg.max));
        }
    };

    const handleGenerateAll = async () => {
        setError('');
        setIsSubmitting(true);
        try {
            // If the Director Bot already created a real project, use that ID directly
            const existingId = selectedProjectId;
            if (existingId && Number.isInteger(existingId) && existingId > 0) {
                console.log(`[Studio] Using existing Director project: ${existingId}`);
                await api.startGeneration(existingId);
                window.location.href = `/dashboard/collection`;
                return;
            }

            // Otherwise create a new project from manual shots
            if (!projectTitle.trim()) {
                setProjectTitle(`Proyecto de Video ${new Date().toLocaleDateString()}`);
            }
            const project = await api.createProject({
                title: projectTitle || 'Proyecto de Video',
                tier: getBaseTier(selectedTier),
                avatar_id: selectedAvatarId || undefined,
                target_duration_sec: targetDurationSec,
                global_prompt: globalPrompt,
                style_preset: stylePreset,
                is_mock: videoEngine === 'mock',
                video_engine: videoEngine,
                shots: shots.map(s => ({
                    prompt: s.prompt,
                    camera_movement: s.camera_movement,
                    lighting: s.lighting,
                    mood: s.mood,
                    dialogue: s.dialogue || undefined,
                    negative_prompt: s.negative_prompt || undefined,
                    duration_target_sec: s.duration_target_sec,
                })),
            });

            await api.startGeneration(project.id);
            window.location.href = `/dashboard/collection`;
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Error al crear el proyecto');
        } finally {
            setIsSubmitting(false);
        }
    };

    // Step indicator header (replaces the old top Navbar)
    const steps: { key: Step; label: string }[] = [
        { key: 'tier', label: 'Tier' },
        { key: 'avatar', label: 'Avatar' },
        { key: 'workflow', label: 'Workflow' },
    ];

    return (
        <div className="flex flex-col h-full bg-[#0c0c0c] text-white font-sans overflow-hidden">

            {/* Step Navigation Bar (inside dashboard layout) */}
            <div className="flex items-center justify-between px-6 py-3 border-b border-white/5 bg-[#0c0c0c] shrink-0">
                {/* Step pills */}
                <div className="flex items-center gap-1">
                    {steps.map((s, idx) => (
                        <button
                            key={s.key}
                            onClick={() => setStep(s.key)}
                            className={cn(
                                "flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-semibold transition-all",
                                step === s.key
                                    ? "bg-accent-purple text-white"
                                    : "text-white/40 hover:text-white/70"
                            )}
                        >
                            <span className={cn(
                                "w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold border",
                                step === s.key
                                    ? "border-white/30 bg-white/20"
                                    : "border-white/20"
                            )}>
                                {idx + 1}
                            </span>
                            {s.label}
                        </button>
                    ))}
                </div>

                {/* Right: project title + generate button */}
                <div className="flex items-center gap-3">
                    <input
                        type="text"
                        placeholder="Nombre del proyecto..."
                        value={projectTitle}
                        onChange={e => setProjectTitle(e.target.value)}
                        className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white placeholder-white/30 focus:outline-none focus:border-accent-purple/60 w-48"
                    />
                    <button
                        onClick={handleGenerateAll}
                        disabled={isSubmitting}
                        className="flex items-center gap-2 bg-accent-purple hover:bg-purple-600 disabled:opacity-50 text-white px-4 py-1.5 rounded-full text-sm font-bold transition-all"
                    >
                        <Zap className="w-4 h-4" />
                        {isSubmitting ? 'Generando...' : 'Continuar'}
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <main className="flex-1 flex flex-col min-h-0 overflow-hidden">

                {/* STEP 1: TIER SELECTION */}
                {step === 'tier' && (
                    <div className="flex-1 overflow-y-auto p-12 bg-[radial-gradient(circle_at_top,_rgba(255,215,0,0.05)_0%,_transparent_50%)]">
                        <div className="max-w-6xl mx-auto space-y-12">
                            <div className="text-center space-y-4">
                                <h1 className="text-4xl font-black uppercase tracking-tighter italic">
                                    {isMasterAdmin ? 'Modo Productor Especial' : 'Selecciona tu Potencia de Fuego'}
                                </h1>
                                <p className="text-white/40 text-sm max-w-xl mx-auto leading-relaxed">
                                    {isMasterAdmin
                                        ? 'Como administrador, tienes acceso total a todos los motores de renderizado sin coste de créditos.'
                                        : 'Cada tier desbloquea motores de vídeo más avanzados e infraestructura de GPU de gama alta.'}
                                </p>
                            </div>
                            <TierSelector
                                selectedTier={selectedTier}
                                onSelect={handleTierSelect}
                                isAdmin={isMasterAdmin}
                            />
                            <div className="flex justify-center">
                                <button
                                    onClick={() => setStep('avatar')}
                                    className="flex items-center gap-2 bg-accent-purple hover:bg-purple-600 text-white px-8 py-3 rounded-full font-bold transition-all"
                                >
                                    Siguiente <ChevronRight className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* STEP 2: AVATAR SELECTION */}
                {step === 'avatar' && (
                    <div className="flex-1 overflow-y-auto p-4 md:p-8 bg-[#050505]">
                        <div className="max-w-7xl mx-auto animate-in slide-in-from-bottom-5 duration-700 pb-20">

                            <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-10 pb-4 border-b border-white/5 sticky top-0 bg-[#050505]/90 backdrop-blur-md z-10">
                                <div>
                                    <h2 className="text-xl font-black uppercase tracking-tighter">Elige tu Avatar</h2>
                                    <p className="text-white/40 text-xs mt-1">Tus avatares guardados aparecen aquí. Puedes crear uno nuevo en cualquier momento.</p>
                                </div>
                                <Link
                                    href="/dashboard/avatars/new"
                                    className="flex items-center gap-2 bg-gradient-to-r from-accent-purple/20 to-transparent border border-accent-purple/30 text-accent-purple px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider hover:border-accent-purple/60 hover:bg-accent-purple/10 transition-all shrink-0"
                                >
                                    <Sparkles className="w-3 h-3" />
                                    Crear Avatar HD
                                </Link>
                            </header>

                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">

                                {/* Crear Nuevo — always first */}
                                <div
                                    onClick={() => setStep('workflow')}
                                    className="group relative rounded-2xl overflow-hidden aspect-[3/4] border-2 border-dashed border-white/20 hover:border-accent-purple/50 bg-gradient-to-b from-white/5 to-transparent transition-all duration-300 flex flex-col items-center justify-center p-6 text-center cursor-pointer hover:bg-white/5"
                                >
                                    <div className="absolute inset-0 bg-accent-purple/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl" />
                                    <div className="w-16 h-16 rounded-full bg-accent-purple/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                        <Users className="w-8 h-8 text-accent-purple" />
                                    </div>
                                    <h3 className="text-xl font-bold tracking-tight mb-2">Sin avatar</h3>
                                    <p className="text-sm text-white/50 mb-6">Continuar directo al workflow</p>
                                    <div className="bg-accent-purple text-white px-6 py-3 rounded-full text-sm font-bold uppercase tracking-wider shadow-lg shadow-purple-500/20 w-fit">
                                        Continuar
                                    </div>
                                </div>

                                {/* Skeleton loaders while fetching */}
                                {avatarsLoading && Array.from({ length: 3 }).map((_, i) => (
                                    <AvatarSkeleton key={`sk-${i}`} />
                                ))}

                                {/* Real saved avatar cards */}
                                {!avatarsLoading && savedAvatars.map((avatar) => {
                                    const imgUrl = avatar.texture_url?.startsWith('http')
                                        ? avatar.texture_url
                                        : `${API_BASE}${avatar.texture_url}`;
                                    const isSelected = selectedAvatarId === avatar.id;
                                    const isHovered = hoveredAvatarId === avatar.id;

                                    return (
                                        <div
                                            key={avatar.id}
                                            onClick={() => handleSelectAvatar(avatar)}
                                            onMouseEnter={() => setHoveredAvatarId(avatar.id)}
                                            onMouseLeave={() => setHoveredAvatarId(null)}
                                            className={cn(
                                                "group relative rounded-3xl overflow-hidden aspect-[3/4] bg-[#111] cursor-pointer transition-all duration-300",
                                                isSelected ? "ring-2 ring-accent-purple ring-offset-2 ring-offset-[#050505]" : "hover:ring-1 hover:ring-white/20"
                                            )}
                                        >
                                            {/* Image */}
                                            <div className="absolute inset-0">
                                                {/*eslint-disable-next-line @next/next/no-img-element*/}
                                                <img
                                                    src={imgUrl}
                                                    alt={avatar.name}
                                                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                                                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                                                />
                                                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent" />
                                            </div>

                                            {/* HD Badge */}
                                            {avatar.texture_url?.includes('avatar_hd_') && (
                                                <div className="absolute top-3 right-3 flex items-center gap-1 bg-gradient-to-r from-yellow-500/90 to-amber-600/90 backdrop-blur-sm px-2 py-0.5 rounded-full">
                                                    <Crown className="w-3 h-3 text-white" />
                                                    <span className="text-[10px] font-black text-white uppercase tracking-wider">HD</span>
                                                </div>
                                            )}

                                            {/* Selected indicator */}
                                            {isSelected && (
                                                <div className="absolute top-3 left-3">
                                                    <CheckCircle2 className="w-5 h-5 text-accent-purple fill-accent-purple/30" />
                                                </div>
                                            )}

                                            {/* Info overlay */}
                                            <div className={cn(
                                                "absolute inset-x-0 bottom-0 p-5 flex flex-col items-start transition-transform duration-300",
                                                isHovered ? "translate-y-0" : "translate-y-3"
                                            )}>
                                                <h3 className="text-xl font-bold text-white tracking-tight drop-shadow-md mb-1 truncate w-full">
                                                    {avatar.name}
                                                </h3>
                                                <p className="text-xs text-white/50 mb-4">
                                                    {new Date(avatar.created_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })}
                                                </p>
                                                <button className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-accent-purple to-purple-500 hover:from-purple-500 hover:to-accent-purple text-white py-2.5 rounded-full text-sm font-bold shadow-lg shadow-purple-500/20 transition-all">
                                                    <Zap className="w-4 h-4" />
                                                    <span>Usar este Avatar</span>
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })}

                            </div>

                            {/* Empty state */}
                            {!avatarsLoading && savedAvatars.length === 0 && (
                                <div className="flex flex-col items-center justify-center py-24 text-center">
                                    <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6">
                                        <ImageOff className="w-10 h-10 text-white/20" />
                                    </div>
                                    <h3 className="text-xl font-bold text-white/60 mb-2">Aún no tienes avatares</h3>
                                    <p className="text-sm text-white/30 mb-8 max-w-sm">
                                        Crea tu primer avatar hiperrealista con el constructor 3D + refinamiento IA.
                                    </p>
                                    <Link
                                        href="/dashboard/avatars/new"
                                        className="flex items-center gap-2 bg-accent-purple hover:bg-purple-600 text-white px-8 py-3 rounded-full font-bold transition-all shadow-lg shadow-purple-500/20"
                                    >
                                        <PlusCircle className="w-5 h-5" />
                                        Crear mi primer Avatar
                                    </Link>
                                </div>
                            )}

                        </div>
                    </div>
                )}

                {/* STEP 3: AUTO-DIRECTOR */}
                {step === 'workflow' && (
                    <AutoDirector
                        shots={shots}
                        onShotsChange={setShots}
                        tier={selectedTier}
                        globalPrompt={globalPrompt || avatarPrompt}
                        onGlobalPromptChange={setGlobalPrompt}
                        onGenerateAll={handleGenerateAll}
                        isGenerating={isSubmitting}
                        isMock={isMock}
                        targetDurationSec={targetDurationSec}
                        onTargetDurationChange={setTargetDurationSec}
                        videoEngine={videoEngine}
                        onVideoEngineChange={setVideoEngine}
                        projectId={selectedProjectId}
                        onProjectIdChange={setSelectedProjectId}
                    />
                )}

            </main>

            {error && (
                <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-red-950 border border-red-500/50 px-6 py-3 rounded-xl text-xs font-bold text-red-100 flex items-center gap-3">
                    <Trash2 className="w-4 h-4 text-red-500" /> {error}
                </div>
            )}
        </div>
    );
}

export default function DashboardStudioPage() {
    return (
        <Suspense fallback={<div className="flex h-full items-center justify-center text-white">Cargando Estudio...</div>}>
            <StudioContent />
        </Suspense>
    );
}
