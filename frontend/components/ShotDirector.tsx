'use client';

import { useState } from 'react';

interface Shot {
    id?: number;
    order: number;
    prompt: string;
    camera_movement: string;
    lighting: string;
    mood: string;
    dialogue: string;
    negative_prompt: string;
    duration_target_sec: number;
}

interface ShotDirectorProps {
    shots: Shot[];
    onShotsChange: (shots: Shot[]) => void;
    tier: number;
    maxShots: number;
    globalPrompt: string;
    onGlobalPromptChange: (val: string) => void;
    stylePreset: string;
    onStylePresetChange: (val: string) => void;
}

const CAMERA_OPTIONS = [
    { value: 'static', label: '📷 Estático' },
    { value: 'pan_left', label: '⬅️ Pan Izquierda' },
    { value: 'pan_right', label: '➡️ Pan Derecha' },
    { value: 'dolly_in', label: '🔍 Acercamiento' },
    { value: 'dolly_out', label: '🔭 Alejamiento' },
    { value: 'orbit', label: '🔄 Órbita' },
    { value: 'tilt_up', label: '⬆️ Tilt Arriba' },
    { value: 'tilt_down', label: '⬇️ Tilt Abajo' },
];

const STYLE_PRESETS = [
    { value: 'cinematic', label: '🎬 Cinematic' },
    { value: 'cyberpunk', label: '⚡ Cyberpunk' },
    { value: 'anime', label: '🎎 Anime' },
    { value: 'hyper-realistic', label: '📸 Realista' },
    { value: 'oil-painting', label: '🎨 Pintura' },
    { value: 'sketch', label: '✏️ Sketch' },
    { value: '3d-render', label: '🎮 3D Render' },
];

const LIGHTING_OPTIONS = ['natural', 'warm golden', 'cold blue', 'neon', 'studio'];
const MOOD_OPTIONS = ['neutral', 'intense', 'dramatic', 'mysterious', 'playful'];

export default function ShotDirector({
    shots, onShotsChange, tier, maxShots,
    globalPrompt, onGlobalPromptChange,
    stylePreset, onStylePresetChange
}: ShotDirectorProps) {
    const [activeShot, setActiveShot] = useState<number | null>(null);

    const updateShot = (index: number, updates: Partial<Shot>) => {
        const newShots = [...shots];
        newShots[index] = { ...newShots[index], ...updates };
        onShotsChange(newShots);
    };

    const addShot = () => {
        if (shots.length < maxShots) {
            onShotsChange([...shots, {
                order: shots.length,
                prompt: '',
                camera_movement: 'static',
                lighting: 'natural',
                mood: 'neutral',
                dialogue: '',
                negative_prompt: '',
                duration_target_sec: 10,
            }]);
            setActiveShot(shots.length);
        }
    };

    return (
        <div style={{ padding: '20px 0' }}>
            {/* Master Board Header */}
            <div className="glass-card" style={{ padding: '24px', marginBottom: '32px', border: '1px solid var(--tier2-color)33' }}>
                <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
                    <div style={{ flex: 2, minWidth: '300px' }}>
                        <label className="label" style={{ color: 'var(--tier2-color)', fontWeight: 700 }}>👤 SUJETO Y CONTEXTO MAESTRO (Coherencia)</label>
                        <textarea
                            className="input-field"
                            placeholder="Describe al protagonista y el entorno base que se mantendrá en TODO el video..."
                            value={globalPrompt}
                            onChange={(e) => onGlobalPromptChange(e.target.value)}
                            style={{ minHeight: '80px', fontSize: '0.9rem' }}
                        />
                    </div>
                    <div style={{ flex: 1, minWidth: '200px' }}>
                        <label className="label" style={{ color: 'var(--tier2-color)', fontWeight: 700 }}>✨ ESTILO VISUAL</label>
                        <select
                            className="input-field"
                            value={stylePreset}
                            onChange={(e) => onStylePresetChange(e.target.value)}
                        >
                            {STYLE_PRESETS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                        </select>
                        <div style={{ marginTop: '12px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                            Este estilo se aplicará automáticamente a todos los shots para mantener la estética.
                        </div>
                    </div>
                </div>
            </div>

            {/* Storyboard Grid */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: '20px',
                marginBottom: '40px'
            }}>
                {shots.map((shot, i) => (
                    <div
                        key={i}
                        className="glass-card"
                        onClick={() => setActiveShot(i)}
                        style={{
                            padding: '20px',
                            cursor: 'pointer',
                            border: activeShot === i ? '2px solid var(--accent-primary)' : '1px solid var(--border-glass)',
                            transition: 'all 0.2s ease',
                            position: 'relative',
                            display: 'flex',
                            flexDirection: 'column',
                            minHeight: '220px'
                        }}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                            <span style={{ fontSize: '0.7rem', fontWeight: 900, color: 'var(--accent-primary)' }}>SHOT {i + 1}</span>
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{shot.duration_target_sec}s</span>
                        </div>

                        <div style={{
                            flex: 1,
                            fontSize: '0.85rem',
                            color: shot.prompt ? 'var(--text-primary)' : 'var(--text-muted)',
                            fontStyle: shot.prompt ? 'normal' : 'italic',
                            overflow: 'hidden',
                            display: '-webkit-box',
                            WebkitLineClamp: 3,
                            WebkitBoxOrient: 'vertical',
                            marginBottom: '16px'
                        }}>
                            {shot.prompt || 'Sin descripción...'}
                        </div>

                        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                            <span style={{ fontSize: '0.65rem', padding: '2px 6px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px' }}>
                                📹 {CAMERA_OPTIONS.find(c => c.value === shot.camera_movement)?.label.split(' ')[1]}
                            </span>
                            <span style={{ fontSize: '0.65rem', padding: '2px 6px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px' }}>
                                💡 {shot.lighting}
                            </span>
                            <span style={{ fontSize: '0.65rem', padding: '2px 6px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px' }}>
                                🎭 {shot.mood}
                            </span>
                        </div>

                        {/* Remove button */}
                        {shots.length > 1 && (
                            <button
                                onClick={(e) => { e.stopPropagation(); onShotsChange(shots.filter((_, idx) => idx !== i)); }}
                                style={{ position: 'absolute', top: '10px', right: '10px', background: 'none', border: 'none', color: '#ef4444', fontSize: '0.8rem', cursor: 'pointer', opacity: 0.5 }}
                            >✕</button>
                        )}
                    </div>
                ))}

                {/* Add Shot Card */}
                {shots.length < maxShots && (
                    <div
                        onClick={addShot}
                        style={{
                            border: '2px dashed var(--border-glass)',
                            borderRadius: 'var(--radius-md)',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer',
                            color: 'var(--text-muted)',
                            transition: 'all 0.2s ease',
                            minHeight: '220px'
                        }}
                        onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--tier1-color)'}
                        onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border-glass)'}
                    >
                        <span style={{ fontSize: '2rem' }}>+</span>
                        <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Añadir Shot</span>
                    </div>
                )}
            </div>

            {/* Detail Editor Modal / Side Panel (Simple conditional for now) */}
            {activeShot !== null && shots[activeShot] && (
                <div style={{
                    position: 'fixed',
                    top: 0, right: 0, bottom: 0, width: '450px',
                    background: 'var(--bg-dark)',
                    borderLeft: '1px solid var(--border-glass)',
                    zIndex: 200,
                    padding: '40px 32px',
                    boxShadow: '-20px 0 50px rgba(0,0,0,0.5)',
                    overflowY: 'auto'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                        <h3 style={{ fontFamily: 'var(--font-heading)' }}>Editar Shot {activeShot + 1}</h3>
                        <button className="btn btn-secondary" onClick={() => setActiveShot(null)}>Cerrar</button>
                    </div>

                    <div style={{ marginBottom: '24px' }}>
                        <label className="label">Acción / Prompt del Shot</label>
                        <textarea
                            className="input-field"
                            value={shots[activeShot].prompt}
                            onChange={(e) => updateShot(activeShot, { prompt: e.target.value })}
                            style={{ minHeight: '120px' }}
                            placeholder="Ej: El personaje camina hacia la ventana y mira hacia fuera..."
                        />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
                        <div>
                            <label className="label">Cámara</label>
                            <select
                                className="input-field"
                                value={shots[activeShot].camera_movement}
                                onChange={(e) => updateShot(activeShot, { camera_movement: e.target.value })}
                            >
                                {CAMERA_OPTIONS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                            </select>
                        </div>
                        <div>
                            <label className="label">Iluminación</label>
                            <select
                                className="input-field"
                                value={shots[activeShot].lighting}
                                onChange={(e) => updateShot(activeShot, { lighting: e.target.value })}
                            >
                                {LIGHTING_OPTIONS.map(l => <option key={l} value={l}>{l}</option>)}
                            </select>
                        </div>
                    </div>

                    <div style={{ marginBottom: '24px' }}>
                        <label className="label">Diálogo / Sonidos</label>
                        <input
                            className="input-field"
                            value={shots[activeShot].dialogue}
                            onChange={(e) => updateShot(activeShot, { dialogue: e.target.value })}
                            placeholder="Texto que dirá el personaje..."
                        />
                    </div>

                    <div style={{ marginBottom: '24px' }}>
                        <label className="label">Duración: {shots[activeShot].duration_target_sec}s</label>
                        <input
                            type="range" min="3" max="15" step="1"
                            className="w-full"
                            value={shots[activeShot].duration_target_sec}
                            onChange={(e) => updateShot(activeShot, { duration_target_sec: Number(e.target.value) })}
                        />
                    </div>

                    <button
                        className="btn btn-primary w-full"
                        onClick={() => setActiveShot(null)}
                    >
                        Guardar Shot
                    </button>
                </div>
            )}
        </div>
    );
}
