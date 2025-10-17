"""
Tâches Celery pour la génération automatique de rapports.
"""
from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import os
import logging
from pathlib import Path

from app.db.session import SessionLocal
from app.models.tenant import Tenant
from app.models.user import User
from app.services.report_service import ReportService
from app.integrations.email import EmailService
from app.config import settings

logger = logging.getLogger(__name__)


@shared_task(name='app.tasks.report_tasks.generate_monthly_reports')
def generate_monthly_reports():
    """
    Tâche périodique: Générer rapports mensuels pour tous les tenants.

    Exécutée le 1er de chaque mois à 08:00.
    Génère le rapport PDF du mois précédent et l'envoie par email.

    Returns:
        dict: Statistiques d'exécution
    """
    logger.info("Starting monthly report generation")

    db = SessionLocal()
    tenants_processed = 0
    tenants_success = 0
    tenants_failed = 0

    try:
        # Calculer mois précédent
        today = datetime.now()
        if today.month == 1:
            month = 12
            year = today.year - 1
        else:
            month = today.month - 1
            year = today.year

        logger.info(f"Generating reports for {month:02d}/{year}")

        # Récupérer tous les tenants actifs
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
        tenants_processed = len(tenants)

        logger.info(f"Found {tenants_processed} active tenants")

        for tenant in tenants:
            try:
                logger.info(f"Processing tenant {tenant.id} - {tenant.name}")

                # Générer PDF
                report_service = ReportService(db)
                pdf = report_service.generate_monthly_summary_pdf(tenant.id, month, year)

                # Créer dossier reports si n'existe pas
                reports_dir = Path(settings.REPORTS_DIR)
                reports_dir.mkdir(parents=True, exist_ok=True)

                # Sauvegarder fichier
                filename = f"synthese_{tenant.id}_{year}_{month:02d}.pdf"
                filepath = reports_dir / filename

                with open(filepath, "wb") as f:
                    f.write(pdf.getvalue())

                logger.info(f"Report saved: {filepath} ({filepath.stat().st_size} bytes)")

                # Envoyer par email
                _send_report_email(db, tenant, str(filepath), month, year)

                tenants_success += 1
                logger.info(f"Successfully processed tenant {tenant.id}")

            except Exception as e:
                tenants_failed += 1
                logger.error(f"Failed to generate report for tenant {tenant.id}: {str(e)}", exc_info=True)
                continue

        result = {
            "tenants_processed": tenants_processed,
            "tenants_success": tenants_success,
            "tenants_failed": tenants_failed,
            "month": month,
            "year": year
        }

        logger.info(f"Monthly report generation completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Fatal error in monthly report generation: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


def _send_report_email(db: Session, tenant: Tenant, filepath: str, month: int, year: int):
    """
    Envoyer rapport par email aux administrateurs du tenant.

    Args:
        db: Session SQLAlchemy
        tenant: Instance Tenant
        filepath: Chemin vers le fichier PDF
        month: Mois du rapport
        year: Année du rapport
    """
    try:
        # Récupérer les emails des admins/managers
        admin_users = db.query(User).filter(
            User.tenant_id == tenant.id,
            User.is_active == True,
            User.role.in_(['admin', 'manager'])
        ).all()

        if not admin_users:
            logger.warning(f"No admin users found for tenant {tenant.id}")
            return

        # Lire fichier PDF
        with open(filepath, "rb") as f:
            pdf_data = f.read()

        month_names = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]

        subject = f"Synthèse Mensuelle - {month_names[month-1]} {year}"

        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4F46E5;">Bonjour,</h2>

                <p>Veuillez trouver ci-joint votre synthèse mensuelle pour <strong>{month_names[month-1]} {year}</strong>.</p>

                <div style="background-color: #F3F4F6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1F2937;">📊 Contenu du rapport:</h3>
                    <ul style="margin: 10px 0;">
                        <li>Les indicateurs clés du mois (CA, transactions, panier moyen)</li>
                        <li>L'évolution de votre chiffre d'affaires</li>
                        <li>Le classement de vos meilleurs produits</li>
                        <li>Les alertes sur la santé de votre stock</li>
                    </ul>
                </div>

                <p>Ce rapport vous permet de suivre la performance de votre activité et d'identifier les opportunités d'amélioration.</p>

                <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 30px 0;">

                <p style="color: #6B7280; font-size: 14px;">
                    Cordialement,<br/>
                    <strong>L'équipe Digiboost PME</strong><br/>
                    Intelligence Supply Chain
                </p>
            </div>
        </body>
        </html>
        """

        # Envoyer à chaque admin
        email_service = EmailService()
        for user in admin_users:
            try:
                email_service.send_email_sync(
                    to_email=user.email,
                    subject=subject,
                    body_html=body_html,
                    attachments=[(f"synthese_{month_names[month-1]}_{year}.pdf", pdf_data)]
                )
                logger.info(f"Report email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send email to {user.email}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in _send_report_email: {str(e)}", exc_info=True)
        raise


@shared_task(name='app.tasks.report_tasks.cleanup_old_reports')
def cleanup_old_reports():
    """
    Tâche périodique: Nettoyer les anciens rapports.

    Supprime les rapports plus vieux que REPORTS_RETENTION_DAYS.
    Exécutée quotidiennement à 02:00.

    Returns:
        dict: Statistiques de nettoyage
    """
    logger.info("Starting old reports cleanup")

    try:
        reports_dir = Path(settings.REPORTS_DIR)

        if not reports_dir.exists():
            logger.info("Reports directory does not exist, nothing to clean")
            return {"files_deleted": 0}

        # Calculer date limite
        cutoff_date = datetime.now() - timedelta(days=settings.REPORTS_RETENTION_DAYS)

        files_deleted = 0
        total_size_freed = 0

        # Parcourir tous les fichiers PDF
        for filepath in reports_dir.glob("*.pdf"):
            try:
                # Vérifier date de modification
                file_mtime = datetime.fromtimestamp(filepath.stat().st_mtime)

                if file_mtime < cutoff_date:
                    file_size = filepath.stat().st_size
                    filepath.unlink()
                    files_deleted += 1
                    total_size_freed += file_size
                    logger.info(f"Deleted old report: {filepath.name} (modified: {file_mtime})")

            except Exception as e:
                logger.error(f"Failed to delete {filepath}: {str(e)}")
                continue

        result = {
            "files_deleted": files_deleted,
            "total_size_freed_mb": round(total_size_freed / (1024 * 1024), 2),
            "retention_days": settings.REPORTS_RETENTION_DAYS
        }

        logger.info(f"Cleanup completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in cleanup_old_reports: {str(e)}", exc_info=True)
        raise
