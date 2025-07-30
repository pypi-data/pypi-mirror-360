# -*- coding: utf-8; -*-

from sideshow.testing import WebTestCase
from sideshow.web import static as mod


class TestIncludeme(WebTestCase):

    def test_coverage(self):
        mod.includeme(self.pyramid_config)
