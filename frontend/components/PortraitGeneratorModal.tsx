'use client';

import React, { useState, useRef } from 'react';
import { X, Shuffle, Image as ImageIcon, Loader2, FolderOpen } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';

interface PortraitGeneratorModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSelectImage: (imageUrl: string) => void;
}

export default function PortraitGeneratorModal({ isOpen, onClose, onSelectImage }: PortraitGeneratorModalProps) {
    const [history, setHistory] = useState<string[]>([]);
    const [selectedImage, setSelectedImage] = useState<string | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleLoadFromFile = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onloadend = () => {
            const dataUrl = reader.result as string;
            setSelectedImage(dataUrl);
            setHistory(prev => [dataUrl, ...prev]);
        };
        reader.readAsDataURL(file);
        // reset input so same file can be re-loaded
        e.target.value = '';
    };

    // Form State
    const [gender, setGender] = useState<'Hombre' | 'Mujer' | 'Secreto'>('Mujer');
    const [age, setAge] = useState(25);
    const [eyeColor, setEyeColor] = useState('Café');
    const [eyeShape, setEyeShape] = useState('Almendrados');
    const [skinTone, setSkinTone] = useState('Medio');
    const [hairColorType, setHairColorType] = useState<'natural' | 'fancy'>('natural');
    const [hairColor, setHairColor] = useState('Castaño medio');
    const [fancyHairColor, setFancyHairColor] = useState('Plateado');
    const [hairShape, setHairShape] = useState('Liso');
    const [hairLength, setHairLength] = useState('Mediano');

    if (!isOpen) return null;

    const handleRandomize = () => {
        setGender(Math.random() > 0.5 ? 'Mujer' : 'Hombre');
        setAge(Math.floor(Math.random() * (50 - 18 + 1)) + 18);
        
        const eyeColors = ['Azul', 'Verde', 'Café', 'Negro', 'Gris'];
        setEyeColor(eyeColors[Math.floor(Math.random() * eyeColors.length)]);
        
        setEyeShape(['Almendrados', 'Redondos', 'Rasgados'][Math.floor(Math.random() * 3)]);
        
        const skinTones = ['Muy claro', 'Claro', 'Medio claro', 'Medio', 'Medio oscuro', 'Oscuro', 'Muy oscuro'];
        setSkinTone(skinTones[Math.floor(Math.random() * skinTones.length)]);
        
        setHairColorType(Math.random() > 0.8 ? 'fancy' : 'natural');
        
        const hairColors = ['Negro profundo', 'Castaño oscuro', 'Castaño medio', 'Castaño claro', 'Rubio oscuro', 'Rubio medio', 'Rubio claro', 'Rubio platino', 'Pelirrojo natural'];
        setHairColor(hairColors[Math.floor(Math.random() * hairColors.length)]);
        
        const fancyColors = ['Azul eléctrico', 'Rosa pastel', 'Morado', 'Verde neón', 'Plateado', 'Blanco puro'];
        setFancyHairColor(fancyColors[Math.floor(Math.random() * fancyColors.length)]);
        
        setHairShape(['Liso', 'Ondulado', 'Rizado'][Math.floor(Math.random() * 3)]);
        setHairLength(['Corto', 'Mediano', 'Largo'][Math.floor(Math.random() * 3)]);
    };

    const handleGenerate = async () => {
        setIsGenerating(true);
        try {
            // Mapping for translation to English for better Flux results
            const translations: Record<string, string> = {
                // Gender
                'Mujer': 'woman', 'Hombre': 'man', 'Secreto': 'person',
                // Eyes Color
                'Azul': 'blue', 'Verde': 'green', 'Café': 'brown', 'Negro': 'black', 'Gris': 'grey',
                // Eyes Shape
                'Almendrados': 'almond-shaped', 'Redondos': 'round', 'Rasgados': 'slanted',
                // Skin Tone
                'Muy claro': 'very fair', 'Claro': 'fair', 'Medio claro': 'light medium', 'Medio': 'medium', 'Medio oscuro': 'tan', 'Oscuro': 'dark', 'Muy oscuro': 'deep dark',
                // Hair Shape
                'Liso': 'straight', 'Ondulado': 'wavy', 'Rizado': 'curly',
                // Hair Length
                'Corto': 'short', 'Mediano': 'medium-length', 'Largo': 'long',
                // Hair Colors (Natural)
                'Negro profundo': 'deep black', 'Castaño oscuro': 'dark brown', 'Castaño medio': 'medium brown', 
                'Castaño claro': 'light brown', 'Rubio oscuro': 'dark blonde', 'Rubio medio': 'medium blonde',
                'Rubio claro': 'light blonde', 'Rubio platino': 'platinum blonde', 'Pelirrojo natural': 'natural redhead',
                // Hair Colors (Fancy)
                'Azul eléctrico': 'electric blue', 'Rosa pastel': 'pastel pink', 'Morado': 'purple',
                'Verde neón': 'neon green', 'Plateado': 'silver', 'Blanco puro': 'pure white'
            };

            const translate = (val: string) => translations[val] || val.toLowerCase();

            // Build Flux Prompt based on user selections
            const hColorRaw = hairColorType === 'natural' ? hairColor : fancyHairColor;
            const hColor = hColorRaw.toLowerCase(); // Colors like "Blue" are mostly the same, but we can refine if needed

            const prompt = `A professional high-fidelity 8k portrait of a ${age} year old ${translate(gender)}. 
            Features: ${translate(eyeColor)} ${translate(eyeShape)} eyes, ${translate(skinTone)} skin tone. 
            Hair: ${translate(hColor)} hair, ${translate(hairShape)} texture, ${translate(hairLength)} style. 
            Cinematic lighting, hyper-realistic, studio background, sharp focus.`;

            const data = await api.generatePortrait(prompt);
            
            const imageUrl = data.image_b64 ? `data:image/png;base64,${data.image_b64}` : data.url;
            
            setHistory(prev => [imageUrl, ...prev]);
            setSelectedImage(imageUrl);
        } catch (error: any) {
            console.error("Error generating portrait:", error);
            const errorMessage = error.message || "Error desconocido al generar la imagen.";
            alert(`Error al generar la imagen: ${errorMessage}`);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
            <div className="bg-white text-black w-full max-w-5xl rounded-2xl shadow-2xl flex flex-col overflow-hidden max-h-[90vh]">
                
                {/* Header */}
                <div className="flex justify-between items-center p-4 border-b border-gray-100">
                    <h2 className="text-xl font-bold flex-1 text-center">Generador de Identidad con IA</h2>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition-colors absolute right-4">
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                <div className="flex flex-1 overflow-hidden">
                    {/* LEFT: History */}
                    <div className="w-[180px] border-r border-gray-100 p-4 overflow-y-auto bg-gray-50/50">
                        <h3 className="text-xs font-bold text-gray-500 uppercase mb-4">Historial</h3>
                        <div className="grid grid-cols-2 gap-2">
                            {history.length > 0 ? history.map((img, i) => (
                                <button 
                                    key={i}
                                    onClick={() => setSelectedImage(img)}
                                    className={cn(
                                        "aspect-square rounded-lg overflow-hidden border-2 transition-all",
                                        selectedImage === img ? "border-pink-500 ring-2 ring-pink-500/20" : "border-transparent hover:border-gray-300"
                                    )}
                                >
                                    <img src={img} alt="History" className="w-full h-full object-cover" />
                                </button>
                            )) : (
                                <p className="text-[10px] text-gray-400 col-span-2 text-center py-4">Sin historial</p>
                            )}
                        </div>
                        {history.length > 0 && <p className="text-[10px] text-gray-400 text-center mt-6">Has llegado al final de la lista.</p>}

                        {/* Load from local file */}
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/png,image/jpeg,image/webp"
                            className="hidden"
                            onChange={handleLoadFromFile}
                        />
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="mt-4 w-full flex items-center justify-center gap-2 py-2 rounded-lg border border-dashed border-gray-300 text-[11px] font-bold text-gray-500 hover:bg-gray-50 hover:border-pink-400 hover:text-pink-600 transition-all"
                        >
                            <FolderOpen className="w-3.5 h-3.5" />
                            Cargar imagen local (sin gastar créditos)
                        </button>
                    </div>

                    {/* CENTER: Preview */}
                    <div className="flex-1 flex flex-col p-6 bg-gray-50/30">
                        <h3 className="text-sm font-bold text-gray-700 mb-4 text-center">Imagen seleccionada</h3>
                        
                        <div className="flex-1 rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50 flex items-center justify-center p-4 overflow-hidden relative group">
                            {selectedImage ? (
                                <img src={selectedImage} alt="Preview" className="w-full h-full object-contain" />
                            ) : (
                                <div className="text-center text-gray-400">
                                    <ImageIcon className="w-12 h-12 mx-auto mb-2 opacity-20" />
                                    <p className="text-sm">Tu generación aparecerá aquí.</p>
                                </div>
                            )}
                            {isGenerating && (
                                <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex flex-col items-center justify-center z-10">
                                    <Loader2 className="w-8 h-8 text-pink-500 animate-spin mb-3" />
                                    <p className="text-sm font-bold text-pink-600 animate-pulse">Sintetizando Identidad...</p>
                                </div>
                            )}
                        </div>

                        <button 
                            disabled={!selectedImage || isGenerating}
                            onClick={() => {
                                if (selectedImage) onSelectImage(selectedImage);
                            }}
                            className={cn(
                                "mt-6 py-4 rounded-xl font-bold text-sm transition-all",
                                selectedImage 
                                    ? "bg-gray-200 text-gray-800 hover:bg-gray-300 active:bg-gray-400" 
                                    : "bg-gray-100 text-gray-400 cursor-not-allowed"
                            )}
                        >
                            Seleccionar esta imagen como referencia
                        </button>
                    </div>

                    {/* RIGHT: Controls */}
                    <div className="w-[340px] border-l border-gray-100 p-6 overflow-y-auto">
                        <button 
                            onClick={handleRandomize}
                            className="w-full flex items-center justify-center gap-2 bg-[#f0386b] hover:bg-[#d62857] text-white py-3 rounded-xl font-bold text-sm transition-all shadow-md shadow-pink-500/20 mb-8"
                        >
                            <Shuffle className="w-4 h-4" />
                            Aleatorio
                        </button>

                        <div className="space-y-6">
                            {/* Gender & Age */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 block">Género</label>
                                    <select 
                                        value={gender} 
                                        onChange={(e) => setGender(e.target.value as any)}
                                        className="w-full bg-white border border-gray-200 text-xs font-bold text-gray-800 rounded-lg px-2 py-2 outline-none focus:border-black"
                                    >
                                        <option value="Mujer">Mujer</option>
                                        <option value="Hombre">Hombre</option>
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <div className="flex justify-between items-end">
                                        <label className="text-xs font-bold text-gray-500">Edad</label>
                                        <span className="text-[10px] font-bold text-gray-800">{age}</span>
                                    </div>
                                    <input 
                                        type="range" min="18" max="70" value={age} 
                                        onChange={(e) => setAge(parseInt(e.target.value))}
                                        className="w-full h-1 bg-gray-200 rounded-full appearance-none outline-none accent-black cursor-pointer"
                                    />
                                </div>
                            </div>

                            {/* Eyes Row */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 block">Ojos: Color</label>
                                    <select 
                                        value={eyeColor} 
                                        onChange={(e) => setEyeColor(e.target.value)}
                                        className="w-full bg-white border border-gray-200 text-xs font-bold text-gray-800 rounded-lg px-2 py-2 outline-none focus:border-black"
                                    >
                                        {['Azul', 'Verde', 'Café', 'Negro', 'Gris'].map(c => <option key={c} value={c}>{c}</option>)}
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 block">Ojos: Forma</label>
                                    <select 
                                        value={eyeShape} 
                                        onChange={(e) => setEyeShape(e.target.value)}
                                        className="w-full bg-white border border-gray-200 text-xs font-bold text-gray-800 rounded-lg px-2 py-2 outline-none focus:border-black"
                                    >
                                        {['Almendrados', 'Redondos', 'Rasgados'].map(s => <option key={s} value={s}>{s}</option>)}
                                    </select>
                                </div>
                            </div>

                            {/* Skin Tone */}
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-gray-500 block">Tono de Piel</label>
                                <select 
                                    value={skinTone} 
                                    onChange={(e) => setSkinTone(e.target.value)}
                                    className="w-full bg-white border border-gray-200 text-xs font-bold text-gray-800 rounded-lg px-2 py-2 outline-none focus:border-black"
                                >
                                    {['Muy claro', 'Claro', 'Medio claro', 'Medio', 'Medio oscuro', 'Oscuro', 'Muy oscuro'].map(t => <option key={t} value={t}>{t}</option>)}
                                </select>
                            </div>

                            {/* Hair Color Selection (Mutually Exclusive) */}
                            <div className="space-y-3 p-3 bg-gray-50 rounded-xl border border-gray-100">
                                <div className="flex gap-4 mb-2">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input 
                                            type="radio" name="hairType" checked={hairColorType === 'natural'} 
                                            onChange={() => setHairColorType('natural')}
                                            className="accent-pink-500"
                                        />
                                        <span className={cn("text-[10px] font-black uppercase tracking-widest", hairColorType === 'natural' ? "text-pink-600" : "text-gray-400")}>Natural</span>
                                    </label>
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input 
                                            type="radio" name="hairType" checked={hairColorType === 'fancy'} 
                                            onChange={() => setHairColorType('fancy')}
                                            className="accent-pink-500"
                                        />
                                        <span className={cn("text-[10px] font-black uppercase tracking-widest", hairColorType === 'fancy' ? "text-pink-600" : "text-gray-400")}>Fantasía</span>
                                    </label>
                                </div>

                                {hairColorType === 'natural' ? (
                                    <select 
                                        value={hairColor} 
                                        onChange={(e) => setHairColor(e.target.value)}
                                        className="w-full bg-white border border-pink-200 text-xs font-bold text-gray-800 rounded-lg px-2 py-2 outline-none"
                                    >
                                        {['Negro profundo', 'Castaño oscuro', 'Castaño medio', 'Castaño claro', 'Rubio oscuro', 'Rubio medio', 'Rubio claro', 'Rubio platino', 'Pelirrojo natural'].map(h => <option key={h} value={h}>{h}</option>)}
                                    </select>
                                ) : (
                                    <select 
                                        value={fancyHairColor} 
                                        onChange={(e) => setFancyHairColor(e.target.value)}
                                        className="w-full bg-white border border-pink-200 text-xs font-bold text-gray-800 rounded-lg px-2 py-2 outline-none"
                                    >
                                        {['Azul eléctrico', 'Rosa pastel', 'Morado', 'Verde neón', 'Plateado', 'Blanco puro'].map(f => <option key={f} value={f}>{f}</option>)}
                                    </select>
                                )}
                            </div>

                            {/* Hair Geometry */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 block">Forma Pelo</label>
                                    <select 
                                        value={hairShape} 
                                        onChange={(e) => setHairShape(e.target.value)}
                                        className="w-full bg-white border border-gray-200 text-xs font-bold text-gray-800 rounded-lg px-2 py-2 outline-none focus:border-black"
                                    >
                                        {['Liso', 'Ondulado', 'Rizado'].map(s => <option key={s} value={s}>{s}</option>)}
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 block">Tamaño Pelo</label>
                                    <select 
                                        value={hairLength} 
                                        onChange={(e) => setHairLength(e.target.value)}
                                        className="w-full bg-white border border-gray-200 text-xs font-bold text-gray-800 rounded-lg px-2 py-2 outline-none focus:border-black"
                                    >
                                        {['Corto', 'Mediano', 'Largo'].map(l => <option key={l} value={l}>{l}</option>)}
                                    </select>
                                </div>
                            </div>
                        </div>

                        {/* Bottom Actions */}
                        <div className="mt-8 pt-6 border-t border-gray-100 flex gap-3">
                            <button 
                                onClick={() => {
                                    setGender('Mujer'); setAge(25); setEyeColor('Café'); setEyeShape('Almendrados'); setSkinTone('Medio');
                                    setHairColorType('natural'); setHairColor('Castaño medio'); setHairShape('Liso'); setHairLength('Mediano');
                                }}
                                className="px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-xl font-bold text-xs text-gray-600 transition-colors"
                            >
                                Restablecer
                            </button>
                            <button 
                                onClick={handleGenerate}
                                disabled={isGenerating}
                                className="flex-1 bg-[#f0386b] hover:bg-[#d62857] text-white py-3 rounded-xl font-bold text-xs transition-colors shadow-md shadow-pink-500/20 disabled:opacity-50"
                            >
                                Generate <span className="font-normal opacity-70 ml-1">-10 créditos</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
