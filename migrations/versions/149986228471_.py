"""empty message

Revision ID: 149986228471
Revises: 83dc7beb75c6
Create Date: 2026-03-26 19:04:58.030027

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '149986228471'
down_revision: Union[str, Sequence[str], None] = '83dc7beb75c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
