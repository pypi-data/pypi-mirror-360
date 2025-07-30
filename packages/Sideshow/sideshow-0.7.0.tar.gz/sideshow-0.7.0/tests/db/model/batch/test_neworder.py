# -*- coding: utf-8; -*-

from wuttjamaican.testing import DataTestCase

from sideshow.db.model.batch import neworder as mod
from sideshow.db.model.products import PendingProduct


class TestNewOrderBatchRow(DataTestCase):

    def test_str(self):

        row = mod.NewOrderBatchRow()
        self.assertEqual(str(row), "")

        row = mod.NewOrderBatchRow(product_description="Vinegar")
        self.assertEqual(str(row), "Vinegar")

        product = PendingProduct(brand_name="Bragg",
                                 description="Vinegar",
                                 size="32oz")
        row = mod.NewOrderBatchRow(pending_product=product)
        self.assertEqual(str(row), "Bragg Vinegar 32oz")
