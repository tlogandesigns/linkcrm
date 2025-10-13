"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-10-13 15:28:55

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
    # Create profiles table
    op.create_table('profiles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('handle', sa.String(length=100), nullable=False),
    sa.Column('display_name', sa.String(length=200), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('avatar_url', sa.Text(), nullable=True),
    sa.Column('email_notifications', sa.Boolean(), nullable=True),
    sa.Column('plan', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profiles_email'), 'profiles', ['email'], unique=True)
    op.create_index(op.f('ix_profiles_handle'), 'profiles', ['handle'], unique=True)

    # Create link_pages table
    op.create_table('link_pages',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('theme', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['profiles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

    # Create links table
    op.create_table('links',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('page_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('url', sa.Text(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('clicks', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['page_id'], ['link_pages.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_links_page_id'), 'links', ['page_id'], unique=False)
    op.create_index(op.f('ix_links_position'), 'links', ['position'], unique=False)

    # Create leads table
    op.create_table('leads',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['profiles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leads_created_at'), 'leads', ['created_at'], unique=False)
    op.create_index(op.f('ix_leads_owner_id'), 'leads', ['owner_id'], unique=False)

    # Create events table
    op.create_table('events',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('page_id', sa.UUID(), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.Column('meta', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['profiles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['page_id'], ['link_pages.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_created_at'), 'events', ['created_at'], unique=False)
    op.create_index(op.f('ix_events_owner_id'), 'events', ['owner_id'], unique=False)
    op.create_index(op.f('ix_events_type'), 'events', ['type'], unique=False)

    # Create subscriptions table
    op.create_table('subscriptions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('plan', sa.String(length=50), nullable=True),
    sa.Column('current_period_end', sa.DateTime(), nullable=True),
    sa.Column('raw', sa.JSON(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['profiles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('owner_id')
    )


def downgrade() -> None:
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_events_type'), table_name='events')
    op.drop_index(op.f('ix_events_owner_id'), table_name='events')
    op.drop_index(op.f('ix_events_created_at'), table_name='events')
    op.drop_table('events')
    op.drop_index(op.f('ix_leads_owner_id'), table_name='leads')
    op.drop_index(op.f('ix_leads_created_at'), table_name='leads')
    op.drop_table('leads')
    op.drop_index(op.f('ix_links_position'), table_name='links')
    op.drop_index(op.f('ix_links_page_id'), table_name='links')
    op.drop_table('links')
    op.drop_table('link_pages')
    op.drop_index(op.f('ix_profiles_handle'), table_name='profiles')
    op.drop_index(op.f('ix_profiles_email'), table_name='profiles')
    op.drop_table('profiles')
