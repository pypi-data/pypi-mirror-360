# -*- coding: utf-8; -*-

from wuttjamaican.testing import DataTestCase

from sideshow.db.model import products as mod


class TestPendingProduct(DataTestCase):

    def test_str(self):
        product = mod.PendingProduct()
        self.assertEqual(str(product), "")

        product = mod.PendingProduct(brand_name="Bragg")
        self.assertEqual(str(product), "Bragg")

        product = mod.PendingProduct(description="Vinegar")
        self.assertEqual(str(product), "Vinegar")

        product = mod.PendingProduct(size="32oz")
        self.assertEqual(str(product), "32oz")

        product = mod.PendingProduct(brand_name="Bragg",
                                     description="Vinegar",
                                     size="32oz")
        self.assertEqual(str(product), "Bragg Vinegar 32oz")

    def test_full_description(self):
        product = mod.PendingProduct()
        self.assertEqual(product.full_description, "")

        product = mod.PendingProduct(brand_name="Bragg")
        self.assertEqual(product.full_description, "Bragg")

        product = mod.PendingProduct(description="Vinegar")
        self.assertEqual(product.full_description, "Vinegar")

        product = mod.PendingProduct(size="32oz")
        self.assertEqual(product.full_description, "32oz")

        product = mod.PendingProduct(brand_name="Bragg",
                                     description="Vinegar",
                                     size="32oz")
        self.assertEqual(product.full_description, "Bragg Vinegar 32oz")
