# -*- coding: utf-8; -*-

from wuttjamaican.testing import DataTestCase

from sideshow import orders as mod


class TestOrderHandler(DataTestCase):

    def make_config(self, **kwargs):
        config = super().make_config(**kwargs)
        config.setdefault('wutta.model_spec', 'sideshow.db.model')
        config.setdefault('wutta.enum_spec', 'sideshow.enum')
        return config

    def make_handler(self):
        return mod.OrderHandler(self.config)

    def test_expose_store_id(self):
        handler = self.make_handler()

        # false by default
        self.assertFalse(handler.expose_store_id())

        # config can enable
        self.config.setdefault('sideshow.orders.expose_store_id', 'true')
        self.assertTrue(handler.expose_store_id())

    def test_get_order_qty_uom_text(self):
        enum = self.app.enum
        handler = self.make_handler()

        # typical, plain text
        text = handler.get_order_qty_uom_text(2, enum.ORDER_UOM_CASE, case_size=12)
        self.assertEqual(text, "2 Cases (x 12 = 24 Units)")

        # typical w/ html
        text = handler.get_order_qty_uom_text(2, enum.ORDER_UOM_CASE, case_size=12, html=True)
        self.assertEqual(text, "2 Cases (&times; 12 = 24 Units)")

        # unknown case size
        text = handler.get_order_qty_uom_text(2, enum.ORDER_UOM_CASE)
        self.assertEqual(text, "2 Cases (x ?? = ?? Units)")
        text = handler.get_order_qty_uom_text(2, enum.ORDER_UOM_CASE, html=True)
        self.assertEqual(text, "2 Cases (&times; ?? = ?? Units)")

        # units only
        text = handler.get_order_qty_uom_text(2, enum.ORDER_UOM_UNIT)
        self.assertEqual(text, "2 Units")
        text = handler.get_order_qty_uom_text(2, enum.ORDER_UOM_UNIT, html=True)
        self.assertEqual(text, "2 Units")

    def test_item_status_to_variant(self):
        enum = self.app.enum
        handler = self.make_handler()

        # typical
        self.assertIsNone(handler.item_status_to_variant(enum.ORDER_ITEM_STATUS_INITIATED))
        self.assertIsNone(handler.item_status_to_variant(enum.ORDER_ITEM_STATUS_READY))
        self.assertIsNone(handler.item_status_to_variant(enum.ORDER_ITEM_STATUS_PLACED))
        self.assertIsNone(handler.item_status_to_variant(enum.ORDER_ITEM_STATUS_RECEIVED))
        self.assertIsNone(handler.item_status_to_variant(enum.ORDER_ITEM_STATUS_CONTACTED))
        self.assertIsNone(handler.item_status_to_variant(enum.ORDER_ITEM_STATUS_PAID))

        # warning
        self.assertEqual(handler.item_status_to_variant(enum.ORDER_ITEM_STATUS_CANCELED), 'warning')
        self.assertEqual(handler.item_status_to_variant(enum.ORDER_ITEM_STATUS_REFUND_PENDING), 'warning')
        self.assertEqual(handler.item_status_to_variant(enum.ORDER_ITEM_STATUS_REFUNDED), 'warning')
        self.assertEqual(handler.item_status_to_variant(enum.ORDER_ITEM_STATUS_RESTOCKED), 'warning')
        self.assertEqual(handler.item_status_to_variant(enum.ORDER_ITEM_STATUS_EXPIRED), 'warning')
        self.assertEqual(handler.item_status_to_variant(enum.ORDER_ITEM_STATUS_INACTIVE), 'warning')

    def test_resolve_pending_product(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        pending = model.PendingProduct(description='vinegar', unit_price_reg=5.99,
                                       status=enum.PendingProductStatus.PENDING,
                                       created_by=user)
        self.session.add(pending)
        order = model.Order(order_id=100, customer_name="Fred Flintstone", created_by=user)
        item = model.OrderItem(pending_product=pending,
                               order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                               status_code=enum.ORDER_ITEM_STATUS_READY)
        order.items.append(item)
        self.session.add(order)
        self.session.flush()

        info = {
            'product_id': '07430500132',
            'scancode': '07430500132',
            'brand_name': "Bragg's",
            'description': "Apple Cider Vinegar",
            'size': "32oz",
            'weighed': False,
            'department_id': None,
            'department_name': None,
            'special_order': False,
            'vendor_name': None,
            'vendor_item_code': None,
            'case_size': 12,
            'unit_cost': 2.99,
            'unit_price_reg': 5.99,
        }

        # first try fails b/c pending status
        self.assertEqual(len(item.events), 0)
        self.assertRaises(ValueError, handler.resolve_pending_product, pending, info, user)

        # resolves okay if ready status
        pending.status = enum.PendingProductStatus.READY
        handler.resolve_pending_product(pending, info, user)
        self.assertEqual(len(item.events), 1)
        self.assertEqual(item.events[0].type_code, enum.ORDER_ITEM_EVENT_PRODUCT_RESOLVED)
        self.assertIsNone(item.events[0].note)

        # more sample data
        pending2 = model.PendingProduct(description='vinegar', unit_price_reg=5.99,
                                        status=enum.PendingProductStatus.READY,
                                        created_by=user)
        self.session.add(pending2)
        order2 = model.Order(order_id=101, customer_name="Wilma Flintstone", created_by=user)
        item2 = model.OrderItem(pending_product=pending2,
                                order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_READY)
        order2.items.append(item2)
        self.session.add(order2)
        self.session.flush()

        # resolve with extra note
        handler.resolve_pending_product(pending2, info, user, note='hello world')
        self.assertEqual(len(item2.events), 2)
        self.assertEqual(item2.events[0].type_code, enum.ORDER_ITEM_EVENT_PRODUCT_RESOLVED)
        self.assertIsNone(item2.events[0].note)
        self.assertEqual(item2.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)
        self.assertEqual(item2.events[1].note, "hello world")

    def test_process_placement(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_READY)
        order.items.append(item1)
        item2 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_READY)
        order.items.append(item2)
        item3 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_READY)
        order.items.append(item3)
        self.session.add(order)
        self.session.flush()

        # two items are updated
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_READY)
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_READY)
        self.assertEqual(len(item1.events), 0)
        self.assertEqual(len(item2.events), 0)
        handler.process_placement([item1, item2], user,
                                      vendor_name="Acme Dist", po_number='ACME123')
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_PLACED)
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_PLACED)
        self.assertEqual(len(item1.events), 1)
        self.assertEqual(len(item2.events), 1)
        self.assertEqual(item1.events[0].note, "PO ACME123 for vendor Acme Dist")
        self.assertEqual(item2.events[0].note, "PO ACME123 for vendor Acme Dist")
        self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_PLACED)
        self.assertEqual(item2.events[0].type_code, enum.ORDER_ITEM_EVENT_PLACED)

        # update last item, without vendor name but extra note
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_READY)
        self.assertEqual(len(item3.events), 0)
        handler.process_placement([item3], user, po_number="939234", note="extra note")
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_PLACED)
        self.assertEqual(len(item3.events), 2)
        self.assertEqual(item3.events[0].note, "PO 939234")
        self.assertEqual(item3.events[1].note, "extra note")
        self.assertEqual(item3.events[0].type_code, enum.ORDER_ITEM_EVENT_PLACED)
        self.assertEqual(item3.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)

    def test_process_receiving(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_PLACED)
        order.items.append(item1)
        item2 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_PLACED)
        order.items.append(item2)
        item3 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_PLACED)
        order.items.append(item3)
        item4 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_PLACED)
        order.items.append(item4)
        item5 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_PLACED)
        order.items.append(item5)
        self.session.add(order)
        self.session.flush()

        # all info provided
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_PLACED)
        self.assertEqual(len(item1.events), 0)
        handler.process_receiving([item1], user, vendor_name="Acme Dist",
                                  invoice_number='INV123', po_number='123')
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item1.events), 1)
        self.assertEqual(item1.events[0].note, "invoice INV123 (PO 123) from vendor Acme Dist")
        self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_RECEIVED)

        # missing PO number
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_PLACED)
        self.assertEqual(len(item2.events), 0)
        handler.process_receiving([item2], user, vendor_name="Acme Dist", invoice_number='INV123')
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item2.events), 1)
        self.assertEqual(item2.events[0].note, "invoice INV123 from vendor Acme Dist")
        self.assertEqual(item2.events[0].type_code, enum.ORDER_ITEM_EVENT_RECEIVED)

        # missing invoice number
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_PLACED)
        self.assertEqual(len(item3.events), 0)
        handler.process_receiving([item3], user, vendor_name="Acme Dist", po_number='123')
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item3.events), 1)
        self.assertEqual(item3.events[0].note, "PO 123 from vendor Acme Dist")
        self.assertEqual(item3.events[0].type_code, enum.ORDER_ITEM_EVENT_RECEIVED)

        # vendor name only
        self.assertEqual(item4.status_code, enum.ORDER_ITEM_STATUS_PLACED)
        self.assertEqual(len(item4.events), 0)
        handler.process_receiving([item4], user, vendor_name="Acme Dist")
        self.assertEqual(item4.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item4.events), 1)
        self.assertEqual(item4.events[0].note, "from vendor Acme Dist")
        self.assertEqual(item4.events[0].type_code, enum.ORDER_ITEM_EVENT_RECEIVED)

        # no info; extra note
        self.assertEqual(item5.status_code, enum.ORDER_ITEM_STATUS_PLACED)
        self.assertEqual(len(item5.events), 0)
        handler.process_receiving([item5], user, note="extra note")
        self.assertEqual(item5.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item5.events), 2)
        self.assertIsNone(item5.events[0].note)
        self.assertEqual(item5.events[0].type_code, enum.ORDER_ITEM_EVENT_RECEIVED)
        self.assertEqual(item5.events[1].note, "extra note")
        self.assertEqual(item5.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)

    def test_process_reorder(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_PLACED)
        order.items.append(item1)
        item2 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_PLACED)
        order.items.append(item2)
        item3 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_PLACED)
        order.items.append(item3)
        self.session.add(order)
        self.session.flush()

        # two items are updated
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_PLACED)
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_PLACED)
        self.assertEqual(len(item1.events), 0)
        self.assertEqual(len(item2.events), 0)
        handler.process_reorder([item1, item2], user)
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_READY)
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_READY)
        self.assertEqual(len(item1.events), 1)
        self.assertEqual(len(item2.events), 1)
        self.assertIsNone(item1.events[0].note)
        self.assertIsNone(item2.events[0].note)
        self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_REORDER)
        self.assertEqual(item2.events[0].type_code, enum.ORDER_ITEM_EVENT_REORDER)

        # update last item, with extra note
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_PLACED)
        self.assertEqual(len(item3.events), 0)
        handler.process_reorder([item3], user, note="extra note")
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_READY)
        self.assertEqual(len(item3.events), 2)
        self.assertIsNone(item3.events[0].note)
        self.assertEqual(item3.events[1].note, "extra note")
        self.assertEqual(item3.events[0].type_code, enum.ORDER_ITEM_EVENT_REORDER)
        self.assertEqual(item3.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)

    def test_process_contact_success(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item1)
        item2 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item2)
        item3 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item3)
        self.session.add(order)
        self.session.flush()

        # two items are updated
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item1.events), 0)
        self.assertEqual(len(item2.events), 0)
        handler.process_contact_success([item1, item2], user)
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_CONTACTED)
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_CONTACTED)
        self.assertEqual(len(item1.events), 1)
        self.assertEqual(len(item2.events), 1)
        self.assertIsNone(item1.events[0].note)
        self.assertIsNone(item2.events[0].note)
        self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_CONTACTED)
        self.assertEqual(item2.events[0].type_code, enum.ORDER_ITEM_EVENT_CONTACTED)

        # update last item, with extra note
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item3.events), 0)
        handler.process_contact_success([item3], user, note="extra note")
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_CONTACTED)
        self.assertEqual(len(item3.events), 2)
        self.assertIsNone(item3.events[0].note)
        self.assertEqual(item3.events[1].note, "extra note")
        self.assertEqual(item3.events[0].type_code, enum.ORDER_ITEM_EVENT_CONTACTED)
        self.assertEqual(item3.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)

    def test_process_contact_failure(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item1)
        item2 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item2)
        item3 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item3)
        self.session.add(order)
        self.session.flush()

        # two items are updated
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item1.events), 0)
        self.assertEqual(len(item2.events), 0)
        handler.process_contact_failure([item1, item2], user)
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_CONTACT_FAILED)
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_CONTACT_FAILED)
        self.assertEqual(len(item1.events), 1)
        self.assertEqual(len(item2.events), 1)
        self.assertIsNone(item1.events[0].note)
        self.assertIsNone(item2.events[0].note)
        self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_CONTACT_FAILED)
        self.assertEqual(item2.events[0].type_code, enum.ORDER_ITEM_EVENT_CONTACT_FAILED)

        # update last item, with extra note
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item3.events), 0)
        handler.process_contact_failure([item3], user, note="extra note")
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_CONTACT_FAILED)
        self.assertEqual(len(item3.events), 2)
        self.assertIsNone(item3.events[0].note)
        self.assertEqual(item3.events[1].note, "extra note")
        self.assertEqual(item3.events[0].type_code, enum.ORDER_ITEM_EVENT_CONTACT_FAILED)
        self.assertEqual(item3.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)

    def test_process_delivery(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item1)
        item2 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item2)
        item3 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item3)
        self.session.add(order)
        self.session.flush()

        # two items are updated
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item1.events), 0)
        self.assertEqual(len(item2.events), 0)
        handler.process_delivery([item1, item2], user)
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_DELIVERED)
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_DELIVERED)
        self.assertEqual(len(item1.events), 1)
        self.assertEqual(len(item2.events), 1)
        self.assertIsNone(item1.events[0].note)
        self.assertIsNone(item2.events[0].note)
        self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_DELIVERED)
        self.assertEqual(item2.events[0].type_code, enum.ORDER_ITEM_EVENT_DELIVERED)

        # update last item, with extra note
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item3.events), 0)
        handler.process_delivery([item3], user, note="extra note")
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_DELIVERED)
        self.assertEqual(len(item3.events), 2)
        self.assertIsNone(item3.events[0].note)
        self.assertEqual(item3.events[1].note, "extra note")
        self.assertEqual(item3.events[0].type_code, enum.ORDER_ITEM_EVENT_DELIVERED)
        self.assertEqual(item3.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)

    def test_process_restock(self):
        model = self.app.model
        enum = self.app.enum
        handler = self.make_handler()

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item1)
        item2 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item2)
        item3 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item3)
        self.session.add(order)
        self.session.flush()

        # two items are updated
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item1.events), 0)
        self.assertEqual(len(item2.events), 0)
        handler.process_restock([item1, item2], user)
        self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_RESTOCKED)
        self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_RESTOCKED)
        self.assertEqual(len(item1.events), 1)
        self.assertEqual(len(item2.events), 1)
        self.assertIsNone(item1.events[0].note)
        self.assertIsNone(item2.events[0].note)
        self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_RESTOCKED)
        self.assertEqual(item2.events[0].type_code, enum.ORDER_ITEM_EVENT_RESTOCKED)

        # update last item, with extra note
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
        self.assertEqual(len(item3.events), 0)
        handler.process_restock([item3], user, note="extra note")
        self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_RESTOCKED)
        self.assertEqual(len(item3.events), 2)
        self.assertIsNone(item3.events[0].note)
        self.assertEqual(item3.events[1].note, "extra note")
        self.assertEqual(item3.events[0].type_code, enum.ORDER_ITEM_EVENT_RESTOCKED)
        self.assertEqual(item3.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)
