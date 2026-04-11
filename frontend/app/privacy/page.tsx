import Navbar from '@/components/Navbar';

export default function PrivacyPage() {
    return (
        <>
            <Navbar />
            <div style={{ paddingTop: '120px', minHeight: '100vh', paddingBottom: '100px', maxWidth: '800px', margin: '0 auto' }} className="container">
                <h1 style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', marginBottom: '32px' }}>Política de Privacidad</h1>

                <div className="glass-card" style={{ padding: '48px', color: 'var(--text-secondary)', lineHeight: 1.8 }}>
                    <p style={{ marginBottom: '24px' }}>Última actualización: 8 de Marzo de 2026</p>

                    <h2 style={{ fontSize: '1.5rem', color: 'white', marginTop: '32px', marginBottom: '16px' }}>1. Información que Recopilamos</h2>
                    <p style={{ marginBottom: '24px' }}>
                        Recopilamos su dirección de correo electrónico cuando se registra en nuestra plataforma de AI Video o en nuestro programa de afiliados. Al realizar pagos, la información de pago es manejada de forma segura por nuestros procesadores de pago (como Cryptomus). **No almacenamos datos sensibles de pago** en nuestros servidores.
                    </p>
                    <p style={{ marginBottom: '24px' }}>
                        Además, guardamos las imágenes (rostros/avatars) subidas y las indicaciones (prompts) que envíe para la generación de videos mediante IA en su cuenta.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', color: 'white', marginTop: '32px', marginBottom: '16px' }}>2. Cómo Usamos su Información</h2>
                    <p style={{ marginBottom: '24px' }}>
                        La información recopilada se utilizará exclusivamente para:
                        <br />• Proporcionar los servicios de generación de video con GPUs en la nube.
                        <br />• Procesar comisiones de afiliados vía USDT/PayPal.
                        <br />• Responder a consultas en soporte al cliente.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', color: 'white', marginTop: '32px', marginBottom: '16px' }}>3. Compartición de Datos</h2>
                    <p style={{ marginBottom: '24px' }}>
                        No venderemos, comercializaremos, ni transferiremos a terceros su información de identificación personal de ninguna manera. Esto no incluye proveedores confiables que ayudan a operar nuestro sitio (ej. infraestructuras de nube o procesadores de pago como Cryptomus), siempre y cuando esas partes mantengan esta información confidencial.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', color: 'white', marginTop: '32px', marginBottom: '16px' }}>4. Seguridad</h2>
                    <p style={{ marginBottom: '24px' }}>
                        Implementamos una variedad de medidas de seguridad para mantener segura su información personal utilizando servicios de encriptación estándar de la industria, como HTTPS. Todas las interacciones de pago se realizan sobre conexiones seguras y cifradas.
                    </p>

                    <h2 style={{ fontSize: '1.5rem', color: 'white', marginTop: '32px', marginBottom: '16px' }}>5. Sus Derechos</h2>
                    <p>
                        Puede solicitar la eliminación total de su cuenta, imágenes, y videos generados en cualquier momento contactando a nuestro equipo de soporte técnico a través del formulario de la página de contacto.
                    </p>

                </div>
            </div>
        </>
    );
}
