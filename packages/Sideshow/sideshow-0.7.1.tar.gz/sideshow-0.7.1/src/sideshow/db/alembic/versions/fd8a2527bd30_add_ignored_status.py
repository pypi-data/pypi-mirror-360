"""add ignored status

Revision ID: fd8a2527bd30
Revises: 13af2ffbc0e0
Create Date: 2025-02-20 12:08:27.374172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util
from alembic_postgresql_enum import TableReference

# revision identifiers, used by Alembic.
revision: str = 'fd8a2527bd30'
down_revision: Union[str, None] = '13af2ffbc0e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # pendingcustomerstatus
    op.sync_enum_values(
        enum_schema='public',
        enum_name='pendingcustomerstatus',
        new_values=['PENDING', 'READY', 'RESOLVED', 'IGNORED'],
        affected_columns=[TableReference(table_schema='public', table_name='sideshow_customer_pending', column_name='status')],
        enum_values_to_rename=[],
    )

    # pendingproductstatus
    op.sync_enum_values(
        enum_schema='public',
        enum_name='pendingproductstatus',
        new_values=['PENDING', 'READY', 'RESOLVED', 'IGNORED'],
        affected_columns=[TableReference(table_schema='public', table_name='sideshow_product_pending', column_name='status')],
        enum_values_to_rename=[],
    )


def downgrade() -> None:

    # pendingproductstatus
    op.sync_enum_values(
        enum_schema='public',
        enum_name='pendingproductstatus',
        new_values=['PENDING', 'READY', 'RESOLVED'],
        affected_columns=[TableReference(table_schema='public', table_name='sideshow_product_pending', column_name='status')],
        enum_values_to_rename=[],
    )

    # pendingcustomerstatus
    op.sync_enum_values(
        enum_schema='public',
        enum_name='pendingcustomerstatus',
        new_values=['PENDING', 'READY', 'RESOLVED'],
        affected_columns=[TableReference(table_schema='public', table_name='sideshow_customer_pending', column_name='status')],
        enum_values_to_rename=[],
    )
