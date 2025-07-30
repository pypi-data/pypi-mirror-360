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
Views for Customers
"""

from wuttaweb.views import MasterView
from wuttaweb.forms.schema import UserRef, WuttaEnum

from sideshow.db.model import LocalCustomer, PendingCustomer


class LocalCustomerView(MasterView):
    """
    Master view for
    :class:`~sideshow.db.model.customers.LocalCustomer`; route prefix
    is ``local_customers``.

    Notable URLs provided by this class:

    * ``/local/customers/``
    * ``/local/customers/new``
    * ``/local/customers/XXX``
    * ``/local/customers/XXX/edit``
    * ``/local/customers/XXX/delete``
    """
    model_class = LocalCustomer
    model_title = "Local Customer"
    route_prefix = 'local_customers'
    url_prefix = '/local/customers'

    labels = {
        'external_id': "External ID",
    }

    grid_columns = [
        'external_id',
        'full_name',
        'first_name',
        'last_name',
        'phone_number',
        'email_address',
    ]

    sort_defaults = 'full_name'

    form_fields = [
        'external_id',
        'full_name',
        'first_name',
        'last_name',
        'phone_number',
        'email_address',
        'orders',
        'new_order_batches',
    ]

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)

        # links
        g.set_link('full_name')
        g.set_link('first_name')
        g.set_link('last_name')
        g.set_link('phone_number')
        g.set_link('email_address')

    def configure_form(self, f):
        """ """
        super().configure_form(f)
        customer = f.model_instance

        # external_id
        if self.creating:
            f.remove('external_id')
        else:
            f.set_readonly('external_id')

        # full_name
        if self.creating or self.editing:
            f.remove('full_name')

        # orders
        if self.creating or self.editing:
            f.remove('orders')
        else:
            f.set_grid('orders', self.make_orders_grid(customer))

        # new_order_batches
        if self.creating or self.editing:
            f.remove('new_order_batches')
        else:
            f.set_grid('new_order_batches', self.make_new_order_batches_grid(customer))

    def make_orders_grid(self, customer):
        """
        Make and return the grid for the Orders field.
        """
        model = self.app.model
        route_prefix = self.get_route_prefix()

        grid = self.make_grid(key=f'{route_prefix}.view.orders',
                              model_class=model.Order,
                              data=customer.orders,
                              columns=[
                                  'order_id',
                                  'total_price',
                                  'created',
                                  'created_by',
                              ],
                              labels={
                                  'order_id': "Order ID",
                              })
        grid.set_renderer('total_price', grid.render_currency)

        if self.request.has_perm('orders.view'):
            url = lambda order, i: self.request.route_url('orders.view', uuid=order.uuid)
            grid.add_action('view', icon='eye', url=url)
            grid.set_link('order_id')

        return grid

    def make_new_order_batches_grid(self, customer):
        """
        Make and return the grid for the New Order Batches field.
        """
        model = self.app.model
        route_prefix = self.get_route_prefix()

        grid = self.make_grid(key=f'{route_prefix}.view.new_order_batches',
                              model_class=model.NewOrderBatch,
                              data=customer.new_order_batches,
                              columns=[
                                  'id',
                                  'total_price',
                                  'created',
                                  'created_by',
                                  'executed',
                              ],
                              labels={
                                  'id': "Batch ID",
                              },
                              renderers={
                                  'id': 'batch_id',
                                  'total_price': 'currency',
                              })

        if self.request.has_perm('neworder_batches.view'):
            url = lambda batch, i: self.request.route_url('neworder_batches.view', uuid=batch.uuid)
            grid.add_action('view', icon='eye', url=url)
            grid.set_link('id')

        return grid

    def objectify(self, form):
        """ """
        enum = self.app.enum
        customer = super().objectify(form)

        customer.full_name = self.app.make_full_name(customer.first_name,
                                                     customer.last_name)

        return customer


class PendingCustomerView(MasterView):
    """
    Master view for
    :class:`~sideshow.db.model.customers.PendingCustomer`; route
    prefix is ``pending_customers``.

    Notable URLs provided by this class:

    * ``/pending/customers/``
    * ``/pending/customers/new``
    * ``/pending/customers/XXX``
    * ``/pending/customers/XXX/edit``
    * ``/pending/customers/XXX/delete``
    """
    model_class = PendingCustomer
    model_title = "Pending Customer"
    route_prefix = 'pending_customers'
    url_prefix = '/pending/customers'

    labels = {
        'customer_id': "Customer ID",
    }

    grid_columns = [
        'full_name',
        'first_name',
        'last_name',
        'phone_number',
        'email_address',
        'customer_id',
        'status',
        'created',
        'created_by',
    ]

    sort_defaults = 'full_name'

    form_fields = [
        'customer_id',
        'full_name',
        'first_name',
        'last_name',
        'phone_number',
        'email_address',
        'status',
        'created',
        'created_by',
        'orders',
        'new_order_batches',
    ]

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)
        enum = self.app.enum

        # status
        g.set_renderer('status', self.grid_render_enum, enum=enum.PendingCustomerStatus)

        # links
        g.set_link('full_name')
        g.set_link('first_name')
        g.set_link('last_name')
        g.set_link('phone_number')
        g.set_link('email_address')

    def configure_form(self, f):
        """ """
        super().configure_form(f)
        enum = self.app.enum
        customer = f.model_instance

        # customer_id
        if self.creating:
            f.remove('customer_id')
        else:
            f.set_readonly('customer_id')

        # status
        if self.creating:
            f.remove('status')
        else:
            f.set_node('status', WuttaEnum(self.request, enum.PendingCustomerStatus))
            f.set_readonly('status')

        # created
        if self.creating:
            f.remove('created')
        else:
            f.set_readonly('created')

        # created_by
        if self.creating:
            f.remove('created_by')
        else:
            f.set_node('created_by', UserRef(self.request))
            f.set_readonly('created_by')

        # orders
        if self.creating or self.editing:
            f.remove('orders')
        else:
            f.set_grid('orders', self.make_orders_grid(customer))

        # new_order_batches
        if self.creating or self.editing:
            f.remove('new_order_batches')
        else:
            f.set_grid('new_order_batches', self.make_new_order_batches_grid(customer))

    def make_orders_grid(self, customer):
        """
        Make and return the grid for the Orders field.
        """
        model = self.app.model
        route_prefix = self.get_route_prefix()

        grid = self.make_grid(key=f'{route_prefix}.view.orders',
                              model_class=model.Order,
                              data=customer.orders,
                              columns=[
                                  'order_id',
                                  'total_price',
                                  'created',
                                  'created_by',
                              ],
                              labels={
                                  'order_id': "Order ID",
                              })
        grid.set_renderer('total_price', grid.render_currency)

        if self.request.has_perm('orders.view'):
            url = lambda order, i: self.request.route_url('orders.view', uuid=order.uuid)
            grid.add_action('view', icon='eye', url=url)
            grid.set_link('order_id')

        return grid

    def make_new_order_batches_grid(self, customer):
        """
        Make and return the grid for the New Order Batches field.
        """
        model = self.app.model
        route_prefix = self.get_route_prefix()

        grid = self.make_grid(key=f'{route_prefix}.view.new_order_batches',
                              model_class=model.NewOrderBatch,
                              data=customer.new_order_batches,
                              columns=[
                                  'id',
                                  'total_price',
                                  'created',
                                  'created_by',
                                  'executed',
                              ],
                              labels={
                                  'id': "Batch ID",
                              },
                              renderers={
                                  'id': 'batch_id',
                                  'total_price': 'currency',
                              })

        if self.request.has_perm('neworder_batches.view'):
            url = lambda batch, i: self.request.route_url('neworder_batches.view', uuid=batch.uuid)
            grid.add_action('view', icon='eye', url=url)
            grid.set_link('id')

        return grid

    def objectify(self, form):
        """ """
        enum = self.app.enum
        customer = super().objectify(form)

        if self.creating:
            customer.status = enum.PendingCustomerStatus.PENDING
            customer.created_by = self.request.user

        return customer

    def delete_instance(self, customer):
        """ """
        model_title = self.get_model_title()

        # avoid deleting if still referenced by order(s)
        for order in customer.orders:
            self.request.session.flash(f"Cannot delete {model_title} still attached "
                                       "to Order(s)", 'warning')
            raise self.redirect(self.get_action_url('view', customer))

        # avoid deleting if still referenced by new order batch(es)
        for batch in customer.new_order_batches:
            if not batch.executed:
                self.request.session.flash(f"Cannot delete {model_title} still attached "
                                           "to New Order Batch(es)", 'warning')
                raise self.redirect(self.get_action_url('view', customer))

        # go ahead and delete per usual
        super().delete_instance(customer)


def defaults(config, **kwargs):
    base = globals()

    LocalCustomerView = kwargs.get('LocalCustomerView', base['LocalCustomerView'])
    LocalCustomerView.defaults(config)

    PendingCustomerView = kwargs.get('PendingCustomerView', base['PendingCustomerView'])
    PendingCustomerView.defaults(config)


def includeme(config):
    defaults(config)
