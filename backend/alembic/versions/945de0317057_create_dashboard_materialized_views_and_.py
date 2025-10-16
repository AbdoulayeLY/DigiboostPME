"""Create dashboard materialized views and functions

Revision ID: 945de0317057
Revises: 96706386dffc
Create Date: 2025-10-15 12:59:49.232733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '945de0317057'
down_revision: Union[str, None] = '96706386dffc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Vue materialisee: Sante Stock
    op.execute("""
        CREATE MATERIALIZED VIEW mv_dashboard_stock_health AS
        SELECT
            p.tenant_id,
            COUNT(DISTINCT p.id) as total_products,
            COUNT(DISTINCT CASE WHEN p.current_stock = 0 THEN p.id END) as rupture_count,
            COUNT(DISTINCT CASE WHEN p.current_stock > 0 AND p.current_stock <= p.min_stock THEN p.id END) as low_stock_count,
            SUM(p.current_stock * p.purchase_price) as total_stock_value
        FROM products p
        WHERE p.is_active = TRUE
        GROUP BY p.tenant_id;
    """)

    op.execute("""
        CREATE UNIQUE INDEX idx_mv_stock_health_tenant
        ON mv_dashboard_stock_health (tenant_id);
    """)

    # Vue materialisee: Performance Ventes
    op.execute("""
        CREATE MATERIALIZED VIEW mv_dashboard_sales_performance AS
        SELECT
            s.tenant_id,
            DATE_TRUNC('day', s.sale_date) as sale_day,
            COUNT(*) as transactions_count,
            SUM(s.total_amount) as daily_revenue,
            SUM(s.quantity) as total_units_sold
        FROM sales s
        WHERE s.sale_date >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY s.tenant_id, DATE_TRUNC('day', s.sale_date);
    """)

    op.execute("""
        CREATE INDEX idx_mv_sales_perf_tenant_day
        ON mv_dashboard_sales_performance (tenant_id, sale_day);
    """)

    # Fonction: Calcul Taux Service
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_calc_taux_service(
            p_tenant_id UUID,
            p_days INT DEFAULT 30
        ) RETURNS DECIMAL AS $$
        DECLARE
            total_orders INT;
            completed_orders INT;
        BEGIN
            SELECT
                COUNT(*),
                COUNT(CASE WHEN status = 'completed' THEN 1 END)
            INTO total_orders, completed_orders
            FROM sales
            WHERE tenant_id = p_tenant_id
                AND sale_date >= CURRENT_DATE - (p_days || ' days')::INTERVAL;

            IF total_orders = 0 THEN
                RETURN 100;
            END IF;

            RETURN ROUND((completed_orders::DECIMAL / total_orders) * 100, 2);
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    # Supprimer fonction
    op.execute("DROP FUNCTION IF EXISTS fn_calc_taux_service(UUID, INT);")

    # Supprimer vues materialisees
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_sales_performance;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_dashboard_stock_health;")
