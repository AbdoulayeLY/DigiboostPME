"""
Modèle OnboardingSession (tracking des sessions d'onboarding).
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TenantMixin


class OnboardingSession(Base, TenantMixin):
    """
    Modèle OnboardingSession - track l'état d'avancement d'un onboarding.

    Permet de reprendre un onboarding en cas d'interruption et d'auditer
    le processus de création des tenants.
    """

    __tablename__ = "onboarding_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    status = Column(String(50), nullable=False)  # in_progress, completed, failed
    current_step = Column(Integer, default=1, nullable=False)  # 1-4
    data = Column(JSONB, default=dict)  # Données temporaires de la session
    created_by = Column(String(255), nullable=True)  # Email/nom de l'admin qui fait l'onboarding
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    completed_at = Column(TIMESTAMP, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relations
    tenant = relationship("Tenant", back_populates="onboarding_sessions")
    import_jobs = relationship("ImportJob", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<OnboardingSession(id={self.id}, tenant_id={self.tenant_id}, status={self.status}, step={self.current_step})>"
