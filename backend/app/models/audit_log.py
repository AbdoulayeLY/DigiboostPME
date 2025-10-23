"""
Modèle AdminAuditLog (logs d'audit pour actions admin critiques).
"""
from datetime import datetime
from sqlalchemy import BigInteger, Column, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base_class import Base


class AdminAuditLog(Base):
    """
    Modèle AdminAuditLog - logs d'audit pour actions administratives.

    Enregistre toutes les actions critiques effectuées par les administrateurs
    pour des raisons de sécurité, conformité et debugging.
    """

    __tablename__ = "admin_audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    admin_user_id = Column(UUID(as_uuid=True), nullable=True)  # NULL si action système
    action_type = Column(String(100), nullable=False)  # create_tenant, create_user, import_data, etc.
    entity_type = Column(String(50), nullable=True)  # tenant, user, product, sale
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    details = Column(JSONB, default=dict)  # Détails spécifiques à l'action
    ip_address = Column(String(45), nullable=True)  # Support IPv4 et IPv6
    user_agent = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<AdminAuditLog(id={self.id}, action={self.action_type}, entity={self.entity_type})>"
