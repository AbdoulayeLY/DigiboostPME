"""
Modèle User (utilisateurs du système).
"""
import uuid
from sqlalchemy import Boolean, Column, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TenantMixin, TimestampMixin


class User(Base, TenantMixin, TimestampMixin):
    """Modèle User - utilisateurs d'un tenant (gérants, employés)."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="user", nullable=False)  # admin, user, viewer
    whatsapp_number = Column(String(20))  # Pour notifications WhatsApp
    is_active = Column(Boolean, default=True, nullable=False)

    # Relation
    tenant = relationship("Tenant", back_populates="users")

    __table_args__ = (
        Index('idx_users_tenant_email', 'tenant_id', 'email'),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
