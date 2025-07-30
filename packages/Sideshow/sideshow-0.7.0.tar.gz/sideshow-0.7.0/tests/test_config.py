# -*- coding: utf-8; -*-

from unittest import TestCase

from wuttjamaican.conf import WuttaConfig

from sideshow import config as mod


class TestSideshowConfig(TestCase):

    def test_configure(self):
        config = WuttaConfig(files=[])
        ext = mod.SideshowConfig()
        ext.configure(config)
        self.assertEqual(config.get('wutta.app_title'), "Sideshow")
        self.assertEqual(config.get('wutta.app_dist'), "Sideshow")
