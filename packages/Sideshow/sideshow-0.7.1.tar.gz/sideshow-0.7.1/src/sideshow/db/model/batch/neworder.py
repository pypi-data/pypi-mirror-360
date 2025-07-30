# -*- coding: utf-8; -*-
################################################################################
#
#  Sideshow -- Case/Special Order Tracker
#  Copyright © 2024 Lance Edgar
#
#  This file is part of Sideshow.
#
#  Sideshow is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Sideshow is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Sideshow.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Data models for New Order Batch

* :class:`NewOrderBatch`
* :class:`NewOrderBatchRow`
"""

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from wuttjamaican.db import model


class NewOrderBatch(model.BatchMixin, model.Base):
    """
    :term:`Batch <batch>` used for entering new :term:`orders <order>`
    into the system.  Each batch ultimately becomes an
    :class:`~sideshow.db.model.orders.Order`.

    See also :class:`~sideshow.batch.neworder.NewOrderBatchHandler`
    which is the default :term:`batch handler` for this :term:`batch
    type`.

    Generic batch attributes (undocumented below) are inherited from
    :class:`~wuttjamaican:wuttjamaican.db.model.batch.BatchMixin`.
    """
    __tablename__ = 'sideshow_batch_neworder'
    __batchrow_class__ = 'NewOrderBatchRow'

    batch_type = 'neworder'
    """
    Official :term:`batch type` key.
    """

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['local_customer_uuid'], ['sideshow_customer_local.uuid']),
            sa.ForeignKeyConstraint(['pending_customer_uuid'], ['sideshow_customer_pending.uuid']),
        )

    STATUS_OK                           = 1

    STATUS = {
        STATUS_OK                       : "ok",
    }

    store_id = sa.Column(sa.String(length=10), nullable=True, doc="""
    ID of the store to which the order pertains, if applicable.
    """)

    customer_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Proper account ID for the :term:`external customer` to which the
    order pertains, if applicable.

    See also :attr:`local_customer` and :attr:`pending_customer`.
    """)

    local_customer_uuid = sa.Column(model.UUID(), nullable=True)

    @declared_attr
    def local_customer(cls):
        return orm.relationship(
            'LocalCustomer',
            back_populates='new_order_batches',
            doc="""
            Reference to the
            :class:`~sideshow.db.model.customers.LocalCustomer` record
            for the order, if applicable.

            See also :attr:`customer_id` and :attr:`pending_customer`.
            """)

    pending_customer_uuid = sa.Column(model.UUID(), nullable=True)

    @declared_attr
    def pending_customer(cls):
        return orm.relationship(
            'PendingCustomer',
            back_populates='new_order_batches',
            doc="""
            Reference to the
            :class:`~sideshow.db.model.customers.PendingCustomer`
            record for the order, if applicable.

            See also :attr:`customer_id` and :attr:`local_customer`.
            """)

    customer_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Name for the customer account.
    """)

    phone_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    Phone number for the customer.
    """)

    email_address = sa.Column(sa.String(length=255), nullable=True, doc="""
    Email address for the customer.
    """)

    total_price = sa.Column(sa.Numeric(precision=10, scale=3), nullable=True, doc="""
    Full price (not including tax etc.) for all items on the order.
    """)


class NewOrderBatchRow(model.BatchRowMixin, model.Base):
    """
    Row of data within a :class:`NewOrderBatch`.  Each row ultimately
    becomes an :class:`~sideshow.db.model.orders.OrderItem`.

    Generic row attributes (undocumented below) are inherited from
    :class:`~wuttjamaican:wuttjamaican.db.model.batch.BatchRowMixin`.
    """
    __tablename__ = 'sideshow_batch_neworder_row'
    __batch_class__ = NewOrderBatch

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['local_product_uuid'], ['sideshow_product_local.uuid']),
            sa.ForeignKeyConstraint(['pending_product_uuid'], ['sideshow_product_pending.uuid']),
        )

    STATUS_OK                           = 1
    """
    This is the default value for :attr:`status_code`.  All rows are
    considered "OK" if they have either a :attr:`product_id` or
    :attr:`pending_product`.
    """

    STATUS_MISSING_PRODUCT              = 2
    """
    Status code indicating the row has no :attr:`product_id` or
    :attr:`pending_product` set.
    """

    STATUS_MISSING_ORDER_QTY            = 3
    """
    Status code indicating the row has no :attr:`order_qty` and/or
    :attr:`order_uom` set.
    """

    STATUS = {
        STATUS_OK                       : "ok",
        STATUS_MISSING_PRODUCT          : "missing product",
        STATUS_MISSING_ORDER_QTY        : "missing order qty/uom",
    }
    """
    Dict of possible status code -> label options.
    """

    product_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Proper ID for the :term:`external product` which the order item
    represents, if applicable.

    See also :attr:`local_product` and :attr:`pending_product`.
    """)

    local_product_uuid = sa.Column(model.UUID(), nullable=True)

    @declared_attr
    def local_product(cls):
        return orm.relationship(
            'LocalProduct',
            back_populates='new_order_batch_rows',
            doc="""
            Reference to the
            :class:`~sideshow.db.model.products.LocalProduct` record
            for the order item, if applicable.

            See also :attr:`product_id` and :attr:`pending_product`.
            """)

    pending_product_uuid = sa.Column(model.UUID(), nullable=True)

    @declared_attr
    def pending_product(cls):
        return orm.relationship(
            'PendingProduct',
            back_populates='new_order_batch_rows',
            doc="""
            Reference to the
            :class:`~sideshow.db.model.products.PendingProduct` record
            for the order item, if applicable.

            See also :attr:`product_id` and :attr:`local_product`.
            """)

    product_scancode = sa.Column(sa.String(length=14), nullable=True, doc="""
    Scancode for the product, as string.

    .. note::

       This column allows 14 chars, so can store a full GPC with check
       digit.  However as of writing the actual format used here does
       not matter to Sideshow logic; "anything" should work.

       That may change eventually, depending on POS integration
       scenarios that come up.  Maybe a config option to declare
       whether check digit should be included or not, etc.
    """)

    product_brand = sa.Column(sa.String(length=100), nullable=True, doc="""
    Brand name for the product - up to 100 chars.
    """)

    product_description = sa.Column(sa.String(length=255), nullable=True, doc="""
    Description for the product - up to 255 chars.
    """)

    product_size = sa.Column(sa.String(length=30), nullable=True, doc="""
    Size of the product, as string - up to 30 chars.
    """)

    product_weighed = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating the product is sold by weight; default is null.
    """)

    department_id = sa.Column(sa.String(length=10), nullable=True, doc="""
    ID of the department to which the product belongs, if known.
    """)

    department_name = sa.Column(sa.String(length=30), nullable=True, doc="""
    Name of the department to which the product belongs, if known.
    """)

    special_order = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating the item is a "special order" - e.g. something not
    normally carried by the store.  Default is null.
    """)

    vendor_name = sa.Column(sa.String(length=50), nullable=True, doc="""
    Name of vendor from which product may be purchased, if known.  See
    also :attr:`vendor_item_code`.
    """)

    vendor_item_code = sa.Column(sa.String(length=20), nullable=True, doc="""
    Item code (SKU) to use when ordering this product from the vendor
    identified by :attr:`vendor_name`, if known.
    """)

    case_size = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Case pack count for the product, if known.

    If this is not set, then customer cannot order a "case" of the item.
    """)

    order_qty = sa.Column(sa.Numeric(precision=10, scale=4), nullable=False, doc="""
    Quantity (as decimal) of product being ordered.

    This must be interpreted along with :attr:`order_uom` to determine
    the *complete* order quantity, e.g. "2 cases".
    """)

    order_uom = sa.Column(sa.String(length=10), nullable=False, doc="""
    Code indicating the unit of measure for product being ordered.

    This should be one of the codes from
    :data:`~sideshow.enum.ORDER_UOM`.

    Sideshow will treat :data:`~sideshow.enum.ORDER_UOM_CASE`
    differently but :data:`~sideshow.enum.ORDER_UOM_UNIT` and others
    are all treated the same (i.e. "unit" is assumed).
    """)

    unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Cost of goods amount for one "unit" (not "case") of the product,
    as decimal to 4 places.
    """)

    unit_price_reg = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Regular price for the item unit.  Unless a sale is in effect,
    :attr:`unit_price_quoted` will typically match this value.
    """)

    unit_price_sale = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Sale price for the item unit, if applicable.  If set, then
    :attr:`unit_price_quoted` will typically match this value.  See
    also :attr:`sale_ends`.
    """)

    sale_ends = sa.Column(sa.DateTime(timezone=True), nullable=True, doc="""
    End date/time for the sale in effect, if any.

    This is only relevant if :attr:`unit_price_sale` is set.
    """)

    unit_price_quoted = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Quoted price for the item unit.  This is the "effective" unit
    price, which is used to calculate :attr:`total_price`.

    This price does *not* reflect the :attr:`discount_percent`.  It
    normally should match either :attr:`unit_price_reg` or
    :attr:`unit_price_sale`.

    See also :attr:`case_price_quoted`, if applicable.
    """)

    case_price_quoted = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Quoted price for a "case" of the item, if applicable.

    This is mostly for display purposes; :attr:`unit_price_quoted` is
    used for calculations.
    """)

    discount_percent = sa.Column(sa.Numeric(precision=5, scale=3), nullable=True, doc="""
    Discount percent to apply when calculating :attr:`total_price`, if
    applicable.
    """)

    total_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Full price (not including tax etc.) which the customer is quoted
    for the order item.

    This is calculated using values from:

    * :attr:`unit_price_quoted`
    * :attr:`order_qty`
    * :attr:`order_uom`
    * :attr:`case_size`
    * :attr:`discount_percent`
    """)

    def __str__(self):
        return str(self.pending_product or self.product_description or "")
