"""
Modèle AlertHistory (historique des déclenchements d'alertes).
"""
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TenantMixin, TimestampMixin


class AlertHistory(Base, TenantMixin, TimestampMixin):
    """Modèle AlertHistory - historique des alertes déclenchées."""

    __tablename__ = "alert_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    alert_id = Column(UUID(as_uuid=True), ForeignKey('alerts.id', ondelete='CASCADE'))

    triggered_at = Column(DateTime(timezone=True), nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL

    message = Column(Text, nullable=False)
    details = Column(JSON)  # Contexte additionnel (produit, valeurs, etc.)

    # Statut d'envoi
    sent_whatsapp = Column(Boolean, default=False)
    sent_email = Column(Boolean, default=False)

    # Relations
    tenant = relationship("Tenant", back_populates="alert_history")
    alert = relationship("Alert", back_populates="history")

    __table_args__ = (
        Index('idx_alert_history_tenant_date', 'tenant_id', 'triggered_at'),
        Index('idx_alert_history_alert', 'alert_id', 'triggered_at'),
    )

    def __repr__(self) -> str:
        return f"<AlertHistory(id={self.id}, type={self.alert_type}, severity={self.severity})>"
