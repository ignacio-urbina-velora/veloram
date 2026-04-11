import Navbar from '@/components/Navbar';

export default function TermsPage() {
    return (
        <>
            <Navbar />
            <div style={{ paddingTop: '120px', minHeight: '100vh', paddingBottom: '100px', maxWidth: '800px', margin: '0 auto' }} className="container">
                <h1 style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', marginBottom: '32px' }}>Términos y Condiciones</h1>

                <div className="glass-card" style={{ padding: '48px', color: 'var(--text-secondary)', lineHeight: 1.8 }}>
                    <p style={{ marginBottom: '24px' }}>Última actualización: 8 de Marzo de 2026</p>

                    <h2 style={{ fontSize: '1.5rem', color: 'white', marginTop: '32px', marginBottom: '16px' }}>1. Aceptación de los Términos</h2>
                    <p style={{ marginBottom: '24px' }}>
                        Al acceder y utilizar este sitio web y los servicios de plataforma de video generados con IA, usted acepta estar sujeto a estos Términos y Condiciones. Si no está de acuerdo con alguna parte, no podrá utilizar el servicio.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', color: 'white', marginTop: '32px', marginBottom: '16px' }}>2. Servicios de Pagos</h2>
                    <p style={{ marginBottom: '24px' }}>
                        Nuestros pagos son procesados de forma segura a través de pasarelas como Cryptomus. Al realizar una compra de cualquier plan (Tier 1, Tier 2 o Tier 3), usted está de acuerdo con las políticas de procesamiento de pagos establecidas por nuestros proveedores. Los pagos pueden realizarse en criptomonedas asegurando una transacción rápida y privada.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', color: 'white', marginTop: '32px', marginBottom: '16px' }}>3. Uso del Servicio</h2>
                    <p style={{ marginBottom: '24px' }}>
                        Usted acepta utilizar el servicio de generación de videos mediante IA solo para fines legales y de acuerdo con estos Términos. Los recursos (GPU en la nube) se asignan basándose en el Tier comprado. Queda estrictamente prohibida la generación de material ilegal.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', color: 'white', marginTop: '32px', marginBottom: '16px' }}>4. Política de Reembolso</h2>
                    <p style={{ marginBottom: '24px' }}>
                        Ofrecemos entregables digitales bajo demanda e interacciones de servidor (como alquiler de GPUs en la nube). Debido a la naturaleza de estos costos incurridos inmediatamente, los pagos por planes no son reembolsables una vez que se ha iniciado la generación de los videos. Excepciones de fuerza mayor serán evaluadas por nuestro equipo de soporte técnico.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', color: 'white', marginTop: '32px', marginBottom: '16px' }}>5. Programa de Afiliados</h2>
                    <p style={{ marginBottom: '24px' }}>
                        Los usuarios pueden registrarse en el Programa de Afiliados de manera gratuita. Los afiliados ganarán una comisión fija según el plan adquirido por sus referidos. El pago mínimo de retiro es de $50 USD. El comportamiento fraudulento para aumentar afiliados resultará en el cierre inmediato de la cuenta sin derecho a pago.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', color: 'white', marginTop: '32px', marginBottom: '16px' }}>6. Modificaciones</h2>
                    <p>
                        Nos reservamos el derecho de modificar estos términos en cualquier momento. Los cambios se notificarán en esta página de forma inmediata.
                    </p>

                </div>
            </div>
        </>
    );
}
