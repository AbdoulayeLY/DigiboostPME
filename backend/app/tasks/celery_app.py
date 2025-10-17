"""
Configuration Celery pour Digiboost PME.
"""
from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Créer instance Celery
celery_app = Celery(
    "digiboost",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configuration générale
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Africa/Dakar',  # Timezone Sénégal (UTC+0)
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max par tâche
    task_soft_time_limit=240,  # Warning à 4 minutes
    worker_prefetch_multiplier=1,  # Exécuter 1 tâche à la fois
    task_acks_late=True,  # Confirmer tâche après exécution (pas avant)
    task_reject_on_worker_lost=True,  # Rejeter si worker crash
)

# Configuration Beat (tâches périodiques)
celery_app.conf.beat_schedule = {
    # Évaluer alertes toutes les 5 minutes
    'evaluate-alerts-every-5-minutes': {
        'task': 'app.tasks.alert_tasks.evaluate_all_tenants_alerts',
        'schedule': 300.0,  # 5 minutes en secondes
        'options': {
            'queue': 'alerts',
            'expires': 60  # Expirer si pas exécutée dans 60s
        }
    },

    # Rafraîchir vues matérialisées toutes les 10 minutes
    'refresh-materialized-views-every-10-minutes': {
        'task': 'app.tasks.dashboard_tasks.refresh_dashboard_views',
        'schedule': 600.0,  # 10 minutes en secondes
        'options': {
            'queue': 'maintenance',
            'expires': 120
        }
    },

    # Générer rapports mensuels le 1er de chaque mois à 08:00
    'generate-monthly-reports': {
        'task': 'app.tasks.report_tasks.generate_monthly_reports',
        'schedule': crontab(day_of_month='1', hour='8', minute='0'),  # 1er du mois à 8h
        'options': {
            'queue': 'reports'
        }
    },

    # Nettoyer anciens rapports tous les jours à 02:00
    'cleanup-old-reports': {
        'task': 'app.tasks.report_tasks.cleanup_old_reports',
        'schedule': crontab(hour='2', minute='0'),  # Tous les jours à 2h
        'options': {
            'queue': 'maintenance'
        }
    },
}

# Routes (queues)
celery_app.conf.task_routes = {
    'app.tasks.alert_tasks.*': {'queue': 'alerts'},
    'app.tasks.dashboard_tasks.*': {'queue': 'maintenance'},
    'app.tasks.report_tasks.*': {'queue': 'reports'},
}

# Auto-découvrir tâches dans modules
celery_app.autodiscover_tasks(['app.tasks'])
