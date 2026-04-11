'use client';

import { useState, Suspense, useEffect, useRef } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { Sparkles, RefreshCw, Check, AlertCircle, ChevronDown, Wand2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import * as THREE from 'three';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';
import AmalaAvatar from './AmalaAvatar';
import { CameraControls, Grid } from '@react-three/drei';

const DEFAULT_SKIN_COLOR = '#d2a679';
const DEFAULT_EYE_COLOR = '#4a3728';
const DEFAULT_HAIR_COLOR = '#1c1c1c';
const MODAL_URL = "https://ignaciourbinakonecta--avatar-generate-fastapi-app.modal.run";

function SliderGroup({
  label, isOpen, onToggle, children
}: {
  label: string; isOpen: boolean; onToggle: () => void; children: React.ReactNode;
}) {
  return (
    <div className="border-b border-white/5">
      <button
        onClick={onToggle}
        className="w-full py-4 flex items-center justify-between text-[11px] font-black uppercase tracking-widest text-white/70 hover:text-white transition-colors"
      >
        {label}
        <ChevronDown className={cn("w-4 h-4 transition-transform", isOpen ? "rotate-180" : "")} />
      </button>
      {isOpen && (
        <div className="pb-6 space-y-5">
          {children}
        </div>
      )}
    </div>
  );
}

function CanvasContent({
  morphs, skinColor, eyeColor, hairColor, hairStyle, onCanvasReady
}: {
  morphs: Record<string, number>;
  skinColor: string;
  eyeColor: string;
  hairColor: string;
  hairStyle: string;
  onCanvasReady: (ctx: any) => void;
}) {
  const { gl, scene, camera } = useThree();
  const cameraControlsRef = useRef<any>(null);

  useEffect(() => {
    onCanvasReady({ gl, scene, camera });
  }, [gl, scene, camera, onCanvasReady]);

  return (
    <>
      <color attach="background" args={['#12122a']} />
      <ambientLight intensity={0.7} />
      <directionalLight position={[5, 5, 5]} intensity={1.5} />
      <pointLight position={[-5, 5, -5]} intensity={0.8} color="#c084fc" />

      {/* Cubo de diagnóstico — siempre visible */}
      <mesh position={[1.2, 0, 0]}>
        <boxGeometry args={[0.3, 0.3, 0.3]} />
        <meshStandardMaterial color="hotpink" />
      </mesh>

      <Suspense fallback={
        <mesh>
          <boxGeometry args={[0.5, 0.5, 0.5]} />
          <meshStandardMaterial color="#3b82f6" wireframe />
        </mesh>
      }>
        <AmalaAvatar
          morphs={morphs}
          skinColor={skinColor}
          eyeColor={eyeColor}
          hairColor={hairColor}
          hairStyle={hairStyle}
          onDebugUpdate={() => {}}
        />
      </Suspense>

      <Grid position={[0, -0.86, 0]} infiniteGrid cellColor="#1e293b" sectionColor="#7c3aed" />
      <CameraControls ref={cameraControlsRef} makeDefault />
    </>
  );
}

export default function ProfessionalAvatarBuilder() {
  const router = useRouter();
  const canvasStateRef = useRef<any>(null);
  const [error, setError] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [openCategory, setOpenCategory] = useState<string | null>('macro');
  const [tier, setTier] = useState<'cinematic' | 'professional' | 'quick'>('professional');

  const [skinColor, setSkinColor] = useState(DEFAULT_SKIN_COLOR);
  const [eyeColor, setEyeColor] = useState(DEFAULT_EYE_COLOR);
  const [hairColor, setHairColor] = useState(DEFAULT_HAIR_COLOR);
  const [hairStyle, setHairStyle] = useState('bald');

  const [morphs, setMorphs] = useState<Record<string, number>>({
    gender: 0.5, muscle: 0.5, weight: 0.5, height: 0.5,
    headShapeRound: 0, headShapeSquare: 0, headShapeOval: 0,
    chinWidth: 0.5, cheekVolume: 0.5,
    eyeSize: 0.5, eyeHeight: 0.5, eyeDistance: 0.5, eyeEpicanthus: 0,
    noseSize: 0.5, noseWidth: 0.5, noseHeight: 0.5, nosePoint: 0.5,
    lipVolume: 0.5, mouthWidth: 0.5,
    vShape: 0.5, stomach: 0.5, hips: 0.5, breastSize: 0.5, buttocks: 0.5,
  });

  const updateMorph = (key: string, val: number) =>
    setMorphs(prev => ({ ...prev, [key]: val }));

  const handleReset = () => setMorphs({
    gender: 0.5, muscle: 0.5, weight: 0.5, height: 0.5,
    headShapeRound: 0, headShapeSquare: 0, headShapeOval: 0,
    chinWidth: 0.5, cheekVolume: 0.5,
    eyeSize: 0.5, eyeHeight: 0.5, eyeDistance: 0.5, eyeEpicanthus: 0,
    noseSize: 0.5, noseWidth: 0.5, noseHeight: 0.5, nosePoint: 0.5,
    lipVolume: 0.5, mouthWidth: 0.5,
    vShape: 0.5, stomach: 0.5, hips: 0.5, breastSize: 0.5, buttocks: 0.5,
  });

  const captureCleanReferencesForFlux = async () => {
    if (!canvasStateRef.current) return [];
    const { gl, scene, camera } = canvasStateRef.current;
    
    // 1. Guardar estado actual
    const originalCamPos = camera.position.clone();
    const originalCamQuat = camera.quaternion.clone();
    const originalBg = scene.background;
    
    // 2. Setup Iluminación Neutra de Estudio
    scene.background = new THREE.Color('#000000'); // Fondo neutro para mejor depth
    const neutralLight = new THREE.DirectionalLight(0xffffff, 1.2);
    neutralLight.position.set(0, 1, 5);
    scene.add(neutralLight);
    
    const views = [
      { name: 'front', pos: [0, 0.5, 2.5] },
      { name: 'left_3_4', pos: [-1.5, 0.5, 2.0] },
      { name: 'right_3_4', pos: [1.5, 0.5, 2.0] }
    ];
    
    const capturedRefs = [];
    
    for (const v of views) {
      camera.position.set(v.pos[0], v.pos[1], v.pos[2]);
      camera.lookAt(0, 0.5, 0);
      gl.render(scene, camera);
      const b64 = gl.domElement.toDataURL('image/png').split(',')[1];
      capturedRefs.push({ view: v.name, base64: b64 });
    }
    
    // 3. Restaurar estado
    scene.remove(neutralLight);
    scene.background = originalBg;
    camera.position.copy(originalCamPos);
    camera.quaternion.copy(originalCamQuat);
    gl.render(scene, camera);
    
    return capturedRefs;
  };

  const handleRefineIA = async () => {
    if (isRefining) return;
    setIsRefining(true);
    setError('');
    
    try {
      // Capturar las 3 vistas requeridas por el nuevo plan
      const references = await captureCleanReferencesForFlux();
      
      const res = await fetch('/api/avatars/generate-texture-8k', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          references,
          tier,
          prompt_enhancement: 'professional editorial macro photography, extreme skin detail, realistic eyes'
        }),
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Error en la generación HD');
      }

      const data = await res.json();
      if (data.image_b64) {
        // En una implementación real, aquí actualizarías una vista previa o guardarías el resultado
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      }
    } catch (err: any) {
      setError(err.message || 'Error en el refinamiento hiperrealista');
    } finally {
      setIsRefining(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const canvas = document.querySelector('canvas');
      const screenshot = canvas ? canvas.toDataURL('image/png') : '';
      await api.saveAvatar({
        name: `Avatar ${new Date().toLocaleDateString('es-CL')}`,
        image_b64: screenshot.split(',')[1] || '',
        morphs,
        styles: { skinColor, eyeColor, hairColor, hairStyle },
      });
      setSaveSuccess(true);
      setTimeout(() => router.push('/dashboard/studio'), 1500);
    } catch {
      setError('No se pudo guardar el avatar. Intenta de nuevo.');
    } finally {
      setIsSaving(false);
    }
  };

  const MORPH_GROUPS = [
    { id: 'macro', label: 'Cuerpo', keys: ['height', 'weight', 'muscle'] },
    { id: 'face', label: 'Rostro', keys: ['chinWidth', 'cheekVolume', 'headShapeRound', 'headShapeSquare'] },
    { id: 'eyes', label: 'Ojos', keys: ['eyeSize', 'eyeHeight', 'eyeDistance', 'eyeEpicanthus'] },
    { id: 'nose', label: 'Nariz', keys: ['noseSize', 'noseWidth', 'noseHeight', 'nosePoint'] },
    { id: 'mouth', label: 'Boca', keys: ['lipVolume', 'mouthWidth'] },
    { id: 'body', label: 'Proporciones', keys: ['vShape', 'stomach', 'hips', 'breastSize', 'buttocks'] },
  ];

  return (
    <div className="flex h-screen w-full bg-[#0a0a0f] overflow-hidden text-white">
      {/* ── Canvas Area ─────────── */}
      <div className="flex-1 relative">
        <Canvas
          shadows
          gl={{ preserveDrawingBuffer: true, antialias: true }}
          camera={{ position: [0, 0.5, 4.0], fov: 35, near: 0.01, far: 100 }}
          style={{ background: '#12122a' }}
        >
          <CanvasContent
            morphs={morphs}
            skinColor={skinColor}
            eyeColor={eyeColor}
            hairColor={hairColor}
            hairStyle={hairStyle}
            onCanvasReady={(ctx) => { canvasStateRef.current = ctx; }}
          />
        </Canvas>

        {/* Botones inferiores */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-4 z-40">
          <button
            onClick={handleReset}
            className="flex items-center gap-2 bg-white/10 backdrop-blur border border-white/20 px-6 py-3 rounded-2xl text-xs font-bold uppercase hover:bg-white/20 transition-all"
          >
            <RefreshCw className="w-4 h-4" /> Reiniciar
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || saveSuccess}
            className={cn(
              "flex items-center gap-2 px-8 py-3 rounded-2xl text-xs font-black uppercase transition-all shadow-xl",
              saveSuccess
                ? "bg-green-500 text-white"
                : "bg-purple-600 hover:bg-purple-500 text-white hover:scale-105"
            )}
          >
            {isSaving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
            {isSaving ? 'Guardando…' : saveSuccess ? '¡Guardado!' : 'Finalizar y Guardar'}
          </button>
        </div>

        {error && (
          <div className="absolute bottom-24 left-1/2 -translate-x-1/2 bg-red-500/20 border border-red-500/50 backdrop-blur px-6 py-3 rounded-2xl flex items-center gap-3 text-sm text-red-200 max-w-md">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* ── Right Panel ─────────── */}
      <div className="w-[420px] h-full bg-[#050508] border-l border-white/5 flex flex-col shadow-[-40px_0_80px_rgba(0,0,0,0.8)] z-40">
        <div className="p-8 space-y-6 overflow-y-auto flex-1">
          <header>
            <h1 className="text-2xl font-black tracking-tighter leading-none mb-1">
              DISEÑA TU{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">
                HUMANO
              </span>
            </h1>
            <p className="text-[9px] text-white/20 font-bold uppercase tracking-[0.3em]">Motor Interactivo</p>
          </header>

          {/* Calidad Tier Selector */}
          <div className="space-y-3">
             <label className="text-[10px] font-black uppercase tracking-widest text-white/40 block">Calidad del Motor 2.0</label>
             <div className="flex gap-2">
                {(['quick', 'professional', 'cinematic'] as const).map(t => (
                  <button
                    key={t}
                    onClick={() => setTier(t)}
                    className={cn(
                      "flex-1 py-2 rounded-xl border text-[9px] font-black uppercase transition-all",
                      tier === t 
                        ? "bg-white/10 border-white/40 text-white" 
                        : "bg-black/20 border-white/5 text-white/20 hover:border-white/20"
                    )}
                  >
                    {t === 'cinematic' ? '🎥 Cinematic' : t === 'professional' ? '👔 Prof.' : '⚡ Quick'}
                  </button>
                ))}
             </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleRefineIA}
              disabled={isRefining}
              className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 px-4 py-2 rounded-xl text-[10px] font-black uppercase hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:pointer-events-none"
            >
              {isRefining ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
              {isRefining ? 'Procesando…' : 'Refinar con IA'}
            </button>
            <button
              onClick={() => {
                const rand: Record<string, number> = {};
                Object.keys(morphs).forEach(k => { rand[k] = Math.random(); });
                setMorphs(rand);
              }}
              className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 transition-all"
              title="Aleatorizar"
            >
              <Wand2 className="w-4 h-4" />
            </button>
          </div>

          {/* Género */}
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => { updateMorph('gender', 0); updateMorph('hips', 0.75); updateMorph('breastSize', 0.65); }}
              className={cn(
                "py-4 rounded-2xl border text-xs font-black uppercase tracking-widest transition-all",
                morphs.gender < 0.5
                  ? "bg-pink-500/20 border-pink-500/60 text-pink-300"
                  : "bg-white/5 border-white/5 text-white/30 hover:border-white/20"
              )}
            >
              ♀ Mujer
            </button>
            <button
              onClick={() => { updateMorph('gender', 1); updateMorph('hips', 0.35); updateMorph('breastSize', 0.1); }}
              className={cn(
                "py-4 rounded-2xl border text-xs font-black uppercase tracking-widest transition-all",
                morphs.gender >= 0.5
                  ? "bg-blue-500/20 border-blue-500/60 text-blue-300"
                  : "bg-white/5 border-white/5 text-white/30 hover:border-white/20"
              )}
            >
              ♂ Hombre
            </button>
          </div>

          {/* Color de Piel */}
          <div>
            <label className="text-[10px] font-black uppercase tracking-widest text-white/40 block mb-3">Color de Piel</label>
            <div className="flex gap-2 flex-wrap">
              {['#f5d0a9', '#d2a679', '#c68642', '#8d5524', '#5c3317'].map(c => (
                <button
                  key={c}
                  onClick={() => setSkinColor(c)}
                  style={{ background: c }}
                  className={cn(
                    "w-9 h-9 rounded-full border-2 transition-transform hover:scale-110",
                    skinColor === c ? "border-white scale-110" : "border-transparent"
                  )}
                />
              ))}
            </div>
          </div>

          {/* Sliders por grupo */}
          {MORPH_GROUPS.map(group => (
            <SliderGroup
              key={group.id}
              label={group.label}
              isOpen={openCategory === group.id}
              onToggle={() => setOpenCategory(prev => prev === group.id ? null : group.id)}
            >
              {group.keys.map(key => (
                <div key={key}>
                  <div className="flex justify-between mb-1">
                    <label className="text-[10px] uppercase font-bold text-white/40">{key}</label>
                    <span className="text-[10px] text-white/30 font-mono">{Math.round(morphs[key] * 100)}</span>
                  </div>
                  <input
                    type="range" min="0" max="1" step="0.01"
                    value={morphs[key]}
                    onChange={e => updateMorph(key, parseFloat(e.target.value))}
                    className="w-full accent-purple-500 cursor-pointer"
                  />
                </div>
              ))}
            </SliderGroup>
          ))}
        </div>
      </div>
    </div>
  );
}
