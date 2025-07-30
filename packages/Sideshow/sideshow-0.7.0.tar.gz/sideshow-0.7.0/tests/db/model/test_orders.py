# -*- coding: utf-8; -*-

from wuttjamaican.testing import DataTestCase

from sideshow.db.model import orders as mod
from sideshow.db.model.products import PendingProduct


class TestOrder(DataTestCase):

    def test_str(self):

        order = mod.Order()
        self.assertEqual(str(order), "None")

        order = mod.Order(order_id=42)
        self.assertEqual(str(order), "42")


class TestOrderItem(DataTestCase):

    def make_config(self, **kw):
        config = super().make_config(**kw)
        config.setdefault('wutta.enum_spec', 'sideshow.enum')
        return config

    def test_full_description(self):

        item = mod.OrderItem()
        self.assertEqual(item.full_description, "")

        item = mod.OrderItem(product_description="Vinegar")
        self.assertEqual(item.full_description, "Vinegar")

        item = mod.OrderItem(product_brand='Bragg',
                             product_description='Vinegar',
                             product_size='32oz')
        self.assertEqual(item.full_description, "Bragg Vinegar 32oz")

    def test_str(self):

        item = mod.OrderItem()
        self.assertEqual(str(item), "")

        item = mod.OrderItem(product_description="Vinegar")
        self.assertEqual(str(item), "Vinegar")

        item = mod.OrderItem(product_brand='Bragg',
                             product_description='Vinegar',
                             product_size='32oz')
        self.assertEqual(str(item), "Bragg Vinegar 32oz")

    def test_add_event(self):
        model = self.app.model
        enum = self.app.enum
        user = model.User(username='barney')
        item = mod.OrderItem()
        self.assertEqual(item.events, [])
        item.add_event(enum.ORDER_ITEM_EVENT_INITIATED, user)
        item.add_event(enum.ORDER_ITEM_EVENT_READY, user)
        self.assertEqual(len(item.events), 2)
        self.assertEqual(item.events[0].type_code, enum.ORDER_ITEM_EVENT_INITIATED)
        self.assertEqual(item.events[1].type_code, enum.ORDER_ITEM_EVENT_READY)
