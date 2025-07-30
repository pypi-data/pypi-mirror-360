# -*- coding: utf-8; -*-

from wuttjamaican.testing import DataTestCase

from sideshow.db.model import stores as mod


class TestPendingCustomer(DataTestCase):

    def test_str(self):
        store = mod.Store()
        self.assertEqual(str(store), "")

        store.name = "Acme Goods"
        self.assertEqual(str(store), "Acme Goods")

        store.store_id = "001"
        self.assertEqual(str(store), "001 Acme Goods")

    def test_get_display(self):
        store = mod.Store()
        self.assertEqual(store.get_display(), "")

        store.name = "Acme Goods"
        self.assertEqual(store.get_display(), "Acme Goods")

        store.store_id = "001"
        self.assertEqual(store.get_display(), "001 Acme Goods")
