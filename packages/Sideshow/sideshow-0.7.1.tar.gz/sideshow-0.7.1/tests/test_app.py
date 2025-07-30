# -*- coding: utf-8; -*-

from wuttjamaican.testing import ConfigTestCase

from sideshow import app as mod
from sideshow.orders import OrderHandler


class TestSideshowAppProvider(ConfigTestCase):

    def make_provider(self):
        return mod.SideshowAppProvider(self.config)

    def test_get_order_handler(self):
        provider = self.make_provider()
        handler = provider.get_order_handler()
        self.assertIsInstance(handler, OrderHandler)
