'use client';

import { useState } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { api } from '@/lib/api';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    // Effect for handling Magic Link tokens
    useState(() => {
        if (typeof window !== 'undefined') {
            const params = new URLSearchParams(window.location.search);
            const token = params.get('token');
            const emailParam = params.get('email');
            
            if (token && emailParam) {
                setLoading(true);
                // Simulate magic login (in production this calls a Supabase verify endpoint)
                setEmail(emailParam);
                setTimeout(async () => {
                    try {
                        // For now we use a placeholder sync, in real prod you'd use Supabase magic link verify
                        await api.loginWithToken(emailParam, token);
                        window.location.href = '/studio';
                    } catch (err: any) {
                        setError('El enlace de acceso ha expirado o es inválido.');
                        setLoading(false);
                    }
                }, 1000);
            }
        }
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await api.login(email, password);
            window.location.href = '/studio';
        } catch (err: any) {
            let msg = 'Error al iniciar sesión';
            const detail = err.message || '';

            if (detail.includes('USER_NOT_FOUND')) {
                msg = 'Este correo electrónico no está registrado.';
            } else if (detail.includes('INVALID_PASSWORD')) {
                msg = 'La contraseña es incorrecta. Inténtalo de nuevo.';
            } else {
                msg = detail || 'Error de conexión con el servidor.';
            }

            setError(msg);
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
                        Bienvenido
                    </h1>
                    <p style={{
                        textAlign: 'center',
                        color: 'rgba(255,255,255,0.4)',
                        fontSize: '0.85rem',
                        fontWeight: '500',
                        marginBottom: '40px',
                    }}>
                        Inicia sesión para acceder al estudio creativo
                    </p>

                    <form onSubmit={handleSubmit}>
                        <div style={{ marginBottom: '20px' }}>
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
                        <div style={{ marginBottom: '12px' }}>
                            <label className="label">Contraseña</label>
                            <input
                                className="input-field"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                required
                            />
                        </div>

                        <div style={{ textAlign: 'right', marginBottom: '32px' }}>
                            <Link href="/forgot-password" style={{ 
                                fontSize: '0.75rem', 
                                color: 'rgba(255,255,255,0.3)', 
                                textDecoration: 'none',
                                fontWeight: '600'
                            }} className="hover:text-white transition-colors">
                                ¿Olvidaste tu contraseña?
                            </Link>
                        </div>

                        {error && (
                            <div style={{
                                padding: '10px',
                                background: 'rgba(239,68,68,0.1)',
                                border: '1px solid rgba(239,68,68,0.3)',
                                borderRadius: 'var(--radius-sm)',
                                color: '#ef4444',
                                fontSize: '0.85rem',
                                marginBottom: '16px',
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
                            {loading ? '⏳ Entrando...' : 'Iniciar Sesión'}
                        </button>
                    </form>

                    <p style={{
                        textAlign: 'center',
                        marginTop: '24px',
                        fontSize: '0.85rem',
                        color: 'var(--text-muted)',
                    }}>
                        ¿No tienes cuenta?{' '}
                        <Link href="/register" style={{ color: 'var(--accent-secondary)', textDecoration: 'none' }}>
                            Regístrate gratis
                        </Link>
                    </p>
                </div>
            </main>
        </>
    );
}
