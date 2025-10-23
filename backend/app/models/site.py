"""
Modèle Site (magasin/point de vente d'un tenant).
"""
import uuid
from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TenantMixin, TimestampMixin


class Site(Base, TenantMixin, TimestampMixin):
    """Modèle Site - représente un magasin/point de vente d'un tenant."""

    __tablename__ = "sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    type = Column(String(50), default="main", nullable=False)  # main, branch
    is_active = Column(Boolean, default=True, nullable=False)

    # Relations
    tenant = relationship("Tenant", back_populates="sites")

    def __repr__(self) -> str:
        return f"<Site(id={self.id}, name={self.name}, type={self.type})>"
