'use client';

import { useState } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { api } from '@/lib/api';

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setMessage('');
        setLoading(true);
        try {
            const res = await api.forgotPassword(email);
            setMessage(res.message || 'Se ha enviado un enlace de recuperación a tu correo.');
        } catch (err: any) {
            setError(err.message || 'Error al procesar la solicitud.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <Navbar />
            <main style={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '120px 32px 60px',
                position: 'relative',
                zIndex: 1,
            }}>
                <div className="glass-card-premium animate-fade-in-up" style={{
                    padding: '48px',
                    maxWidth: '440px',
                    width: '100%',
                }}>
                    <h1 style={{
                        fontFamily: 'var(--font-heading)',
                        fontSize: '2.2rem',
                        fontWeight: '900',
                        textAlign: 'center',
                        marginBottom: '8px',
                        letterSpacing: '-0.02em'
                    }}>
                        Recuperar Acceso
                    </h1>
                    <p style={{
                        textAlign: 'center',
                        color: 'rgba(255,255,255,0.4)',
                        fontSize: '0.85rem',
                        fontWeight: '500',
                        marginBottom: '40px',
                    }}>
                        Introduce tu correo y te enviaremos un enlace de recuperación.
                    </p>

                    <form onSubmit={handleSubmit}>
                        <div style={{ marginBottom: '32px' }}>
                            <label className="label">Correo Electrónico</label>
                            <input
                                className="input-field"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="tu@email.com"
                                required
                            />
                        </div>

                        {message && (
                            <div style={{
                                padding: '12px',
                                background: 'rgba(34,197,94,0.1)',
                                border: '1px solid rgba(34,197,94,0.3)',
                                borderRadius: 'var(--radius-sm)',
                                color: '#4ade80',
                                fontSize: '0.85rem',
                                marginBottom: '24px',
                                textAlign: 'center'
                            }}>
                                {message}
                            </div>
                        )}

                        {error && (
                            <div style={{
                                padding: '12px',
                                background: 'rgba(239,68,68,0.1)',
                                border: '1px solid rgba(239,68,68,0.3)',
                                borderRadius: 'var(--radius-sm)',
                                color: '#ef4444',
                                fontSize: '0.85rem',
                                marginBottom: '24px',
                                textAlign: 'center'
                            }}>
                                {error}
                            </div>
                        )}

                        <button
                            className="btn btn-primary"
                            type="submit"
                            disabled={loading}
                            style={{ width: '100%', padding: '14px' }}
                        >
                            {loading ? '⏳ Enviando...' : 'Enviar Enlace'}
                        </button>
                    </form>

                    <p style={{
                        textAlign: 'center',
                        marginTop: '24px',
                        fontSize: '0.85rem',
                        color: 'var(--text-muted)',
                    }}>
                        ¿Recordaste tu contraseña?{' '}
                        <Link href="/login" style={{ color: 'var(--accent-secondary)', textDecoration: 'none' }}>
                            Volver al login
                        </Link>
                    </p>
                </div>
            </main>
        </>
    );
}
