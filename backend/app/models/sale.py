"""
Modèle Sale (ventes).
"""
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TenantMixin, TimestampMixin


class Sale(Base, TenantMixin, TimestampMixin):
    """Modèle Sale - ventes de produits."""

    __tablename__ = "sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)

    sale_date = Column(DateTime(timezone=True), nullable=False)
    quantity = Column(Numeric(15, 3), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)

    # Optionnel
    order_number = Column(String(100))
    customer_name = Column(String(255))
    status = Column(String(50), default='DELIVERED')  # DELIVERED, PENDING, CANCELLED

    # Relations
    tenant = relationship("Tenant", back_populates="sales")
    product = relationship("Product", back_populates="sales")

    __table_args__ = (
        Index('idx_sales_tenant_date', 'tenant_id', 'sale_date'),
        Index('idx_sales_product_date', 'product_id', 'sale_date'),
    )

    def __repr__(self) -> str:
        return f"<Sale(id={self.id}, product_id={self.product_id}, total={self.total_amount})>"
