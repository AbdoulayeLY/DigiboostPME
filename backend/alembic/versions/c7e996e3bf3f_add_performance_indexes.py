"""add_performance_indexes

Revision ID: c7e996e3bf3f
Revises: bd2625f321eb
Create Date: 2025-10-17 11:39:24.527650

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7e996e3bf3f'
down_revision: Union[str, None] = 'bd2625f321eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for critical queries"""

    # Index composite sur sales pour les requêtes par tenant + date
    op.create_index(
        'idx_sales_tenant_date_product',
        'sales',
        ['tenant_id', 'sale_date', 'product_id'],
        unique=False
    )

    # Index composite sur products pour les filtres actifs avec stock
    op.create_index(
        'idx_products_tenant_active_stock',
        'products',
        ['tenant_id', 'is_active', 'current_stock'],
        unique=False,
        postgresql_where=sa.text('is_active = TRUE')
    )

    # Index sur categories pour les jointures fréquentes
    op.create_index(
        'idx_categories_tenant_name',
        'categories',
        ['tenant_id', 'name'],
        unique=False
    )

    # Index sur mv_dashboard_stock_health pour lookup rapide
    op.create_index(
        'idx_mv_dashboard_stock_health_tenant',
        'mv_dashboard_stock_health',
        ['tenant_id'],
        unique=False
    )

    # Mettre à jour les statistiques PostgreSQL
    op.execute('ANALYZE products')
    op.execute('ANALYZE sales')
    op.execute('ANALYZE categories')


def downgrade() -> None:
    """Remove performance indexes"""

    op.drop_index('idx_mv_dashboard_stock_health_tenant', table_name='mv_dashboard_stock_health')
    op.drop_index('idx_categories_tenant_name', table_name='categories')
    op.drop_index('idx_products_tenant_active_stock', table_name='products')
    op.drop_index('idx_sales_tenant_date_product', table_name='sales')
