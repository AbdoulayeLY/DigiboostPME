"""Add index for active alerts

Revision ID: 17ead6febdec
Revises: 945de0317057
Create Date: 2025-10-15 16:07:05.215830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17ead6febdec'
down_revision: Union[str, None] = '945de0317057'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add index for active alerts filtering."""
    # Index pour optimiser les requêtes sur les alertes actives d'un tenant
    op.create_index(
        'idx_alerts_tenant_active',
        'alerts',
        ['tenant_id', 'is_active'],
        postgresql_where=sa.text('is_active = TRUE')
    )


def downgrade() -> None:
    """Remove index for active alerts."""
    op.drop_index('idx_alerts_tenant_active', table_name='alerts')
