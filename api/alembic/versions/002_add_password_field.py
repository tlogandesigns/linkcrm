"""add password field

Revision ID: 002
Revises: 001
Create Date: 2025-10-13 16:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add password_hash column (nullable temporarily for existing users)
    op.add_column('profiles', sa.Column('password_hash', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('profiles', 'password_hash')
