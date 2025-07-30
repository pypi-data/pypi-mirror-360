# -*- coding: utf-8; -*-

import datetime
from unittest.mock import patch

from pyramid.httpexceptions import HTTPFound

from sideshow.testing import WebTestCase
from sideshow.web.views import customers as mod
from sideshow.batch.neworder import NewOrderBatchHandler


class TestIncludeme(WebTestCase):

    def test_coverage(self):
        mod.includeme(self.pyramid_config)


class TestLocalCustomerView(WebTestCase):

    def make_view(self):
        return mod.LocalCustomerView(self.request)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.LocalCustomer)
        self.assertNotIn('full_name', grid.linked_columns)
        view.configure_grid(grid)
        self.assertIn('full_name', grid.linked_columns)

    def test_configure_form(self):
        model = self.app.model
        view = self.make_view()

        # creating
        with patch.object(view, 'creating', new=True):
            form = view.make_form(model_class=model.LocalCustomer)
            view.configure_form(form)
            self.assertNotIn('external_id', form)
            self.assertNotIn('full_name', form)
            self.assertNotIn('orders', form)
            self.assertNotIn('new_order_batches', form)

        user = model.User(username='barney')
        self.session.add(user)
        customer = model.LocalCustomer()
        self.session.add(customer)
        self.session.commit()

        # viewing
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=customer)
            view.configure_form(form)
            self.assertIn('external_id', form)
            self.assertIn('full_name', form)
            self.assertIn('orders', form)
            self.assertIn('new_order_batches', form)

    def test_make_orders_grid(self):
        model = self.app.model
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        customer = model.LocalCustomer()
        self.session.add(customer)
        order = model.Order(order_id=42, local_customer=customer, created_by=user)
        self.session.add(order)
        self.session.commit()

        # no view perm
        grid = view.make_orders_grid(customer)
        self.assertEqual(len(grid.actions), 0)

        # with view perm
        with patch.object(self.request, 'is_root', new=True):
            grid = view.make_orders_grid(customer)
            self.assertEqual(len(grid.actions), 1)
            self.assertEqual(grid.actions[0].key, 'view')

    def test_make_new_order_batches_grid(self):
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        customer = model.LocalCustomer()
        self.session.add(customer)
        batch = handler.make_batch(self.session, local_customer=customer, created_by=user)
        self.session.add(batch)
        self.session.commit()

        # no view perm
        grid = view.make_new_order_batches_grid(customer)
        self.assertEqual(len(grid.actions), 0)

        # with view perm
        with patch.object(self.request, 'is_root', new=True):
            grid = view.make_new_order_batches_grid(customer)
            self.assertEqual(len(grid.actions), 1)
            self.assertEqual(grid.actions[0].key, 'view')

    def test_objectify(self):
        model = self.app.model
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        with patch.object(view, 'creating', new=True):
            with patch.object(self.request, 'user', new=user):
                form = view.make_model_form()
                with patch.object(form, 'validated', create=True, new={
                        'first_name': 'Chuck',
                        'last_name': 'Norris',
                }):
                    customer = view.objectify(form)
                    self.assertIsInstance(customer, model.LocalCustomer)
                    self.assertEqual(customer.first_name, 'Chuck')
                    self.assertEqual(customer.last_name, 'Norris')
                    self.assertEqual(customer.full_name, 'Chuck Norris')


class TestPendingCustomerView(WebTestCase):

    def make_view(self):
        return mod.PendingCustomerView(self.request)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        # nb. mostly just getting coverage here
        grid = view.make_grid(model_class=model.PendingCustomer)
        view.configure_grid(grid)
        self.assertIn('full_name', grid.linked_columns)

    def test_configure_form(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        # creating
        with patch.object(view, 'creating', new=True):
            form = view.make_form(model_class=model.PendingCustomer)
            view.configure_form(form)
            self.assertNotIn('status', form)
            self.assertNotIn('created', form)
            self.assertNotIn('created_by', form)
            self.assertNotIn('orders', form)
            self.assertNotIn('new_order_batches', form)

        user = model.User(username='barney')
        self.session.add(user)
        customer = model.PendingCustomer(status=enum.PendingCustomerStatus.PENDING,
                                         created_by=user)
        self.session.add(customer)
        self.session.commit()

        # viewing
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=customer)
            view.configure_form(form)
            self.assertIn('status', form)
            self.assertIn('created', form)
            self.assertIn('created_by', form)
            self.assertIn('orders', form)
            self.assertIn('new_order_batches', form)

    def test_make_orders_grid(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        customer = model.PendingCustomer(status=enum.PendingCustomerStatus.PENDING,
                                         created_by=user)
        self.session.add(customer)
        order = model.Order(order_id=42, pending_customer=customer, created_by=user)
        self.session.add(order)
        self.session.commit()

        # no view perm
        grid = view.make_orders_grid(customer)
        self.assertEqual(len(grid.actions), 0)

        # with view perm
        with patch.object(self.request, 'is_root', new=True):
            grid = view.make_orders_grid(customer)
            self.assertEqual(len(grid.actions), 1)
            self.assertEqual(grid.actions[0].key, 'view')

    def test_make_new_order_batches_grid(self):
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        customer = model.PendingCustomer(status=enum.PendingCustomerStatus.PENDING,
                                         created_by=user)
        self.session.add(customer)
        batch = handler.make_batch(self.session, pending_customer=customer, created_by=user)
        self.session.add(batch)
        self.session.commit()

        # no view perm
        grid = view.make_new_order_batches_grid(customer)
        self.assertEqual(len(grid.actions), 0)

        # with view perm
        with patch.object(self.request, 'is_root', new=True):
            grid = view.make_new_order_batches_grid(customer)
            self.assertEqual(len(grid.actions), 1)
            self.assertEqual(grid.actions[0].key, 'view')

    def test_objectify(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        with patch.object(view, 'creating', new=True):
            with patch.object(self.request, 'user', new=user):
                form = view.make_model_form()
                with patch.object(form, 'validated', create=True, new={
                        'full_name': "Fred Flinstone",
                }):
                    customer = view.objectify(form)
                    self.assertIsInstance(customer, model.PendingCustomer)
                    self.assertIs(customer.created_by, user)
                    self.assertEqual(customer.status, enum.PendingCustomerStatus.PENDING)

    def test_delete_instance(self):
        self.pyramid_config.add_route('pending_customers.view', '/pending/customers/{uuid}')
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)

        # 1st customer is standalone, will be deleted
        customer = model.PendingCustomer(status=enum.PendingCustomerStatus.PENDING,
                                         created_by=user)
        self.session.add(customer)
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)
        view.delete_instance(customer)
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 0)

        # 2nd customer is attached to new order batch, will not be deleted
        customer = model.PendingCustomer(status=enum.PendingCustomerStatus.PENDING,
                                         created_by=user)
        self.session.add(customer)
        batch = handler.make_batch(self.session, created_by=user, pending_customer=customer)
        self.session.add(batch)
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)
        self.assertRaises(HTTPFound, view.delete_instance, customer)
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)

        # but after batch is executed, 2nd customer can be deleted
        batch.executed = datetime.datetime.now()
        batch.executed_by = user
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)
        view.delete_instance(customer)
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 0)

        # 3rd customer is attached to order, will not be deleted
        customer = model.PendingCustomer(status=enum.PendingCustomerStatus.PENDING,
                                         created_by=user)
        self.session.add(customer)
        order = model.Order(order_id=42, created_by=user, pending_customer=customer)
        self.session.add(order)
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)
        self.assertRaises(HTTPFound, view.delete_instance, customer)
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingCustomer).count(), 1)
