"""
Module tasks - Celery tasks for Digiboost PME.
"""
from app.tasks.celery_app import celery_app
from app.tasks.alert_tasks import (
    evaluate_all_tenants_alerts,
    test_whatsapp_connection,
)
from app.tasks.report_tasks import (
    generate_monthly_reports,
    cleanup_old_reports,
)
from app.tasks.dashboard_tasks import (
    refresh_dashboard_views,
)

__all__ = [
    "celery_app",
    "evaluate_all_tenants_alerts",
    "test_whatsapp_connection",
    "generate_monthly_reports",
    "cleanup_old_reports",
    "refresh_dashboard_views",
]
