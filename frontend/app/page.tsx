'use client';

import Navbar from '@/components/Navbar';
import HeroBackground from '@/components/HeroBackground';
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';

export default function LandingPage() {

  return (
    <>
      <Navbar />

      {/* Hero Section */}
      {/* Hero Section */}
      <section className="relative min-h-screen overflow-hidden flex flex-col">
        <HeroBackground />
        
        {/* Top Logo - Fixed / Absolute Centered */}
        <div className="absolute top-8 left-1/2 -translate-x-1/2 z-30 transition-all hover:scale-105">
           <Link href="/">
            <img 
              src="/logo.png" 
              alt="Velora Studio Logo" 
              className="h-10 md:h-14 drop-shadow-[0_0_20px_rgba(255,0,0,0.3)]"
            />
          </Link>
        </div>

        {/* Hero Content Container */}
        <div className="relative z-20 flex-1 flex flex-col md:flex-row items-center justify-between px-6 md:px-16 lg:px-24 py-32 md:py-0">
          
          {/* Left Column: Vision & Action */}
          <div className="flex-1 max-w-xl animate-in slide-in-from-left duration-1000">
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-black text-white leading-[1.1] mb-6 tracking-tight">
              Crea tu <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-white/60">
                Influencer Digital
              </span>
            </h1>
            
            <div className="mt-10 flex flex-col gap-6">
              <Link href="/studio" className="group relative w-fit">
                <div className="absolute -inset-1 bg-gradient-to-r from-white/20 to-transparent rounded-lg blur opacity-20 group-hover:opacity-40 transition" />
                <button className="relative bg-white text-black px-10 py-4 rounded-lg font-black text-sm uppercase tracking-widest hover:bg-neutral-200 transition-all shadow-2xl shadow-white/10">
                  CREAR GRATIS
                </button>
              </Link>
              
              <div className="flex items-center gap-4 text-white/40 text-[10px] font-bold uppercase tracking-[0.2em]">
                <span>Impacto de Escala</span>
                <span className="w-1 h-1 rounded-full bg-white/20" />
                <span>Monetizar tu influencia</span>
              </div>
            </div>
          </div>

          {/* Spacer / Center Area for the Subject Visibility */}
          <div className="hidden lg:block flex-1 pointer-events-none" />

          {/* Right Column: Affiliate / Context Box */}
          <div className="mt-16 md:mt-0 max-w-sm w-full animate-in slide-in-from-right duration-1000">
            <div className="glass-card-premium p-8 md:p-10 border border-white/10 bg-white/[0.03] backdrop-blur-3xl rounded-3xl relative group overflow-hidden">
               {/* Animated subtle glow */}
               <div className="absolute -top-24 -right-24 w-48 h-48 bg-red-600/10 blur-[100px] group-hover:bg-red-600/20 transition-all duration-700" />
               
               <div className="relative z-10">
                 <div className="flex items-center gap-2 mb-6">
                   <div className="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
                   <span className="text-[10px] font-black tracking-[0.3em] uppercase text-white/40">Colaboración</span>
                 </div>

                 <h3 className="text-xl md:text-2xl font-bold text-white mb-4 leading-snug">
                   Gana de <span className="text-emerald-400">$1,000</span> a <span className="text-emerald-400">$5,000</span> como afiliado
                 </h3>
                 
                 <p className="text-sm text-white/50 leading-relaxed mb-8">
                   Refiere Velora Studio y obtén comisiones recurrentes de por vida. El mercado de influencers IA está explotando.
                 </p><Link href="http://localhost:3004/affiliates" className="flex items-center justify-between group/btn bg-white/5 hover:bg-white/10 border border-white/10 p-4 rounded-xl transition-all">
                   <span className="text-xs font-bold text-white">Únete al Programa</span>
                   <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center group-hover/btn:translate-x-1 transition-transform">
                     <ChevronRight className="w-4 h-4 text-white" />
                   </div>
                 </Link>
               </div>
            </div>

          </div>

        </div>

        {/* Floating Scroll Indicator style - Optional but subtle */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 opacity-20 pointer-events-none mb-4 md:mb-0">
          <div className="w-[1px] h-12 bg-gradient-to-b from-white to-transparent" />
        </div>
      </section>

      {/* Pricing / Products Section Preview for Moderation */}
      <section className="py-24 px-6 md:px-16 container mx-auto text-center" id="pricing">
        <h2 className="text-3xl md:text-5xl font-black text-white mb-6">Planes de Producción de Video IA</h2>
        <p className="text-white/60 mb-12 max-w-2xl mx-auto">Ofrecemos servicios de generación de video de alta calidad para creadores de contenido usando nuestra granja de GPUs. (Pagos seguros vía Cryptomus)</p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { name: "Standard AI Pack", price: "$50", desc: "Desde 5 Videos LTX-2" },
            { name: "Professional Creator Pack", price: "$90", desc: "Desde 5 Videos Wan 2.2" },
            { name: "Cinema Grade Media Pack", price: "$350", desc: "Desde 5 Videos HunyuanVideo" }
          ].map((plan, i) => (
            <div key={i} className="glass-card p-8 flex flex-col items-center justify-between border border-white/10 rounded-2xl bg-white/[0.02]">
              <div className="mb-4">
                <h3 className="text-xl font-bold text-white mb-2">{plan.name}</h3>
                <p className="text-white/50 text-sm mb-6">{plan.desc}</p>
                <div className="text-4xl font-black text-emerald-400 mb-8">{plan.price}</div>
              </div>
              <Link href="http://localhost:3004" className="w-full py-3 rounded-lg bg-white/10 hover:bg-white/20 transition-all text-white font-bold border border-white/10">
                Ver Catálogo Completo
              </Link>
            </div>
          ))}
        </div>
      </section>

      <footer style={{
        padding: '60px 32px 40px',
        borderTop: '1px solid var(--border-glass)',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: '0.85rem',
        zIndex: 1,
        position: 'relative',
      }}>
        <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '24px', marginBottom: '16px' }}>
          <Link href="http://localhost:3004" className="hover:text-white transition-colors">Planes y Precios</Link>
          <Link href="/terms" className="hover:text-white transition-colors">Términos y Condiciones</Link>
          <Link href="/privacy" className="hover:text-white transition-colors">Política de Privacidad</Link>
          <Link href="/contact" className="hover:text-white transition-colors">Contacto</Link>
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '24px', marginBottom: '24px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <Link href="/terms#deepfakes" className="hover:text-white transition-colors">Prohibición de deepfakes no consentidos</Link>
          <Link href="/terms#ai-content" className="hover:text-white transition-colors">Contenido generado por IA</Link>
          <Link href="/terms#anti-csam" className="hover:text-white transition-colors">Política anti-CSAM</Link>
        </div>
        <div style={{ marginBottom: '24px', color: 'var(--text-secondary)' }}>
          <p>Email de contacto: <a href="mailto:admin@velora-studio.site" className="text-white hover:underline">admin@velora-studio.site</a></p>
        </div>
        <p>◆ Velora Studio · GPU-powered by vast.ai · ComfyUI + LTX-2 / Wan 2.2 / HunyuanVideo</p>
        <p style={{ marginTop: '8px', opacity: 0.6 }}>
          © 2026 Velora Studio. All rights reserved
        </p>
      </footer>
    </>
  );
}
