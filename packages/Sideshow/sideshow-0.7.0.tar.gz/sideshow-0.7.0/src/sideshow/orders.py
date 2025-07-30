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
Sideshow Order Handler
"""

from wuttjamaican.app import GenericHandler


class OrderHandler(GenericHandler):
    """
    Base class and default implementation for the :term:`order
    handler`.

    This is responsible for business logic involving customer orders
    after they have been first created.  (The :term:`new order batch`
    handler is responsible for creation logic.)
    """

    def expose_store_id(self):
        """
        Returns boolean indicating whether the ``store_id`` field
        should be exposed at all.  This is false by default.
        """
        return self.config.get_bool('sideshow.orders.expose_store_id',
                                    default=False)

    def get_order_qty_uom_text(self, order_qty, order_uom, case_size=None, html=False):
        """
        Return the display text for a given order quantity.

        Default logic will return something like ``"3 Cases (x 6 = 18
        Units)"``.

        :param order_qty: Numeric quantity.

        :param order_uom: An order UOM constant; should be something
           from :data:`~sideshow.enum.ORDER_UOM`.

        :param case_size: Case size for the product, if known.

        :param html: Whether the return value should include any HTML.
           If false (the default), it will be plain text only.  If
           true, will replace the ``x`` character with ``&times;``.

        :returns: Display text.
        """
        enum = self.app.enum

        if order_uom == enum.ORDER_UOM_CASE:
            if case_size is None:
                case_qty = unit_qty = '??'
            else:
                case_qty = self.app.render_quantity(case_size)
                unit_qty = self.app.render_quantity(order_qty * case_size)
            CS = enum.ORDER_UOM[enum.ORDER_UOM_CASE]
            EA = enum.ORDER_UOM[enum.ORDER_UOM_UNIT]
            order_qty = self.app.render_quantity(order_qty)
            times = '&times;' if html else 'x'
            return (f"{order_qty} {CS} ({times} {case_qty} = {unit_qty} {EA})")

        # units
        unit_qty = self.app.render_quantity(order_qty)
        EA = enum.ORDER_UOM[enum.ORDER_UOM_UNIT]
        return f"{unit_qty} {EA}"

    def item_status_to_variant(self, status_code):
        """
        Return a Buefy style variant for the given status code.

        Default logic will return ``None`` for "normal" item status,
        but may return ``'warning'`` for some (e.g. canceled).

        :param status_code: The status code for an order item.

        :returns: Style variant string (e.g. ``'warning'``) or
           ``None``.
        """
        enum = self.app.enum
        if status_code in (enum.ORDER_ITEM_STATUS_CANCELED,
                           enum.ORDER_ITEM_STATUS_REFUND_PENDING,
                           enum.ORDER_ITEM_STATUS_REFUNDED,
                           enum.ORDER_ITEM_STATUS_RESTOCKED,
                           enum.ORDER_ITEM_STATUS_EXPIRED,
                           enum.ORDER_ITEM_STATUS_INACTIVE):
            return 'warning'

    def resolve_pending_product(self, pending_product, product_info, user, note=None):
        """
        Resolve a :term:`pending product`, to reflect the given
        product info.

        At a high level this does 2 things:

        * update the ``pending_product``
        * find and update any related :term:`order item(s) <order item>`

        The first step just sets
        :attr:`~sideshow.db.model.products.PendingProduct.product_id`
        from the provided info, and gives it the "resolved" status.
        Note that it does *not* update the pending product record
        further, so it will not fully "match" the product info.

        The second step will fetch all
        :class:`~sideshow.db.model.orders.OrderItem` records which
        reference the ``pending_product`` **and** which do not yet
        have a ``product_id`` value.  For each, it then updates the
        order item to contain all data from ``product_info``.  And
        finally, it adds an event to the item history, indicating who
        resolved and when.  (If ``note`` is specified, a *second*
        event is added for that.)

        :param pending_product:
           :class:`~sideshow.db.model.products.PendingProduct` to be
           resolved.

        :param product_info: Dict of product info, as obtained from
           :meth:`~sideshow.batch.neworder.NewOrderBatchHandler.get_product_info_external()`.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User` who
           is performing the action.

        :param note: Optional note to be added to event history for
           related order item(s).
        """
        enum = self.app.enum
        model = self.app.model
        session = self.app.get_session(pending_product)

        if pending_product.status != enum.PendingProductStatus.READY:
            raise ValueError("pending product does not have 'ready' status")

        info = product_info
        pending_product.product_id = info['product_id']
        pending_product.status = enum.PendingProductStatus.RESOLVED

        items = session.query(model.OrderItem)\
                       .filter(model.OrderItem.pending_product == pending_product)\
                       .filter(model.OrderItem.product_id == None)\
                       .all()

        for item in items:
            item.product_id = info['product_id']
            item.product_scancode = info['scancode']
            item.product_brand = info['brand_name']
            item.product_description = info['description']
            item.product_size = info['size']
            item.product_weighed = info['weighed']
            item.department_id = info['department_id']
            item.department_name = info['department_name']
            item.special_order = info['special_order']
            item.vendor_name = info['vendor_name']
            item.vendor_item_code = info['vendor_item_code']
            item.case_size = info['case_size']
            item.unit_cost = info['unit_cost']
            item.unit_price_reg = info['unit_price_reg']

            item.add_event(enum.ORDER_ITEM_EVENT_PRODUCT_RESOLVED, user)
            if note:
                item.add_event(enum.ORDER_ITEM_EVENT_NOTE_ADDED, user, note=note)

    def process_placement(self, items, user, vendor_name=None, po_number=None, note=None):
        """
        Process the "placement" step for the given order items.

        This may eventually do something involving an *actual*
        purchase order, or at least a minimal representation of one,
        but for now it does not.

        Instead, this will simply update each item to indicate its new
        status.  A note will be attached to indicate the vendor and/or
        PO number, if provided.

        :param items: Sequence of
           :class:`~sideshow.db.model.orders.OrderItem` records.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User`
           performing the action.

        :param vendor_name: Name of the vendor to which purchase order
           is placed, if known.

        :param po_number: Purchase order number, if known.

        :param note: Optional *additional* note to be attached to each
           order item.
        """
        enum = self.app.enum

        placed = None
        if vendor_name:
            placed = f"PO {po_number or ''} for vendor {vendor_name}"
        elif po_number:
            placed = f"PO {po_number}"

        for item in items:
            item.add_event(enum.ORDER_ITEM_EVENT_PLACED, user, note=placed)
            if note:
                item.add_event(enum.ORDER_ITEM_EVENT_NOTE_ADDED, user, note=note)
            item.status_code = enum.ORDER_ITEM_STATUS_PLACED

    def process_receiving(self, items, user, vendor_name=None,
                          invoice_number=None, po_number=None, note=None):
        """
        Process the "receiving" step for the given order items.

        This will update the status for each item, to indicate they
        are "received".

        TODO: This also should email the customer notifying their
        items are ready for pickup etc.

        :param items: Sequence of
           :class:`~sideshow.db.model.orders.OrderItem` records.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User`
           performing the action.

        :param vendor_name: Name of the vendor, if known.

        :param po_number: Purchase order number, if known.

        :param invoice_number: Invoice number, if known.

        :param note: Optional *additional* note to be attached to each
           order item.
        """
        enum = self.app.enum

        received = None
        if invoice_number and po_number and vendor_name:
            received = f"invoice {invoice_number} (PO {po_number}) from vendor {vendor_name}"
        elif invoice_number and vendor_name:
            received = f"invoice {invoice_number} from vendor {vendor_name}"
        elif po_number and vendor_name:
            received = f"PO {po_number} from vendor {vendor_name}"
        elif vendor_name:
            received = f"from vendor {vendor_name}"

        for item in items:
            item.add_event(enum.ORDER_ITEM_EVENT_RECEIVED, user, note=received)
            if note:
                item.add_event(enum.ORDER_ITEM_EVENT_NOTE_ADDED, user, note=note)
            item.status_code = enum.ORDER_ITEM_STATUS_RECEIVED

    def process_reorder(self, items, user, note=None):
        """
        Process the "reorder" step for the given order items.

        This will update the status for each item, to indicate they
        are "ready" (again) for placement.

        :param items: Sequence of
           :class:`~sideshow.db.model.orders.OrderItem` records.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User`
           performing the action.

        :param note: Optional *additional* note to be attached to each
           order item.
        """
        enum = self.app.enum

        for item in items:
            item.add_event(enum.ORDER_ITEM_EVENT_REORDER, user)
            if note:
                item.add_event(enum.ORDER_ITEM_EVENT_NOTE_ADDED, user, note=note)
            item.status_code = enum.ORDER_ITEM_STATUS_READY

    def process_contact_success(self, items, user, note=None):
        """
        Process the "successful contact" step for the given order
        items.

        This will update the status for each item, to indicate they
        are "contacted" and awaiting delivery.

        :param items: Sequence of
           :class:`~sideshow.db.model.orders.OrderItem` records.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User`
           performing the action.

        :param note: Optional *additional* note to be attached to each
           order item.
        """
        enum = self.app.enum

        for item in items:
            item.add_event(enum.ORDER_ITEM_EVENT_CONTACTED, user)
            if note:
                item.add_event(enum.ORDER_ITEM_EVENT_NOTE_ADDED, user, note=note)
            item.status_code = enum.ORDER_ITEM_STATUS_CONTACTED

    def process_contact_failure(self, items, user, note=None):
        """
        Process the "failed contact" step for the given order items.

        This will update the status for each item, to indicate
        "contact failed".

        :param items: Sequence of
           :class:`~sideshow.db.model.orders.OrderItem` records.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User`
           performing the action.

        :param note: Optional *additional* note to be attached to each
           order item.
        """
        enum = self.app.enum

        for item in items:
            item.add_event(enum.ORDER_ITEM_EVENT_CONTACT_FAILED, user)
            if note:
                item.add_event(enum.ORDER_ITEM_EVENT_NOTE_ADDED, user, note=note)
            item.status_code = enum.ORDER_ITEM_STATUS_CONTACT_FAILED

    def process_delivery(self, items, user, note=None):
        """
        Process the "delivery" step for the given order items.

        This will update the status for each item, to indicate they
        are "delivered".

        :param items: Sequence of
           :class:`~sideshow.db.model.orders.OrderItem` records.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User`
           performing the action.

        :param note: Optional *additional* note to be attached to each
           order item.
        """
        enum = self.app.enum

        for item in items:
            item.add_event(enum.ORDER_ITEM_EVENT_DELIVERED, user)
            if note:
                item.add_event(enum.ORDER_ITEM_EVENT_NOTE_ADDED, user, note=note)
            item.status_code = enum.ORDER_ITEM_STATUS_DELIVERED

    def process_restock(self, items, user, note=None):
        """
        Process the "restock" step for the given order items.

        This will update the status for each item, to indicate they
        are "restocked".

        :param items: Sequence of
           :class:`~sideshow.db.model.orders.OrderItem` records.

        :param user:
           :class:`~wuttjamaican:wuttjamaican.db.model.auth.User`
           performing the action.

        :param note: Optional *additional* note to be attached to each
           order item.
        """
        enum = self.app.enum

        for item in items:
            item.add_event(enum.ORDER_ITEM_EVENT_RESTOCKED, user)
            if note:
                item.add_event(enum.ORDER_ITEM_EVENT_NOTE_ADDED, user, note=note)
            item.status_code = enum.ORDER_ITEM_STATUS_RESTOCKED
