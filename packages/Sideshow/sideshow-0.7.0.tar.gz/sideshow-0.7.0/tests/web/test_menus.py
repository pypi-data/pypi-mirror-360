# -*- coding: utf-8; -*-

from sideshow.testing import WebTestCase
from sideshow.web import menus as mod


class TestSideshowMenuHandler(WebTestCase):

    def test_make_menus(self):
        handler = mod.SideshowMenuHandler(self.config)
        menus = handler.make_menus(self.request)
        titles = [menu['title'] for menu in menus]
        self.assertEqual(titles, [
            'Orders',
            'Customers',
            'Products',
            'Batches',
            'Other',
            'Admin',
        ])
