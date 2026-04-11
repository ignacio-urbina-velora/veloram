import Navbar from '@/components/Navbar';
import Link from 'next/link';
import { Check } from 'lucide-react';

export default function PricingPage() {
    const tiers = [
        {
            name: 'Tier 1 - Quick',
            description: 'LTX-2 fp8',
            features: ['Generación en minutos', 'Calidad LTX-2', 'Soporte Básico', 'Resolución 720p', 'Interpolación estándar'],
            plans: [
                { name: 'Basic', price: 50, videos: 5, credits: 22.5, specs: 'Hasta 5 videos generados' },
                { name: 'Medium', price: 85, videos: 10, credits: 45.0, specs: 'Hasta 10 videos generados' },
                { name: 'Full', price: 150, videos: 20, credits: 90.0, specs: 'Hasta 20 videos generados' },
            ],
            color: 'var(--accent-primary)',
            bg: 'rgba(139,92,246,0.1)'
        },
        {
            name: 'Tier 2 - Pro',
            description: 'Wan 2.2 FP8 + NSFW LoRA',
            features: ['Soporte oficial Estilo Anime', 'Generación en Alta Calidad', 'Modelo Wan 2.2 Avanzado', 'Resolución 1080p', 'Soporte LoRA especializado'],
            plans: [
                { name: 'Basic Pro', price: 90, videos: 5, credits: 55.0, specs: 'Hasta 5 videos generados' },
                { name: 'Medium Pro', price: 159, videos: 10, credits: 110.0, specs: 'Hasta 10 videos generados' },
                { name: 'Full Pro', price: 299, videos: 20, credits: 220.0, specs: 'Hasta 20 videos generados' },
            ],
            color: 'var(--accent-secondary)',
            bg: 'rgba(236,72,153,0.1)'
        },
        {
            name: 'Tier 3 - Cinematic Ultra',
            description: 'HunyuanVideo bf16 + post-producción pesada',
            features: ['Calidad Cinematográfica', 'Modelo HunyuanVideo Premium', 'Soporte 24/7', 'Resolución 4K', 'Post-producción pesada a 60 FPS'],
            plans: [
                { name: 'Basic Cinematic', price: 350, videos: 5, credits: 182.5, specs: 'Hasta 5 videos generados' },
                { name: 'Medium Cinematic', price: 680, videos: 10, credits: 365.0, specs: 'Hasta 10 videos generados' },
                { name: 'Full Cinematic', price: 1350, videos: 20, credits: 730.0, specs: 'Hasta 20 videos generados' },
            ],
            color: '#fbbf24',
            bg: 'rgba(251,191,36,0.1)'
        }
    ];

    return (
        <>
            <Navbar />
            <div style={{ paddingTop: '100px', minHeight: '100vh', paddingBottom: '100px' }} className="container">
                <div style={{ textAlign: 'center', marginBottom: '80px' }}>
                    <h1 style={{
                        fontFamily: 'var(--font-heading)',
                        fontSize: '3rem',
                        marginBottom: '16px',
                        background: 'var(--accent-gradient)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                    }}>
                        Planes y Precios
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto' }}>
                        Selecciona el Tier de producción y el paquete de videos que mejor se adapte a tus necesidades. Todos los valores están en dólares estadounidenses (USD).
                    </p>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '64px' }}>
                    {tiers.map((tier, idx) => (
                        <div key={idx} className="glass-card" style={{ padding: '48px', position: 'relative', overflow: 'hidden' }}>
                            <div style={{
                                position: 'absolute', top: '-100px', right: '-100px', width: '300px', height: '300px',
                                background: tier.bg, filter: 'blur(80px)', borderRadius: '50%', zIndex: 0
                            }} />

                            <div style={{ position: 'relative', zIndex: 1 }}>
                                <div style={{ marginBottom: '32px', textAlign: 'center' }}>
                                    <h2 style={{ fontSize: '2rem', fontFamily: 'var(--font-heading)', color: tier.color, marginBottom: '8px' }}>
                                        {tier.name}
                                    </h2>
                                    <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>{tier.description}</p>
                                </div>

                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px', marginBottom: '48px' }}>
                                    {tier.plans.map((plan, pIdx) => (
                                        <div key={pIdx} style={{
                                            border: '1px solid var(--border-glass)',
                                            borderRadius: 'var(--radius-lg)',
                                            padding: '32px 24px',
                                            background: 'rgba(255,255,255,0.02)',
                                            textAlign: 'center',
                                            display: 'flex',
                                            flexDirection: 'column',
                                            justifyContent: 'space-between',
                                            transition: 'transform 0.2s',
                                            cursor: 'pointer',
                                        }}
                                            className="hover:scale-105"
                                        >
                                            <div>
                                                <h3 style={{ fontSize: '1.3rem', fontWeight: 600, marginBottom: '16px' }}>{plan.name}</h3>
                                                {plan.credits && (
                                                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '8px', fontWeight: 500 }}>
                                                        {plan.credits} créditos de generación
                                                    </div>
                                                )}
                                                <div style={{ fontSize: '3rem', fontWeight: 800, fontFamily: 'var(--font-heading)', marginBottom: '8px', color: tier.color }}>
                                                    ${plan.price}
                                                </div>
                                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '24px' }}>
                                                    USD / pago único
                                                </p>
                                                <p style={{ fontWeight: 600, fontSize: '1.1rem', marginBottom: '8px' }}>{plan.videos} Videos</p>
                                                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{plan.specs}</p>
                                            </div>

                                            <Link href="http://localhost:3004" className="btn btn-primary" style={{ marginTop: '24px', width: '100%', background: tier.bg, color: tier.color, border: `1px solid ${tier.color}` }}>
                                                Comprar Plan
                                            </Link>
                                        </div>
                                    ))}
                                </div>

                                <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '32px' }}>
                                    <h4 style={{ fontSize: '1.2rem', marginBottom: '24px', textAlign: 'center' }}>Características Incluidas</h4>
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                                        {tier.features.map((feat, fIdx) => (
                                            <div key={fIdx} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                <div style={{ background: tier.bg, color: tier.color, padding: '4px', borderRadius: '50%' }}>
                                                    <Check size={16} />
                                                </div>
                                                <span style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>{feat}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                            </div>
                        </div>
                    ))}
                </div>

                {/* Support Banner for CCBill */}
                <div style={{ marginTop: '80px', textAlign: 'center', padding: '48px', border: '1px solid var(--border-glass)', borderRadius: 'var(--radius-lg)', background: 'rgba(255,255,255,0.02)' }}>
                    <h3 style={{ fontSize: '1.5rem', marginBottom: '16px' }}>¿Necesitas Ayuda?</h3>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>Si tienes alguna pregunta sobre nuestros planes o necesitas soporte técnico o de facturación, estamos aquí para ti.</p>
                    <Link href="/contact" className="btn btn-secondary">Contactar Soporte</Link>
                </div>
            </div>
        </>
    );
}
