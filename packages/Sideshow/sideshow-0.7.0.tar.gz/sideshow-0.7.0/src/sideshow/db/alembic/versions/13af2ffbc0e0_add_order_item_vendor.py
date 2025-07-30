"""add order_item.vendor*

Revision ID: 13af2ffbc0e0
Revises: a4273360d379
Create Date: 2025-02-19 19:36:30.308840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = '13af2ffbc0e0'
down_revision: Union[str, None] = 'a4273360d379'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # sideshow_batch_neworder_row
    op.add_column('sideshow_batch_neworder_row', sa.Column('vendor_name', sa.String(length=50), nullable=True))
    op.add_column('sideshow_batch_neworder_row', sa.Column('vendor_item_code', sa.String(length=20), nullable=True))

    # sideshow_order_item
    op.add_column('sideshow_order_item', sa.Column('vendor_name', sa.String(length=50), nullable=True))
    op.add_column('sideshow_order_item', sa.Column('vendor_item_code', sa.String(length=20), nullable=True))


def downgrade() -> None:

    # sideshow_order_item
    op.drop_column('sideshow_order_item', 'vendor_item_code')
    op.drop_column('sideshow_order_item', 'vendor_name')

    # sideshow_batch_neworder_row
    op.drop_column('sideshow_batch_neworder_row', 'vendor_item_code')
    op.drop_column('sideshow_batch_neworder_row', 'vendor_name')
