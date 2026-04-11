'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const HERO_IMAGES = [
    {
        url: '/hero-assets/hero_ai_influencer_1_1773070991712.png',
        alt: 'AI Influencer Digital',
    }
];

export default function HeroBackground() {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => {
            setIndex((prev) => (prev + 1) % HERO_IMAGES.length);
        }, 6000); // 6 seconds per image (4s view + 2s transition overlap)
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="absolute inset-0 overflow-hidden z-0">
            <AnimatePresence mode="wait">
                <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 1.1 }}
                    animate={{ opacity: 1, scale: 1.05 }}
                    exit={{ opacity: 0, scale: 1 }}
                    transition={{ duration: 2, ease: "easeInOut" }}
                    className="absolute inset-0 w-full h-full"
                >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                        src={HERO_IMAGES[index].url}
                        alt={HERO_IMAGES[index].alt}
                        className="w-full h-full object-cover"
                    />
                </motion.div>
            </AnimatePresence>

            {/* Premium Overlays: Red & Cinematic */}
            <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-transparent to-red-600/20 z-10" />
            <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-black/40 z-10" />
            <div className="absolute inset-0 radial-vignette z-10" />
            <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-red-600/10 to-transparent z-10 mix-blend-overlay" />

            <style jsx>{`
                .radial-vignette {
                    background: radial-gradient(circle, transparent 20%, rgba(0,0,0,0.4) 100%);
                }
            `}</style>
        </div>
    );
}
