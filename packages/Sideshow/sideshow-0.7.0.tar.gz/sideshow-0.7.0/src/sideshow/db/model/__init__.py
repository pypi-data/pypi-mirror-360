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
Sideshow data models

This is the default :term:`app model` module for Sideshow.

This namespace exposes everything from
:mod:`wuttjamaican:wuttjamaican.db.model`, plus the following.

Primary :term:`data models <data model>`:

* :class:`~sideshow.db.model.stores.Store`
* :class:`~sideshow.db.model.orders.Order`
* :class:`~sideshow.db.model.orders.OrderItem`
* :class:`~sideshow.db.model.orders.OrderItemEvent`
* :class:`~sideshow.db.model.customers.LocalCustomer`
* :class:`~sideshow.db.model.products.LocalProduct`
* :class:`~sideshow.db.model.customers.PendingCustomer`
* :class:`~sideshow.db.model.products.PendingProduct`

And the :term:`batch` models:

* :class:`~sideshow.db.model.batch.neworder.NewOrderBatch`
* :class:`~sideshow.db.model.batch.neworder.NewOrderBatchRow`
"""

# bring in all of wutta
from wuttjamaican.db.model import *

# sideshow models
from .stores import Store
from .customers import LocalCustomer, PendingCustomer
from .products import LocalProduct, PendingProduct
from .orders import Order, OrderItem, OrderItemEvent

# batch models
from .batch.neworder import NewOrderBatch, NewOrderBatchRow
