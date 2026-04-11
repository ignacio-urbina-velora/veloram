'use client';

import DashboardSidebar from '@/components/DashboardSidebar';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex h-screen bg-[#050505] overflow-hidden">
            <DashboardSidebar />

            {/* Main Content */}
            <main className="flex-1 h-full overflow-y-auto relative">
                {children}
            </main>
        </div>
    );
}
