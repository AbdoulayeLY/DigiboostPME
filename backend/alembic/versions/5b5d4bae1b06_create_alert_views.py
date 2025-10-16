"""Create alert views

Revision ID: 5b5d4bae1b06
Revises: 17ead6febdec
Create Date: 2025-10-15 16:11:43.568701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b5d4bae1b06'
down_revision: Union[str, None] = '17ead6febdec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create views for alert detection."""

    # Vue: Produits en rupture de stock par tenant
    op.execute("""
        CREATE VIEW v_alert_rupture_stock AS
        SELECT
            p.tenant_id,
            p.id as product_id,
            p.code,
            p.name,
            p.current_stock,
            p.min_stock,
            c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.current_stock = 0
            AND p.is_active = TRUE
    """)

    # Vue: Produits en stock faible par tenant
    op.execute("""
        CREATE VIEW v_alert_stock_faible AS
        SELECT
            p.tenant_id,
            p.id as product_id,
            p.code,
            p.name,
            p.current_stock,
            p.min_stock,
            (p.min_stock - p.current_stock) as deficit,
            c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.current_stock > 0
            AND p.current_stock <= p.min_stock
            AND p.is_active = TRUE
    """)


def downgrade() -> None:
    """Drop alert detection views."""
    op.execute("DROP VIEW IF EXISTS v_alert_stock_faible")
    op.execute("DROP VIEW IF EXISTS v_alert_rupture_stock")
