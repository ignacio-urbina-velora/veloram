'use client';

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import { api } from '@/lib/api';
import { Copy, CheckCircle, Wallet, Users, DollarSign } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function AffiliateDashboard() {
    const [affiliateData, setAffiliateData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [copied, setCopied] = useState(false);
    const router = useRouter();

    useEffect(() => {
        if (!api.isLoggedIn()) {
            router.push('/login?redirect=/affiliates');
            return;
        }

        const fetchAffiliateData = async () => {
            try {
                const data = await api.getAffiliateMe();
                setAffiliateData(data);
            } catch (err: any) {
                if (err.message.includes('404')) {
                    const user = api.getUser();
                    const cleanUsername = user?.username?.toLowerCase().replace(/[^a-z0-9]/g, '_') || `user_${Date.now()}`;
                    
                    try {
                        const newData = await api.applyAffiliate({
                            code: cleanUsername,
                            payment_method: 'PayPal / USDT',
                            payment_details: 'Not set'
                        });
                        setAffiliateData(newData);
                    } catch (applyErr) {
                        console.error('Error applying for affiliate:', applyErr);
                    }
                } else {
                    console.error('Error fetching affiliate data:', err);
                }
            } finally {
                setLoading(false);
            }
        };

        fetchAffiliateData();
    }, [router]);

    const copyLink = () => {
        const link = `${window.location.origin}/?ref=${affiliateData?.code}`;
        navigator.clipboard.writeText(link);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (loading) {
        return (
            <>
                <Navbar />
                <div className="min-h-screen flex items-center justify-center">
                    <div className="animate-pulse text-xl">Cargando tu perfil de socio...</div>
                </div>
            </>
        );
    }

    if (!affiliateData) {
        return (
            <>
                <Navbar />
                <div className="min-h-screen flex items-center justify-center p-8 text-center">
                    <div className="glass-card p-12">
                        <h2 className="text-2xl mb-4">Iniciando Programa de Afiliados</h2>
                        <p className="text-muted mb-6">Estamos configurando tu enlace único. Por favor refresca la página.</p>
                        <button onClick={() => window.location.reload()} className="btn btn-primary">Refrescar</button>
                    </div>
                </div>
            </>
        );
    }

    return (
        <>
            <Navbar />
            <div style={{ paddingTop: '100px', minHeight: '100vh', paddingBottom: '100px' }} className="container">
                <h1 style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', marginBottom: '8px' }}>
                    Dashboard de Afiliados
                </h1>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '48px' }}>
                    Gana hasta $135 USD por cada venta referida. Pagos mínimos $50 vía USDT o PayPal.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>

                    {/* Stats row */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px' }}>

                        <div className="glass-card" style={{ padding: '32px', display: 'flex', alignItems: 'center', gap: '24px' }}>
                            <div style={{ padding: '16px', background: 'rgba(139,92,246,0.1)', borderRadius: '16px', color: 'var(--accent-primary)' }}>
                                <Users size={32} />
                            </div>
                            <div>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Total Referidos</p>
                                <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{affiliateData.total_referrals || 0}</p>
                            </div>
                        </div>

                        <div className="glass-card" style={{ padding: '32px', display: 'flex', alignItems: 'center', gap: '24px' }}>
                            <div style={{ padding: '16px', background: 'rgba(236,72,153,0.1)', borderRadius: '16px', color: 'var(--accent-secondary)' }}>
                                <DollarSign size={32} />
                            </div>
                            <div>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Ganancias ($)</p>
                                <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>${affiliateData.total_earnings?.toFixed(2) || '0.00'}</p>
                            </div>
                        </div>

                        <div className="glass-card" style={{ padding: '32px', display: 'flex', alignItems: 'center', gap: '24px', border: '1px solid rgba(251,191,36,0.3)' }}>
                            <div style={{ padding: '16px', background: 'rgba(251,191,36,0.1)', borderRadius: '16px', color: '#fbbf24' }}>
                                <Wallet size={32} />
                            </div>
                            <div>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Saldo Disponible</p>
                                <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fbbf24' }}>${affiliateData.pending_payout?.toFixed(2) || '0.00'}</p>
                            </div>
                        </div>

                    </div>

                    {/* Link generator */}
                    <div className="glass-card" style={{ padding: '32px' }}>
                        <h3 style={{ fontSize: '1.3rem', marginBottom: '16px' }}>Tu Enlace de Afiliado</h3>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
                            Comparte este enlace. ¡Obtendrás una comisión fija en USDT/PayPal por cada compra que hagan los usuarios que lleguen a través de tu enlace!
                        </p>

                        <div style={{ display: 'flex', gap: '16px' }}>
                            <input
                                type="text"
                                readOnly
                                value={`${typeof window !== 'undefined' ? window.location.origin : ''}/?ref=${affiliateData.code}`}
                                style={{ flex: 1, padding: '16px', borderRadius: 'var(--radius-md)', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-glass)', color: 'white' }}
                            />
                            <button
                                onClick={copyLink}
                                className="btn btn-secondary"
                                style={{ display: 'flex', gap: '8px', alignItems: 'center' }}
                            >
                                {copied ? <CheckCircle size={18} /> : <Copy size={18} />}
                                {copied ? 'Copiado' : 'Copiar'}
                            </button>
                        </div>
                    </div>

                    {/* Referrals Table */}
                    <div className="glass-card" style={{ padding: '32px' }}>
                        <h3 style={{ fontSize: '1.3rem', marginBottom: '24px' }}>Mis Referidos</h3>
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <thead>
                                    <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border-glass)' }}>
                                        <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>ID Usuario</th>
                                        <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Comisión</th>
                                        <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Estado</th>
                                        <th style={{ padding: '16px', color: 'var(--text-secondary)' }}>Fecha</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(affiliateData.referrals || []).length === 0 ? (
                                        <tr>
                                            <td colSpan={4} style={{ padding: '32px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                                                Aún no tienes referidos. ¡Comparte tu enlace para empezar a ganar!
                                            </td>
                                        </tr>
                                    ) : (
                                        affiliateData.referrals.map((ref: any) => (
                                            <tr key={ref.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                                <td style={{ padding: '16px' }}>user_{ref.referred_user_id}</td>
                                                <td style={{ padding: '16px', fontWeight: 'bold' }}>${ref.commission_amount.toFixed(2)}</td>
                                                <td style={{ padding: '16px' }}>
                                                    <span style={{ 
                                                        padding: '4px 8px', 
                                                        borderRadius: '4px', 
                                                        fontSize: '0.8rem',
                                                        background: ref.commission_paid ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)',
                                                        color: ref.commission_paid ? '#10b981' : '#f59e0b'
                                                    }}>
                                                        {ref.commission_paid ? 'Pagado' : 'Pendiente'}
                                                    </span>
                                                </td>
                                                <td style={{ padding: '16px', color: 'var(--text-secondary)' }}>
                                                    {new Date(ref.created_at).toLocaleDateString()}
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                </div>
            </div>
        </>
    );
}
