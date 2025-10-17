"""
Service d'envoi d'emails avec support pièces jointes.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Tuple, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service pour l'envoi d'emails via SMTP."""

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL

    def send_email_sync(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        attachments: Optional[List[Tuple[str, bytes]]] = None
    ) -> bool:
        """
        Envoyer un email (version synchrone pour Celery).

        Args:
            to_email: Email destinataire
            subject: Sujet de l'email
            body_html: Corps HTML de l'email
            attachments: Liste de tuples (nom_fichier, données_binaires)

        Returns:
            bool: True si envoi réussi, False sinon
        """
        try:
            # Vérifier configuration
            if not self.smtp_server or not self.smtp_user:
                logger.warning("SMTP not configured, skipping email send")
                logger.info(f"Would have sent email to {to_email}: {subject}")
                return False

            # Créer message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Ajouter corps HTML
            msg.attach(MIMEText(body_html, 'html', 'utf-8'))

            # Ajouter pièces jointes
            if attachments:
                for filename, data in attachments:
                    attachment = MIMEApplication(data, Name=filename)
                    attachment['Content-Disposition'] = f'attachment; filename="{filename}"'
                    msg.attach(attachment)

            # Envoyer email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        attachments: Optional[List[Tuple[str, bytes]]] = None
    ) -> bool:
        """
        Envoyer un email (version asynchrone).

        Wrapper autour de send_email_sync pour compatibilité async.

        Args:
            to_email: Email destinataire
            subject: Sujet de l'email
            body_html: Corps HTML de l'email
            attachments: Liste de tuples (nom_fichier, données_binaires)

        Returns:
            bool: True si envoi réussi, False sinon
        """
        return self.send_email_sync(to_email, subject, body_html, attachments)
