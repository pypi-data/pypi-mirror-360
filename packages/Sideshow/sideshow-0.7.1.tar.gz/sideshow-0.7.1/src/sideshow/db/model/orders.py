# -*- coding: utf-8; -*-
################################################################################
#
#  Sideshow -- Case/Special Order Tracker
#  Copyright © 2024-2025 Lance Edgar
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
Data models for Orders
"""

import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.orderinglist import ordering_list

from wuttjamaican.db import model


class Order(model.Base):
    """
    Represents an :term:`order` for a customer.  Each order has one or
    more :attr:`items`.

    Usually, orders are created by way of a
    :class:`~sideshow.db.model.batch.neworder.NewOrderBatch`.
    """
    __tablename__ = 'sideshow_order'

    # TODO: this feels a bit hacky yet but it does avoid problems
    # showing the Orders grid for a PendingCustomer
    __colanderalchemy_config__ = {
        'excludes': ['items'],
    }

    uuid = model.uuid_column()

    order_id = sa.Column(sa.Integer(), nullable=False, doc="""
    Unique ID for the order.

    When the order is created from New Order Batch, this order ID will
    match the batch ID.
    """)

    store_id = sa.Column(sa.String(length=10), nullable=True, doc="""
    ID of the store to which the order pertains, if applicable.
    """)

    store = orm.relationship(
        'Store',
        primaryjoin='Store.store_id == Order.store_id',
        foreign_keys='Order.store_id',
        doc="""
        Reference to the :class:`~sideshow.db.model.stores.Store`
        record, if applicable.
        """)

    customer_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Proper account ID for the :term:`external customer` to which the
    order pertains, if applicable.

    See also :attr:`local_customer` and :attr:`pending_customer`.
    """)

    local_customer_uuid = model.uuid_fk_column('sideshow_customer_local.uuid', nullable=True)
    local_customer = orm.relationship(
        'LocalCustomer',
        cascade_backrefs=False,
        back_populates='orders',
        doc="""
        Reference to the
        :class:`~sideshow.db.model.customers.LocalCustomer` record
        for the order, if applicable.

        See also :attr:`customer_id` and :attr:`pending_customer`.
        """)

    pending_customer_uuid = model.uuid_fk_column('sideshow_customer_pending.uuid', nullable=True)
    pending_customer = orm.relationship(
        'PendingCustomer',
        cascade_backrefs=False,
        back_populates='orders',
        doc="""
        Reference to the
        :class:`~sideshow.db.model.customers.PendingCustomer` record
        for the order, if applicable.

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

    created = sa.Column(sa.DateTime(timezone=True), nullable=False, default=datetime.datetime.now, doc="""
    Timestamp when the order was created.

    If the order is created via New Order Batch, this will match the
    batch execution timestamp.
    """)

    created_by_uuid = model.uuid_fk_column('user.uuid', nullable=False)
    created_by = orm.relationship(
        model.User,
        cascade_backrefs=False,
        doc="""
        Reference to the
        :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
        created the order.
        """)

    items = orm.relationship(
        'OrderItem',
        collection_class=ordering_list('sequence', count_from=1),
        cascade='all, delete-orphan',
        cascade_backrefs=False,
        back_populates='order',
        doc="""
        List of :class:`OrderItem` records belonging to the order.
        """)

    def __str__(self):
        return str(self.order_id)


class OrderItem(model.Base):
    """
    Represents an :term:`order item` within an :class:`Order`.

    Usually these are created from
    :class:`~sideshow.db.model.batch.neworder.NewOrderBatchRow`
    records.
    """
    __tablename__ = 'sideshow_order_item'

    uuid = model.uuid_column()

    order_uuid = model.uuid_fk_column('sideshow_order.uuid', nullable=False)
    order = orm.relationship(
        Order,
        cascade_backrefs=False,
        back_populates='items',
        doc="""
        Reference to the :class:`Order` to which the item belongs.
        """)

    sequence = sa.Column(sa.Integer(), nullable=False, doc="""
    1-based numeric sequence for the item, i.e. its line number within
    the order.
    """)

    product_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Proper ID for the :term:`external product` which the order item
    represents, if applicable.

    See also :attr:`local_product` and :attr:`pending_product`.
    """)

    local_product_uuid = model.uuid_fk_column('sideshow_product_local.uuid', nullable=True)
    local_product = orm.relationship(
        'LocalProduct',
        cascade_backrefs=False,
        back_populates='order_items',
        doc="""
        Reference to the
        :class:`~sideshow.db.model.products.LocalProduct` record for
        the order item, if applicable.

        See also :attr:`product_id` and :attr:`pending_product`.
        """)

    pending_product_uuid = model.uuid_fk_column('sideshow_product_pending.uuid', nullable=True)
    pending_product = orm.relationship(
        'PendingProduct',
        cascade_backrefs=False,
        back_populates='order_items',
        doc="""
        Reference to the
        :class:`~sideshow.db.model.products.PendingProduct` record for
        the order item, if applicable.

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

    status_code = sa.Column(sa.Integer(), nullable=False, doc="""
    Code indicating current status for the order item.
    """)

    paid_amount = sa.Column(sa.Numeric(precision=8, scale=3), nullable=False, default=0, doc="""
    Amount which the customer has paid toward the :attr:`total_price`
    of the item.
    """)

    payment_transaction_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    Transaction number in which payment for the order was taken, if
    applicable/known.
    """)

    events = orm.relationship(
        'OrderItemEvent',
        order_by='OrderItemEvent.occurred, OrderItemEvent.uuid',
        cascade='all, delete-orphan',
        cascade_backrefs=False,
        back_populates='item',
        doc="""
        List of :class:`OrderItemEvent` records for the item.
        """)

    @property
    def full_description(self):
        """ """
        fields = [
            self.product_brand or '',
            self.product_description or '',
            self.product_size or '']
        fields = [f.strip() for f in fields if f.strip()]
        return ' '.join(fields)

    def __str__(self):
        return self.full_description

    def add_event(self, type_code, user, **kwargs):
        """
        Convenience method to add a new :class:`OrderItemEvent` for
        the item.
        """
        kwargs['type_code'] = type_code
        kwargs['actor'] = user
        self.events.append(OrderItemEvent(**kwargs))


class OrderItemEvent(model.Base):
    """
    An event in the life of an :term:`order item`.
    """
    __tablename__ = 'sideshow_order_item_event'

    uuid = model.uuid_column()

    item_uuid = model.uuid_fk_column('sideshow_order_item.uuid', nullable=False)
    item = orm.relationship(
        OrderItem,
        cascade_backrefs=False,
        back_populates='events',
        doc="""
        Reference to the :class:`OrderItem` to which the event
        pertains.
        """)

    type_code = sa.Column(sa.Integer, nullable=False, doc="""
    Code indicating the type of event; values must be defined in
    :data:`~sideshow.enum.ORDER_ITEM_EVENT`.
    """)

    occurred = sa.Column(sa.DateTime(timezone=True), nullable=False, default=datetime.datetime.now, doc="""
    Date and time when the event occurred.
    """)

    actor_uuid = model.uuid_fk_column('user.uuid', nullable=False)
    actor = orm.relationship(
        model.User,
        doc="""
        :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
        performed the action.
        """)

    note = sa.Column(sa.Text(), nullable=True, doc="""
    Optional note recorded for the event.
    """)
