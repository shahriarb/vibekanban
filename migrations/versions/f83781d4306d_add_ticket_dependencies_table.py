"""Add ticket dependencies table

Revision ID: f83781d4306d
Revises: 54152bc9890f
Create Date: 2025-03-23 17:00:40.839076

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f83781d4306d'
down_revision = '54152bc9890f'
branch_labels = None
depends_on = None


def upgrade():
    # Create the ticket dependencies association table
    op.create_table('ticket_dependencies',
        sa.Column('dependent_id', sa.Integer(), nullable=False),
        sa.Column('dependency_id', sa.Integer(), nullable=False),
        sa.Column('created_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['dependency_id'], ['tickets.id'], ),
        sa.ForeignKeyConstraint(['dependent_id'], ['tickets.id'], ),
        sa.PrimaryKeyConstraint('dependent_id', 'dependency_id')
    )


def downgrade():
    # Drop the ticket dependencies table
    op.drop_table('ticket_dependencies') 