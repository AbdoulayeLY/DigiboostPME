"""
Classes de base pour les modèles SQLAlchemy.
"""
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative


@as_declarative()
class Base:
    """Classe de base pour tous les modèles."""

    id: Any
    __name__: str

    # Générer le nom de table automatiquement
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"


class TenantBaseModel(Base):
    """
    Classe de base pour les modèles multi-tenant.
    Tous les modèles héritant de cette classe auront:
    - id (UUID)
    - tenant_id (UUID) pour l'isolation multi-tenant
    - created_at, updated_at pour l'audit
    """

    __abstract__ = True

    id = Column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )

    tenant_id = Column(
        PostgresUUID(as_uuid=True),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
