"""
Module tasks - Celery tasks for Digiboost PME.
"""
from app.tasks.celery_app import celery_app
from app.tasks.alert_tasks import (
    evaluate_all_tenants_alerts,
    test_whatsapp_connection,
)

__all__ = [
    "celery_app",
    "evaluate_all_tenants_alerts",
    "test_whatsapp_connection",
]
