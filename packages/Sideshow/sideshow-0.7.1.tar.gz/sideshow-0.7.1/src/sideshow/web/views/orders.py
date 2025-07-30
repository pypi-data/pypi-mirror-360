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
Views for Orders
"""

import decimal
import json
import logging
import re

import colander
import sqlalchemy as sa
from sqlalchemy import orm

from webhelpers2.html import tags, HTML

from wuttaweb.views import MasterView
from wuttaweb.forms.schema import UserRef, WuttaMoney, WuttaQuantity, WuttaEnum, WuttaDictEnum
from wuttaweb.util import make_json_safe

from sideshow.db.model import Order, OrderItem
from sideshow.batch.neworder import NewOrderBatchHandler
from sideshow.web.forms.schema import (OrderRef,
                                       LocalCustomerRef, LocalProductRef,
                                       PendingCustomerRef, PendingProductRef)


log = logging.getLogger(__name__)


class OrderView(MasterView):
    """
    Master view for :class:`~sideshow.db.model.orders.Order`; route
    prefix is ``orders``.

    Notable URLs provided by this class:

    * ``/orders/``
    * ``/orders/new``
    * ``/orders/XXX``
    * ``/orders/XXX/delete``

    Note that the "edit" view is not exposed here; user must perform
    various other workflow actions to modify the order.

    .. attribute:: order_handler

       Reference to the :term:`order handler` as returned by
       :meth:`~sideshow.app.SideshowAppProvider.get_order_handler()`.
       This gets set in the constructor.

    .. attribute:: batch_handler

       Reference to the :term:`new order batch` handler.  This gets
       set in the constructor.
    """
    model_class = Order
    editable = False
    configurable = True

    labels = {
        'order_id': "Order ID",
        'store_id': "Store ID",
        'customer_id': "Customer ID",
    }

    grid_columns = [
        'order_id',
        'store_id',
        'customer_id',
        'customer_name',
        'total_price',
        'created',
        'created_by',
    ]

    sort_defaults = ('order_id', 'desc')

    form_fields = [
        'order_id',
        'store_id',
        'customer_id',
        'local_customer',
        'pending_customer',
        'customer_name',
        'phone_number',
        'email_address',
        'total_price',
        'created',
        'created_by',
    ]

    has_rows = True
    row_model_class = OrderItem
    rows_title = "Order Items"
    rows_sort_defaults = 'sequence'
    rows_viewable = True

    row_labels = {
        'product_scancode': "Scancode",
        'product_brand': "Brand",
        'product_description': "Description",
        'product_size': "Size",
        'department_name': "Department",
        'order_uom': "Order UOM",
        'status_code': "Status",
    }

    row_grid_columns = [
        'sequence',
        'product_scancode',
        'product_brand',
        'product_description',
        'product_size',
        'department_name',
        'special_order',
        'order_qty',
        'order_uom',
        'discount_percent',
        'total_price',
        'status_code',
    ]

    PENDING_PRODUCT_ENTRY_FIELDS = [
        'scancode',
        'brand_name',
        'description',
        'size',
        'department_id',
        'department_name',
        'vendor_name',
        'vendor_item_code',
        'case_size',
        'unit_cost',
        'unit_price_reg',
    ]

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        self.order_handler = self.app.get_order_handler()
        self.batch_handler = self.app.get_batch_handler('neworder')

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)

        # store_id
        if not self.order_handler.expose_store_id():
            g.remove('store_id')

        # order_id
        g.set_link('order_id')

        # customer_id
        g.set_link('customer_id')

        # customer_name
        g.set_link('customer_name')

        # total_price
        g.set_renderer('total_price', g.render_currency)

    def create(self):
        """
        Instead of the typical "create" view, this displays a "wizard"
        of sorts.

        Under the hood a
        :class:`~sideshow.db.model.batch.neworder.NewOrderBatch` is
        automatically created for the user when they first visit this
        page.  They can select a customer, add items etc.

        When user is finished assembling the order (i.e. populating
        the batch), they submit it.  This of course executes the
        batch, which in turn creates a true
        :class:`~sideshow.db.model.orders.Order`, and user is
        redirected to the "view order" page.

        See also these methods which may be called from this one,
        based on user actions:

        * :meth:`start_over()`
        * :meth:`cancel_order()`
        * :meth:`set_store()`
        * :meth:`assign_customer()`
        * :meth:`unassign_customer()`
        * :meth:`set_pending_customer()`
        * :meth:`get_product_info()`
        * :meth:`add_item()`
        * :meth:`update_item()`
        * :meth:`delete_item()`
        * :meth:`submit_order()`
        """
        model = self.app.model
        enum = self.app.enum
        session = self.Session()
        batch = self.get_current_batch()
        self.creating = True

        context = self.get_context_customer(batch)

        if self.request.method == 'POST':

            # first we check for traditional form post
            action = self.request.POST.get('action')
            post_actions = [
                'start_over',
                'cancel_order',
            ]
            if action in post_actions:
                return getattr(self, action)(batch)

            # okay then, we'll assume newer JSON-style post params
            data = dict(self.request.json_body)
            action = data.pop('action')
            json_actions = [
                'set_store',
                'assign_customer',
                'unassign_customer',
                # 'update_phone_number',
                # 'update_email_address',
                'set_pending_customer',
                # 'get_customer_info',
                # # 'set_customer_data',
                'get_product_info',
                'get_past_products',
                'add_item',
                'update_item',
                'delete_item',
                'submit_order',
            ]
            if action in json_actions:
                try:
                    result = getattr(self, action)(batch, data)
                except Exception as error:
                    log.warning("error calling json action for order", exc_info=True)
                    result = {'error': self.app.render_error(error)}
                return self.json_response(result)

            return self.json_response({'error': "unknown form action"})

        context.update({
            'batch': batch,
            'normalized_batch': self.normalize_batch(batch),
            'order_items': [self.normalize_row(row)
                            for row in batch.rows],
            'default_uom_choices': self.batch_handler.get_default_uom_choices(),
            'default_uom': None, # TODO?
            'expose_store_id': self.order_handler.expose_store_id(),
            'allow_item_discounts': self.batch_handler.allow_item_discounts(),
            'allow_unknown_products': (self.batch_handler.allow_unknown_products()
                                       and self.has_perm('create_unknown_product')),
            'pending_product_required_fields': self.get_pending_product_required_fields(),
            'allow_past_item_reorder': True, # TODO: make configurable?
        })

        if context['expose_store_id']:
            stores = session.query(model.Store)\
                            .filter(model.Store.archived == False)\
                            .order_by(model.Store.store_id)\
                            .all()
            context['stores'] = [{'store_id': store.store_id, 'display': store.get_display()}
                                 for store in stores]

            # set default so things just work
            if not batch.store_id:
                batch.store_id = self.batch_handler.get_default_store_id()

        if context['allow_item_discounts']:
            context['allow_item_discounts_if_on_sale'] = self.batch_handler\
                                                             .allow_item_discounts_if_on_sale()
            # nb. render quantity so that '10.0' => '10'
            context['default_item_discount'] = self.app.render_quantity(
                self.batch_handler.get_default_item_discount())
            context['dept_item_discounts'] = dict([(d['department_id'], d['default_item_discount'])
                                                   for d in self.get_dept_item_discounts()])

        return self.render_to_response('create', context)

    def get_current_batch(self):
        """
        Returns the current batch for the current user.

        This looks for a new order batch which was created by the
        user, but not yet executed.  If none is found, a new batch is
        created.

        :returns:
           :class:`~sideshow.db.model.batch.neworder.NewOrderBatch`
           instance
        """
        model = self.app.model
        session = self.Session()

        user = self.request.user
        if not user:
            raise self.forbidden()

        try:
            # there should be at most *one* new batch per user
            batch = session.query(model.NewOrderBatch)\
                           .filter(model.NewOrderBatch.created_by == user)\
                           .filter(model.NewOrderBatch.executed == None)\
                           .one()

        except orm.exc.NoResultFound:
            # no batch yet for this user, so make one
            batch = self.batch_handler.make_batch(session, created_by=user)
            session.add(batch)
            session.flush()

        return batch

    def customer_autocomplete(self):
        """
        AJAX view for customer autocomplete, when entering new order.

        This invokes one of the following on the
        :attr:`batch_handler`:

        * :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.autocomplete_customers_external()`
        * :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.autocomplete_customers_local()`

        :returns: List of search results; each should be a dict with
           ``value`` and ``label`` keys.
        """
        session = self.Session()
        term = self.request.GET.get('term', '').strip()
        if not term:
            return []

        handler = self.batch_handler
        if handler.use_local_customers():
            return handler.autocomplete_customers_local(session, term, user=self.request.user)
        else:
            return handler.autocomplete_customers_external(session, term, user=self.request.user)

    def product_autocomplete(self):
        """
        AJAX view for product autocomplete, when entering new order.

        This invokes one of the following on the
        :attr:`batch_handler`:

        * :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.autocomplete_products_external()`
        * :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.autocomplete_products_local()`

        :returns: List of search results; each should be a dict with
           ``value`` and ``label`` keys.
        """
        session = self.Session()
        term = self.request.GET.get('term', '').strip()
        if not term:
            return []

        handler = self.batch_handler
        if handler.use_local_products():
            return handler.autocomplete_products_local(session, term, user=self.request.user)
        else:
            return handler.autocomplete_products_external(session, term, user=self.request.user)

    def get_pending_product_required_fields(self):
        """ """
        required = []
        for field in self.PENDING_PRODUCT_ENTRY_FIELDS:
            require = self.config.get_bool(
                f'sideshow.orders.unknown_product.fields.{field}.required')
            if require is None and field == 'description':
                require = True
            if require:
                required.append(field)
        return required

    def get_dept_item_discounts(self):
        """
        Returns the list of per-department default item discount settings.

        Each entry in the list will look like::

           {
               'department_id': '42',
               'department_name': 'Grocery',
               'default_item_discount': 10,
           }

        :returns: List of department settings as shown above.
        """
        model = self.app.model
        session = self.Session()
        pattern = re.compile(r'^sideshow\.orders\.departments\.([^.]+)\.default_item_discount$')

        dept_item_discounts = []
        settings = session.query(model.Setting)\
                          .filter(model.Setting.name.like('sideshow.orders.departments.%.default_item_discount'))\
                          .all()
        for setting in settings:
            match = pattern.match(setting.name)
            if not match:
                log.warning("invalid setting name: %s", setting.name)
                continue
            deptid = match.group(1)
            name = self.app.get_setting(session, f'sideshow.orders.departments.{deptid}.name')
            dept_item_discounts.append({
                'department_id': deptid,
                'department_name': name,
                'default_item_discount': setting.value,
            })
        dept_item_discounts.sort(key=lambda d: d['department_name'])
        return dept_item_discounts

    def start_over(self, batch):
        """
        This will delete the user's current batch, then redirect user
        back to "Create Order" page, which in turn will auto-create a
        new batch for them.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`cancel_order()`
        * :meth:`submit_order()`
        """
        # drop current batch
        self.batch_handler.do_delete(batch, self.request.user)
        self.Session.flush()

        # send back to "create order" which makes new batch
        route_prefix = self.get_route_prefix()
        url = self.request.route_url(f'{route_prefix}.create')
        return self.redirect(url)

    def cancel_order(self, batch):
        """
        This will delete the user's current batch, then redirect user
        back to "List Orders" page.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`start_over()`
        * :meth:`submit_order()`
        """
        self.batch_handler.do_delete(batch, self.request.user)
        self.Session.flush()

        # set flash msg just to be more obvious
        self.request.session.flash("New order has been deleted.")

        # send user back to orders list, w/ no new batch generated
        url = self.get_index_url()
        return self.redirect(url)

    def set_store(self, batch, data):
        """
        Assign the
        :attr:`~sideshow.db.model.batch.neworder.NewOrderBatch.store_id`
        for a batch.

        This is a "batch action" method which may be called from
        :meth:`create()`.
        """
        store_id = data.get('store_id')
        if not store_id:
            return {'error': "Must provide store_id"}

        batch.store_id = store_id
        return self.get_context_customer(batch)

    def get_context_customer(self, batch):
        """ """
        context = {
            'store_id': batch.store_id,
            'customer_is_known': True,
            'customer_id': None,
            'customer_name': batch.customer_name,
            'phone_number': batch.phone_number,
            'email_address': batch.email_address,
        }

        # customer_id
        use_local = self.batch_handler.use_local_customers()
        if use_local:
            local = batch.local_customer
            if local:
                context['customer_id'] = local.uuid.hex
        else: # use external
            context['customer_id'] = batch.customer_id

        # pending customer
        pending = batch.pending_customer
        if pending:
            context.update({
                'new_customer_first_name': pending.first_name,
                'new_customer_last_name': pending.last_name,
                'new_customer_full_name': pending.full_name,
                'new_customer_phone': pending.phone_number,
                'new_customer_email': pending.email_address,
            })

        # declare customer "not known" only if pending is in use
        if (pending
            and not batch.customer_id and not batch.local_customer
            and batch.customer_name):
            context['customer_is_known'] = False

        return context

    def assign_customer(self, batch, data):
        """
        Assign the true customer account for a batch.

        This calls
        :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.set_customer()`
        for the heavy lifting.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`unassign_customer()`
        * :meth:`set_pending_customer()`
        """
        customer_id = data.get('customer_id')
        if not customer_id:
            return {'error': "Must provide customer_id"}

        self.batch_handler.set_customer(batch, customer_id)
        return self.get_context_customer(batch)

    def unassign_customer(self, batch, data):
        """
        Clear the customer info for a batch.

        This calls
        :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.set_customer()`
        for the heavy lifting.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`assign_customer()`
        * :meth:`set_pending_customer()`
        """
        self.batch_handler.set_customer(batch, None)
        return self.get_context_customer(batch)

    def set_pending_customer(self, batch, data):
        """
        This will set/update the batch pending customer info.

        This calls
        :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.set_customer()`
        for the heavy lifting.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`assign_customer()`
        * :meth:`unassign_customer()`
        """
        self.batch_handler.set_customer(batch, data, user=self.request.user)
        return self.get_context_customer(batch)

    def get_product_info(self, batch, data):
        """
        Fetch data for a specific product.

        Depending on config, this calls one of the following to get
        its primary data:

        * :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.get_product_info_local()`
        * :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.get_product_info_external()`

        It then may supplement the data with additional fields.

        This is a "batch action" method which may be called from
        :meth:`create()`.

        :returns: Dict of product info.
        """
        product_id = data.get('product_id')
        if not product_id:
            return {'error': "Must specify a product ID"}

        session = self.Session()
        use_local = self.batch_handler.use_local_products()
        if use_local:
            data = self.batch_handler.get_product_info_local(session, product_id)
        else:
            data = self.batch_handler.get_product_info_external(session, product_id)

        if 'error' in data:
            return data

        if 'unit_price_reg' in data and 'unit_price_reg_display' not in data:
            data['unit_price_reg_display'] = self.app.render_currency(data['unit_price_reg'])

        if 'unit_price_reg' in data and 'unit_price_quoted' not in data:
            data['unit_price_quoted'] = data['unit_price_reg']

        if 'unit_price_quoted' in data and 'unit_price_quoted_display' not in data:
            data['unit_price_quoted_display'] = self.app.render_currency(data['unit_price_quoted'])

        if 'case_price_quoted' not in data:
            if data.get('unit_price_quoted') is not None and data.get('case_size') is not None:
                data['case_price_quoted'] = data['unit_price_quoted'] * data['case_size']

        if 'case_price_quoted' in data and 'case_price_quoted_display' not in data:
            data['case_price_quoted_display'] = self.app.render_currency(data['case_price_quoted'])

        decimal_fields = [
            'case_size',
            'unit_price_reg',
            'unit_price_quoted',
            'case_price_quoted',
            'default_item_discount',
        ]

        for field in decimal_fields:
            if field in list(data):
                value = data[field]
                if isinstance(value, decimal.Decimal):
                    data[field] = float(value)

        return data

    def get_past_products(self, batch, data):
        """
        Fetch past products for convenient re-ordering.

        This essentially calls
        :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.get_past_products()`
        on the :attr:`batch_handler` and returns the result.

        This is a "batch action" method which may be called from
        :meth:`create()`.

        :returns: List of product info dicts.
        """
        past_products = self.batch_handler.get_past_products(batch)
        return make_json_safe(past_products)

    def add_item(self, batch, data):
        """
        This adds a row to the user's current new order batch.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`update_item()`
        * :meth:`delete_item()`
        """
        kw = {'user': self.request.user}
        if 'discount_percent' in data and self.batch_handler.allow_item_discounts():
            kw['discount_percent'] = data['discount_percent']
        row = self.batch_handler.add_item(batch, data['product_info'],
                                          data['order_qty'], data['order_uom'], **kw)

        return {'batch': self.normalize_batch(batch),
                'row': self.normalize_row(row)}

    def update_item(self, batch, data):
        """
        This updates a row in the user's current new order batch.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`add_item()`
        * :meth:`delete_item()`
        """
        model = self.app.model
        session = self.Session()

        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify row UUID"}

        row = session.get(model.NewOrderBatchRow, uuid)
        if not row:
            return {'error': "Row not found"}

        if row.batch is not batch:
            return {'error': "Row is for wrong batch"}

        kw = {'user': self.request.user}
        if 'discount_percent' in data and self.batch_handler.allow_item_discounts():
            kw['discount_percent'] = data['discount_percent']
        self.batch_handler.update_item(row, data['product_info'],
                                       data['order_qty'], data['order_uom'], **kw)

        return {'batch': self.normalize_batch(batch),
                'row': self.normalize_row(row)}

    def delete_item(self, batch, data):
        """
        This deletes a row from the user's current new order batch.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`add_item()`
        * :meth:`update_item()`
        """
        model = self.app.model
        session = self.app.get_session(batch)

        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a row UUID"}

        row = session.get(model.NewOrderBatchRow, uuid)
        if not row:
            return {'error': "Row not found"}

        if row.batch is not batch:
            return {'error': "Row is for wrong batch"}

        self.batch_handler.do_remove_row(row)
        return {'batch': self.normalize_batch(batch)}

    def submit_order(self, batch, data):
        """
        This submits the user's current new order batch, hence
        executing the batch and creating the true order.

        This is a "batch action" method which may be called from
        :meth:`create()`.  See also:

        * :meth:`start_over()`
        * :meth:`cancel_order()`
        """
        user = self.request.user
        reason = self.batch_handler.why_not_execute(batch, user=user)
        if reason:
            return {'error': reason}

        try:
            order = self.batch_handler.do_execute(batch, user)
        except Exception as error:
            log.warning("failed to execute new order batch: %s", batch,
                        exc_info=True)
            return {'error': self.app.render_error(error)}

        return {
            'next_url': self.get_action_url('view', order),
        }

    def normalize_batch(self, batch):
        """ """
        return {
            'uuid': batch.uuid.hex,
            'total_price': str(batch.total_price or 0),
            'total_price_display': self.app.render_currency(batch.total_price),
            'status_code': batch.status_code,
            'status_text': batch.status_text,
        }

    def normalize_row(self, row):
        """ """
        data = {
            'uuid': row.uuid.hex,
            'sequence': row.sequence,
            'product_id': None,
            'product_scancode': row.product_scancode,
            'product_brand': row.product_brand,
            'product_description': row.product_description,
            'product_size': row.product_size,
            'product_full_description': self.app.make_full_name(row.product_brand,
                                                                row.product_description,
                                                                row.product_size),
            'product_weighed': row.product_weighed,
            'department_id': row.department_id,
            'department_name': row.department_name,
            'special_order': row.special_order,
            'vendor_name': row.vendor_name,
            'vendor_item_code': row.vendor_item_code,
            'case_size': float(row.case_size) if row.case_size is not None else None,
            'order_qty': float(row.order_qty),
            'order_uom': row.order_uom,
            'discount_percent': self.app.render_quantity(row.discount_percent),
            'unit_price_quoted': float(row.unit_price_quoted) if row.unit_price_quoted is not None else None,
            'unit_price_quoted_display': self.app.render_currency(row.unit_price_quoted),
            'case_price_quoted': float(row.case_price_quoted) if row.case_price_quoted is not None else None,
            'case_price_quoted_display': self.app.render_currency(row.case_price_quoted),
            'total_price': float(row.total_price) if row.total_price is not None else None,
            'total_price_display': self.app.render_currency(row.total_price),
            'status_code': row.status_code,
            'status_text': row.status_text,
        }

        use_local = self.batch_handler.use_local_products()

        # product_id
        if use_local:
            if row.local_product:
                data['product_id'] = row.local_product.uuid.hex
        else:
            data['product_id'] = row.product_id

        # vendor_name
        if use_local:
            if row.local_product:
                data['vendor_name'] = row.local_product.vendor_name
        else: # use external
            pass                # TODO
        if not data.get('product_id') and row.pending_product:
            data['vendor_name'] = row.pending_product.vendor_name

        if row.unit_price_reg:
            data['unit_price_reg'] = float(row.unit_price_reg)
            data['unit_price_reg_display'] = self.app.render_currency(row.unit_price_reg)

        if row.unit_price_sale:
            data['unit_price_sale'] = float(row.unit_price_sale)
            data['unit_price_sale_display'] = self.app.render_currency(row.unit_price_sale)
        if row.sale_ends:
            sale_ends = row.sale_ends
            data['sale_ends'] = str(row.sale_ends)
            data['sale_ends_display'] = self.app.render_date(row.sale_ends)

        if row.pending_product:
            pending = row.pending_product
            data['pending_product'] = {
                'uuid': pending.uuid.hex,
                'scancode': pending.scancode,
                'brand_name': pending.brand_name,
                'description': pending.description,
                'size': pending.size,
                'department_id': pending.department_id,
                'department_name': pending.department_name,
                'unit_price_reg': float(pending.unit_price_reg) if pending.unit_price_reg is not None else None,
                'vendor_name': pending.vendor_name,
                'vendor_item_code': pending.vendor_item_code,
                'unit_cost': float(pending.unit_cost) if pending.unit_cost is not None else None,
                'case_size': float(pending.case_size) if pending.case_size is not None else None,
                'notes': pending.notes,
                'special_order': pending.special_order,
            }

        # display text for order qty/uom
        data['order_qty_display'] = self.order_handler.get_order_qty_uom_text(
            row.order_qty, row.order_uom, case_size=row.case_size, html=True)

        return data

    def get_instance_title(self, order):
        """ """
        return f"#{order.order_id} for {order.customer_name}"

    def configure_form(self, f):
        """ """
        super().configure_form(f)
        order = f.model_instance

        # store_id
        if not self.order_handler.expose_store_id():
            f.remove('store_id')

        # local_customer
        if order.customer_id and not order.local_customer:
            f.remove('local_customer')
        else:
            f.set_node('local_customer', LocalCustomerRef(self.request))

        # pending_customer
        if order.customer_id or order.local_customer:
            f.remove('pending_customer')
        else:
            f.set_node('pending_customer', PendingCustomerRef(self.request))

        # total_price
        f.set_node('total_price', WuttaMoney(self.request))

        # created_by
        f.set_node('created_by', UserRef(self.request))
        f.set_readonly('created_by')

    def get_xref_buttons(self, order):
        """ """
        buttons = super().get_xref_buttons(order)
        model = self.app.model
        session = self.Session()

        if self.request.has_perm('neworder_batches.view'):
            batch = session.query(model.NewOrderBatch)\
                           .filter(model.NewOrderBatch.id == order.order_id)\
                           .first()
            if batch:
                url = self.request.route_url('neworder_batches.view', uuid=batch.uuid)
                buttons.append(
                    self.make_button("View the Batch", primary=True, icon_left='eye', url=url))

        return buttons

    def get_row_grid_data(self, order):
        """ """
        model = self.app.model
        session = self.Session()
        return session.query(model.OrderItem)\
                      .filter(model.OrderItem.order == order)

    def configure_row_grid(self, g):
        """ """
        super().configure_row_grid(g)
        # enum = self.app.enum

        # sequence
        g.set_label('sequence', "Seq.", column_only=True)
        g.set_link('sequence')

        # product_scancode
        g.set_link('product_scancode')

        # product_brand
        g.set_link('product_brand')

        # product_description
        g.set_link('product_description')

        # product_size
        g.set_link('product_size')

        # TODO
        # order_uom
        #g.set_renderer('order_uom', self.grid_render_enum, enum=enum.OrderUOM)

        # discount_percent
        g.set_renderer('discount_percent', 'percent')
        g.set_label('discount_percent', "Disc. %", column_only=True)

        # total_price
        g.set_renderer('total_price', g.render_currency)

        # status_code
        g.set_renderer('status_code', self.render_status_code)

        # TODO: upstream should set this automatically
        g.row_class = self.row_grid_row_class

    def row_grid_row_class(self, item, data, i):
        """ """
        variant = self.order_handler.item_status_to_variant(item.status_code)
        if variant:
            return f'has-background-{variant}'

    def render_status_code(self, item, key, value):
        """ """
        enum = self.app.enum
        return enum.ORDER_ITEM_STATUS[value]

    def get_row_action_url_view(self, item, i):
        """ """
        return self.request.route_url('order_items.view', uuid=item.uuid)

    def configure_get_simple_settings(self):
        """ """
        settings = [

            # stores
            {'name': 'sideshow.orders.expose_store_id',
             'type': bool},
            {'name': 'sideshow.orders.default_store_id'},

            # customers
            {'name': 'sideshow.orders.use_local_customers',
             # nb. this is really a bool but we present as string in config UI
             #'type': bool,
             'default': 'true'},

            # products
            {'name': 'sideshow.orders.use_local_products',
             # nb. this is really a bool but we present as string in config UI
             #'type': bool,
             'default': 'true'},
            {'name': 'sideshow.orders.allow_unknown_products',
             'type': bool,
             'default': True},

            # pricing
            {'name': 'sideshow.orders.allow_item_discounts',
             'type': bool},
            {'name': 'sideshow.orders.allow_item_discounts_if_on_sale',
             'type': bool},
            {'name': 'sideshow.orders.default_item_discount',
             'type': float},

            # batches
            {'name': 'wutta.batch.neworder.handler.spec'},
        ]

        # required fields for new product entry
        for field in self.PENDING_PRODUCT_ENTRY_FIELDS:
            setting = {'name': f'sideshow.orders.unknown_product.fields.{field}.required',
                       'type': bool}
            if field == 'description':
                setting['default'] = True
            settings.append(setting)

        return settings

    def configure_get_context(self, **kwargs):
        """ """
        context = super().configure_get_context(**kwargs)

        context['pending_product_fields'] = self.PENDING_PRODUCT_ENTRY_FIELDS

        handlers = self.app.get_batch_handler_specs('neworder')
        handlers = [{'spec': spec} for spec in handlers]
        context['batch_handlers'] = handlers

        context['dept_item_discounts'] = self.get_dept_item_discounts()

        return context

    def configure_gather_settings(self, data, simple_settings=None):
        """ """
        settings = super().configure_gather_settings(data, simple_settings=simple_settings)

        for dept in json.loads(data['dept_item_discounts']):
            deptid = dept['department_id']
            settings.append({'name': f'sideshow.orders.departments.{deptid}.name',
                             'value': dept['department_name']})
            settings.append({'name': f'sideshow.orders.departments.{deptid}.default_item_discount',
                             'value': dept['default_item_discount']})

        return settings

    def configure_remove_settings(self, **kwargs):
        """ """
        model = self.app.model
        session = self.Session()

        super().configure_remove_settings(**kwargs)

        to_delete = session.query(model.Setting)\
                           .filter(sa.or_(
                               model.Setting.name.like('sideshow.orders.departments.%.name'),
                               model.Setting.name.like('sideshow.orders.departments.%.default_item_discount')))\
                           .all()
        for setting in to_delete:
            self.app.delete_setting(session, setting.name)


    @classmethod
    def defaults(cls, config):
        cls._order_defaults(config)
        cls._defaults(config)

    @classmethod
    def _order_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        url_prefix = cls.get_url_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # fix perm group
        config.add_wutta_permission_group(permission_prefix,
                                          model_title_plural,
                                          overwrite=False)

        # extra perm required to create order with unknown/pending product
        config.add_wutta_permission(permission_prefix,
                                    f'{permission_prefix}.create_unknown_product',
                                    f"Create new {model_title} for unknown/pending product")

        # customer autocomplete
        config.add_route(f'{route_prefix}.customer_autocomplete',
                         f'{url_prefix}/customer-autocomplete',
                         request_method='GET')
        config.add_view(cls, attr='customer_autocomplete',
                        route_name=f'{route_prefix}.customer_autocomplete',
                        renderer='json',
                        permission=f'{permission_prefix}.list')

        # product autocomplete
        config.add_route(f'{route_prefix}.product_autocomplete',
                         f'{url_prefix}/product-autocomplete',
                         request_method='GET')
        config.add_view(cls, attr='product_autocomplete',
                        route_name=f'{route_prefix}.product_autocomplete',
                        renderer='json',
                        permission=f'{permission_prefix}.list')


class OrderItemView(MasterView):
    """
    Master view for :class:`~sideshow.db.model.orders.OrderItem`;
    route prefix is ``order_items``.

    Notable URLs provided by this class:

    * ``/order-items/``
    * ``/order-items/XXX``

    This class serves both as a proper master view (for "all" order
    items) as well as a base class for other "workflow" master views,
    each of which auto-filters by order item status:

    * :class:`PlacementView`
    * :class:`ReceivingView`
    * :class:`ContactView`
    * :class:`DeliveryView`

    Note that this does not expose create, edit or delete.  The user
    must perform various other workflow actions to modify the item.

    .. attribute:: order_handler

       Reference to the :term:`order handler` as returned by
       :meth:`get_order_handler()`.
    """
    model_class = OrderItem
    model_title = "Order Item (All)"
    model_title_plural = "Order Items (All)"
    route_prefix = 'order_items'
    url_prefix = '/order-items'
    creatable = False
    editable = False
    deletable = False

    labels = {
        'order_id': "Order ID",
        'store_id': "Store ID",
        'product_id': "Product ID",
        'product_scancode': "Scancode",
        'product_brand': "Brand",
        'product_description': "Description",
        'product_size': "Size",
        'product_weighed': "Sold by Weight",
        'department_id': "Department ID",
        'order_uom': "Order UOM",
        'status_code': "Status",
    }

    grid_columns = [
        'order_id',
        'store_id',
        'customer_name',
        # 'sequence',
        'product_scancode',
        'product_brand',
        'product_description',
        'product_size',
        'department_name',
        'special_order',
        'order_qty',
        'order_uom',
        'total_price',
        'status_code',
    ]

    sort_defaults = ('order_id', 'desc')

    form_fields = [
        'order',
        # 'customer_name',
        'sequence',
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
        'special_order',
        'case_size',
        'unit_cost',
        'unit_price_reg',
        'unit_price_sale',
        'sale_ends',
        'unit_price_quoted',
        'case_price_quoted',
        'order_qty',
        'order_uom',
        'discount_percent',
        'total_price',
        'status_code',
        'paid_amount',
        'payment_transaction_number',
    ]

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        self.order_handler = self.app.get_order_handler()

    def get_fallback_templates(self, template):
        """ """
        templates = super().get_fallback_templates(template)
        templates.insert(0, f'/order-items/{template}.mako')
        return templates

    def get_query(self, session=None):
        """ """
        query = super().get_query(session=session)
        model = self.app.model
        return query.join(model.Order)

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)
        model = self.app.model
        # enum = self.app.enum

        # store_id
        if not self.order_handler.expose_store_id():
            g.remove('store_id')

        # order_id
        g.set_sorter('order_id', model.Order.order_id)
        g.set_renderer('order_id', self.render_order_attr)
        g.set_link('order_id')

        # store_id
        g.set_sorter('store_id', model.Order.store_id)
        g.set_renderer('store_id', self.render_order_attr)

        # customer_name
        g.set_label('customer_name', "Customer", column_only=True)
        g.set_renderer('customer_name', self.render_order_attr)
        g.set_sorter('customer_name', model.Order.customer_name)
        g.set_filter('customer_name', model.Order.customer_name)

        # # sequence
        # g.set_label('sequence', "Seq.", column_only=True)

        # product_scancode
        g.set_link('product_scancode')

        # product_brand
        g.set_link('product_brand')

        # product_description
        g.set_link('product_description')

        # product_size
        g.set_link('product_size')

        # order_uom
        # TODO
        #g.set_renderer('order_uom', self.grid_render_enum, enum=enum.OrderUOM)

        # total_price
        g.set_renderer('total_price', g.render_currency)

        # status_code
        g.set_renderer('status_code', self.render_status_code)

    def render_order_attr(self, item, key, value):
        """ """
        order = item.order
        return getattr(order, key)

    def render_status_code(self, item, key, value):
        """ """
        enum = self.app.enum
        return enum.ORDER_ITEM_STATUS[value]

    def grid_row_class(self, item, data, i):
        """ """
        variant = self.order_handler.item_status_to_variant(item.status_code)
        if variant:
            return f'has-background-{variant}'

    def configure_form(self, f):
        """ """
        super().configure_form(f)
        enum = self.app.enum
        item = f.model_instance

        # order
        f.set_node('order', OrderRef(self.request))

        # local_product
        f.set_node('local_product', LocalProductRef(self.request))

        # pending_product
        if item.product_id or item.local_product:
            f.remove('pending_product')
        else:
            f.set_node('pending_product', PendingProductRef(self.request))

        # order_qty
        f.set_node('order_qty', WuttaQuantity(self.request))

        # order_uom
        f.set_node('order_uom', WuttaDictEnum(self.request, enum.ORDER_UOM))

        # case_size
        f.set_node('case_size', WuttaQuantity(self.request))

        # unit_cost
        f.set_node('unit_cost', WuttaMoney(self.request, scale=4))

        # unit_price_reg
        f.set_node('unit_price_reg', WuttaMoney(self.request))

        # unit_price_quoted
        f.set_node('unit_price_quoted', WuttaMoney(self.request))

        # case_price_quoted
        f.set_node('case_price_quoted', WuttaMoney(self.request))

        # total_price
        f.set_node('total_price', WuttaMoney(self.request))

        # status
        f.set_node('status_code', WuttaDictEnum(self.request, enum.ORDER_ITEM_STATUS))

        # paid_amount
        f.set_node('paid_amount', WuttaMoney(self.request))

    def get_template_context(self, context):
        """ """
        if self.viewing:
            model = self.app.model
            enum = self.app.enum
            route_prefix = self.get_route_prefix()
            item = context['instance']
            form = context['form']

            context['expose_store_id'] = self.order_handler.expose_store_id()

            context['item'] = item
            context['order'] = item.order
            context['order_qty_uom_text'] = self.order_handler.get_order_qty_uom_text(
                item.order_qty, item.order_uom, case_size=item.case_size, html=True)
            context['item_status_variant'] = self.order_handler.item_status_to_variant(item.status_code)

            grid = self.make_grid(key=f'{route_prefix}.view.events',
                                  model_class=model.OrderItemEvent,
                                  data=item.events,
                                  columns=[
                                      'occurred',
                                      'actor',
                                      'type_code',
                                      'note',
                                  ],
                                  labels={
                                      'occurred': "Date/Time",
                                      'actor': "User",
                                      'type_code': "Event Type",
                                  })
            grid.set_renderer('type_code', lambda e, k, v: enum.ORDER_ITEM_EVENT[v])
            grid.set_renderer('note', self.render_event_note)
            if self.request.has_perm('users.view'):
                grid.set_renderer('actor', lambda e, k, v: tags.link_to(
                    e.actor, self.request.route_url('users.view', uuid=e.actor.uuid)))
            form.add_grid_vue_context(grid)
            context['events_grid'] = grid

        return context

    def render_event_note(self, event, key, value):
        """ """
        enum = self.app.enum
        if event.type_code == enum.ORDER_ITEM_EVENT_NOTE_ADDED:
            return HTML.tag('span', class_='has-background-info-light',
                            style='padding: 0.25rem 0.5rem;',
                            c=[value])
        return value

    def get_xref_buttons(self, item):
        """ """
        buttons = super().get_xref_buttons(item)

        if self.request.has_perm('orders.view'):
            url = self.request.route_url('orders.view', uuid=item.order_uuid)
            buttons.append(
                self.make_button("View the Order", url=url,
                                 primary=True, icon_left='eye'))

        return buttons

    def add_note(self):
        """
        View which adds a note to an order item.  This is POST-only;
        will redirect back to the item view.
        """
        enum = self.app.enum
        item = self.get_instance()

        item.add_event(enum.ORDER_ITEM_EVENT_NOTE_ADDED, self.request.user,
                       note=self.request.POST['note'])

        return self.redirect(self.get_action_url('view', item))

    def change_status(self):
        """
        View which changes status for an order item.  This is
        POST-only; will redirect back to the item view.
        """
        model = self.app.model
        enum = self.app.enum
        main_item = self.get_instance()
        session = self.Session()
        redirect = self.redirect(self.get_action_url('view', main_item))

        extra_note = self.request.POST.get('note')

        # validate new status
        new_status_code = int(self.request.POST['new_status'])
        if new_status_code not in enum.ORDER_ITEM_STATUS:
            self.request.session.flash("Invalid status code", 'error')
            return redirect
        new_status_text = enum.ORDER_ITEM_STATUS[new_status_code]

        # locate all items to which new status will be applied
        items = [main_item]
        # uuids = self.request.POST.get('uuids')
        # if uuids:
        #     for uuid in uuids.split(','):
        #         item = Session.get(model.OrderItem, uuid)
        #         if item:
        #             items.append(item)

        # update item(s)
        for item in items:
            if item.status_code != new_status_code:

                # event: change status
                note = 'status changed from "{}" to "{}"'.format(
                    enum.ORDER_ITEM_STATUS[item.status_code],
                    new_status_text)
                item.add_event(enum.ORDER_ITEM_EVENT_STATUS_CHANGE,
                               self.request.user, note=note)

                # event: add note
                if extra_note:
                    item.add_event(enum.ORDER_ITEM_EVENT_NOTE_ADDED,
                                   self.request.user, note=extra_note)

                # new status
                item.status_code = new_status_code

        self.request.session.flash(f"Status has been updated to: {new_status_text}")
        return redirect

    def get_order_items(self, uuids):
        """
        This method provides common logic to fetch a list of order
        items based on a list of UUID keys.  It is used by various
        workflow action methods.

        Note that if no order items are found, this will set a flash
        warning message and raise a redirect back to the index page.

        :param uuids: List (or comma-delimited string) of UUID keys.

        :returns: List of :class:`~sideshow.db.model.orders.OrderItem`
           records.
        """
        model = self.app.model
        session = self.Session()

        if uuids is None:
            uuids = []
        elif isinstance(uuids, str):
            uuids = uuids.split(',')

        items = []
        for uuid in uuids:
            if isinstance(uuid, str):
                uuid = uuid.strip()
            if uuid:
                try:
                    item = session.get(model.OrderItem, uuid)
                except sa.exc.StatementError:
                    pass        # nb. invalid UUID
                else:
                    if item:
                        items.append(item)

        if not items:
            self.request.session.flash("Must specify valid order item(s).", 'warning')
            raise self.redirect(self.get_index_url())

        return items

    @classmethod
    def defaults(cls, config):
        """ """
        cls._order_item_defaults(config)
        cls._defaults(config)

    @classmethod
    def _order_item_defaults(cls, config):
        """ """
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # fix perm group
        config.add_wutta_permission_group(permission_prefix,
                                          model_title_plural,
                                          overwrite=False)

        # add note
        config.add_route(f'{route_prefix}.add_note',
                         f'{instance_url_prefix}/add_note',
                         request_method='POST')
        config.add_view(cls, attr='add_note',
                        route_name=f'{route_prefix}.add_note',
                        renderer='json',
                        permission=f'{permission_prefix}.add_note')
        config.add_wutta_permission(permission_prefix,
                                    f'{permission_prefix}.add_note',
                                    f"Add note for {model_title}")

        # change status
        config.add_route(f'{route_prefix}.change_status',
                         f'{instance_url_prefix}/change-status',
                         request_method='POST')
        config.add_view(cls, attr='change_status',
                        route_name=f'{route_prefix}.change_status',
                        renderer='json',
                        permission=f'{permission_prefix}.change_status')
        config.add_wutta_permission(permission_prefix,
                                    f'{permission_prefix}.change_status',
                                    f"Change status for {model_title}")


class PlacementView(OrderItemView):
    """
    Master view for the "placement" phase of
    :class:`~sideshow.db.model.orders.OrderItem`; route prefix is
    ``placement``.  This is a subclass of :class:`OrderItemView`.

    This class auto-filters so only order items with the following
    status codes are shown:

    * :data:`~sideshow.enum.ORDER_ITEM_STATUS_READY`

    Notable URLs provided by this class:

    * ``/placement/``
    * ``/placement/XXX``
    """
    model_title = "Order Item (Placement)"
    model_title_plural = "Order Items (Placement)"
    route_prefix = 'order_items_placement'
    url_prefix = '/placement'

    grid_columns = [
        'order_id',
        'store_id',
        'customer_name',
        'product_brand',
        'product_description',
        'product_size',
        'department_name',
        'special_order',
        'vendor_name',
        'vendor_item_code',
        'order_qty',
        'order_uom',
        'total_price',
    ]

    filter_defaults = {
        'vendor_name': {'active': True},
    }

    def get_query(self, session=None):
        """ """
        query = super().get_query(session=session)
        model = self.app.model
        enum = self.app.enum
        return query.filter(model.OrderItem.status_code == enum.ORDER_ITEM_STATUS_READY)

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)

        # checkable
        if self.has_perm('process_placement'):
            g.checkable = True

        # tool button: Order Placed
        if self.has_perm('process_placement'):
            button = self.make_button("Order Placed", primary=True,
                                      icon_left='arrow-circle-right',
                                      **{'@click': "$emit('process-placement', checkedRows)",
                                         ':disabled': '!checkedRows.length'})
            g.add_tool(button, key='process_placement')

    def process_placement(self):
        """
        View to process the "placement" step for some order item(s).

        This requires a POST request with data:

        :param item_uuids: Comma-delimited list of
           :class:`~sideshow.db.model.orders.OrderItem` UUID keys.

        :param vendor_name: Optional name of vendor.

        :param po_number: Optional PO number.

        :param note: Optional note text from the user.

        This invokes
        :meth:`~sideshow.orders.OrderHandler.process_placement()` on
        the :attr:`~OrderItemView.order_handler`, then redirects user
        back to the index page.
        """
        items = self.get_order_items(self.request.POST.get('item_uuids', ''))
        vendor_name = self.request.POST.get('vendor_name', '').strip() or None
        po_number = self.request.POST.get('po_number', '').strip() or None
        note = self.request.POST.get('note', '').strip() or None

        self.order_handler.process_placement(items, self.request.user,
                                             vendor_name=vendor_name,
                                             po_number=po_number,
                                             note=note)

        self.request.session.flash(f"{len(items)} Order Items were marked as placed")
        return self.redirect(self.get_index_url())

    @classmethod
    def defaults(cls, config):
        cls._order_item_defaults(config)
        cls._placement_defaults(config)
        cls._defaults(config)

    @classmethod
    def _placement_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        url_prefix = cls.get_url_prefix()
        model_title_plural = cls.get_model_title_plural()

        # process placement
        config.add_wutta_permission(permission_prefix,
                                    f'{permission_prefix}.process_placement',
                                    f"Process placement for {model_title_plural}")
        config.add_route(f'{route_prefix}.process_placement',
                         f'{url_prefix}/process-placement',
                         request_method='POST')
        config.add_view(cls, attr='process_placement',
                        route_name=f'{route_prefix}.process_placement',
                        permission=f'{permission_prefix}.process_placement')


class ReceivingView(OrderItemView):
    """
    Master view for the "receiving" phase of
    :class:`~sideshow.db.model.orders.OrderItem`; route prefix is
    ``receiving``.  This is a subclass of :class:`OrderItemView`.

    This class auto-filters so only order items with the following
    status codes are shown:

    * :data:`~sideshow.enum.ORDER_ITEM_STATUS_PLACED`

    Notable URLs provided by this class:

    * ``/receiving/``
    * ``/receiving/XXX``
    """
    model_title = "Order Item (Receiving)"
    model_title_plural = "Order Items (Receiving)"
    route_prefix = 'order_items_receiving'
    url_prefix = '/receiving'

    grid_columns = [
        'order_id',
        'store_id',
        'customer_name',
        'product_brand',
        'product_description',
        'product_size',
        'department_name',
        'special_order',
        'vendor_name',
        'vendor_item_code',
        'order_qty',
        'order_uom',
        'total_price',
    ]

    filter_defaults = {
        'vendor_name': {'active': True},
    }

    def get_query(self, session=None):
        """ """
        query = super().get_query(session=session)
        model = self.app.model
        enum = self.app.enum
        return query.filter(model.OrderItem.status_code == enum.ORDER_ITEM_STATUS_PLACED)

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)

        # checkable
        if self.has_any_perm('process_receiving', 'process_reorder'):
            g.checkable = True

        # tool button: Received
        if self.has_perm('process_receiving'):
            button = self.make_button("Received", primary=True,
                                      icon_left='arrow-circle-right',
                                      **{'@click': "$emit('process-receiving', checkedRows)",
                                         ':disabled': '!checkedRows.length'})
            g.add_tool(button, key='process_receiving')

        # tool button: Re-Order
        if self.has_perm('process_reorder'):
            button = self.make_button("Re-Order",
                                      icon_left='redo',
                                      **{'@click': "$emit('process-reorder', checkedRows)",
                                         ':disabled': '!checkedRows.length'})
            g.add_tool(button, key='process_reorder')

    def process_receiving(self):
        """
        View to process the "receiving" step for some order item(s).

        This requires a POST request with data:

        :param item_uuids: Comma-delimited list of
           :class:`~sideshow.db.model.orders.OrderItem` UUID keys.

        :param vendor_name: Optional name of vendor.

        :param invoice_number: Optional invoice number.

        :param po_number: Optional PO number.

        :param note: Optional note text from the user.

        This invokes
        :meth:`~sideshow.orders.OrderHandler.process_receiving()` on
        the :attr:`~OrderItemView.order_handler`, then redirects user
        back to the index page.
        """
        items = self.get_order_items(self.request.POST.get('item_uuids', ''))
        vendor_name = self.request.POST.get('vendor_name', '').strip() or None
        invoice_number = self.request.POST.get('invoice_number', '').strip() or None
        po_number = self.request.POST.get('po_number', '').strip() or None
        note = self.request.POST.get('note', '').strip() or None

        self.order_handler.process_receiving(items, self.request.user,
                                             vendor_name=vendor_name,
                                             invoice_number=invoice_number,
                                             po_number=po_number,
                                             note=note)

        self.request.session.flash(f"{len(items)} Order Items were marked as received")
        return self.redirect(self.get_index_url())

    def process_reorder(self):
        """
        View to process the "reorder" step for some order item(s).

        This requires a POST request with data:

        :param item_uuids: Comma-delimited list of
           :class:`~sideshow.db.model.orders.OrderItem` UUID keys.

        :param note: Optional note text from the user.

        This invokes
        :meth:`~sideshow.orders.OrderHandler.process_reorder()` on the
        :attr:`~OrderItemView.order_handler`, then redirects user back
        to the index page.
        """
        items = self.get_order_items(self.request.POST.get('item_uuids', ''))
        note = self.request.POST.get('note', '').strip() or None

        self.order_handler.process_reorder(items, self.request.user, note=note)

        self.request.session.flash(f"{len(items)} Order Items were marked as ready for placement")
        return self.redirect(self.get_index_url())

    @classmethod
    def defaults(cls, config):
        cls._order_item_defaults(config)
        cls._receiving_defaults(config)
        cls._defaults(config)

    @classmethod
    def _receiving_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        url_prefix = cls.get_url_prefix()
        model_title_plural = cls.get_model_title_plural()

        # process receiving
        config.add_wutta_permission(permission_prefix,
                                    f'{permission_prefix}.process_receiving',
                                    f"Process receiving for {model_title_plural}")
        config.add_route(f'{route_prefix}.process_receiving',
                         f'{url_prefix}/process-receiving',
                         request_method='POST')
        config.add_view(cls, attr='process_receiving',
                        route_name=f'{route_prefix}.process_receiving',
                        permission=f'{permission_prefix}.process_receiving')

        # process reorder
        config.add_wutta_permission(permission_prefix,
                                    f'{permission_prefix}.process_reorder',
                                    f"Process re-order for {model_title_plural}")
        config.add_route(f'{route_prefix}.process_reorder',
                         f'{url_prefix}/process-reorder',
                         request_method='POST')
        config.add_view(cls, attr='process_reorder',
                        route_name=f'{route_prefix}.process_reorder',
                        permission=f'{permission_prefix}.process_reorder')


class ContactView(OrderItemView):
    """
    Master view for the "contact" phase of
    :class:`~sideshow.db.model.orders.OrderItem`; route prefix is
    ``contact``.  This is a subclass of :class:`OrderItemView`.

    This class auto-filters so only order items with the following
    status codes are shown:

    * :data:`~sideshow.enum.ORDER_ITEM_STATUS_RECEIVED`
    * :data:`~sideshow.enum.ORDER_ITEM_STATUS_CONTACT_FAILED`

    Notable URLs provided by this class:

    * ``/contact/``
    * ``/contact/XXX``
    """
    model_title = "Order Item (Contact)"
    model_title_plural = "Order Items (Contact)"
    route_prefix = 'order_items_contact'
    url_prefix = '/contact'

    def get_query(self, session=None):
        """ """
        query = super().get_query(session=session)
        model = self.app.model
        enum = self.app.enum
        return query.filter(model.OrderItem.status_code.in_((
            enum.ORDER_ITEM_STATUS_RECEIVED,
            enum.ORDER_ITEM_STATUS_CONTACT_FAILED)))

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)

        # checkable
        if self.has_perm('process_contact'):
            g.checkable = True

        # tool button: Contact Success
        if self.has_perm('process_contact'):
            button = self.make_button("Contact Success", primary=True,
                                      icon_left='phone',
                                      **{'@click': "$emit('process-contact-success', checkedRows)",
                                         ':disabled': '!checkedRows.length'})
            g.add_tool(button, key='process_contact_success')

        # tool button: Contact Failure
        if self.has_perm('process_contact'):
            button = self.make_button("Contact Failure", variant='is-warning',
                                      icon_left='phone',
                                      **{'@click': "$emit('process-contact-failure', checkedRows)",
                                         ':disabled': '!checkedRows.length'})
            g.add_tool(button, key='process_contact_failure')

    def process_contact_success(self):
        """
        View to process the "contact success" step for some order
        item(s).

        This requires a POST request with data:

        :param item_uuids: Comma-delimited list of
           :class:`~sideshow.db.model.orders.OrderItem` UUID keys.

        :param note: Optional note text from the user.

        This invokes
        :meth:`~sideshow.orders.OrderHandler.process_contact_success()`
        on the :attr:`~OrderItemView.order_handler`, then redirects
        user back to the index page.
        """
        items = self.get_order_items(self.request.POST.get('item_uuids', ''))
        note = self.request.POST.get('note', '').strip() or None

        self.order_handler.process_contact_success(items, self.request.user, note=note)

        self.request.session.flash(f"{len(items)} Order Items were marked as contacted")
        return self.redirect(self.get_index_url())

    def process_contact_failure(self):
        """
        View to process the "contact failure" step for some order
        item(s).

        This requires a POST request with data:

        :param item_uuids: Comma-delimited list of
           :class:`~sideshow.db.model.orders.OrderItem` UUID keys.

        :param note: Optional note text from the user.

        This invokes
        :meth:`~sideshow.orders.OrderHandler.process_contact_failure()`
        on the :attr:`~OrderItemView.order_handler`, then redirects
        user back to the index page.
        """
        items = self.get_order_items(self.request.POST.get('item_uuids', ''))
        note = self.request.POST.get('note', '').strip() or None

        self.order_handler.process_contact_failure(items, self.request.user, note=note)

        self.request.session.flash(f"{len(items)} Order Items were marked as contact failed")
        return self.redirect(self.get_index_url())

    @classmethod
    def defaults(cls, config):
        cls._order_item_defaults(config)
        cls._contact_defaults(config)
        cls._defaults(config)

    @classmethod
    def _contact_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        url_prefix = cls.get_url_prefix()
        model_title_plural = cls.get_model_title_plural()

        # common perm for processing contact success + failure
        config.add_wutta_permission(permission_prefix,
                                    f'{permission_prefix}.process_contact',
                                    f"Process contact success/failure for {model_title_plural}")

        # process contact success
        config.add_route(f'{route_prefix}.process_contact_success',
                         f'{url_prefix}/process-contact-success',
                         request_method='POST')
        config.add_view(cls, attr='process_contact_success',
                        route_name=f'{route_prefix}.process_contact_success',
                        permission=f'{permission_prefix}.process_contact')

        # process contact failure
        config.add_route(f'{route_prefix}.process_contact_failure',
                         f'{url_prefix}/process-contact-failure',
                         request_method='POST')
        config.add_view(cls, attr='process_contact_failure',
                        route_name=f'{route_prefix}.process_contact_failure',
                        permission=f'{permission_prefix}.process_contact')


class DeliveryView(OrderItemView):
    """
    Master view for the "delivery" phase of
    :class:`~sideshow.db.model.orders.OrderItem`; route prefix is
    ``delivery``.  This is a subclass of :class:`OrderItemView`.

    This class auto-filters so only order items with the following
    status codes are shown:

    * :data:`~sideshow.enum.ORDER_ITEM_STATUS_RECEIVED`
    * :data:`~sideshow.enum.ORDER_ITEM_STATUS_CONTACTED`

    Notable URLs provided by this class:

    * ``/delivery/``
    * ``/delivery/XXX``
    """
    model_title = "Order Item (Delivery)"
    model_title_plural = "Order Items (Delivery)"
    route_prefix = 'order_items_delivery'
    url_prefix = '/delivery'

    def get_query(self, session=None):
        """ """
        query = super().get_query(session=session)
        model = self.app.model
        enum = self.app.enum
        return query.filter(model.OrderItem.status_code.in_((
            enum.ORDER_ITEM_STATUS_RECEIVED,
            enum.ORDER_ITEM_STATUS_CONTACTED)))

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)

        # checkable
        if self.has_any_perm('process_delivery', 'process_restock'):
            g.checkable = True

        # tool button: Delivered
        if self.has_perm('process_delivery'):
            button = self.make_button("Delivered", primary=True,
                                      icon_left='check',
                                      **{'@click': "$emit('process-delivery', checkedRows)",
                                         ':disabled': '!checkedRows.length'})
            g.add_tool(button, key='process_delivery')

        # tool button: Restocked
        if self.has_perm('process_restock'):
            button = self.make_button("Restocked",
                                      icon_left='redo',
                                      **{'@click': "$emit('process-restock', checkedRows)",
                                         ':disabled': '!checkedRows.length'})
            g.add_tool(button, key='process_restock')

    def process_delivery(self):
        """
        View to process the "delivery" step for some order item(s).

        This requires a POST request with data:

        :param item_uuids: Comma-delimited list of
           :class:`~sideshow.db.model.orders.OrderItem` UUID keys.

        :param note: Optional note text from the user.

        This invokes
        :meth:`~sideshow.orders.OrderHandler.process_delivery()` on
        the :attr:`~OrderItemView.order_handler`, then redirects user
        back to the index page.
        """
        items = self.get_order_items(self.request.POST.get('item_uuids', ''))
        note = self.request.POST.get('note', '').strip() or None

        self.order_handler.process_delivery(items, self.request.user, note=note)

        self.request.session.flash(f"{len(items)} Order Items were marked as delivered")
        return self.redirect(self.get_index_url())

    def process_restock(self):
        """
        View to process the "restock" step for some order item(s).

        This requires a POST request with data:

        :param item_uuids: Comma-delimited list of
           :class:`~sideshow.db.model.orders.OrderItem` UUID keys.

        :param note: Optional note text from the user.

        This invokes
        :meth:`~sideshow.orders.OrderHandler.process_restock()` on the
        :attr:`~OrderItemView.order_handler`, then redirects user back
        to the index page.
        """
        items = self.get_order_items(self.request.POST.get('item_uuids', ''))
        note = self.request.POST.get('note', '').strip() or None

        self.order_handler.process_restock(items, self.request.user, note=note)

        self.request.session.flash(f"{len(items)} Order Items were marked as restocked")
        return self.redirect(self.get_index_url())

    @classmethod
    def defaults(cls, config):
        cls._order_item_defaults(config)
        cls._delivery_defaults(config)
        cls._defaults(config)

    @classmethod
    def _delivery_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        url_prefix = cls.get_url_prefix()
        model_title_plural = cls.get_model_title_plural()

        # process delivery
        config.add_wutta_permission(permission_prefix,
                                    f'{permission_prefix}.process_delivery',
                                    f"Process delivery for {model_title_plural}")
        config.add_route(f'{route_prefix}.process_delivery',
                         f'{url_prefix}/process-delivery',
                         request_method='POST')
        config.add_view(cls, attr='process_delivery',
                        route_name=f'{route_prefix}.process_delivery',
                        permission=f'{permission_prefix}.process_delivery')

        # process restock
        config.add_wutta_permission(permission_prefix,
                                    f'{permission_prefix}.process_restock',
                                    f"Process restock for {model_title_plural}")
        config.add_route(f'{route_prefix}.process_restock',
                         f'{url_prefix}/process-restock',
                         request_method='POST')
        config.add_view(cls, attr='process_restock',
                        route_name=f'{route_prefix}.process_restock',
                        permission=f'{permission_prefix}.process_restock')


def defaults(config, **kwargs):
    base = globals()

    OrderView = kwargs.get('OrderView', base['OrderView'])
    OrderView.defaults(config)

    OrderItemView = kwargs.get('OrderItemView', base['OrderItemView'])
    OrderItemView.defaults(config)

    PlacementView = kwargs.get('PlacementView', base['PlacementView'])
    PlacementView.defaults(config)

    ReceivingView = kwargs.get('ReceivingView', base['ReceivingView'])
    ReceivingView.defaults(config)

    ContactView = kwargs.get('ContactView', base['ContactView'])
    ContactView.defaults(config)

    DeliveryView = kwargs.get('DeliveryView', base['DeliveryView'])
    DeliveryView.defaults(config)


def includeme(config):
    defaults(config)
