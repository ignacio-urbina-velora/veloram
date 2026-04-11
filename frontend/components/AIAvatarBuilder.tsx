'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Shuffle, Image as ImageIcon, Loader2, Check, RefreshCw, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';

export default function AIAvatarBuilder() {
    const router = useRouter();

    const [selectedImage, setSelectedImage] = useState<string | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [saveSuccess, setSaveSuccess] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Form State
    const [gender, setGender] = useState<'Hombre' | 'Mujer' | 'Secreto'>('Mujer');
    const [age, setAge] = useState(25);
    const [ethnicity, setEthnicity] = useState('Latina');
    const [eyeColor, setEyeColor] = useState('Café');
    const [eyeShape, setEyeShape] = useState('Almendrados');
    const [skinTone, setSkinTone] = useState('Natural');
    const [hairColorType, setHairColorType] = useState<'natural' | 'fancy'>('natural');
    const [hairColor, setHairColor] = useState('Castaño oscuro');
    const [fancyHairColor, setFancyHairColor] = useState('Plateado');
    const [hairShape, setHairShape] = useState('Ondulado');
    const [hairLength, setHairLength] = useState('Largo');
    const [expression, setExpression] = useState('Sonrisa sutil');
    const [lighting, setLighting] = useState('Luz natural');
    const [clothingStyle, setClothingStyle] = useState('Casual');
    const [tier, setTier] = useState<'cinematic' | 'professional' | 'quick'>('professional');

    const handleRandomize = () => {
        setGender(Math.random() > 0.5 ? 'Mujer' : 'Hombre');
        setAge(Math.floor(Math.random() * (45 - 19 + 1)) + 19);
        
        const ethnicities = ['Latina', 'Europea', 'Asiática', 'Afroamericana', 'Árabe', 'Escandinava', 'Chilena'];
        setEthnicity(ethnicities[Math.floor(Math.random() * ethnicities.length)]);

        const eyeColors = ['Azul', 'Verde', 'Café', 'Negro', 'Ámbar'];
        setEyeColor(eyeColors[Math.floor(Math.random() * eyeColors.length)]);
        
        setEyeShape(['Almendrados', 'Redondos', 'Rasgados', 'Profundos'][Math.floor(Math.random() * 4)]);
        setSkinTone(['Muy claro', 'Pálido', 'Natural', 'Cálido', 'Oliva', 'Bronceado', 'Oscuro'][Math.floor(Math.random() * 7)]);
        
        setHairColorType(Math.random() > 0.9 ? 'fancy' : 'natural');
        setHairColor(['Negro', 'Castaño oscuro', 'Castaño medio', 'Rubio', 'Pelirrojo'][Math.floor(Math.random() * 5)]);
        
        setHairShape(['Liso', 'Ondulado', 'Rizado'][Math.floor(Math.random() * 3)]);
        setHairLength(['Corto', 'Mediano', 'Largo'][Math.floor(Math.random() * 3)]);
        
        const expressions = ['Sonrisa sutil', 'Seria / Contemplativa', 'Mirada directa', 'Alegre', 'Neutral'];
        setExpression(expressions[Math.floor(Math.random() * expressions.length)]);

        const lightings = ['Luz natural', 'Golden Hour', 'Estudio suave', 'Dramática', 'Contraluz solar'];
        setLighting(lightings[Math.floor(Math.random() * lightings.length)]);

        const clothing = ['Casual', 'Traje formal', 'Deportivo', 'Streetwear', 'UGC Casual'];
        setClothingStyle(clothing[Math.floor(Math.random() * clothing.length)]);
    };

    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);
        try {
            // Send parameters directly to backend to use the NEW v3.0 Wan 2.2 Prompt Builder
            const data = await api.generatePortrait({
                gender,
                age,
                country: ethnicity,
                eyes: eyeColor,
                hair_color: hairColorType === 'natural' ? hairColor : fancyHairColor,
                hairstyle: hairShape,
                hair_length: hairLength,
                skin_tone: skinTone,
                eye_shape: eyeShape,
                expression: expression,
                lighting: lighting,
                clothing: clothingStyle,
                tier: tier
            });
            
            const imageUrl = data.image_b64 ? `data:image/png;base64,${data.image_b64}` : data.url;
            setSelectedImage(imageUrl);
        } catch (err: any) {
            console.error("Error generating portrait:", err);
            if (err.status === 402 || (err.message && err.message.includes("Créditos insuficientes"))) {
                setError("Créditos insuficientes. Por favor, recarga tu saldo.");
            } else {
                setError(err.message || "Error al conectar con Wan 2.2. Intenta de nuevo.");
            }
        } finally {
            setIsGenerating(false);
        }
    };

    const handleSave = async () => {
        if (!selectedImage || isSaving || saveSuccess) return;
        setIsSaving(true);
        setError(null);
        try {
            const hColorRaw = hairColorType === 'natural' ? hairColor : fancyHairColor;
            
            const morphsData = {
                gender,
                age,
                eyeColor,
                eyeShape,
                skinTone,
                hairType: hairColorType,
                hairColor: hColorRaw,
                hairShape,
                hairLength,
                clothingStyle
            };

            const res = await api.saveAvatar({
                name: `Avatar IA - ${new Date().toLocaleDateString('es-CL')} ${new Date().toLocaleTimeString('es-CL')}`,
                image_b64: selectedImage,
                morphs: morphsData as unknown as Record<string, number>,
                styles: { type: "flux_portrait_only", origin: "ai_builder" },
            });
            
            setSaveSuccess(true);
            setTimeout(() => {
                // Redirigir al studio pre-seleccionando este avatar
                router.push(`/dashboard/studio?avatar_id=${res.id}`);
            }, 1500);
        } catch (e: any) {
            console.error('Error guardando avatar:', e);
            setError(e.detail || e.message || 'No se pudo guardar el avatar. Intenta de nuevo.');
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="flex h-full w-full bg-[#0a0a0a] text-white">
            {/* Left Panel - Controls */}
            <div className="w-[420px] h-full bg-[#050505] border-r border-white/5 flex flex-col shadow-[40px_0_80px_rgba(0,0,0,0.8)] z-40">
                <div className="p-8 space-y-8 overflow-y-auto flex-1">
                    <header className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl font-black tracking-tighter leading-none mb-1">
                                CREADOR <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-violet-500">EXPRESS</span>
                            </h1>
                            <p className="text-[9px] text-white/40 font-bold uppercase tracking-[0.3em]">IA Generativa - 30s</p>
                        </div>
                        <button 
                            onClick={handleRandomize}
                            className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 transition-all shadow-xl"
                            title="Aleatorizar Atributos"
                        >
                            <Shuffle className="w-4 h-4" />
                        </button>
                    </header>

                    <div className="space-y-6">
                        {/* Gender & Age */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-white/40">Género</label>
                                <select 
                                    value={gender} 
                                    onChange={(e) => setGender(e.target.value as any)}
                                    className="w-full bg-white/5 border border-white/10 text-xs font-bold text-white rounded-xl px-3 py-3 outline-none focus:border-pink-500 transition-colors"
                                >
                                    <option className="bg-[#050505]" value="Mujer">Mujer</option>
                                    <option className="bg-[#050505]" value="Hombre">Hombre</option>
                                </select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-white/40">Etnia / Origen</label>
                                <select 
                                    value={ethnicity} 
                                    onChange={(e) => setEthnicity(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 text-xs font-bold text-white rounded-xl px-3 py-3 outline-none focus:border-pink-500 transition-colors"
                                >
                                    {['Latina', 'Europea', 'Asiática', 'Afroamericana', 'Árabe', 'Escandinava', 'Chilena'].map(e => <option className="bg-[#050505]" key={e} value={e}>{e}</option>)}
                                </select>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex justify-between items-end">
                                <label className="text-[10px] font-black uppercase tracking-widest text-white/40">Edad Exacta</label>
                                <span className="text-[10px] font-bold text-white/80 bg-white/5 px-2 py-0.5 rounded">{age} años</span>
                            </div>
                            <input 
                                type="range" min="18" max="75" value={age} 
                                onChange={(e) => setAge(parseInt(e.target.value))}
                                className="w-full h-1.5 mt-2 bg-white/10 rounded-full appearance-none outline-none accent-pink-500 cursor-pointer"
                            />
                        </div>

                        {/* Eyes */}
                        <div className="grid grid-cols-2 gap-4 border-t border-white/5 pt-6">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-white/40">Ojos: Color</label>
                                <select 
                                    value={eyeColor} 
                                    onChange={(e) => setEyeColor(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 text-xs font-bold text-white rounded-xl px-3 py-3 outline-none focus:border-pink-500 transition-colors"
                                >
                                    {['Azul', 'Verde', 'Café', 'Negro', 'Gris'].map(c => <option className="bg-[#050505]" key={c} value={c}>{c}</option>)}
                                </select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-white/40">Ojos: Forma</label>
                                <select 
                                    value={eyeShape} 
                                    onChange={(e) => setEyeShape(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 text-xs font-bold text-white rounded-xl px-3 py-3 outline-none focus:border-pink-500 transition-colors"
                                >
                                    {['Almendrados', 'Redondos', 'Rasgados'].map(s => <option className="bg-[#050505]" key={s} value={s}>{s}</option>)}
                                </select>
                            </div>
                        </div>

                        {/* Skin Tone */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-white/40">Tono de Piel</label>
                                <select 
                                    value={skinTone} 
                                    onChange={(e) => setSkinTone(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 text-xs font-bold text-white rounded-xl px-3 py-3 outline-none focus:border-pink-500 transition-colors"
                                >
                                    {['Muy claro', 'Pálido', 'Natural', 'Cálido', 'Oliva', 'Bronceado', 'Oscuro'].map(t => <option className="bg-[#050505]" key={t} value={t}>{t}</option>)}
                                </select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-white/40">Expresión</label>
                                <select 
                                    value={expression} 
                                    onChange={(e) => setExpression(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 text-xs font-bold text-white rounded-xl px-3 py-3 outline-none focus:border-pink-500 transition-colors"
                                >
                                    {['Sonrisa sutil', 'Seria / Contemplativa', 'Mirada directa', 'Alegre', 'Neutral'].map(x => <option className="bg-[#050505]" key={x} value={x}>{x}</option>)}
                                </select>
                            </div>
                        </div>

                        <div className="space-y-2 pt-4">
                            <label className="text-[10px] font-black uppercase tracking-widest text-white/40">Iluminación</label>
                            <select 
                                value={lighting} 
                                onChange={(e) => setLighting(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 text-xs font-bold text-white rounded-xl px-3 py-3 outline-none focus:border-pink-500 transition-colors"
                            >
                                {['Luz natural', 'Golden Hour', 'Estudio suave', 'Dramática', 'Contraluz solar'].map(l => <option className="bg-[#050505]" key={l} value={l}>{l}</option>)}
                            </select>
                        </div>

                        {/* Hair */}
                        <div className="space-y-4 pt-6 border-t border-white/5">
                            <label className="text-[10px] font-black uppercase tracking-widest text-white/40 block">Cabello</label>
                            
                            <div className="flex gap-4">
                                <label className="flex items-center gap-2 cursor-pointer group">
                                    <input 
                                        type="radio" name="hairType_ai" checked={hairColorType === 'natural'} 
                                        onChange={() => setHairColorType('natural')}
                                        className="accent-pink-500 w-4 h-4"
                                    />
                                    <span className={cn("text-xs font-bold transition-colors", hairColorType === 'natural' ? "text-white" : "text-white/40 group-hover:text-white/70")}>Natural</span>
                                </label>
                                <label className="flex items-center gap-2 cursor-pointer group">
                                    <input 
                                        type="radio" name="hairType_ai" checked={hairColorType === 'fancy'} 
                                        onChange={() => setHairColorType('fancy')}
                                        className="accent-pink-500 w-4 h-4"
                                    />
                                    <span className={cn("text-xs font-bold transition-colors", hairColorType === 'fancy' ? "text-white" : "text-white/40 group-hover:text-white/70")}>Fantasía</span>
                                </label>
                            </div>

                            {hairColorType === 'natural' ? (
                                <select 
                                    value={hairColor} 
                                    onChange={(e) => setHairColor(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 text-xs font-bold text-white rounded-xl px-3 py-3 outline-none focus:border-pink-500 transition-colors"
                                >
                                    {['Negro profundo', 'Castaño oscuro', 'Castaño medio', 'Castaño claro', 'Rubio oscuro', 'Rubio medio', 'Rubio claro', 'Rubio platino', 'Pelirrojo natural'].map(h => <option className="bg-[#050505]" key={h} value={h}>{h}</option>)}
                                </select>
                            ) : (
                                <select 
                                    value={fancyHairColor} 
                                    onChange={(e) => setFancyHairColor(e.target.value)}
                                    className="w-full bg-white/5 border border-white/10 text-xs font-bold text-white rounded-xl px-3 py-3 outline-none focus:border-pink-500 transition-colors"
                                >
                                    {['Azul eléctrico', 'Rosa pastel', 'Morado', 'Verde neón', 'Plateado', 'Blanco puro'].map(f => <option className="bg-[#050505]" key={f} value={f}>{f}</option>)}
                                </select>
                            )}
                            
                            <div className="grid grid-cols-2 gap-4 pt-2">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black uppercase tracking-widest text-white/40 block">Forma Pelo</label>
                                    <select 
                                        value={hairShape} 
                                        onChange={(e) => setHairShape(e.target.value)}
                                        className="w-full bg-white/5 border border-white/10 text-xs font-bold text-white rounded-xl px-3 py-3 outline-none focus:border-pink-500 transition-colors"
                                    >
                                        {['Liso', 'Ondulado', 'Rizado'].map(s => <option className="bg-[#050505]" key={s} value={s}>{s}</option>)}
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black uppercase tracking-widest text-white/40 block">Largo Pelo</label>
                                    <select 
                                        value={hairLength} 
                                        onChange={(e) => setHairLength(e.target.value)}
                                        className="w-full bg-white/5 border border-white/10 text-xs font-bold text-white rounded-xl px-3 py-3 outline-none focus:border-pink-500 transition-colors"
                                    >
                                        {['Corto', 'Mediano', 'Largo'].map(l => <option className="bg-[#050505]" key={l} value={l}>{l}</option>)}
                                    </select>
                                </div>
                            </div>
                        </div>

                        {/* Clothing */}
                        <div className="space-y-2 pt-6 border-t border-white/5">
                            <label className="text-[10px] font-black uppercase tracking-widest text-white/40">Estilo de Ropa</label>
                            <select 
                                value={clothingStyle} 
                                onChange={(e) => setClothingStyle(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 text-xs font-bold text-white rounded-xl px-3 py-3 outline-none focus:border-pink-500 transition-colors"
                            >
                                {['Casual', 'Traje formal', 'Deportivo', 'Streetwear', 'Alta costura'].map(c => <option className="bg-[#050505]" key={c} value={c}>{c}</option>)}
                            </select>
                        </div>

                        {/* Motor 2.0 Tier */}
                        <div className="space-y-3 pt-6 border-t border-white/5">
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

                        {/* Generation Action */}
                        <div className="pt-8">
                            <button 
                                onClick={handleGenerate}
                                disabled={isGenerating}
                                className="w-full bg-gradient-to-r from-pink-500 to-violet-500 text-white py-4 rounded-2xl font-black text-xs uppercase tracking-[0.2em] hover:scale-[1.02] transition-all shadow-[0_0_30px_rgba(236,72,153,0.3)] disabled:opacity-50 disabled:hover:scale-100 flex items-center justify-center gap-2"
                            >
                                {isGenerating ? (
                                    <span className="inline-flex items-center gap-2"><RefreshCw className="w-4 h-4 animate-spin" /> Creando...</span>
                                ) : (
                                    <span className="inline-flex items-center gap-2"><span>Generar Avatar</span> <span className="font-medium opacity-70">-10 Créditos</span></span>
                                )}
                            </button>
                            {error && (
                                <div className="mt-4 bg-red-500/10 border border-red-500/30 text-red-200 text-xs p-3 rounded-lg flex items-start gap-2">
                                    <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                                    <span>{error}</span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Panel - Preview */}
            <div className="flex-1 flex flex-col justify-center items-center p-8 bg-[radial-gradient(circle_at_50%_50%,#1a1a2e_0%,#0a0a0a_100%)] relative">
                <div className="w-full max-w-2xl aspect-[3/4] max-h-[85vh] rounded-3xl border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl flex flex-col items-center justify-center overflow-hidden relative">
                    {selectedImage ? (
                        <div className="w-full h-full relative group">
                            <img src={selectedImage} alt="Preview" className="w-full h-full object-cover transition-transform duration-700 hover:scale-105" />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                    ) : (
                        <div className="text-center text-white/20 animate-pulse">
                            <ImageIcon className="w-24 h-24 mx-auto mb-6 opacity-50" />
                            <p className="text-sm font-bold tracking-widest uppercase">Tu Avatar IA aparecerá aquí</p>
                        </div>
                    )}

                    {isGenerating && (
                        <div className="absolute inset-0 bg-black/80 backdrop-blur-md flex flex-col items-center justify-center z-10 transition-all duration-500">
                             <div className="relative">
                                <div className="w-24 h-24 border-2 border-white/10 rounded-full animate-[ping_2s_infinite]" />
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="w-12 h-12 border-4 border-pink-500/30 border-t-pink-500 rounded-full animate-spin" />
                                </div>
                             </div>
                             <p className="mt-8 text-sm font-black tracking-[0.2em] text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-violet-500 animate-pulse uppercase">
                                Sintetizando Rostro...
                             </p>
                             <p className="text-[10px] text-white/40 uppercase tracking-widest mt-2">Tomará aproximadamente 15 segundos</p>
                        </div>
                    )}
                </div>

                {/* Save Block */}
                <div className="absolute bottom-12 left-1/2 -translate-x-1/2 animate-in slide-in-from-bottom-8 fade-in duration-500 z-20">
                    <button 
                        onClick={handleSave}
                        disabled={!selectedImage || isGenerating || isSaving || saveSuccess}
                        className={cn(
                            "px-10 py-4 rounded-full font-black text-xs tracking-[0.2em] uppercase transition-all shadow-2xl flex items-center gap-3",
                            !selectedImage 
                                ? "opacity-0 pointer-events-none" 
                                : saveSuccess
                                    ? "bg-green-500 text-white shadow-[0_0_30px_rgba(34,197,94,0.4)] scale-105"
                                    : "bg-white text-black hover:bg-gray-200 hover:scale-105 active:scale-95 shadow-[0_0_30px_rgba(255,255,255,0.2)]"
                        )}
                    >
                        {isSaving ? (
                            <span className="inline-flex items-center gap-2"><RefreshCw className="w-4 h-4 animate-spin" /> Guardando...</span>
                        ) : saveSuccess ? (
                            <span className="inline-flex items-center gap-2"><Check className="w-4 h-4" /> Avatar Guardado</span>
                        ) : (
                            <span className="inline-flex items-center gap-2"><Check className="w-4 h-4" /> Usar este Avatar</span>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
