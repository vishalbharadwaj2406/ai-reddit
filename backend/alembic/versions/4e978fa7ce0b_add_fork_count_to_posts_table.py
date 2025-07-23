"""Add fork_count to posts table

Revision ID: 4e978fa7ce0b
Revises: fa51e3bf0f60
Create Date: 2025-07-23 14:28:04.199326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e978fa7ce0b'
down_revision: Union[str, None] = 'fa51e3bf0f60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add fork_count column to posts table
    op.add_column('posts', sa.Column('fork_count', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove fork_count column from posts table
    op.drop_column('posts', 'fork_count')
