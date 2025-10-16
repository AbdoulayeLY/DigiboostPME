"""
Modèle StockMovement (mouvements de stock).
"""
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TenantMixin, TimestampMixin


class StockMovement(Base, TenantMixin, TimestampMixin):
    """Modèle StockMovement - mouvements de stock (entrées/sorties)."""

    __tablename__ = "stock_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)

    movement_date = Column(DateTime(timezone=True), nullable=False)
    movement_type = Column(String(50), nullable=False)  # ENTRY, EXIT, ADJUSTMENT
    quantity = Column(Numeric(15, 3), nullable=False)

    # Contexte
    reference = Column(String(100))  # Référence bon de livraison, etc.
    reason = Column(Text)

    # Relations
    tenant = relationship("Tenant", back_populates="stock_movements")
    product = relationship("Product", back_populates="stock_movements")

    __table_args__ = (
        Index('idx_stock_movements_tenant_date', 'tenant_id', 'movement_date'),
        Index('idx_stock_movements_product_date', 'product_id', 'movement_date'),
    )

    def __repr__(self) -> str:
        return f"<StockMovement(id={self.id}, type={self.movement_type}, qty={self.quantity})>"
