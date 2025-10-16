"""
Modèle Alert (configuration des alertes).
"""
import uuid
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TenantMixin, TimestampMixin


class Alert(Base, TenantMixin, TimestampMixin):
    """Modèle Alert - configuration des alertes automatiques."""

    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    alert_type = Column(String(50), nullable=False)  # LOW_STOCK, RUPTURE, SERVICE_RATE, etc.

    # Configuration (JSON)
    conditions = Column(JSON, nullable=False)  # Seuils, paramètres de déclenchement
    channels = Column(JSON, nullable=False)  # WhatsApp, Email, etc.
    recipients = Column(JSON, nullable=False)  # Numéros/emails des destinataires

    is_active = Column(Boolean, default=True, nullable=False)

    # Relations
    tenant = relationship("Tenant", back_populates="alerts")
    history = relationship("AlertHistory", back_populates="alert", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, name={self.name}, type={self.alert_type})>"
