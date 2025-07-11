"""create user table

Revision ID: 060b0151a2de
Revises: fbf5adbc0fbf
Create Date: 2025-07-11 22:37:55.522903

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '060b0151a2de'
down_revision: Union[str, Sequence[str], None] = 'fbf5adbc0fbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='user')
    )


def downgrade():
    op.drop_table('user')