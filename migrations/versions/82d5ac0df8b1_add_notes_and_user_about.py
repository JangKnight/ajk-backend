"""add notes and user about

Revision ID: 82d5ac0df8b1
Revises: 1646dd5fed00
Create Date: 2026-03-27 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82d5ac0df8b1'
down_revision: Union[str, Sequence[str], None] = '1646dd5fed00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "about" not in user_columns:
        op.add_column("users", sa.Column("about", sa.Text(), nullable=True))

    table_names = set(inspector.get_table_names())
    if "notes" not in table_names:
        op.create_table(
            "notes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("content", sa.Text(), nullable=True),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    note_indexes = {index["name"] for index in inspector.get_indexes("notes")}
    if "ix_notes_id" not in note_indexes:
        op.create_index(op.f("ix_notes_id"), "notes", ["id"], unique=False)
    if "ix_notes_owner_id" not in note_indexes:
        op.create_index("ix_notes_owner_id", "notes", ["owner_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_notes_owner_id', table_name='notes')
    op.drop_index(op.f('ix_notes_id'), table_name='notes')
    op.drop_table('notes')
    op.drop_column('users', 'about')
