# -*- coding: utf-8; -*-

import datetime
from unittest.mock import patch

from wuttaweb.forms.schema import WuttaMoney

from sideshow.testing import WebTestCase
from sideshow.web.views.batch import neworder as mod
from sideshow.web.forms.schema import PendingCustomerRef
from sideshow.batch.neworder import NewOrderBatchHandler


class TestIncludeme(WebTestCase):

    def test_coverage(self):
        mod.includeme(self.pyramid_config)


class TestNewOrderBatchView(WebTestCase):

    def make_view(self):
        return mod.NewOrderBatchView(self.request)

    def test_get_batch_handler(self):
        view = self.make_view()
        handler = view.get_batch_handler()
        self.assertIsInstance(handler, NewOrderBatchHandler)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()

        # store_id not exposed by default
        grid = view.make_grid(model_class=model.NewOrderBatch)
        self.assertIn('store_id', grid.columns)
        view.configure_grid(grid)
        self.assertNotIn('store_id', grid.columns)

        # store_id is exposed if configured
        self.config.setdefault('sideshow.orders.expose_store_id', 'true')
        grid = view.make_grid(model_class=model.NewOrderBatch)
        self.assertIn('store_id', grid.columns)
        view.configure_grid(grid)
        self.assertIn('store_id', grid.columns)

    def test_configure_form(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        handler = view.batch_handler

        user = model.User(username='barney')
        self.session.add(user)
        customer = model.PendingCustomer(status=enum.PendingCustomerStatus.PENDING,
                                         created_by=user)
        self.session.add(customer)
        batch = handler.make_batch(self.session, pending_customer=customer, created_by=user)
        self.session.add(batch)
        self.session.commit()

        # viewing
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=batch)
            view.configure_form(form)
            schema = form.get_schema()
            self.assertIsInstance(schema['pending_customer'].typ, PendingCustomerRef)
            self.assertIsInstance(schema['total_price'].typ, WuttaMoney)

            # store_id not exposed by default
            form = view.make_form(model_instance=batch)
            self.assertIn('store_id', form)
            view.configure_form(form)
            self.assertNotIn('store_id', form)

            # store_id is exposed if configured
            self.config.setdefault('sideshow.orders.expose_store_id', 'true')
            form = view.make_form(model_instance=batch)
            self.assertIn('store_id', form)
            view.configure_form(form)
            self.assertIn('store_id', form)

    def test_configure_row_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.NewOrderBatchRow)
        self.assertNotIn('total_price', grid.renderers)
        view.configure_row_grid(grid)
        self.assertIn('total_price', grid.renderers)

    def test_get_xref_buttons(self):
        self.pyramid_config.add_route('orders.view', '/orders/{uuid}')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        handler = view.batch_handler

        user = model.User(username='barney')
        self.session.add(user)
        customer = model.PendingCustomer(status=enum.PendingCustomerStatus.PENDING,
                                         created_by=user)
        self.session.add(customer)

        # 1st batch has no order
        batch = handler.make_batch(self.session, pending_customer=customer, created_by=user)
        self.session.add(batch)
        self.session.flush()
        buttons = view.get_xref_buttons(batch)
        self.assertEqual(len(buttons), 0)

        # 2nd batch is executed; has order
        batch = handler.make_batch(self.session, pending_customer=customer, created_by=user,
                                   executed=datetime.datetime.now(), executed_by=user)
        self.session.add(batch)
        self.session.flush()
        order = model.Order(order_id=batch.id, created_by=user)
        self.session.add(order)
        self.session.flush()
        with patch.object(view, 'Session', return_value=self.session):
            # nb. this also requires perm
            with patch.object(self.request, 'is_root', new=True):
                buttons = view.get_xref_buttons(batch)
                self.assertEqual(len(buttons), 1)
