# -*- coding: utf-8; -*-

from unittest import TestCase

from asgiref.wsgi import WsgiToAsgi
from pyramid.router import Router

from wuttjamaican.testing import DataTestCase

from sideshow.web import app as mod


class TestMain(DataTestCase):

    def test_coverage(self):
        app = mod.main({}, **{'wutta_config': self.config})
        self.assertIsInstance(app, Router)


class TestMakeWsgiApp(DataTestCase):

    def test_coverage(self):
        app = mod.make_wsgi_app(config=self.config)
        self.assertIsInstance(app, Router)


class TestMakeAsgiApp(DataTestCase):

    def test_coverage(self):
        app = mod.make_asgi_app(config=self.config)
        self.assertIsInstance(app, WsgiToAsgi)
