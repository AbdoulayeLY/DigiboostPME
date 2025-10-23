"""
Centralized import of all models for Alembic autogenerate.
"""
from app.db.base_class import Base
from app.models.alert import Alert
from app.models.alert_history import AlertHistory
from app.models.audit_log import AdminAuditLog
from app.models.base import TenantMixin, TimestampMixin
from app.models.category import Category
from app.models.import_job import ImportJob
from app.models.onboarding import OnboardingSession
from app.models.product import Product
from app.models.sale import Sale
from app.models.site import Site
from app.models.stock_movement import StockMovement
from app.models.supplier import Supplier
from app.models.tenant import Tenant
from app.models.user import User

__all__ = [
    "Base",
    "TenantMixin",
    "TimestampMixin",
    "Tenant",
    "User",
    "Site",
    "Category",
    "Supplier",
    "Product",
    "Sale",
    "StockMovement",
    "Alert",
    "AlertHistory",
    "OnboardingSession",
    "AdminAuditLog",
    "ImportJob",
]
