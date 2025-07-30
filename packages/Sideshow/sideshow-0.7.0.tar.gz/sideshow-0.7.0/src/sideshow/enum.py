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
Enum Values
"""

from enum import Enum
from collections import OrderedDict

from wuttjamaican.enum import *


ORDER_UOM_CASE          = 'CS'
"""
UOM code for ordering a "case" of product.

Sideshow will treat "case" orders somewhat differently as compared to
"unit" orders.
"""

ORDER_UOM_UNIT          = 'EA'
"""
UOM code for ordering a "unit" of product.

This is the default "unit" UOM but in practice all others are treated
the same by Sideshow, whereas "case" orders are treated somewhat
differently.
"""

ORDER_UOM_KILOGRAM      = 'KG'
"""
UOM code for ordering a "kilogram" of product.

This is treated same as "unit" by Sideshow.  However it should
(probably?) only be used for items where
e.g. :attr:`~sideshow.db.model.orders.OrderItem.product_weighed` is
true.
"""

ORDER_UOM_POUND         = 'LB'
"""
UOM code for ordering a "pound" of product.

This is treated same as "unit" by Sideshow.  However it should
(probably?) only be used for items where
e.g. :attr:`~sideshow.db.model.orders.OrderItem.product_weighed` is
true.
"""

ORDER_UOM = OrderedDict([
    (ORDER_UOM_CASE,            "Cases"),
    (ORDER_UOM_UNIT,            "Units"),
    (ORDER_UOM_KILOGRAM,        "Kilograms"),
    (ORDER_UOM_POUND,           "Pounds"),
])
"""
Dict of possible code -> label options for ordering unit of measure.

These codes are referenced by:

* :attr:`sideshow.db.model.batch.neworder.NewOrderBatchRow.order_uom`
* :attr:`sideshow.db.model.orders.OrderItem.order_uom`
"""


class PendingCustomerStatus(Enum):
    """
    Enum values for
    :attr:`sideshow.db.model.customers.PendingCustomer.status`.
    """
    PENDING = 'pending'
    READY = 'ready'
    RESOLVED = 'resolved'
    IGNORED = 'ignored'


class PendingProductStatus(Enum):
    """
    Enum values for
    :attr:`sideshow.db.model.products.PendingProduct.status`.
    """
    PENDING = 'pending'
    READY = 'ready'
    RESOLVED = 'resolved'
    IGNORED = 'ignored'


########################################
# Order Item Status
########################################

ORDER_ITEM_STATUS_UNINITIATED       = 1
"""
Indicates the item is "not yet initiated" - this probably is not
useful but exists as a possibility just in case.
"""

ORDER_ITEM_STATUS_INITIATED         = 10
"""
Indicates the item is "initiated" (aka. created) but not yet "ready"
for buyer/PO.  This may imply the price needs confirmation etc.
"""

ORDER_ITEM_STATUS_PAID_BEFORE       = 50
"""
Indicates the customer has fully paid for the item, up-front before
the buyer places PO etc.  It implies the item is not yet "ready" for
some reason.
"""

# TODO: deprecate / remove this one
ORDER_ITEM_STATUS_PAID              = ORDER_ITEM_STATUS_PAID_BEFORE

ORDER_ITEM_STATUS_READY             = 100
"""
Indicates the item is "ready" for buyer to include it on a vendor
purchase order.
"""

ORDER_ITEM_STATUS_PLACED            = 200
"""
Indicates the buyer has placed a vendor purchase order which includes
this item.  The item is thereby "on order" until the truck arrives.
"""

ORDER_ITEM_STATUS_RECEIVED          = 300
"""
Indicates the item has been received as part of a vendor delivery.
The item is thereby "on hand" until customer comes in for pickup.
"""

ORDER_ITEM_STATUS_CONTACTED         = 350
"""
Indicates the customer has been notified that the item is "on hand"
and awaiting their pickup.
"""

ORDER_ITEM_STATUS_CONTACT_FAILED    = 375
"""
Indicates the attempt(s) to notify customer have failed.  The item is
on hand but the customer does not know to pickup.
"""

ORDER_ITEM_STATUS_DELIVERED         = 500
"""
Indicates the customer has picked up the item.
"""

ORDER_ITEM_STATUS_PAID_AFTER        = 550
"""
Indicates the customer has fully paid for the item, as part of their
pickup.  This completes the cycle for orders which require payment on
the tail end.
"""

ORDER_ITEM_STATUS_CANCELED          = 900
"""
Indicates the order item has been canceled.
"""

ORDER_ITEM_STATUS_REFUND_PENDING    = 910
"""
Indicates the order item has been canceled, and the customer is due a
(pending) refund.
"""

ORDER_ITEM_STATUS_REFUNDED          = 920
"""
Indicates the order item has been canceled, and the customer has been
given a refund.
"""

ORDER_ITEM_STATUS_RESTOCKED         = 930
"""
Indicates the product has been restocked, e.g. after the order item
was canceled.
"""

ORDER_ITEM_STATUS_EXPIRED           = 940
"""
Indicates the order item and/or product has expired.
"""

ORDER_ITEM_STATUS_INACTIVE          = 950
"""
Indicates the order item has become inactive.
"""

ORDER_ITEM_STATUS = OrderedDict([
    (ORDER_ITEM_STATUS_UNINITIATED,         "uninitiated"),
    (ORDER_ITEM_STATUS_INITIATED,           "initiated"),
    (ORDER_ITEM_STATUS_PAID_BEFORE,         "paid"),
    (ORDER_ITEM_STATUS_READY,               "ready"),
    (ORDER_ITEM_STATUS_PLACED,              "placed"),
    (ORDER_ITEM_STATUS_RECEIVED,            "received"),
    (ORDER_ITEM_STATUS_CONTACTED,           "contacted"),
    (ORDER_ITEM_STATUS_CONTACT_FAILED,      "contact failed"),
    (ORDER_ITEM_STATUS_DELIVERED,           "delivered"),
    (ORDER_ITEM_STATUS_PAID_AFTER,          "paid"),
    (ORDER_ITEM_STATUS_CANCELED,            "canceled"),
    (ORDER_ITEM_STATUS_REFUND_PENDING,      "refund pending"),
    (ORDER_ITEM_STATUS_REFUNDED,            "refunded"),
    (ORDER_ITEM_STATUS_RESTOCKED,           "restocked"),
    (ORDER_ITEM_STATUS_EXPIRED,             "expired"),
    (ORDER_ITEM_STATUS_INACTIVE,            "inactive"),
])
"""
Dict of possible code -> label options for :term:`order item` status.

These codes are referenced by:

* :attr:`sideshow.db.model.orders.OrderItem.status_code`
"""


########################################
# Order Item Event Type
########################################

ORDER_ITEM_EVENT_INITIATED          = 10
"""
Indicates the item was "initiated" - this occurs when the
:term:`order` is first created.
"""

ORDER_ITEM_EVENT_PRICE_CONFIRMED    = 20
"""
Indicates the item's price was confirmed by a user who is authorized
to do that.
"""

ORDER_ITEM_EVENT_PAYMENT_RECEIVED   = 50
"""
Indicates payment was received for the item.  This may occur toward
the beginning, or toward the end, of the item's life cycle depending
on app configuration etc.
"""

# TODO: deprecate / remove this
ORDER_ITEM_EVENT_PAID               = ORDER_ITEM_EVENT_PAYMENT_RECEIVED

ORDER_ITEM_EVENT_READY              = 100
"""
Indicates the item has become "ready" for buyer placement on a new
vendor purchase order.  Often this will occur when the :term:`order`
is first created, if the data is suitable.  However this may be
delayed if e.g. the price needs confirmation.
"""

ORDER_ITEM_EVENT_CUSTOMER_RESOLVED  = 120
"""
Indicates the customer for the :term:`order` has been assigned to a
"proper" (existing) account.  This may happen (after the fact) if the
order was first created with a new/unknown customer.
"""

ORDER_ITEM_EVENT_PRODUCT_RESOLVED   = 140
"""
Indicates the product for the :term:`order item` has been assigned to
a "proper" (existing) product record.  This may happen (after the
fact) if the order was first created with a new/unknown product.
"""

ORDER_ITEM_EVENT_PLACED             = 200
"""
Indicates the buyer has placed a vendor purchase order which includes
this item.  So the item is "on order" until the truck arrives.
"""

ORDER_ITEM_EVENT_REORDER             = 210
"""
Indicates the item was not received with the delivery on which it was
expected, and must be re-ordered from vendor.
"""

ORDER_ITEM_EVENT_RECEIVED           = 300
"""
Indicates the receiver has found the item while receiving a vendor
delivery.  The item is set aside and is "on hand" until customer comes
in to pick it up.
"""

ORDER_ITEM_EVENT_CONTACTED          = 350
"""
Indicates the customer has been contacted, to notify them of the item
being on hand and ready for pickup.
"""

ORDER_ITEM_EVENT_CONTACT_FAILED     = 375
"""
Indicates an attempt was made to contact the customer, to notify them
of item being on hand, but the attempt failed, e.g. due to bad phone
or email on file.
"""

ORDER_ITEM_EVENT_DELIVERED          = 500
"""
Indicates the customer has picked up the item.
"""

ORDER_ITEM_EVENT_STATUS_CHANGE      = 700
"""
Indicates a manual status change was made.  Such an event should
ideally contain a note with further explanation.
"""

ORDER_ITEM_EVENT_NOTE_ADDED         = 750
"""
Indicates an arbitrary note was added.
"""

ORDER_ITEM_EVENT_CANCELED           = 900
"""
Indicates the :term:`order item` was canceled.
"""

ORDER_ITEM_EVENT_REFUND_PENDING     = 910
"""
Indicates the customer is due a (pending) refund for the item.
"""

ORDER_ITEM_EVENT_REFUNDED           = 920
"""
Indicates the customer has been refunded for the item.
"""

ORDER_ITEM_EVENT_RESTOCKED          = 930
"""
Indicates the product has been restocked, e.g. due to the order item
being canceled.
"""

ORDER_ITEM_EVENT_EXPIRED            = 940
"""
Indicates the order item (or its product) has expired.
"""

ORDER_ITEM_EVENT_INACTIVE           = 950
"""
Indicates the order item has become inactive.
"""

ORDER_ITEM_EVENT_OTHER              = 999
"""
Arbitrary event type which does not signify anything in particular.
If used, the event should be given an explanatory note.
"""

ORDER_ITEM_EVENT = OrderedDict([
    (ORDER_ITEM_EVENT_INITIATED,            "initiated"),
    (ORDER_ITEM_EVENT_PRICE_CONFIRMED,      "price confirmed"),
    (ORDER_ITEM_EVENT_PAYMENT_RECEIVED,     "payment received"),
    (ORDER_ITEM_EVENT_READY,                "ready to proceed"),
    (ORDER_ITEM_EVENT_CUSTOMER_RESOLVED,    "customer resolved"),
    (ORDER_ITEM_EVENT_PRODUCT_RESOLVED,     "product resolved"),
    (ORDER_ITEM_EVENT_PLACED,               "placed with vendor"),
    (ORDER_ITEM_EVENT_REORDER,              "marked for re-order"),
    (ORDER_ITEM_EVENT_RECEIVED,             "received from vendor"),
    (ORDER_ITEM_EVENT_CONTACTED,            "customer contacted"),
    (ORDER_ITEM_EVENT_CONTACT_FAILED,       "contact failed"),
    (ORDER_ITEM_EVENT_DELIVERED,            "delivered"),
    (ORDER_ITEM_EVENT_STATUS_CHANGE,        "changed status"),
    (ORDER_ITEM_EVENT_NOTE_ADDED,           "added note"),
    (ORDER_ITEM_EVENT_CANCELED,             "canceled"),
    (ORDER_ITEM_EVENT_REFUND_PENDING,       "refund pending"),
    (ORDER_ITEM_EVENT_REFUNDED,             "refunded"),
    (ORDER_ITEM_EVENT_RESTOCKED,            "restocked"),
    (ORDER_ITEM_EVENT_EXPIRED,              "expired"),
    (ORDER_ITEM_EVENT_INACTIVE,             "inactive"),
    (ORDER_ITEM_EVENT_OTHER,                "other"),
])
"""
Dict of possible code -> label options for :term:`order item` event
types.

These codes are referenced by:

* :attr:`sideshow.db.model.orders.OrderItemEvent.type_code`
"""
