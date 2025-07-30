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
Sideshow Menu
"""

from wuttaweb import menus as base


class SideshowMenuHandler(base.MenuHandler):
    """
    Sideshow menu handler
    """

    def make_menus(self, request, **kwargs):
        """ """
        return [
            self.make_orders_menu(request),
            self.make_customers_menu(request),
            self.make_products_menu(request),
            self.make_batch_menu(request),
            self.make_other_menu(request),
            self.make_admin_menu(request),
        ]

    def make_orders_menu(self, request, **kwargs):
        """
        Generate the Orders menu.
        """
        return {
            'title': "Orders",
            'type': 'menu',
            'items': [
                {
                    'title': "Create New Order",
                    'route': 'orders.create',
                    'perm': 'orders.create',
                },
                {'type': 'sep'},
                {
                    'title': "Placement",
                    'route': 'order_items_placement',
                    'perm': 'order_items_placement.list',
                },
                {
                    'title': "Receiving",
                    'route': 'order_items_receiving',
                    'perm': 'order_items_receiving.list',
                },
                {
                    'title': "Contact",
                    'route': 'order_items_contact',
                    'perm': 'order_items_contact.list',
                },
                {
                    'title': "Delivery",
                    'route': 'order_items_delivery',
                    'perm': 'order_items_delivery.list',
                },
                {'type': 'sep'},
                {
                    'title': "All Order Items",
                    'route': 'order_items',
                    'perm': 'order_items.list',
                },
                {
                    'title': "All Orders",
                    'route': 'orders',
                    'perm': 'orders.list',
                },
            ],
        }

    def make_customers_menu(self, request, **kwargs):
        """
        Generate the Customers menu.
        """
        return {
            'title': "Customers",
            'type': 'menu',
            'items': [
                {
                    'title': "Local Customers",
                    'route': 'local_customers',
                    'perm': 'local_customers.list',
                },
                {
                    'title': "Pending Customers",
                    'route': 'pending_customers',
                    'perm': 'pending_customers.list',
                },
            ],
        }

    def make_products_menu(self, request, **kwargs):
        """
        Generate the Products menu.
        """
        return {
            'title': "Products",
            'type': 'menu',
            'items': [
                {
                    'title': "Local Products",
                    'route': 'local_products',
                    'perm': 'local_products.list',
                },
                {
                    'title': "Pending Products",
                    'route': 'pending_products',
                    'perm': 'pending_products.list',
                },
            ],
        }

    def make_batch_menu(self, request, **kwargs):
        """
        Generate the Batch menu.
        """
        return {
            'title': "Batches",
            'type': 'menu',
            'items': [
                {
                    'title': "New Orders",
                    'route': 'neworder_batches',
                    'perm': 'neworder_batches.list',
                },
            ],
        }

    def make_other_menu(self, request, **kwargs):
        """
        Generate the "Other" menu.
        """
        return {
            'title': "Other",
            'type': 'menu',
            'items': [],
        }

    def make_admin_menu(self, request, **kwargs):
        """ """
        kwargs['include_people'] = True
        menu = super().make_admin_menu(request, **kwargs)

        menu['items'].insert(0, {
            'title': "Stores",
            'route': 'stores',
            'perm': 'stores.list',
        })

        return menu
