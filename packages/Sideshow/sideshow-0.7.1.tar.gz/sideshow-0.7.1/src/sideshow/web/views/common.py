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
Common Views
"""

from wuttaweb.views import common as base


class CommonView(base.CommonView):
    """
    Sideshow overrides for common view logic.
    """

    def setup_enhance_admin_user(self, user):
        """
        Adds the "Order Admin" role with all relevant permissions.

        The default logic for creating a new user will create the
        "Site Admin" role with permissions for app and user account
        maintenance etc.  Sideshow needs another role for the order
        maintenance.
        """
        model = self.app.model
        session = self.app.get_session(user)
        auth = self.app.get_auth_handler()

        admin = model.Role(name="Order Admin")
        admin.notes = ("this role was auto-created; "
                       "you can change or remove it as needed.")

        session.add(admin)
        user.roles.append(admin)

        order_admin_perms = [
            'local_customers.list',
            'local_customers.view',
            'local_products.list',
            'local_products.view',
            'neworder_batches.list',
            'neworder_batches.view',
            'order_items.add_note',
            'order_items.change_status',
            'order_items.list',
            'order_items.view',
            'order_items_contact.add_note',
            'order_items_contact.change_status',
            'order_items_contact.list',
            'order_items_contact.process_contact',
            'order_items_contact.view',
            'order_items_delivery.add_note',
            'order_items_delivery.change_status',
            'order_items_delivery.list',
            'order_items_delivery.process_delivery',
            'order_items_delivery.process_restock',
            'order_items_delivery.view',
            'order_items_placement.add_note',
            'order_items_placement.change_status',
            'order_items_placement.list',
            'order_items_placement.process_placement',
            'order_items_placement.view',
            'order_items_receiving.add_note',
            'order_items_receiving.change_status',
            'order_items_receiving.list',
            'order_items_receiving.process_receiving',
            'order_items_receiving.process_reorder',
            'order_items_receiving.view',
            'orders.configure',
            'orders.create',
            'orders.create_unknown_product',
            'orders.list',
            'orders.view',
            'pending_customers.list',
            'pending_customers.view',
            'pending_products.list',
            'pending_products.view',
        ]

        for perm in order_admin_perms:
            auth.grant_permission(admin, perm)


def includeme(config):
    base.defaults(config, **{'CommonView': CommonView})
