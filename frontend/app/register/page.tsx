'use client';

import { useState } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { api } from '@/lib/api';

export default function RegisterPage() {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await api.register(email, username, password);
            window.location.href = '/studio';
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Registration failed');
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
                        Crear Cuenta
                    </h1>
                    <p style={{
                        textAlign: 'center',
                        color: 'rgba(255,255,255,0.4)',
                        fontSize: '0.85rem',
                        fontWeight: '500',
                        marginBottom: '40px',
                    }}>
                        Empieza con $5 de créditos gratis hoy
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
                        <div style={{ marginBottom: '20px' }}>
                            <label className="label">Nombre de Usuario</label>
                            <input
                                className="input-field"
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="tu_username"
                                required
                                minLength={3}
                            />
                        </div>
                        <div style={{ marginBottom: '32px' }}>
                            <label className="label">Contraseña</label>
                            <input
                                className="input-field"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Mínimo 8 caracteres"
                                required
                                minLength={8}
                            />
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
                            {loading ? '⏳ Creando...' : '🚀 Crear Cuenta Gratis'}
                        </button>
                    </form>

                    <p style={{
                        textAlign: 'center',
                        marginTop: '24px',
                        fontSize: '0.85rem',
                        color: 'var(--text-muted)',
                    }}>
                        ¿Ya tienes cuenta?{' '}
                        <Link href="/login" style={{ color: 'var(--accent-secondary)', textDecoration: 'none' }}>
                            Inicia sesión
                        </Link>
                    </p>
                </div>
            </main>
        </>
    );
}
