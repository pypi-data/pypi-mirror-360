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
Data models for Products
"""

import datetime

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.db import model

from sideshow.enum import PendingProductStatus


class ProductMixin:
    """
    Base class for product tables.  This has shared columns, used by e.g.:

    * :class:`LocalProduct`
    * :class:`PendingProduct`
    """

    scancode = sa.Column(sa.String(length=14), nullable=True, doc="""
    Scancode for the product, as string.

    .. note::

       This column allows 14 chars, so can store a full GPC with check
       digit.  However as of writing the actual format used here does
       not matter to Sideshow logic; "anything" should work.

       That may change eventually, depending on POS integration
       scenarios that come up.  Maybe a config option to declare
       whether check digit should be included or not, etc.
    """)

    brand_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Brand name for the product - up to 100 chars.
    """)

    description = sa.Column(sa.String(length=255), nullable=True, doc="""
    Description for the product - up to 255 chars.
    """)

    size = sa.Column(sa.String(length=30), nullable=True, doc="""
    Size of the product, as string - up to 30 chars.
    """)

    weighed = sa.Column(sa.Boolean(), nullable=True, doc="""
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

    case_size = sa.Column(sa.Numeric(precision=9, scale=4), nullable=True, doc="""
    Case pack count for the product, if known.
    """)

    unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Cost of goods amount for one "unit" (not "case") of the product,
    as decimal to 4 places.
    """)

    unit_price_reg = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Regular price for a "unit" of the product.
    """)

    notes = sa.Column(sa.Text(), nullable=True, doc="""
    Arbitrary notes regarding the product, if applicable.
    """)

    @property
    def full_description(self):
        """ """
        fields = [
            self.brand_name or '',
            self.description or '',
            self.size or '']
        fields = [f.strip() for f in fields if f.strip()]
        return ' '.join(fields)

    def __str__(self):
        return self.full_description


class LocalProduct(ProductMixin, model.Base):
    """
    This table contains the :term:`local product` records.

    Sideshow will do customer lookups against this table by default,
    unless it's configured to use :term:`external products <external
    product>` instead.

    Also by default, when a :term:`new order batch` with
    :term:`pending product(s) <pending product>` is executed, new
    record(s) will be added to this local products table, for lookup
    next time.
    """
    __tablename__ = 'sideshow_product_local'

    uuid = model.uuid_column()

    external_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    ID of the true external product associated with this record, if
    applicable.
    """)

    order_items = orm.relationship(
        'OrderItem',
        back_populates='local_product',
        cascade_backrefs=False,
        doc="""
        List of :class:`~sideshow.db.model.orders.OrderItem` records
        associated with this product.
        """)

    new_order_batch_rows = orm.relationship(
        'NewOrderBatchRow',
        back_populates='local_product',
        cascade_backrefs=False,
        doc="""
        List of
        :class:`~sideshow.db.model.batch.neworder.NewOrderBatchRow`
        records associated with this product.
        """)


class PendingProduct(ProductMixin, model.Base):
    """
    This table contains the :term:`pending product` records, used when
    creating an :term:`order` for new/unknown product(s).

    Sideshow will automatically create and (hopefully) delete these
    records as needed.

    By default, when a :term:`new order batch` with pending product(s)
    is executed, new record(s) will be added to the :term:`local
    products <local product>` table, for lookup next time.
    """
    __tablename__ = 'sideshow_product_pending'

    uuid = model.uuid_column()

    product_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    ID of the :term:`external product` associated with this record, if
    applicable/known.
    """)

    status = sa.Column(sa.Enum(PendingProductStatus), nullable=False, doc="""
    Status code for the product record.
    """)

    created = sa.Column(sa.DateTime(timezone=True), nullable=False,
                        default=datetime.datetime.now, doc="""
    Timestamp when the product record was created.
    """)

    created_by_uuid = model.uuid_fk_column('user.uuid', nullable=False)
    created_by = orm.relationship(
        model.User,
        cascade_backrefs=False,
        doc="""
        Reference to the
        :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
        created the product record.
        """)

    order_items = orm.relationship(
        'OrderItem',
        back_populates='pending_product',
        cascade_backrefs=False,
        doc="""
        List of :class:`~sideshow.db.model.orders.OrderItem` records
        associated with this product.
        """)

    new_order_batch_rows = orm.relationship(
        'NewOrderBatchRow',
        back_populates='pending_product',
        cascade_backrefs=False,
        doc="""
        List of
        :class:`~sideshow.db.model.batch.neworder.NewOrderBatchRow`
        records associated with this product.
        """)
