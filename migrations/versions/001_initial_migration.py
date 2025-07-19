"""Initial migration - create jobs table

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create the initial jobs table.
    
    TODO: Add the following upgrade features:
    - Additional indexes for performance
    - Database constraints
    - Default values
    - Triggers for audit logging
    """
    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('correlation_id', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='jobstatus'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on correlation_id for fast lookups
    op.create_index('ix_jobs_correlation_id', 'jobs', ['correlation_id'], unique=True)
    
    # Create index on status for filtering
    op.create_index('ix_jobs_status', 'jobs', ['status'], unique=False)
    
    # Create index on created_at for sorting
    op.create_index('ix_jobs_created_at', 'jobs', ['created_at'], unique=False)
    
    # TODO: Add more indexes and constraints
    # op.create_index('ix_jobs_updated_at', 'jobs', ['updated_at'], unique=False)
    # op.create_foreign_key('fk_jobs_created_by', 'jobs', 'users', ['created_by'], ['id'])
    # op.create_check_constraint('ck_jobs_created_before_updated', 'jobs', 'created_at <= updated_at')


def downgrade() -> None:
    """
    Drop the jobs table and related objects.
    
    TODO: Add the following downgrade features:
    - Data backup before dropping
    - Cascading deletes
    - Cleanup of related objects
    """
    # Drop indexes
    op.drop_index('ix_jobs_created_at', table_name='jobs')
    op.drop_index('ix_jobs_status', table_name='jobs')
    op.drop_index('ix_jobs_correlation_id', table_name='jobs')
    
    # Drop table
    op.drop_table('jobs')
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS jobstatus")