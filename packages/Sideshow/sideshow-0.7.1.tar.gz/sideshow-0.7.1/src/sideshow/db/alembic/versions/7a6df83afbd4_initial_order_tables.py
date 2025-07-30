"""initial order tables

Revision ID: 7a6df83afbd4
Revises: 
Create Date: 2024-12-30 18:53:51.358163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = '7a6df83afbd4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = ('sideshow',)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # enums
    sa.Enum('PENDING', 'READY', 'RESOLVED', name='pendingcustomerstatus').create(op.get_bind())
    sa.Enum('PENDING', 'READY', 'RESOLVED', name='pendingproductstatus').create(op.get_bind())

    # sideshow_customer_pending
    op.create_table('sideshow_customer_pending',
                    sa.Column('uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('customer_id', sa.String(length=20), nullable=True),
                    sa.Column('full_name', sa.String(length=100), nullable=True),
                    sa.Column('first_name', sa.String(length=50), nullable=True),
                    sa.Column('last_name', sa.String(length=50), nullable=True),
                    sa.Column('phone_number', sa.String(length=20), nullable=True),
                    sa.Column('email_address', sa.String(length=255), nullable=True),
                    sa.Column('status', postgresql.ENUM('PENDING', 'READY', 'RESOLVED', name='pendingcustomerstatus', create_type=False), nullable=False),
                    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('created_by_uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name=op.f('fk_sideshow_customer_pending_created_by_uuid_user')),
                    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_sideshow_customer_pending'))
                    )

    # sideshow_customer_local
    op.create_table('sideshow_customer_local',
                    sa.Column('full_name', sa.String(length=100), nullable=True),
                    sa.Column('first_name', sa.String(length=50), nullable=True),
                    sa.Column('last_name', sa.String(length=50), nullable=True),
                    sa.Column('phone_number', sa.String(length=20), nullable=True),
                    sa.Column('email_address', sa.String(length=255), nullable=True),
                    sa.Column('uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('external_id', sa.String(length=20), nullable=True),
                    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_sideshow_customer_local'))
                    )

    # sideshow_product_pending
    op.create_table('sideshow_product_pending',
                    sa.Column('uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('product_id', sa.String(length=20), nullable=True),
                    sa.Column('scancode', sa.String(length=14), nullable=True),
                    sa.Column('department_id', sa.String(length=10), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('size', sa.String(length=30), nullable=True),
                    sa.Column('weighed', sa.Boolean(), nullable=True),
                    sa.Column('vendor_name', sa.String(length=50), nullable=True),
                    sa.Column('vendor_item_code', sa.String(length=20), nullable=True),
                    sa.Column('unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('case_size', sa.Numeric(precision=9, scale=4), nullable=True),
                    sa.Column('unit_price_reg', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('special_order', sa.Boolean(), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('status', postgresql.ENUM('PENDING', 'READY', 'RESOLVED', name='pendingproductstatus', create_type=False), nullable=False),
                    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('created_by_uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name=op.f('fk_sideshow_product_pending_created_by_uuid_user')),
                    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_sideshow_product_pending'))
                    )

    # sideshow_product_local
    op.create_table('sideshow_product_local',
                    sa.Column('scancode', sa.String(length=14), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('size', sa.String(length=30), nullable=True),
                    sa.Column('weighed', sa.Boolean(), nullable=True),
                    sa.Column('department_id', sa.String(length=10), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('special_order', sa.Boolean(), nullable=True),
                    sa.Column('vendor_name', sa.String(length=50), nullable=True),
                    sa.Column('vendor_item_code', sa.String(length=20), nullable=True),
                    sa.Column('case_size', sa.Numeric(precision=9, scale=4), nullable=True),
                    sa.Column('unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('unit_price_reg', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('external_id', sa.String(length=20), nullable=True),
                    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_sideshow_product_local'))
                    )

    # sideshow_order
    op.create_table('sideshow_order',
                    sa.Column('uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('order_id', sa.Integer(), nullable=False),
                    sa.Column('store_id', sa.String(length=10), nullable=True),
                    sa.Column('customer_id', sa.String(length=20), nullable=True),
                    sa.Column('local_customer_uuid', wuttjamaican.db.util.UUID(), nullable=True),
                    sa.Column('pending_customer_uuid', wuttjamaican.db.util.UUID(), nullable=True),
                    sa.Column('customer_name', sa.String(length=100), nullable=True),
                    sa.Column('phone_number', sa.String(length=20), nullable=True),
                    sa.Column('email_address', sa.String(length=255), nullable=True),
                    sa.Column('total_price', sa.Numeric(precision=10, scale=3), nullable=True),
                    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('created_by_uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.ForeignKeyConstraint(['local_customer_uuid'], ['sideshow_customer_local.uuid'], name=op.f('fk_order_local_customer_uuid_local_customer')),
                    sa.ForeignKeyConstraint(['pending_customer_uuid'], ['sideshow_customer_pending.uuid'], name=op.f('fk_order_pending_customer_uuid_pending_customer')),
                    sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name=op.f('fk_order_created_by_uuid_user')),
                    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_order'))
                    )

    # sideshow_order_item
    op.create_table('sideshow_order_item',
                    sa.Column('uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('order_uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('sequence', sa.Integer(), nullable=False),
                    sa.Column('product_id', sa.String(length=20), nullable=True),
                    sa.Column('local_product_uuid', wuttjamaican.db.util.UUID(), nullable=True),
                    sa.Column('pending_product_uuid', wuttjamaican.db.util.UUID(), nullable=True),
                    sa.Column('product_scancode', sa.String(length=14), nullable=True),
                    sa.Column('product_brand', sa.String(length=100), nullable=True),
                    sa.Column('product_description', sa.String(length=255), nullable=True),
                    sa.Column('product_size', sa.String(length=30), nullable=True),
                    sa.Column('product_weighed', sa.Boolean(), nullable=True),
                    sa.Column('department_id', sa.String(length=10), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('special_order', sa.Boolean(), nullable=True),
                    sa.Column('case_size', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('order_qty', sa.Numeric(precision=10, scale=4), nullable=False),
                    sa.Column('order_uom', sa.String(length=10), nullable=False),
                    sa.Column('unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('unit_price_reg', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('unit_price_sale', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('sale_ends', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('unit_price_quoted', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('case_price_quoted', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('discount_percent', sa.Numeric(precision=5, scale=3), nullable=True),
                    sa.Column('total_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('status_code', sa.Integer(), nullable=False),
                    sa.Column('paid_amount', sa.Numeric(precision=8, scale=3), nullable=False),
                    sa.Column('payment_transaction_number', sa.String(length=20), nullable=True),
                    sa.ForeignKeyConstraint(['order_uuid'], ['sideshow_order.uuid'], name=op.f('fk_sideshow_order_item_order_uuid_order')),
                    sa.ForeignKeyConstraint(['local_product_uuid'], ['sideshow_product_local.uuid'], name=op.f('fk_sideshow_order_item_local_product_uuid_local_product')),
                    sa.ForeignKeyConstraint(['pending_product_uuid'], ['sideshow_product_pending.uuid'], name=op.f('fk_sideshow_order_item_pending_product_uuid_pending_product')),
                    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_order_item'))
                    )

    # sideshow_order_item_event
    op.create_table('sideshow_order_item_event',
                    sa.Column('uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('item_uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('type_code', sa.Integer(), nullable=False),
                    sa.Column('occurred', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('actor_uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('note', sa.Text(), nullable=True),
                    sa.ForeignKeyConstraint(['actor_uuid'], ['user.uuid'], name=op.f('fk_sideshow_order_item_event_actor_uuid_user')),
                    sa.ForeignKeyConstraint(['item_uuid'], ['sideshow_order_item.uuid'], name=op.f('fk_sideshow_order_item_event_item_uuid_sideshow_order_item')),
                    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_sideshow_order_item_event'))
                    )

    # sideshow_batch_neworder
    op.create_table('sideshow_batch_neworder',
                    sa.Column('uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('row_count', sa.Integer(), nullable=True),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.Column('status_text', sa.String(length=255), nullable=True),
                    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('created_by_uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('executed', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('executed_by_uuid', wuttjamaican.db.util.UUID(), nullable=True),
                    sa.Column('store_id', sa.String(length=10), nullable=True),
                    sa.Column('customer_id', sa.String(length=20), nullable=True),
                    sa.Column('local_customer_uuid', wuttjamaican.db.util.UUID(), nullable=True),
                    sa.Column('pending_customer_uuid', wuttjamaican.db.util.UUID(), nullable=True),
                    sa.Column('customer_name', sa.String(length=100), nullable=True),
                    sa.Column('phone_number', sa.String(length=20), nullable=True),
                    sa.Column('email_address', sa.String(length=255), nullable=True),
                    sa.Column('total_price', sa.Numeric(precision=10, scale=3), nullable=True),
                    sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name=op.f('fk_sideshow_batch_neworder_created_by_uuid_user')),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], ['user.uuid'], name=op.f('fk_sideshow_batch_neworder_executed_by_uuid_user')),
                    sa.ForeignKeyConstraint(['local_customer_uuid'], ['sideshow_customer_local.uuid'], name=op.f('fk_sideshow_batch_neworder_local_customer_uuid_local_customer')),
                    sa.ForeignKeyConstraint(['pending_customer_uuid'], ['sideshow_customer_pending.uuid'], name=op.f('fk_sideshow_batch_neworder_pending_customer_uuid_pending_customer')),
                    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_sideshow_batch_neworder'))
                    )

    # sideshow_batch_neworder_row
    op.create_table('sideshow_batch_neworder_row',
                    sa.Column('uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('batch_uuid', wuttjamaican.db.util.UUID(), nullable=False),
                    sa.Column('sequence', sa.Integer(), nullable=False),
                    sa.Column('status_text', sa.String(length=255), nullable=True),
                    sa.Column('modified', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('product_id', sa.String(length=20), nullable=True),
                    sa.Column('local_product_uuid', wuttjamaican.db.util.UUID(), nullable=True),
                    sa.Column('pending_product_uuid', wuttjamaican.db.util.UUID(), nullable=True),
                    sa.Column('product_scancode', sa.String(length=14), nullable=True),
                    sa.Column('product_brand', sa.String(length=100), nullable=True),
                    sa.Column('product_description', sa.String(length=255), nullable=True),
                    sa.Column('product_size', sa.String(length=30), nullable=True),
                    sa.Column('product_weighed', sa.Boolean(), nullable=True),
                    sa.Column('department_id', sa.String(length=10), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('special_order', sa.Boolean(), nullable=True),
                    sa.Column('case_size', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('order_qty', sa.Numeric(precision=10, scale=4), nullable=False),
                    sa.Column('order_uom', sa.String(length=10), nullable=False),
                    sa.Column('unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('unit_price_reg', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('unit_price_sale', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('sale_ends', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('unit_price_quoted', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('case_price_quoted', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('discount_percent', sa.Numeric(precision=5, scale=3), nullable=True),
                    sa.Column('total_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], ['sideshow_batch_neworder.uuid'], name=op.f('fk_sideshow_batch_neworder_row_batch_uuid_batch_neworder')),
                    sa.ForeignKeyConstraint(['local_product_uuid'], ['sideshow_product_local.uuid'], name=op.f('fk_sideshow_batch_neworder_row_local_product_uuid_local_product')),
                    sa.ForeignKeyConstraint(['pending_product_uuid'], ['sideshow_product_pending.uuid'], name=op.f('fk_sideshow_batch_neworder_row_pending_product_uuid_pending_product')),
                    sa.PrimaryKeyConstraint('uuid', name=op.f('pk_sideshow_batch_neworder_row'))
                    )


def downgrade() -> None:

    # sideshow_batch_neworder*
    op.drop_table('sideshow_batch_neworder_row')
    op.drop_table('sideshow_batch_neworder')

    # sideshow_order_item_event
    op.drop_table('sideshow_order_item_event')

    # sideshow_order_item
    op.drop_table('sideshow_order_item')

    # sideshow_order
    op.drop_table('sideshow_order')

    # sideshow_product_local
    op.drop_table('sideshow_product_local')

    # sideshow_product_pending
    op.drop_table('sideshow_product_pending')

    # sideshow_customer_local
    op.drop_table('sideshow_customer_local')

    # sideshow_customer_pending
    op.drop_table('sideshow_customer_pending')

    # enums
    sa.Enum('PENDING', 'READY', 'RESOLVED', name='pendingproductstatus').drop(op.get_bind())
    sa.Enum('PENDING', 'READY', 'RESOLVED', name='pendingcustomerstatus').drop(op.get_bind())
