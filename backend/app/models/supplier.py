"""
Modèle Supplier (fournisseurs).
"""
import uuid
from sqlalchemy import Column, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TenantMixin, TimestampMixin


class Supplier(Base, TenantMixin, TimestampMixin):
    """Modèle Supplier - fournisseurs de produits."""

    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    contact_name = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))
    lead_time_days = Column(Integer, default=7)  # Délai de livraison moyen en jours

    # Relations
    tenant = relationship("Tenant", back_populates="suppliers")
    products = relationship("Product", back_populates="supplier")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uq_supplier_tenant_code'),
        Index('idx_suppliers_tenant_code', 'tenant_id', 'code'),
    )

    def __repr__(self) -> str:
        return f"<Supplier(id={self.id}, name={self.name})>"
