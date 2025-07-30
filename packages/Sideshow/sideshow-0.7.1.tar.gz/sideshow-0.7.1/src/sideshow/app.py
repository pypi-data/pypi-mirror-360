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
Sideshow app provider
"""

from wuttjamaican import app as base


class SideshowAppProvider(base.AppProvider):
    """
    The :term:`app provider` for Sideshow.

    This adds the :meth:`get_order_handler()` method to the :term:`app
    handler`.
    """

    def get_order_handler(self, **kwargs):
        """
        Get the configured :term:`order handler` for the app.

        You can specify a custom handler in your :term:`config file`
        like:

        .. code-block:: ini

           [sideshow]
           orders.handler_spec = poser.orders:PoserOrderHandler

        :returns: Instance of :class:`~sideshow.orders.OrderHandler`.
        """
        if 'order_handler' not in self.__dict__:
            spec = self.config.get('sideshow.orders.handler_spec',
                                   default='sideshow.orders:OrderHandler')
            self.order_handler = self.app.load_object(spec)(self.config)
        return self.order_handler
