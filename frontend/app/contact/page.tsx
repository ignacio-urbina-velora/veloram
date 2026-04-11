import Navbar from '@/components/Navbar';
import Link from 'next/link';

export default function ContactPage() {
    return (
        <>
            <Navbar />
            <div style={{ paddingTop: '120px', minHeight: '100vh', paddingBottom: '100px', maxWidth: '800px', margin: '0 auto' }} className="container">
                <h1 style={{ fontSize: '3rem', fontFamily: 'var(--font-heading)', marginBottom: '24px', textAlign: 'center' }}>Contacto y Soporte</h1>

                <div className="glass-card" style={{ padding: '40px', marginTop: '48px' }}>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', marginBottom: '32px', textAlign: 'center' }}>
                        Si tienes dudas sobre facturación, pagos con criptomonedas (Cryptomus), suscripciones, o necesitas soporte técnico, por favor envíanos un mensaje y te responderemos a la brevedad.
                    </p>

                    <form style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                            <div>
                                <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Nombre</label>
                                <input type="text" className="input" placeholder="Tu nombre" style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-glass)', borderRadius: 'var(--radius-md)', color: 'white' }} required />
                            </div>
                            <div>
                                <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Correo Electrónico</label>
                                <input type="email" className="input" placeholder="tu@email.com" style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-glass)', borderRadius: 'var(--radius-md)', color: 'white' }} required />
                            </div>
                        </div>

                        <div>
                            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Asunto</label>
                            <select className="input" style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-glass)', borderRadius: 'var(--radius-md)', color: 'white' }}>
                                <option value="billing">Facturación / Pagos</option>
                                <option value="support">Soporte Técnico</option>
                                <option value="affiliates">Afiliados</option>
                                <option value="other">Otro</option>
                            </select>
                        </div>

                        <div>
                            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>Mensaje</label>
                            <textarea className="input" rows={6} placeholder="¿En qué podemos ayudarte?" style={{ width: '100%', padding: '12px', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border-glass)', borderRadius: 'var(--radius-md)', color: 'white' }} required></textarea>
                        </div>

                        <button type="button" className="btn btn-primary" style={{ padding: '16px', fontSize: '1.1rem' }}>
                            Enviar Mensaje
                        </button>
                    </form>
                </div>

                <div style={{ marginTop: '48px', display: 'flex', justifyContent: 'center', gap: '48px', color: 'var(--text-secondary)' }}>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>📧</div>
                        <div>support@velora-studio.site</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>💬</div>
                        <div>Chat en vivo 24/7 (Próximamente)</div>
                    </div>
                </div>
            </div>
        </>
    );
}
