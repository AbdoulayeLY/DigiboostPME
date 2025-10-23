"""add_onboarding_infrastructure

Revision ID: 0c6ed652bf16
Revises: c7e996e3bf3f
Create Date: 2025-10-23 12:06:36.274733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c6ed652bf16'
down_revision: Union[str, None] = 'c7e996e3bf3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # EXTENSION TABLE TENANTS
    # ============================================================
    # Ajouter colonnes pour onboarding (sector déjà existe via ninea dans POC)
    op.add_column('tenants', sa.Column('sector', sa.String(50), nullable=True))
    op.add_column('tenants', sa.Column('country', sa.String(2), server_default='SN'))
    op.add_column('tenants', sa.Column('created_by', sa.String(100), nullable=True))

    # ============================================================
    # EXTENSION TABLE USERS
    # ============================================================
    # Modifier email pour être nullable (car on peut avoir phone à la place)
    op.alter_column('users', 'email', nullable=True)

    # Ajouter colonnes pour login alternatif et changement MDP obligatoire
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('users', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('must_change_password', sa.Boolean(), server_default='false'))
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), server_default='false'))
    op.add_column('users', sa.Column('last_login', sa.TIMESTAMP(), nullable=True))

    # Migrer full_name vers first_name/last_name pour données existantes
    op.execute("""
        UPDATE users
        SET first_name = SPLIT_PART(full_name, ' ', 1),
            last_name = SPLIT_PART(full_name, ' ', 2)
        WHERE full_name IS NOT NULL
    """)

    # Créer contraintes unicité et checks
    op.create_unique_constraint('unique_phone', 'users', ['phone'])
    op.create_check_constraint(
        'check_identifier',
        'users',
        'email IS NOT NULL OR phone IS NOT NULL'
    )

    # Indexes pour performance
    op.create_index('idx_users_phone', 'users', ['phone'], unique=False)
    op.create_index('idx_users_must_change_pwd', 'users', ['must_change_password'],
                    postgresql_where=sa.text('must_change_password = TRUE'))

    # ============================================================
    # NOUVELLE TABLE SITES
    # ============================================================
    op.create_table(
        'sites',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('type', sa.String(50), server_default='main'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_sites_tenant', 'sites', ['tenant_id'])

    # ============================================================
    # NOUVELLE TABLE ONBOARDING_SESSIONS
    # ============================================================
    op.create_table(
        'onboarding_sessions',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),  # in_progress, completed, failed
        sa.Column('current_step', sa.Integer(), server_default='1'),
        sa.Column('data', sa.dialects.postgresql.JSONB(), server_default='{}'),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_onboarding_tenant_status', 'onboarding_sessions', ['tenant_id', 'status'])
    op.create_index('idx_onboarding_status', 'onboarding_sessions', ['status', 'created_at'])

    # ============================================================
    # NOUVELLE TABLE ADMIN_AUDIT_LOGS
    # ============================================================
    op.create_table(
        'admin_audit_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('admin_user_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action_type', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', sa.dialects.postgresql.JSONB(), server_default='{}'),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
    )
    op.create_index('idx_audit_action_date', 'admin_audit_logs', ['action_type', 'created_at'])
    op.create_index('idx_audit_entity', 'admin_audit_logs', ['entity_type', 'entity_id'])

    # ============================================================
    # NOUVELLE TABLE IMPORT_JOBS
    # ============================================================
    op.create_table(
        'import_jobs',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('celery_task_id', sa.String(255), unique=True, nullable=True),
        sa.Column('status', sa.String(50), nullable=False),  # pending, running, success, failed
        sa.Column('file_name', sa.String(255), nullable=True),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('progress_percent', sa.Integer(), server_default='0'),
        sa.Column('stats', sa.dialects.postgresql.JSONB(), server_default='{}'),
        sa.Column('error_details', sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column('started_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['onboarding_sessions.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_import_tenant_status', 'import_jobs', ['tenant_id', 'status'])
    op.create_index('idx_import_celery_task', 'import_jobs', ['celery_task_id'])

    # ============================================================
    # INDEXES PERFORMANCE ADDITIONNELS
    # ============================================================
    op.create_index('idx_tenants_active', 'tenants', ['is_active'])


def downgrade() -> None:
    # ============================================================
    # SUPPRESSION DANS L'ORDRE INVERSE
    # ============================================================

    # Drop indexes
    op.drop_index('idx_tenants_active', 'tenants')
    op.drop_index('idx_import_celery_task', 'import_jobs')
    op.drop_index('idx_import_tenant_status', 'import_jobs')
    op.drop_index('idx_audit_entity', 'admin_audit_logs')
    op.drop_index('idx_audit_action_date', 'admin_audit_logs')
    op.drop_index('idx_onboarding_status', 'onboarding_sessions')
    op.drop_index('idx_onboarding_tenant_status', 'onboarding_sessions')
    op.drop_index('idx_sites_tenant', 'sites')
    op.drop_index('idx_users_must_change_pwd', 'users')
    op.drop_index('idx_users_phone', 'users')

    # Drop tables
    op.drop_table('import_jobs')
    op.drop_table('admin_audit_logs')
    op.drop_table('onboarding_sessions')
    op.drop_table('sites')

    # Drop constraints users
    op.drop_constraint('check_identifier', 'users', type_='check')
    op.drop_constraint('unique_phone', 'users', type_='unique')

    # Drop columns users
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'must_change_password')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'phone')

    # Restore email NOT NULL
    op.alter_column('users', 'email', nullable=False)

    # Drop columns tenants
    op.drop_column('tenants', 'created_by')
    op.drop_column('tenants', 'country')
    op.drop_column('tenants', 'sector')
