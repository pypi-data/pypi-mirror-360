# -*- coding: utf-8; -*-

from wuttjamaican.testing import DataTestCase

from sideshow.db.model import customers as mod


class TestPendingCustomer(DataTestCase):

    def test_str(self):
        customer = mod.PendingCustomer()
        self.assertEqual(str(customer), "")

        customer.full_name = "Fred Flintstone"
        self.assertEqual(str(customer), "Fred Flintstone")
