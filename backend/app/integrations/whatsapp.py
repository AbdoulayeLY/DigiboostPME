"""
Service WhatsApp avec Twilio SDK.
"""
import logging
from typing import Dict, List

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service d'envoi de messages WhatsApp via Twilio."""

    def __init__(self):
        """Initialiser le client Twilio."""
        self.enabled = settings.WHATSAPP_ENABLED
        self.from_number = settings.TWILIO_WHATSAPP_FROM

        if self.enabled and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                logger.info("WhatsApp service initialized with Twilio")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
                self.enabled = False
                self.client = None
        else:
            logger.warning("WhatsApp service disabled (missing credentials)")
            self.client = None

    def send_alert(self, recipient: str, message: str) -> bool:
        """
        Envoyer une alerte WhatsApp à un destinataire.

        Args:
            recipient: Numéro de téléphone au format international (+221771234567)
            message: Contenu du message (max 1600 caractères)

        Returns:
            bool: True si envoi réussi, False sinon
        """
        if not self.enabled:
            logger.info(f"WhatsApp disabled, skipping send to {recipient}")
            logger.debug(f"Message would be: {message}")
            return False

        if not self.client:
            logger.error("Twilio client not initialized")
            return False

        # Nettoyer le numéro (enlever espaces, tirets)
        recipient_clean = recipient.replace(" ", "").replace("-", "")

        # Valider le format
        if not recipient_clean.startswith("+"):
            logger.error(f"Invalid WhatsApp number format: {recipient}")
            return False

        # Préparer le numéro au format Twilio WhatsApp
        to_number = f"whatsapp:{recipient_clean}"

        try:
            # Limiter la taille du message
            if len(message) > 1600:
                logger.warning(f"Message too long ({len(message)} chars), truncating to 1600")
                message = message[:1597] + "..."

            # Envoyer le message
            tw_message = self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=to_number
            )

            logger.info(
                f"WhatsApp sent successfully to {recipient_clean} "
                f"(SID: {tw_message.sid}, Status: {tw_message.status})"
            )
            return True

        except TwilioRestException as e:
            logger.error(
                f"Twilio API error {e.code}: {e.msg} "
                f"(to: {recipient_clean})"
            )
            return False

        except Exception as e:
            logger.error(
                f"WhatsApp send failed to {recipient_clean}: {str(e)}",
                exc_info=True
            )
            return False

    def send_bulk_alerts(
        self,
        recipients: List[str],
        message: str
    ) -> Dict[str, List[str]]:
        """
        Envoi groupé de messages WhatsApp.

        Args:
            recipients: Liste de numéros de téléphone
            message: Contenu du message

        Returns:
            Dict avec "success" et "failed" contenant les listes de numéros
        """
        results = {
            "success": [],
            "failed": []
        }

        if not recipients:
            logger.warning("No recipients provided for bulk send")
            return results

        logger.info(f"Sending WhatsApp to {len(recipients)} recipients")

        for recipient in recipients:
            success = self.send_alert(recipient, message)

            if success:
                results["success"].append(recipient)
            else:
                results["failed"].append(recipient)

        logger.info(
            f"Bulk send completed: {len(results['success'])} success, "
            f"{len(results['failed'])} failed"
        )

        return results

    def get_status(self) -> Dict[str, any]:
        """
        Obtenir le statut du service WhatsApp.

        Returns:
            Dict avec informations sur le service
        """
        return {
            "enabled": self.enabled,
            "provider": "Twilio",
            "from_number": self.from_number if self.enabled else None,
            "client_initialized": self.client is not None
        }


# Instance singleton du service WhatsApp
whatsapp_service = WhatsAppService()
