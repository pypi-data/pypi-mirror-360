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
Form schema types
"""

from wuttaweb.forms.schema import ObjectRef


class OrderRef(ObjectRef):
    """
    Schema type for an :class:`~sideshow.db.model.orders.Order`
    reference field.

    This is a subclass of
    :class:`~wuttaweb:wuttaweb.forms.schema.ObjectRef`.
    """

    @property
    def model_class(self):
        """ """
        model = self.app.model
        return model.Order

    def sort_query(self, query):
        """ """
        return query.order_by(self.model_class.order_id)

    def get_object_url(self, order):
        """ """
        return self.request.route_url('orders.view', uuid=order.uuid)


class LocalCustomerRef(ObjectRef):
    """
    Schema type for a
    :class:`~sideshow.db.model.customers.LocalCustomer` reference
    field.

    This is a subclass of
    :class:`~wuttaweb:wuttaweb.forms.schema.ObjectRef`.
    """

    @property
    def model_class(self):
        """ """
        model = self.app.model
        return model.LocalCustomer

    def sort_query(self, query):
        """ """
        return query.order_by(self.model_class.full_name)

    def get_object_url(self, customer):
        """ """
        return self.request.route_url('local_customers.view', uuid=customer.uuid)


class PendingCustomerRef(ObjectRef):
    """
    Schema type for a
    :class:`~sideshow.db.model.customers.PendingCustomer` reference
    field.

    This is a subclass of
    :class:`~wuttaweb:wuttaweb.forms.schema.ObjectRef`.
    """

    @property
    def model_class(self):
        """ """
        model = self.app.model
        return model.PendingCustomer

    def sort_query(self, query):
        """ """
        return query.order_by(self.model_class.full_name)

    def get_object_url(self, customer):
        """ """
        return self.request.route_url('pending_customers.view', uuid=customer.uuid)


class LocalProductRef(ObjectRef):
    """
    Schema type for a
    :class:`~sideshow.db.model.products.LocalProduct` reference field.

    This is a subclass of
    :class:`~wuttaweb:wuttaweb.forms.schema.ObjectRef`.
    """

    @property
    def model_class(self):
        """ """
        model = self.app.model
        return model.LocalProduct

    def sort_query(self, query):
        """ """
        return query.order_by(self.model_class.scancode)

    def get_object_url(self, product):
        """ """
        return self.request.route_url('local_products.view', uuid=product.uuid)


class PendingProductRef(ObjectRef):
    """
    Schema type for a
    :class:`~sideshow.db.model.products.PendingProduct` reference
    field.

    This is a subclass of
    :class:`~wuttaweb:wuttaweb.forms.schema.ObjectRef`.
    """

    @property
    def model_class(self):
        """ """
        model = self.app.model
        return model.PendingProduct

    def sort_query(self, query):
        """ """
        return query.order_by(self.model_class.scancode)

    def get_object_url(self, product):
        """ """
        return self.request.route_url('pending_products.view', uuid=product.uuid)
