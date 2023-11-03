"""Sequence int

Revision ID: cda0da0b31e1
Revises: 
Create Date: 2023-11-03 09:41:29.529800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'cda0da0b31e1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    connection = op.get_bind()
    result = connection.execute(text("SELECT to_regclass('public.url_table_id_seq')"))
    exists = result.scalar() is not None
    if not exists:
        op.execute(
            sa.schema.CreateSequence(sa.Sequence('url_table_id_seq'))
        )

def downgrade():
    op.execute(
        sa.schema.DropSequence(sa.Sequence('url_table_id_seq'))
    )