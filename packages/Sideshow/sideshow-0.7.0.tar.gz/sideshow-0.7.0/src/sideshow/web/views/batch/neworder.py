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
Views for New Order Batch
"""

from wuttaweb.views.batch import BatchMasterView
from wuttaweb.forms.schema import WuttaMoney

from sideshow.db.model import NewOrderBatch
from sideshow.batch.neworder import NewOrderBatchHandler
from sideshow.web.forms.schema import LocalCustomerRef, PendingCustomerRef


class NewOrderBatchView(BatchMasterView):
    """
    Master view for :class:`~sideshow.db.model.batch.neworder.NewOrderBatch`.

    Route prefix is ``neworder_batches``.

    Notable URLs provided by this class:

    * ``/batch/neworder/``
    * ``/batch/neworder/XXX``
    * ``/batch/neworder/XXX/delete``

    The purpose of this class is to expose "raw" batch data, e.g. for
    troubleshooting purposes by the admin.  Ideally it is not very
    useful.

    Note that the "create" and "edit" views are not exposed here,
    since those should be handled by
    :class:`~sideshow.web.views.orders.OrderView` instead.
    """
    model_class = NewOrderBatch
    model_title = "New Order Batch"
    model_title_plural = "New Order Batches"
    route_prefix = 'neworder_batches'
    url_prefix = '/batch/neworder'
    creatable = False
    editable = False

    labels = {
        'store_id': "Store ID",
        'customer_id': "Customer ID",
    }

    grid_columns = [
        'id',
        'store_id',
        'customer_id',
        'customer_name',
        'phone_number',
        'email_address',
        'total_price',
        'row_count',
        'created',
        'created_by',
        'executed',
    ]

    filter_defaults = {
        'executed': {'active': True, 'verb': 'is_null'},
    }

    form_fields = [
        'id',
        'store_id',
        'customer_id',
        'local_customer',
        'pending_customer',
        'customer_name',
        'phone_number',
        'email_address',
        'total_price',
        'row_count',
        'status_code',
        'created',
        'created_by',
        'executed',
        'executed_by',
    ]

    row_labels = {
        'product_scancode': "Scancode",
        'product_brand': "Brand",
        'product_description': "Description",
        'product_size': "Size",
        'order_uom': "Order UOM",
    }

    row_grid_columns = [
        'sequence',
        'product_scancode',
        'product_brand',
        'product_description',
        'product_size',
        'special_order',
        'unit_price_quoted',
        'case_size',
        'case_price_quoted',
        'order_qty',
        'order_uom',
        'discount_percent',
        'total_price',
        'status_code',
    ]

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        self.order_handler = self.app.get_order_handler()

    def get_batch_handler(self):
        """ """
        # TODO: call self.app.get_batch_handler()
        return NewOrderBatchHandler(self.config)

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)

        # store_id
        if not self.order_handler.expose_store_id():
            g.remove('store_id')

        # total_price
        g.set_renderer('total_price', 'currency')

    def configure_form(self, f):
        """ """
        super().configure_form(f)

        # store_id
        if not self.order_handler.expose_store_id():
            f.remove('store_id')

        # local_customer
        f.set_node('local_customer', LocalCustomerRef(self.request))

        # pending_customer
        f.set_node('pending_customer', PendingCustomerRef(self.request))

        # total_price
        f.set_node('total_price', WuttaMoney(self.request))

    def configure_row_grid(self, g):
        """ """
        super().configure_row_grid(g)
        enum = self.app.enum

        # TODO
        # order_uom
        #g.set_renderer('order_uom', self.grid_render_enum, enum=enum.ORDER_UOM)

        # unit_price_quoted
        g.set_label('unit_price_quoted', "Unit Price", column_only=True)
        g.set_renderer('unit_price_quoted', 'currency')

        # case_price_quoted
        g.set_label('case_price_quoted', "Case Price", column_only=True)
        g.set_renderer('case_price_quoted', 'currency')

        # discount_percent
        g.set_renderer('discount_percent', 'percent')
        g.set_label('discount_percent', "Disc. %", column_only=True)

        # total_price
        g.set_renderer('total_price', 'currency')

    def get_xref_buttons(self, batch):
        """
        Adds "View this Order" button, if batch has been executed and
        a corresponding :class:`~sideshow.db.model.orders.Order` can
        be located.
        """
        buttons = super().get_xref_buttons(batch)
        model = self.app.model
        session = self.Session()

        if batch.executed and self.request.has_perm('orders.view'):
            order = session.query(model.Order)\
                           .filter(model.Order.order_id == batch.id)\
                           .first()
            if order:
                url = self.request.route_url('orders.view', uuid=order.uuid)
                buttons.append(
                    self.make_button("View the Order", primary=True, icon_left='eye', url=url))

        return buttons


def defaults(config, **kwargs):
    base = globals()

    NewOrderBatchView = kwargs.get('NewOrderBatchView', base['NewOrderBatchView'])
    NewOrderBatchView.defaults(config)


def includeme(config):
    defaults(config)
