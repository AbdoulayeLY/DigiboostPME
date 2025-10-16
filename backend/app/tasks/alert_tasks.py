"""
Tâches Celery pour le système d'alertes.
"""
import asyncio
import logging
from celery import shared_task
from sqlalchemy import and_
from app.db.session import SessionLocal
from app.models.tenant import Tenant
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)


@shared_task(name='app.tasks.alert_tasks.evaluate_all_tenants_alerts')
def evaluate_all_tenants_alerts():
    """
    Tâche périodique: évaluer alertes de tous les tenants actifs.
    Exécutée toutes les 5 minutes par Celery Beat.

    Returns:
        Dict avec statistiques d'exécution
    """
    logger.info("🔔 Starting alert evaluation for all tenants")

    db = SessionLocal()
    try:
        # Récupérer tous les tenants actifs
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()

        logger.info(f"Found {len(tenants)} active tenant(s)")

        total_triggered = 0
        total_sent = 0

        for tenant in tenants:
            try:
                logger.info(f"Evaluating alerts for tenant: {tenant.name} ({tenant.id})")
                result = asyncio.run(_evaluate_tenant_alerts(tenant.id, db))

                total_triggered += result["triggered"]
                total_sent += result["sent"]

                logger.info(
                    f"Tenant {tenant.name}: {result['triggered']} triggered, "
                    f"{result['sent']} sent"
                )

            except Exception as e:
                logger.error(
                    f"Error evaluating alerts for tenant {tenant.id}: {str(e)}",
                    exc_info=True
                )
                continue

        logger.info(
            f"✅ Alert evaluation completed: {total_triggered} triggered, "
            f"{total_sent} sent across {len(tenants)} tenant(s)"
        )

        return {
            "tenants_processed": len(tenants),
            "alerts_triggered": total_triggered,
            "notifications_sent": total_sent
        }

    except Exception as e:
        logger.error(f"Fatal error in alert evaluation: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


async def _evaluate_tenant_alerts(tenant_id, db):
    """
    Évaluer alertes d'un tenant et envoyer notifications.

    Args:
        tenant_id: UUID du tenant
        db: Session base de données

    Returns:
        Dict avec triggered et sent count
    """
    service = AlertService(db)

    # Évaluer toutes les alertes actives
    triggered_alerts = service.evaluate_all_alerts(tenant_id)

    notifications_sent = 0

    for item in triggered_alerts:
        alert = item["alert"]
        result = item["result"]

        try:
            # Créer entrée historique
            history = service.create_history_entry(alert, result)

            # Envoyer notifications (WhatsApp, Email, etc.)
            service.send_alert_notifications(alert, result, history)

            notifications_sent += 1

            logger.info(
                f"Alert {alert.name} processed: "
                f"history={history.id}, sent_whatsapp={history.sent_whatsapp}"
            )

        except Exception as e:
            logger.error(
                f"Failed to send notification for alert {alert.id}: {str(e)}",
                exc_info=True
            )
            # Continue avec les autres alertes même si une échoue
            continue

    return {
        "triggered": len(triggered_alerts),
        "sent": notifications_sent
    }


@shared_task(name='app.tasks.alert_tasks.test_whatsapp_connection')
def test_whatsapp_connection():
    """
    Tâche test: vérifier connexion WhatsApp.
    Peut être exécutée manuellement pour debug.

    Returns:
        Dict avec success status
    """
    logger.info("Testing WhatsApp connection...")

    from app.integrations.whatsapp import whatsapp_service
    from app.integrations.whatsapp_templates import format_test_message

    # Numéro de test par défaut
    test_number = "+33645090636"
    message = format_test_message()

    try:
        result = whatsapp_service.send_alert(test_number, message)

        if result:
            logger.info(f"✅ WhatsApp test successful to {test_number}")
        else:
            logger.warning(f"⚠️  WhatsApp test failed (service may be disabled)")

        return {"success": result, "recipient": test_number}

    except Exception as e:
        logger.error(f"WhatsApp test error: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}
