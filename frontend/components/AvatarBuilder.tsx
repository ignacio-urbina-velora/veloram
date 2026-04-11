'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Sparkles, Check } from 'lucide-react';

// Tipos de atributos seleccionables
type AttributeCategory = {
    id: string;
    label: string;
    options: {
        id: string;
        label: string;
        image: string;
    }[];
};

const ATTRIBUTES: AttributeCategory[] = [
    {
        id: 'hair_style',
        label: 'Elige tu estilo de cabello',
        options: [
            { id: 'liso', label: 'Liso', image: 'https://images.unsplash.com/photo-1595959183082-7b570b7e08e2?w=150&q=80' },
            { id: 'flequillo', label: 'Flequillo', image: 'https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=150&q=80' },
            { id: 'rizado', label: 'Rizado', image: 'https://images.unsplash.com/photo-1605980776566-0486c3ac7617?w=150&q=80' },
            { id: 'mono', label: 'Moño', image: 'https://images.unsplash.com/photo-1563452675059-efa1e2e7a787?w=150&q=80' },
            { id: 'corto', label: 'Corto', image: 'https://images.unsplash.com/photo-1541216970279-affbfdd55aa8?w=150&q=80' },
            { id: 'coleta', label: 'Coleta', image: 'https://images.unsplash.com/photo-1520694478166-daaaaaec94b6?w=150&q=80' },
        ]
    },
    {
        id: 'hair_color',
        label: 'Elige el color del cabello',
        options: [
            { id: 'castano', label: 'Castaño', image: 'https://images.unsplash.com/photo-1514316454349-750ca2234aa3?w=150&q=80' },
            { id: 'rubio', label: 'Rubio', image: 'https://images.unsplash.com/photo-1600608678082-f6735db9d3de?w=150&q=80' },
            { id: 'negro', label: 'Negro', image: 'https://images.unsplash.com/photo-1555529733-0e670560f7e1?w=150&q=80' },
            { id: 'pelirrojo', label: 'Pelirrojo', image: 'https://images.unsplash.com/photo-1550937813-f4325a666ea3?w=150&q=80' },
            { id: 'rosa', label: 'Rosa', image: 'https://images.unsplash.com/photo-1534066228781-309ea6402ec9?w=150&q=80' },
        ]
    },
    {
        id: 'body_type',
        label: 'Elige el tipo de cuerpo',
        options: [
            { id: 'delgada', label: 'Delgada', image: 'https://images.unsplash.com/photo-1512413912949-b5ac1432f7de?w=150&q=80' },
            { id: 'atletica', label: 'Atlética', image: 'https://images.unsplash.com/photo-1579444703816-24e5251664d9?w=150&q=80' },
            { id: 'regular', label: 'Regular', image: 'https://images.unsplash.com/photo-1515934751635-c81c6bc9a2d8?w=150&q=80' },
            { id: 'curvas', label: 'Con curvas', image: 'https://images.unsplash.com/photo-1611796030919-49195e34db02?w=150&q=80' },
        ]
    },
    {
        id: 'breast_size',
        label: 'Elige el tamaño del pecho',
        options: [
            { id: 'pequeno', label: 'Pequeño', image: 'https://images.unsplash.com/photo-1502283944641-fcb2acfc5bd7?w=150&q=80' },
            { id: 'mediano', label: 'Mediano', image: 'https://images.unsplash.com/photo-1510832842233-5bef4bb1a1cf?w=150&q=80' },
            { id: 'grande', label: 'Grande', image: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&q=80' },
        ]
    }
];

interface AvatarBuilderProps {
    onComplete: (prompt: string) => void;
}

export default function AvatarBuilder({ onComplete }: AvatarBuilderProps) {
    const [selections, setSelections] = useState<Record<string, string>>({
        hair_style: 'liso',
        hair_color: 'negro',
        body_type: 'delgada',
        breast_size: 'grande'
    });

    const handleSelect = (categoryId: string, optionId: string) => {
        setSelections(prev => ({
            ...prev,
            [categoryId]: optionId
        }));
    };

    const generatePrompt = () => {
        // Convierte las selecciones visuales en un prompt de texto para la IA
        const prompt = `portrait of a beautiful woman, ${selections.hair_color} ${selections.hair_style} hair, ${selections.body_type} body type, ${selections.breast_size} breasts, highly detailed, 8k resolution, photorealistic, cinematic lighting`;
        onComplete(prompt);
    };

    return (
        <div className="w-full max-w-5xl mx-auto pb-20">
            <div className="space-y-16">

                {ATTRIBUTES.map((category) => (
                    <div key={category.id} className="flex flex-col items-center">
                        <h2 className="text-xl font-bold mb-8 text-white tracking-wide">
                            {category.label}
                        </h2>

                        <div className="flex flex-wrap justify-center gap-4">
                            {category.options.map((option) => {
                                const isSelected = selections[category.id] === option.id;

                                return (
                                    <button
                                        key={option.id}
                                        onClick={() => handleSelect(category.id, option.id)}
                                        className={cn(
                                            "relative group rounded-2xl overflow-hidden aspect-[3/4] w-32 md:w-40 transition-all duration-300",
                                            isSelected
                                                ? "ring-2 ring-white ring-offset-2 ring-offset-[#050505] scale-105"
                                                : "hover:ring-1 hover:ring-white/50 opacity-70 hover:opacity-100"
                                        )}
                                    >
                                        <div className="absolute inset-0">
                                            {/*eslint-disable-next-line @next/next/no-img-element*/}
                                            <img
                                                src={option.image}
                                                alt={option.label}
                                                className="w-full h-full object-cover"
                                            />
                                            {/* Gradiente oscuro inferior para texto */}
                                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
                                        </div>

                                        {/* Icono de Check redondo en la esquina */}
                                        {isSelected && (
                                            <div className="absolute top-2 right-2 bg-white text-black rounded-full p-1 shadow-md">
                                                <Check className="w-3 h-3 font-bold" />
                                            </div>
                                        )}

                                        <div className="absolute bottom-3 inset-x-0 text-center">
                                            <span className="text-base font-bold text-white drop-shadow-md">
                                                {option.label}
                                            </span>
                                        </div>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                ))}

            </div>

            <div className="mt-16 text-center pb-10">
                <button
                    onClick={generatePrompt}
                    className="bg-accent-purple hover:bg-purple-500 text-white px-12 py-4 rounded-full text-sm font-bold uppercase tracking-wider shadow-lg shadow-purple-500/20 transition-all flex items-center gap-2 mx-auto"
                >
                    <Sparkles className="w-5 h-5" />
                    Generar Avatar (15 Créditos)
                </button>
            </div>
        </div>
    );
}
