"""
Mixins et classes de base pour les modèles.
"""
from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

from app.db.base_class import Base


class TimestampMixin:
    """Mixin pour ajouter created_at et updated_at automatiquement."""

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class TenantMixin:
    """Mixin pour ajouter tenant_id avec foreign key vers tenants."""

    @declared_attr
    def tenant_id(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey('tenants.id', ondelete='CASCADE'),
            nullable=False,
            index=True
        )


__all__ = ["Base", "TimestampMixin", "TenantMixin"]
