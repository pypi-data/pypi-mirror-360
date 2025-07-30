"""add stores

Revision ID: a4273360d379
Revises: 7a6df83afbd4
Create Date: 2025-01-27 17:48:20.638664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = 'a4273360d379'
down_revision: Union[str, None] = '7a6df83afbd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # sideshow_store
    op.create_table('sideshow_store',
                    sa.Column('uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('store_id', sa.String(length=10), nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=False),
                    sa.Column('archived', sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_sideshow_store')),
                    sa.UniqueConstraint('store_id', name=op.f('uq_sideshow_store_store_id')),
                    sa.UniqueConstraint('name', name=op.f('uq_sideshow_store_name'))
                    )


def downgrade() -> None:

    # sideshow_store
    op.drop_table('sideshow_store')
