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
New Order Batch Handler
"""

import datetime
import decimal
from collections import OrderedDict

import sqlalchemy as sa

from wuttjamaican.batch import BatchHandler

from sideshow.db.model import NewOrderBatch


class NewOrderBatchHandler(BatchHandler):
    """
    The :term:`batch handler` for :term:`new order batches <new order
    batch>`.

    This is responsible for business logic around the creation of new
    :term:`orders <order>`.  A
    :class:`~sideshow.db.model.batch.neworder.NewOrderBatch` tracks
    all user input until they "submit" (execute) at which point an
    :class:`~sideshow.db.model.orders.Order` is created.

    After the batch has executed the :term:`order handler` takes over
    responsibility for the rest of the order lifecycle.
    """
    model_class = NewOrderBatch

    def get_default_store_id(self):
        """
        Returns the configured default value for
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatch.store_id`,
        or ``None``.
        """
        return self.config.get('sideshow.orders.default_store_id')

    def use_local_customers(self):
        """
        Returns boolean indicating whether :term:`local customer`
        accounts should be used.  This is true by default, but may be
        false for :term:`external customer` lookups.
        """
        return self.config.get_bool('sideshow.orders.use_local_customers',
                                    default=True)

    def use_local_products(self):
        """
        Returns boolean indicating whether :term:`local product`
        records should be used.  This is true by default, but may be
        false for :term:`external product` lookups.
        """
        return self.config.get_bool('sideshow.orders.use_local_products',
                                    default=True)

    def allow_unknown_products(self):
        """
        Returns boolean indicating whether :term:`pending products
        <pending product>` are allowed when creating an order.

        This is true by default, so user can enter new/unknown product
        when creating an order.  This can be disabled, to force user
        to choose existing local/external product.
        """
        return self.config.get_bool('sideshow.orders.allow_unknown_products',
                                    default=True)

    def allow_item_discounts(self):
        """
        Returns boolean indicating whether per-item discounts are
        allowed when creating an order.
        """
        return self.config.get_bool('sideshow.orders.allow_item_discounts',
                                    default=False)

    def allow_item_discounts_if_on_sale(self):
        """
        Returns boolean indicating whether per-item discounts are
        allowed even when the item is already on sale.
        """
        return self.config.get_bool('sideshow.orders.allow_item_discounts_if_on_sale',
                                    default=False)

    def get_default_item_discount(self):
        """
        Returns the default item discount percentage, e.g. 15.

        :rtype: :class:`~python:decimal.Decimal` or ``None``
        """
        discount = self.config.get('sideshow.orders.default_item_discount')
        if discount:
            return decimal.Decimal(discount)

    def autocomplete_customers_external(self, session, term, user=None):
        """
        Return autocomplete search results for :term:`external
        customer` records.

        There is no default logic here; subclass must implement.

        :param session: Current app :term:`db session`.

        :param term: Search term string from user input.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is doing the search, if known.

        :returns: List of search results; each should be a dict with
           ``value`` and ``label`` keys.
        """
        raise NotImplementedError

    def autocomplete_customers_local(self, session, term, user=None):
        """
        Return autocomplete search results for
        :class:`~sideshow.db.model.customers.LocalCustomer` records.

        :param session: Current app :term:`db session`.

        :param term: Search term string from user input.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is doing the search, if known.

        :returns: List of search results; each should be a dict with
           ``value`` and ``label`` keys.
        """
        model = self.app.model

        # base query
        query = session.query(model.LocalCustomer)

        # filter query
        criteria = [model.LocalCustomer.full_name.ilike(f'%{word}%')
                    for word in term.split()]
        query = query.filter(sa.and_(*criteria))

        # sort query
        query = query.order_by(model.LocalCustomer.full_name)

        # get data
        # TODO: need max_results option
        customers = query.all()

        # get results
        def result(customer):
            return {'value': customer.uuid.hex,
                    'label': customer.full_name}
        return [result(c) for c in customers]

    def init_batch(self, batch, session=None, progress=None, **kwargs):
        """
        Initialize a new batch.

        This sets the
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatch.store_id`,
        if the batch does not yet have one and a default is
        configured.
        """
        if not batch.store_id:
            batch.store_id = self.get_default_store_id()

    def set_customer(self, batch, customer_info, user=None):
        """
        Set/update customer info for the batch.

        This will first set one of the following:

        * :attr:`~sideshow.db.model.batch.neworder.NewOrderBatch.customer_id`
        * :attr:`~sideshow.db.model.batch.neworder.NewOrderBatch.local_customer`
        * :attr:`~sideshow.db.model.batch.neworder.NewOrderBatch.pending_customer`

        Note that a new
        :class:`~sideshow.db.model.customers.PendingCustomer` record
        is created if necessary.

        And then it will update customer-related attributes via one of:

        * :meth:`refresh_batch_from_external_customer()`
        * :meth:`refresh_batch_from_local_customer()`
        * :meth:`refresh_batch_from_pending_customer()`

        Note that ``customer_info`` may be ``None``, which will cause
        customer attributes to be set to ``None`` also.

        :param batch:
           :class:`~sideshow.db.model.batch.neworder.NewOrderBatch` to
           update.

        :param customer_info: Customer ID string, or dict of
           :class:`~sideshow.db.model.customers.PendingCustomer` data,
           or ``None`` to clear the customer info.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is performing the action.  This is used to set
           :attr:`~sideshow.db.model.customers.PendingCustomer.created_by`
           on the pending customer, if applicable.  If not specified,
           the batch creator is assumed.
        """
        model = self.app.model
        enum = self.app.enum
        session = self.app.get_session(batch)
        use_local = self.use_local_customers()

        # set customer info
        if isinstance(customer_info, str):
            if use_local:

                # local_customer
                customer = session.get(model.LocalCustomer, customer_info)
                if not customer:
                    raise ValueError("local customer not found")
                batch.local_customer = customer
                self.refresh_batch_from_local_customer(batch)

            else: # external customer_id
                batch.customer_id = customer_info
                self.refresh_batch_from_external_customer(batch)

        elif customer_info:

            # pending_customer
            batch.customer_id = None
            batch.local_customer = None
            customer = batch.pending_customer
            if not customer:
                customer = model.PendingCustomer(status=enum.PendingCustomerStatus.PENDING,
                                                 created_by=user or batch.created_by)
                session.add(customer)
                batch.pending_customer = customer
            fields = [
                'full_name',
                'first_name',
                'last_name',
                'phone_number',
                'email_address',
            ]
            for key in fields:
                setattr(customer, key, customer_info.get(key))
            if 'full_name' not in customer_info:
                customer.full_name = self.app.make_full_name(customer.first_name,
                                                             customer.last_name)
            self.refresh_batch_from_pending_customer(batch)

        else:

            # null
            batch.customer_id = None
            batch.local_customer = None
            batch.customer_name = None
            batch.phone_number = None
            batch.email_address = None

        session.flush()

    def refresh_batch_from_external_customer(self, batch):
        """
        Update customer-related attributes on the batch, from its
        :term:`external customer` record.

        This is called automatically from :meth:`set_customer()`.

        There is no default logic here; subclass must implement.
        """
        raise NotImplementedError

    def refresh_batch_from_local_customer(self, batch):
        """
        Update customer-related attributes on the batch, from its
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatch.local_customer`
        record.

        This is called automatically from :meth:`set_customer()`.
        """
        customer = batch.local_customer
        batch.customer_name = customer.full_name
        batch.phone_number = customer.phone_number
        batch.email_address = customer.email_address

    def refresh_batch_from_pending_customer(self, batch):
        """
        Update customer-related attributes on the batch, from its
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatch.pending_customer`
        record.

        This is called automatically from :meth:`set_customer()`.
        """
        customer = batch.pending_customer
        batch.customer_name = customer.full_name
        batch.phone_number = customer.phone_number
        batch.email_address = customer.email_address

    def autocomplete_products_external(self, session, term, user=None):
        """
        Return autocomplete search results for :term:`external
        product` records.

        There is no default logic here; subclass must implement.

        :param session: Current app :term:`db session`.

        :param term: Search term string from user input.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is doing the search, if known.

        :returns: List of search results; each should be a dict with
           ``value`` and ``label`` keys.
        """
        raise NotImplementedError

    def autocomplete_products_local(self, session, term, user=None):
        """
        Return autocomplete search results for
        :class:`~sideshow.db.model.products.LocalProduct` records.

        :param session: Current app :term:`db session`.

        :param term: Search term string from user input.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is doing the search, if known.

        :returns: List of search results; each should be a dict with
           ``value`` and ``label`` keys.
        """
        model = self.app.model

        # base query
        query = session.query(model.LocalProduct)

        # filter query
        criteria = []
        for word in term.split():
            criteria.append(sa.or_(
                model.LocalProduct.brand_name.ilike(f'%{word}%'),
                model.LocalProduct.description.ilike(f'%{word}%')))
        query = query.filter(sa.and_(*criteria))

        # sort query
        query = query.order_by(model.LocalProduct.brand_name,
                               model.LocalProduct.description)

        # get data
        # TODO: need max_results option
        products = query.all()

        # get results
        def result(product):
            return {'value': product.uuid.hex,
                    'label': product.full_description}
        return [result(c) for c in products]

    def get_default_uom_choices(self):
        """
        Returns a list of ordering UOM choices which should be
        presented to the user by default.

        The built-in logic here will return everything from
        :data:`~sideshow.enum.ORDER_UOM`.

        :returns: List of dicts, each with ``key`` and ``value``
           corresponding to the UOM code and label, respectively.
        """
        enum = self.app.enum
        return [{'key': key, 'value': val}
                for key, val in enum.ORDER_UOM.items()]

    def get_product_info_external(self, session, product_id, user=None):
        """
        Returns basic info for an :term:`external product` as pertains
        to ordering.

        When user has located a product via search, and must then
        choose order quantity and UOM based on case size, pricing
        etc., this method is called to retrieve the product info.

        There is no default logic here; subclass must implement.  See
        also :meth:`get_product_info_local()`.

        :param session: Current app :term:`db session`.

        :param product_id: Product ID string for which to retrieve
           info.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is performing the action, if known.

        :returns: Dict of product info.  Should raise error instead of
           returning ``None`` if product not found.

        This method should only be called after a product has been
        identified via autocomplete/search lookup; therefore the
        ``product_id`` should be valid, and the caller can expect this
        method to *always* return a dict.  If for some reason the
        product cannot be found here, an error should be raised.

        The dict should contain as much product info as is available
        and needed; if some are missing it should not cause too much
        trouble in the app.  Here is a basic example::

           def get_product_info_external(self, session, product_id, user=None):
               ext_model = get_external_model()
               ext_session = make_external_session()

               ext_product = ext_session.get(ext_model.Product, product_id)
               if not ext_product:
                   ext_session.close()
                   raise ValueError(f"external product not found: {product_id}")

               info = {
                   'product_id': product_id,
                   'scancode': product.scancode,
                   'brand_name': product.brand_name,
                   'description': product.description,
                   'size': product.size,
                   'weighed': product.sold_by_weight,
                   'special_order': False,
                   'department_id': str(product.department_number),
                   'department_name': product.department_name,
                   'case_size': product.case_size,
                   'unit_price_reg': product.unit_price_reg,
                   'vendor_name': product.vendor_name,
                   'vendor_item_code': product.vendor_item_code,
               }

               ext_session.close()
               return info
        """
        raise NotImplementedError

    def get_product_info_local(self, session, uuid, user=None):
        """
        Returns basic info for a :term:`local product` as pertains to
        ordering.

        When user has located a product via search, and must then
        choose order quantity and UOM based on case size, pricing
        etc., this method is called to retrieve the product info.

        See :meth:`get_product_info_external()` for more explanation.

        This method will locate the
        :class:`~sideshow.db.model.products.LocalProduct` record, then
        (if found) it calls :meth:`normalize_local_product()` and
        returns the result.

        :param session: Current :term:`db session`.

        :param uuid: UUID for the desired
           :class:`~sideshow.db.model.products.LocalProduct`.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is performing the action, if known.

        :returns: Dict of product info.
        """
        model = self.app.model
        product = session.get(model.LocalProduct, uuid)
        if not product:
            raise ValueError(f"Local Product not found: {uuid}")

        return self.normalize_local_product(product)

    def normalize_local_product(self, product):
        """
        Returns a normalized dict of info for the given :term:`local
        product`.

        This is called by:

        * :meth:`get_product_info_local()`
        * :meth:`get_past_products()`

        :param product:
           :class:`~sideshow.db.model.products.LocalProduct` instance.

        :returns: Dict of product info.

        The keys for this dict should essentially one-to-one for the
        product fields, with one exception:

        * ``product_id`` will be set to the product UUID as string
        """
        return {
            'product_id': product.uuid.hex,
            'scancode': product.scancode,
            'brand_name': product.brand_name,
            'description': product.description,
            'size': product.size,
            'full_description': product.full_description,
            'weighed': product.weighed,
            'special_order': product.special_order,
            'department_id': product.department_id,
            'department_name': product.department_name,
            'case_size': product.case_size,
            'unit_price_reg': product.unit_price_reg,
            'vendor_name': product.vendor_name,
            'vendor_item_code': product.vendor_item_code,
        }

    def get_past_orders(self, batch):
        """
        Retrieve a (possibly empty) list of past :term:`orders
        <order>` for the batch customer.

        This is called by :meth:`get_past_products()`.

        :param batch:
           :class:`~sideshow.db.model.batch.neworder.NewOrderBatch`
           instance.

        :returns: List of :class:`~sideshow.db.model.orders.Order`
           records.
        """
        model = self.app.model
        session = self.app.get_session(batch)
        orders = session.query(model.Order)

        if batch.customer_id:
            orders = orders.filter(model.Order.customer_id == batch.customer_id)
        elif batch.local_customer:
            orders = orders.filter(model.Order.local_customer == batch.local_customer)
        else:
            raise ValueError(f"batch has no customer: {batch}")

        orders = orders.order_by(model.Order.created.desc())
        return orders.all()

    def get_past_products(self, batch, user=None):
        """
        Retrieve a (possibly empty) list of products which have been
        previously ordered by the batch customer.

        Note that this does not return :term:`order items <order
        item>`, nor does it return true product records, but rather it
        returns a list of dicts.  Each will have product info but will
        *not* have order quantity etc.

        This method calls :meth:`get_past_orders()` and then iterates
        through each order item therein.  Any duplicated products
        encountered will be skipped, so the final list contains unique
        products.

        Each dict in the result is obtained by calling one of:

        * :meth:`normalize_local_product()`
        * :meth:`get_product_info_external()`

        :param batch:
           :class:`~sideshow.db.model.batch.neworder.NewOrderBatch`
           instance.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is performing the action, if known.

        :returns: List of product info dicts.
        """
        model = self.app.model
        session = self.app.get_session(batch)
        use_local = self.use_local_products()
        user = user or batch.created_by
        products = OrderedDict()

        # track down all order items for batch contact
        for order in self.get_past_orders(batch):
            for item in order.items:

                # nb. we only need the first match for each product
                if use_local:
                    product = item.local_product
                    if product and product.uuid not in products:
                        products[product.uuid] = self.normalize_local_product(product)
                elif item.product_id and item.product_id not in products:
                    products[item.product_id] = self.get_product_info_external(
                        session, item.product_id, user=user)

        products = list(products.values())
        for product in products:

            price = product['unit_price_reg']

            if 'unit_price_reg_display' not in product:
                product['unit_price_reg_display'] = self.app.render_currency(price)

            if 'unit_price_quoted' not in product:
                product['unit_price_quoted'] = price

            if 'unit_price_quoted_display' not in product:
                product['unit_price_quoted_display'] = product['unit_price_reg_display']

            if ('case_price_quoted' not in product
                and product.get('unit_price_quoted') is not None
                and product.get('case_size') is not None):
                product['case_price_quoted'] = product['unit_price_quoted'] * product['case_size']

            if ('case_price_quoted_display' not in product
                and 'case_price_quoted' in product):
                product['case_price_quoted_display'] = self.app.render_currency(
                    product['case_price_quoted'])

        return products

    def add_item(self, batch, product_info, order_qty, order_uom,
                 discount_percent=None, user=None):
        """
        Add a new item/row to the batch, for given product and quantity.

        See also :meth:`update_item()`.

        :param batch:
           :class:`~sideshow.db.model.batch.neworder.NewOrderBatch` to
           update.

        :param product_info: Product ID string, or dict of
           :class:`~sideshow.db.model.products.PendingProduct` data.

        :param order_qty:
           :attr:`~sideshow.db.model.batch.neworder.NewOrderBatchRow.order_qty`
           value for the new row.

        :param order_uom:
           :attr:`~sideshow.db.model.batch.neworder.NewOrderBatchRow.order_uom`
           value for the new row.

        :param discount_percent: Sets the
           :attr:`~sideshow.db.model.batch.neworder.NewOrderBatchRow.discount_percent`
           for the row, if allowed.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is performing the action.  This is used to set
           :attr:`~sideshow.db.model.products.PendingProduct.created_by`
           on the pending product, if applicable.  If not specified,
           the batch creator is assumed.

        :returns:
           :class:`~sideshow.db.model.batch.neworder.NewOrderBatchRow`
           instance.
        """
        model = self.app.model
        enum = self.app.enum
        session = self.app.get_session(batch)
        use_local = self.use_local_products()
        row = self.make_row()

        # set product info
        if isinstance(product_info, str):
            if use_local:

                # local_product
                local = session.get(model.LocalProduct, product_info)
                if not local:
                    raise ValueError("local product not found")
                row.local_product = local

            else: # external product_id
                row.product_id = product_info

        else:
            # pending_product
            if not self.allow_unknown_products():
                raise TypeError("unknown/pending product not allowed for new orders")
            row.product_id = None
            row.local_product = None
            pending = model.PendingProduct(status=enum.PendingProductStatus.PENDING,
                                           created_by=user or batch.created_by)
            fields = [
                'scancode',
                'brand_name',
                'description',
                'size',
                'weighed',
                'department_id',
                'department_name',
                'special_order',
                'vendor_name',
                'vendor_item_code',
                'case_size',
                'unit_cost',
                'unit_price_reg',
                'notes',
            ]
            for key in fields:
                setattr(pending, key, product_info.get(key))

            # nb. this may convert float to decimal etc.
            session.add(pending)
            session.flush()
            session.refresh(pending)
            row.pending_product = pending

        # set order info
        row.order_qty = order_qty
        row.order_uom = order_uom

        # discount
        if self.allow_item_discounts():
            row.discount_percent = discount_percent or 0

        # add row to batch
        self.add_row(batch, row)
        session.flush()
        return row

    def update_item(self, row, product_info, order_qty, order_uom,
                    discount_percent=None, user=None):
        """
        Update an item/row, per given product and quantity.

        See also :meth:`add_item()`.

        :param row:
           :class:`~sideshow.db.model.batch.neworder.NewOrderBatchRow`
           to update.

        :param product_info: Product ID string, or dict of
           :class:`~sideshow.db.model.products.PendingProduct` data.

        :param order_qty: New
           :attr:`~sideshow.db.model.batch.neworder.NewOrderBatchRow.order_qty`
           value for the row.

        :param order_uom: New
           :attr:`~sideshow.db.model.batch.neworder.NewOrderBatchRow.order_uom`
           value for the row.

        :param discount_percent: Sets the
           :attr:`~sideshow.db.model.batch.neworder.NewOrderBatchRow.discount_percent`
           for the row, if allowed.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is performing the action.  This is used to set
           :attr:`~sideshow.db.model.products.PendingProduct.created_by`
           on the pending product, if applicable.  If not specified,
           the batch creator is assumed.
        """
        model = self.app.model
        enum = self.app.enum
        session = self.app.get_session(row)
        use_local = self.use_local_products()

        # set product info
        if isinstance(product_info, str):
            if use_local:

                # local_product
                local = session.get(model.LocalProduct, product_info)
                if not local:
                    raise ValueError("local product not found")
                row.local_product = local

            else: # external product_id
                row.product_id = product_info

        else:
            # pending_product
            if not self.allow_unknown_products():
                raise TypeError("unknown/pending product not allowed for new orders")
            row.product_id = None
            row.local_product = None
            pending = row.pending_product
            if not pending:
                pending = model.PendingProduct(status=enum.PendingProductStatus.PENDING,
                                               created_by=user or row.batch.created_by)
                session.add(pending)
                row.pending_product = pending
            fields = [
                'scancode',
                'brand_name',
                'description',
                'size',
                'weighed',
                'department_id',
                'department_name',
                'special_order',
                'vendor_name',
                'vendor_item_code',
                'case_size',
                'unit_cost',
                'unit_price_reg',
                'notes',
            ]
            for key in fields:
                setattr(pending, key, product_info.get(key))

            # nb. this may convert float to decimal etc.
            session.flush()
            session.refresh(pending)

        # set order info
        row.order_qty = order_qty
        row.order_uom = order_uom

        # discount
        if self.allow_item_discounts():
            row.discount_percent = discount_percent or 0

        # nb. this may convert float to decimal etc.
        session.flush()
        session.refresh(row)

        # refresh per new info
        self.refresh_row(row)

    def refresh_row(self, row):
        """
        Refresh data for the row.  This is called when adding a new
        row to the batch, or anytime the row is updated (e.g. when
        changing order quantity).

        This calls one of the following to update product-related
        attributes:

        * :meth:`refresh_row_from_external_product()`
        * :meth:`refresh_row_from_local_product()`
        * :meth:`refresh_row_from_pending_product()`

        It then re-calculates the row's
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatchRow.total_price`
        and updates the batch accordingly.

        It also sets the row
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatchRow.status_code`.
        """
        enum = self.app.enum
        row.status_code = None
        row.status_text = None

        # ensure product
        if not row.product_id and not row.local_product and not row.pending_product:
            row.status_code = row.STATUS_MISSING_PRODUCT
            return

        # ensure order qty/uom
        if not row.order_qty or not row.order_uom:
            row.status_code = row.STATUS_MISSING_ORDER_QTY
            return

        # update product attrs on row
        if row.product_id:
            self.refresh_row_from_external_product(row)
        elif row.local_product:
            self.refresh_row_from_local_product(row)
        else:
            self.refresh_row_from_pending_product(row)

        # we need to know if total price changes
        old_total = row.total_price

        # update quoted price
        row.unit_price_quoted = None
        row.case_price_quoted = None
        if row.unit_price_sale is not None and (
                not row.sale_ends
                or row.sale_ends > datetime.datetime.now()):
            row.unit_price_quoted = row.unit_price_sale
        else:
            row.unit_price_quoted = row.unit_price_reg
        if row.unit_price_quoted is not None and row.case_size:
            row.case_price_quoted = row.unit_price_quoted * row.case_size

        # update row total price
        row.total_price = None
        if row.order_uom == enum.ORDER_UOM_CASE:
            # TODO: why are we not using case price again?
            # if row.case_price_quoted:
            #     row.total_price = row.case_price_quoted * row.order_qty
            if row.unit_price_quoted is not None and row.case_size is not None:
                row.total_price = row.unit_price_quoted * row.case_size * row.order_qty
        else: # ORDER_UOM_UNIT (or similar)
            if row.unit_price_quoted is not None:
                row.total_price = row.unit_price_quoted * row.order_qty
        if row.total_price is not None:
            if row.discount_percent and self.allow_item_discounts():
                row.total_price = (float(row.total_price)
                                   * (100 - float(row.discount_percent))
                                   / 100.0)
            row.total_price = decimal.Decimal(f'{row.total_price:0.2f}')

        # update batch if total price changed
        if row.total_price != old_total:
            batch = row.batch
            batch.total_price = ((batch.total_price or 0)
                                 + (row.total_price or 0)
                                 - (old_total or 0))

        # all ok
        row.status_code = row.STATUS_OK

    def refresh_row_from_local_product(self, row):
        """
        Update product-related attributes on the row, from its
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatchRow.local_product`
        record.

        This is called automatically from :meth:`refresh_row()`.
        """
        product = row.local_product
        row.product_scancode = product.scancode
        row.product_brand = product.brand_name
        row.product_description = product.description
        row.product_size = product.size
        row.product_weighed = product.weighed
        row.department_id = product.department_id
        row.department_name = product.department_name
        row.special_order = product.special_order
        row.vendor_name = product.vendor_name
        row.vendor_item_code = product.vendor_item_code
        row.case_size = product.case_size
        row.unit_cost = product.unit_cost
        row.unit_price_reg = product.unit_price_reg

    def refresh_row_from_pending_product(self, row):
        """
        Update product-related attributes on the row, from its
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatchRow.pending_product`
        record.

        This is called automatically from :meth:`refresh_row()`.
        """
        product = row.pending_product
        row.product_scancode = product.scancode
        row.product_brand = product.brand_name
        row.product_description = product.description
        row.product_size = product.size
        row.product_weighed = product.weighed
        row.department_id = product.department_id
        row.department_name = product.department_name
        row.special_order = product.special_order
        row.vendor_name = product.vendor_name
        row.vendor_item_code = product.vendor_item_code
        row.case_size = product.case_size
        row.unit_cost = product.unit_cost
        row.unit_price_reg = product.unit_price_reg

    def refresh_row_from_external_product(self, row):
        """
        Update product-related attributes on the row, from its
        :term:`external product` record indicated by
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatchRow.product_id`.

        This is called automatically from :meth:`refresh_row()`.

        There is no default logic here; subclass must implement as
        needed.
        """
        raise NotImplementedError

    def remove_row(self, row):
        """
        Remove a row from its batch.

        This also will update the batch
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatch.total_price`
        accordingly.
        """
        if row.total_price:
            batch = row.batch
            batch.total_price = (batch.total_price or 0) - row.total_price

        super().remove_row(row)

    def do_delete(self, batch, user, **kwargs):
        """
        Delete a batch completely.

        If the batch has :term:`pending customer` or :term:`pending
        product` records, they are also deleted - unless still
        referenced by some order(s).
        """
        session = self.app.get_session(batch)

        # maybe delete pending customer
        customer = batch.pending_customer
        if customer and not customer.orders:
            session.delete(customer)

        # maybe delete pending products
        for row in batch.rows:
            product = row.pending_product
            if product and not product.order_items:
                session.delete(product)

        # continue with normal deletion
        super().do_delete(batch, user, **kwargs)

    def why_not_execute(self, batch, **kwargs):
        """
        By default this checks to ensure the batch has a customer with
        phone number, and at least one item.  It also may check to
        ensure the store is assigned, if applicable.
        """
        if not batch.store_id:
            order_handler = self.app.get_order_handler()
            if order_handler.expose_store_id():
                return "Must assign the store"

        if not batch.customer_name:
            return "Must assign the customer"

        if not batch.phone_number:
            return "Customer phone number is required"

        rows = self.get_effective_rows(batch)
        if not rows:
            return "Must add at least one valid item"

    def get_effective_rows(self, batch):
        """
        Only rows with
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatchRow.STATUS_OK`
        are "effective" - i.e. rows with other status codes will not
        be created as proper order items.
        """
        return [row for row in batch.rows
                if row.status_code == row.STATUS_OK]

    def execute(self, batch, user=None, progress=None, **kwargs):
        """
        Execute the batch; this should make a proper :term:`order`.

        By default, this will call:

        * :meth:`make_local_customer()`
        * :meth:`process_pending_products()`
        * :meth:`make_new_order()`

        And will return the new
        :class:`~sideshow.db.model.orders.Order` instance.

        Note that callers should use
        :meth:`~wuttjamaican:wuttjamaican.batch.BatchHandler.do_execute()`
        instead, which calls this method automatically.
        """
        rows = self.get_effective_rows(batch)
        self.make_local_customer(batch)
        self.process_pending_products(batch, rows)
        order = self.make_new_order(batch, rows, user=user, progress=progress, **kwargs)
        return order

    def make_local_customer(self, batch):
        """
        If applicable, this converts the batch :term:`pending
        customer` into a :term:`local customer`.

        This is called automatically from :meth:`execute()`.

        This logic will happen only if :meth:`use_local_customers()`
        returns true, and the batch has pending instead of local
        customer (so far).

        It will create a new
        :class:`~sideshow.db.model.customers.LocalCustomer` record and
        populate it from the batch
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatch.pending_customer`.
        The latter is then deleted.
        """
        if not self.use_local_customers():
            return

        # nothing to do if no pending customer
        pending = batch.pending_customer
        if not pending:
            return

        session = self.app.get_session(batch)

        # maybe convert pending to local customer
        if not batch.local_customer:
            model = self.app.model
            inspector = sa.inspect(model.LocalCustomer)
            local = model.LocalCustomer()
            for prop in inspector.column_attrs:
                if hasattr(pending, prop.key):
                    setattr(local, prop.key, getattr(pending, prop.key))
            session.add(local)
            batch.local_customer = local

        # remove pending customer
        batch.pending_customer = None
        session.delete(pending)
        session.flush()

    def process_pending_products(self, batch, rows):
        """
        Process any :term:`pending products <pending product>` which
        are present in the batch.

        This is called automatically from :meth:`execute()`.

        If :term:`local products <local product>` are used, this will
        convert the pending products to local products.

        If :term:`external products <external product>` are used, this
        will update the pending product records' status to indicate
        they are ready to be resolved.
        """
        enum = self.app.enum
        model = self.app.model
        session = self.app.get_session(batch)

        if self.use_local_products():
            inspector = sa.inspect(model.LocalProduct)
            for row in rows:

                if row.local_product or not row.pending_product:
                    continue

                pending = row.pending_product
                local = model.LocalProduct()

                for prop in inspector.column_attrs:
                    if hasattr(pending, prop.key):
                        setattr(local, prop.key, getattr(pending, prop.key))
                session.add(local)

                row.local_product = local
                row.pending_product = None
                session.delete(pending)

        else:    # external products; pending should be marked 'ready'
            for row in rows:
                pending = row.pending_product
                if pending:
                    pending.status = enum.PendingProductStatus.READY

        session.flush()

    def make_new_order(self, batch, rows, user=None, progress=None, **kwargs):
        """
        Create a new :term:`order` from the batch data.

        This is called automatically from :meth:`execute()`.

        :param batch:
           :class:`~sideshow.db.model.batch.neworder.NewOrderBatch`
           instance.

        :param rows: List of effective rows for the batch, i.e. which
           rows should be converted to :term:`order items <order
           item>`.

        :returns: :class:`~sideshow.db.model.orders.Order` instance.
        """
        model = self.app.model
        enum = self.app.enum
        session = self.app.get_session(batch)

        batch_fields = [
            'store_id',
            'customer_id',
            'local_customer',
            'pending_customer',
            'customer_name',
            'phone_number',
            'email_address',
            'total_price',
        ]

        row_fields = [
            'product_id',
            'local_product',
            'pending_product',
            'product_scancode',
            'product_brand',
            'product_description',
            'product_size',
            'product_weighed',
            'department_id',
            'department_name',
            'vendor_name',
            'vendor_item_code',
            'case_size',
            'order_qty',
            'order_uom',
            'unit_cost',
            'unit_price_quoted',
            'case_price_quoted',
            'unit_price_reg',
            'unit_price_sale',
            'sale_ends',
            'discount_percent',
            'total_price',
            'special_order',
        ]

        # make order
        kw = dict([(field, getattr(batch, field))
                   for field in batch_fields])
        kw['order_id'] = batch.id
        kw['created_by'] = user
        order = model.Order(**kw)
        session.add(order)
        session.flush()

        def convert(row, i):

            # make order item
            kw = dict([(field, getattr(row, field))
                       for field in row_fields])
            item = model.OrderItem(**kw)
            order.items.append(item)

            # set item status
            self.set_initial_item_status(item, user)

        self.app.progress_loop(convert, rows, progress,
                               message="Converting batch rows to order items")
        session.flush()
        return order

    def set_initial_item_status(self, item, user, **kwargs):
        """
        Set the initial status and attach event(s) for the given item.

        This is called from :meth:`make_new_order()` for each item
        after it is added to the order.

        Default logic will set status to
        :data:`~sideshow.enum.ORDER_ITEM_STATUS_READY` and attach 2
        events:

        * :data:`~sideshow.enum.ORDER_ITEM_EVENT_INITIATED`
        * :data:`~sideshow.enum.ORDER_ITEM_EVENT_READY`

        :param item: :class:`~sideshow.db.model.orders.OrderItem`
           being added to the new order.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is performing the action.
        """
        enum = self.app.enum
        item.add_event(enum.ORDER_ITEM_EVENT_INITIATED, user)
        item.add_event(enum.ORDER_ITEM_EVENT_READY, user)
        item.status_code = enum.ORDER_ITEM_STATUS_READY
