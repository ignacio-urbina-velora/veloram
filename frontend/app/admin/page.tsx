'use client';

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import { api } from '@/lib/api';

interface Stats {
    total_users: number;
    total_affiliates: number;
    active_affiliates: number;
    total_revenue: number;
    total_commissions: number;
    total_paid_out: number;
    pending_payouts: number;
    total_projects: number;
    projects_completed: number;
    projects_queued: number;
}

interface UserAdmin {
    id: number;
    email: string;
    username: string;
    credits: number;
    is_admin: boolean;
    created_at: string;
}

interface QueueItem {
    id: number;
    user_email: string;
    title: string;
    tier: number;
    status: string;
    created_at: string;
}

interface ReferralLog {
    id: number;
    affiliate_code: string;
    referred_email: string;
    sale_amount: number;
    commission_amount: number;
    created_at: string;
}

interface Affiliate {
    id: number;
    user_id: number;
    code: string;
    username: string;
    email: string;
    commission_rate: number;
    discount_pct: number;
    total_referrals: number;
    total_earnings: number;
    pending_payout: number;
    is_active: boolean;
    notes?: string;
}

export default function AdminDashboard() {
    const [stats, setStats] = useState<Stats | null>(null);
    const [affiliates, setAffiliates] = useState<Affiliate[]>([]);
    const [users, setUsers] = useState<UserAdmin[]>([]);
    const [queue, setQueue] = useState<QueueItem[]>([]);
    const [referrals, setReferrals] = useState<ReferralLog[]>([]);
    const [activeTab, setActiveTab] = useState<'stats' | 'users' | 'queue' | 'affiliates' | 'referrals'>('stats');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                if (!api.isLoggedIn()) {
                    setError('No estás autenticado');
                    setLoading(false);
                    return;
                }

                const [sData, aData, uData, qData, rData] = await Promise.all([
                    api.getAdminStats(),
                    api.getAdminAffiliates(),
                    api.getAdminUsers(),
                    api.getAdminQueue(),
                    api.getAdminReferrals(),
                ]);

                setStats(sData);
                setAffiliates(aData);
                setUsers(uData);
                setQueue(qData);
                setReferrals(rData);
            } catch (e: any) {
                setError(`Error de acceso: ${e.message || 'Error desconocido'}`);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handlePayout = async (affId: number, amount: number) => {
        if (!confirm(`¿Confirmar pago de $${amount}?`)) return;
        try {
            await api.processPayout(affId, amount);
            window.location.reload();
        } catch (e: any) {
            alert(`Error al procesar pago: ${e.message}`);
        }
    };

    if (loading) return <div className="min-h-screen bg-dark flex items-center justify-center">Cargando...</div>;
    if (error) return <div className="min-h-screen bg-dark flex items-center justify-center text-red-500">{error}</div>;

    return (
        <main className="min-h-screen bg-dark">
            <Navbar />

            <div className="pt-24 pb-12 px-6 max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold font-heading">Panel de Administración</h1>
                    <div className="flex gap-2 bg-white/5 p-1 rounded-xl">
                        <TabBtn label="Dashboard" active={activeTab === 'stats'} onClick={() => setActiveTab('stats')} />
                        <TabBtn label="Usuarios" active={activeTab === 'users'} onClick={() => setActiveTab('users')} />
                        <TabBtn label="Cola" active={activeTab === 'queue'} onClick={() => setActiveTab('queue')} />
                        <TabBtn label="Afiliados" active={activeTab === 'affiliates'} onClick={() => setActiveTab('affiliates')} />
                        <TabBtn label="Referidos" active={activeTab === 'referrals'} onClick={() => setActiveTab('referrals')} />
                    </div>
                </div>

                {activeTab === 'stats' && (
                    <div className="animate-fade-in">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                            <StatCard title="Usuarios Totales" value={stats?.total_users || 0} icon="👥" />
                            <StatCard title="Ingresos Totales" value={`$${stats?.total_revenue.toFixed(2)}`} icon="💰" />
                            <StatCard title="Cola Activa" value={stats?.projects_queued || 0} icon="⚡" color="var(--accent-primary)" />
                            <StatCard title="Proyectos Listos" value={stats?.projects_completed || 0} icon="✅" color="var(--tier1-color)" />
                        </div>
                        {/* More summary charts could go here */}
                    </div>
                )}

                {activeTab === 'users' && (
                    <div className="glass-card animate-fade-in overflow-hidden">
                        <div className="p-6 border-b border-white/10 flex justify-between items-center">
                            <h2 className="text-xl font-semibold">Gestión de Usuarios</h2>
                            <span className="text-sm text-muted">{users.length} registrados</span>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-white/5 text-xs uppercase tracking-wider text-muted font-bold">
                                    <tr>
                                        <th className="px-6 py-4">Usuario</th>
                                        <th className="px-6 py-4">Créditos</th>
                                        <th className="px-6 py-4">Rol</th>
                                        <th className="px-6 py-4">Antigüedad</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/10">
                                    {users.map(u => (
                                        <tr key={u.id} className="hover:bg-white/5 transition-colors">
                                            <td className="px-6 py-4">
                                                <div className="font-semibold">{u.username}</div>
                                                <div className="text-xs text-muted">{u.email}</div>
                                            </td>
                                            <td className="px-6 py-4 font-bold text-accent">{u.credits} <span className="text-[10px] font-normal text-muted">vids</span></td>
                                            <td className="px-6 py-4">
                                                <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${u.is_admin ? 'bg-purple-500/20 text-purple-400' : 'bg-white/10 text-muted'}`}>
                                                    {u.is_admin ? 'Admin' : 'Usuario'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-sm">{new Date(u.created_at).toLocaleDateString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {activeTab === 'queue' && (
                    <div className="glass-card animate-fade-in overflow-hidden">
                        <div className="p-6 border-b border-white/10">
                            <h2 className="text-xl font-semibold">Cola de Procesamiento</h2>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-white/5 text-xs uppercase tracking-wider text-muted font-bold">
                                    <tr>
                                        <th className="px-6 py-4">Proyecto</th>
                                        <th className="px-6 py-4">Usuario</th>
                                        <th className="px-6 py-4">Tier</th>
                                        <th className="px-6 py-4">Estado</th>
                                        <th className="px-6 py-4">Iniciado</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/10">
                                    {queue.length === 0 ? (
                                        <tr><td colSpan={5} className="px-6 py-12 text-center text-muted">La cola de videos está vacía.</td></tr>
                                    ) : (
                                        queue.map(q => (
                                            <tr key={q.id} className="hover:bg-white/5 transition-colors">
                                                <td className="px-6 py-4 font-semibold">{q.title}</td>
                                                <td className="px-6 py-4 text-sm">{q.user_email}</td>
                                                <td className="px-6 py-4">
                                                    <span className="text-xs bg-white/10 px-2 py-1 rounded">Tier {q.tier}</span>
                                                </td>
                                                <td className="px-6 py-4 text-xs">
                                                    <span className="animate-pulse text-accent uppercase font-bold tracking-tighter">{q.status}</span>
                                                </td>
                                                <td className="px-6 py-4 text-sm">{new Date(q.created_at).toLocaleTimeString()}</td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {activeTab === 'referrals' && (
                    <div className="glass-card animate-fade-in overflow-hidden">
                        <div className="p-6 border-b border-white/10">
                            <h2 className="text-xl font-semibold">Historial de Referidos</h2>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-white/5 text-xs uppercase tracking-wider text-muted font-bold">
                                    <tr>
                                        <th className="px-6 py-4">Referido</th>
                                        <th className="px-6 py-4">Código Usado</th>
                                        <th className="px-6 py-4">Venta</th>
                                        <th className="px-6 py-4">Comisión</th>
                                        <th className="px-6 py-4">Fecha</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/10">
                                    {referrals.map(r => (
                                        <tr key={r.id} className="hover:bg-white/5 transition-colors">
                                            <td className="px-6 py-4 text-sm">{r.referred_email}</td>
                                            <td className="px-6 py-4">
                                                <span className="bg-purple-500/10 text-purple-400 px-2 py-1 rounded font-mono text-xs">{r.affiliate_code}</span>
                                            </td>
                                            <td className="px-6 py-4 font-semibold">${r.sale_amount.toFixed(2)}</td>
                                            <td className="px-6 py-4 text-accent font-bold">${r.commission_amount.toFixed(2)}</td>
                                            <td className="px-6 py-4 text-sm">{new Date(r.created_at).toLocaleDateString()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {activeTab === 'affiliates' && (
                    <div className="glass-card animate-fade-in overflow-hidden">
                        <div className="p-6 border-b border-white/10 flex justify-between items-center">
                            <h2 className="text-xl font-semibold">Gestión de Afiliados</h2>
                            <span className="text-sm text-muted">{affiliates.length} afiliados</span>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-white/5 text-xs uppercase tracking-wider text-muted font-bold">
                                    <tr>
                                        <th className="px-6 py-4">Usuario</th>
                                        <th className="px-6 py-4">Código</th>
                                        <th className="px-6 py-4">Referidos</th>
                                        <th className="px-6 py-4">Pendiente</th>
                                        <th className="px-6 py-4">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/10">
                                    {affiliates.map(aff => (
                                        <tr key={aff.id} className="hover:bg-white/5 transition-colors">
                                            <td className="px-6 py-4">
                                                <div className="font-semibold">{aff.username}</div>
                                                <div className="text-xs text-muted">{aff.email}</div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="bg-white/10 px-2 py-1 rounded font-mono text-sm">{aff.code}</span>
                                            </td>
                                            <td className="px-6 py-4">{aff.total_referrals}</td>
                                            <td className="px-6 py-4 font-bold text-yellow-500">${aff.pending_payout.toFixed(2)}</td>
                                            <td className="px-6 py-4">
                                                <button
                                                    className="btn btn-secondary text-[10px] py-1 px-3"
                                                    disabled={aff.pending_payout <= 0}
                                                    onClick={() => handlePayout(aff.id, aff.pending_payout)}
                                                >
                                                    Pagar
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}

function StatCard({ title, value, icon, color = 'white' }: { title: string, value: string | number, icon: string, color?: string }) {
    return (
        <div className="glass-card p-6 flex items-center gap-4 hover:border-white/20 transition-all cursor-default group">
            <div className="text-3xl bg-white/5 w-14 h-14 flex items-center justify-center rounded-2xl group-hover:scale-110 transition-transform">
                {icon}
            </div>
            <div>
                <p className="text-xs text-muted font-bold uppercase tracking-widest">{title}</p>
                <p className="text-2xl font-bold" style={{ color }}>{value}</p>
            </div>
        </div>
    );
}

function TabBtn({ label, active, onClick }: { label: string, active: boolean, onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${active ? 'bg-white/10 text-white shadow-lg' : 'text-muted hover:text-white hover:bg-white/5'}`}
        >
            {label}
        </button>
    );
}
