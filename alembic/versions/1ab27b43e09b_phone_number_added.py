"""phone number added

Revision ID: 1ab27b43e09b
Revises: 
Create Date: 2025-03-15 16:23:32.254648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ab27b43e09b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(table_name='users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    pass
