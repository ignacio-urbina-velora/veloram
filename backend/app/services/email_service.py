"""Email service using Resend API."""

import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.base_url = "https://api.resend.com/emails"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def send_email(self, to: str, subject: str, html_content: str):
        """Sends an email using Resend."""
        if not self.api_key:
            logger.warning("RESEND_API_KEY not configured. Email NOT sent.")
            return False

        payload = {
            "from": settings.EMAIL_FROM,
            "to": [to],
            "subject": subject,
            "html": html_content
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                logger.info(f"Email sent successfully: {data.get('id')}")
                return True
        except Exception as e:
            logger.error(f"Error sending email through Resend: {str(e)}")
            return False

    async def send_welcome_email(self, to_email: str, username: str):
        """Sends a welcome email to a new user."""
        subject = "¡Bienvenido a Velora Studio! 🚀"
        html = f"""
        <div style="font-family: sans-serif; background: #0c0c0c; color: white; padding: 40px; border-radius: 10px;">
            <h1 style="color: #8b5cf6;">Hola {username},</h1>
            <p style="font-size: 16px; line-height: 1.6;">
                ¡Gracias por unirse a <b>Velora Studio</b>! Estamos emocionados de tenerte a bordo.
                Ahora tienes acceso a nuestro workflow único para crear influencers digitales y generar contenido de alta calidad.
            </p>
            <p style="font-size: 16px;">Hemos añadido <b>$5.00 de créditos gratis</b> a tu cuenta para que empieces hoy mismo.</p>
            <div style="margin-top: 30px; text-align: center;">
                <a href="https://velora-studio.site/studio" style="background: #8b5cf6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Empezar a Crear
                </a>
            </div>
            <p style="margin-top: 40px; font-size: 12px; color: #666;">
                © 2026 Velora Studio
            </p>
        </div>
        """
        return await self.send_email(to_email, subject, html)

    async def send_generation_complete(self, to_email: str, project_title: str, project_id: int):
        """Notifies user when a video is ready."""
        subject = "¡Tu vídeo está listo! 🎬"
        html = f"""
        <div style="font-family: sans-serif; background: #0c0c0c; color: white; padding: 40px; border-radius: 10px;">
            <h1 style="color: #8b5cf6;">¡Grandes noticias!</h1>
            <p style="font-size: 16px; line-height: 1.6;">
                La producción de tu vídeo <b>"{project_title}"</b> ha finalizado con éxito.
            </p>
            <p style="font-size: 16px;">Ya puedes verlo y descargarlo desde tu colección.</p>
            <div style="margin-top: 30px; text-align: center;">
                <a href="https://velora-studio.site/dashboard/collection" style="background: #8b5cf6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Ver en mi Colección
                </a>
            </div>
            <p style="margin-top: 40px; font-size: 12px; color: #666;">
                © 2026 Velora Studio
            </p>
        </div>
        """
        return await self.send_email(to_email, subject, html)

    async def send_password_reset_email(self, to_email: str, reset_link: str):
        """Sends a password reset link to the user."""
        subject = "Recupera tu acceso a Velora Studio 🔑"
        html = f"""
        <div style="font-family: sans-serif; background: #0c0c0c; color: white; padding: 40px; border-radius: 10px;">
            <h1 style="color: #8b5cf6;">¿Olvidaste tu contraseña?</h1>
            <p style="font-size: 16px; line-height: 1.6;">
                No te preocupes, sucede a los mejores. Haz clic en el botón de abajo para elegir una nueva contraseña y volver al estudio.
            </p>
            <div style="margin-top: 30px; text-align: center;">
                <a href="{reset_link}" style="background: #8b5cf6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Resetear Contraseña
                </a>
            </div>
            <p style="margin-top: 30px; font-size: 14px; color: #888;">
                Si no solicitaste este cambio, puedes ignorar este correo con seguridad.
            </p>
            <p style="margin-top: 40px; font-size: 12px; color: #666;">
                © 2026 Velora Studio
            </p>
        </div>
        """
        return await self.send_email(to_email, subject, html)

email_service = EmailService()
