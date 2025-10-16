"""
Modèle Product (produits en stock).
"""
import uuid
from sqlalchemy import Boolean, Column, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TenantMixin, TimestampMixin


class Product(Base, TenantMixin, TimestampMixin):
    """Modèle Product - produits en stock."""

    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    code = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)

    # Foreign keys
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='SET NULL'))
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('suppliers.id', ondelete='SET NULL'))

    # Tarification
    purchase_price = Column(Numeric(15, 2), nullable=False)
    sale_price = Column(Numeric(15, 2), nullable=False)
    unit = Column(String(50), default='unité')  # sac, kg, litre, etc.

    # Stock
    current_stock = Column(Numeric(15, 3), default=0)
    min_stock = Column(Numeric(15, 3))
    max_stock = Column(Numeric(15, 3))

    # Métadonnées
    description = Column(Text)
    barcode = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)

    # Relations
    tenant = relationship("Tenant", back_populates="products")
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    sales = relationship("Sale", back_populates="product")
    stock_movements = relationship("StockMovement", back_populates="product")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uq_product_tenant_code'),
        Index('idx_products_tenant_code', 'tenant_id', 'code'),
        Index('idx_products_tenant_active', 'tenant_id', 'is_active'),
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, code={self.code}, name={self.name})>"
