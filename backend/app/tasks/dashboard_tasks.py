"""
Tâches Celery pour maintenance des dashboards.
"""
import logging
from celery import shared_task
from sqlalchemy import text
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


@shared_task(name='app.tasks.dashboard_tasks.refresh_dashboard_views')
def refresh_dashboard_views():
    """
    Rafraîchir vues matérialisées des dashboards.
    Exécutée toutes les 10 minutes par Celery Beat.

    Returns:
        Dict avec nombre de vues rafraîchies
    """
    logger.info("🔄 Refreshing materialized views for dashboards")

    db = SessionLocal()
    try:
        # Liste des vues matérialisées à rafraîchir
        views = [
            'mv_dashboard_stock_health',
            'mv_dashboard_sales_performance'
        ]

        refreshed_count = 0

        for view in views:
            try:
                # Rafraîchir la vue (CONCURRENTLY permet l'accès en lecture pendant le refresh)
                logger.info(f"Refreshing view: {view}")
                db.execute(text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}"))
                db.commit()

                refreshed_count += 1
                logger.info(f"✅ View {view} refreshed successfully")

            except Exception as e:
                logger.error(f"Failed to refresh view {view}: {str(e)}", exc_info=True)
                db.rollback()
                # Continue avec les autres vues même si une échoue
                continue

        logger.info(f"✅ Dashboard views refresh completed: {refreshed_count}/{len(views)}")

        return {
            "views_total": len(views),
            "views_refreshed": refreshed_count,
            "views_failed": len(views) - refreshed_count
        }

    except Exception as e:
        logger.error(f"Fatal error refreshing views: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


@shared_task(name='app.tasks.dashboard_tasks.cleanup_old_alert_history')
def cleanup_old_alert_history(days_to_keep: int = 90):
    """
    Nettoyer ancien historique d'alertes (optionnel).
    Garde seulement les X derniers jours pour optimiser la base.

    Args:
        days_to_keep: Nombre de jours à garder (défaut: 90)

    Returns:
        Dict avec nombre de lignes supprimées
    """
    logger.info(f"🧹 Cleaning up alert history older than {days_to_keep} days")

    db = SessionLocal()
    try:
        query = text("""
            DELETE FROM alert_history
            WHERE triggered_at < CURRENT_DATE - INTERVAL ':days days'
        """)

        result = db.execute(query, {"days": days_to_keep})
        deleted_count = result.rowcount

        db.commit()

        logger.info(f"✅ Deleted {deleted_count} old alert history entries")

        return {
            "days_kept": days_to_keep,
            "entries_deleted": deleted_count
        }

    except Exception as e:
        logger.error(f"Error cleaning up alert history: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
