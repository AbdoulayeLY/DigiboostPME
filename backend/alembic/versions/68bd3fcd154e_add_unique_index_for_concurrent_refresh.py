"""add_unique_index_for_concurrent_refresh

Revision ID: 68bd3fcd154e
Revises: 5b5d4bae1b06
Create Date: 2025-10-15 18:07:49.912096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68bd3fcd154e'
down_revision: Union[str, None] = '5b5d4bae1b06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the non-unique index on mv_dashboard_sales_performance
    op.execute("""
        DROP INDEX IF EXISTS idx_mv_sales_perf_tenant_day;
    """)

    # Create a unique index instead (required for CONCURRENT refresh)
    op.execute("""
        CREATE UNIQUE INDEX idx_mv_sales_perf_tenant_day
        ON mv_dashboard_sales_performance (tenant_id, sale_day);
    """)


def downgrade() -> None:
    # Drop unique index
    op.execute("""
        DROP INDEX IF EXISTS idx_mv_sales_perf_tenant_day;
    """)

    # Recreate non-unique index
    op.execute("""
        CREATE INDEX idx_mv_sales_perf_tenant_day
        ON mv_dashboard_sales_performance (tenant_id, sale_day);
    """)
