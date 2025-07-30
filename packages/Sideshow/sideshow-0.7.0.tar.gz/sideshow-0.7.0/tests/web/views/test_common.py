# -*- coding: utf-8; -*-

from sideshow.testing import WebTestCase
from sideshow.web.views import common as mod


class TestIncludeme(WebTestCase):

    def test_coverage(self):
        mod.includeme(self.pyramid_config)


class TestCommonView(WebTestCase):

    def make_view(self):
        return mod.CommonView(self.request)

    def test_setup_enhance_admin_user(self):
        model = self.app.model
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.flush()

        self.assertEqual(len(user.roles), 0)
        view.setup_enhance_admin_user(user)
        self.assertEqual(len(user.roles), 1)
        self.assertEqual(user.roles[0].name, 'Order Admin')
