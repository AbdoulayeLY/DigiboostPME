"""
Modèle Tenant (PME cliente).
"""
import uuid
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin


class Tenant(Base, TimestampMixin):
    """Modèle Tenant - représente une PME cliente."""

    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    ninea = Column(String(50))  # Numéro d'identification entreprise Sénégal
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    settings = Column(JSON, default=dict)  # Configuration alertes, objectifs
    is_active = Column(Boolean, default=True, nullable=False)

    # Relations
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="tenant", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", back_populates="tenant", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="tenant", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="tenant", cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="tenant", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="tenant", cascade="all, delete-orphan")
    alert_history = relationship("AlertHistory", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, name={self.name})>"
