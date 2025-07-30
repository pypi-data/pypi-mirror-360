# -*- coding: utf-8; -*-

from sqlalchemy import orm

from sideshow.testing import WebTestCase
from sideshow.web.forms import schema as mod


class TestOrderRef(WebTestCase):

    def test_sort_query(self):
        typ = mod.OrderRef(self.request, session=self.session)
        query = typ.get_query()
        self.assertIsInstance(query, orm.Query)
        sorted_query = typ.sort_query(query)
        self.assertIsInstance(sorted_query, orm.Query)
        self.assertIsNot(sorted_query, query)

    def test_get_object_url(self):
        self.pyramid_config.add_route('orders.view', '/orders/{uuid}')
        model = self.app.model

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        self.session.commit()

        typ = mod.OrderRef(self.request, session=self.session)
        url = typ.get_object_url(order)
        self.assertIsNotNone(url)
        self.assertIn(f'/orders/{order.uuid}', url)


class TestLocalCustomerRef(WebTestCase):

    def test_sort_query(self):
        typ = mod.LocalCustomerRef(self.request, session=self.session)
        query = typ.get_query()
        self.assertIsInstance(query, orm.Query)
        sorted_query = typ.sort_query(query)
        self.assertIsInstance(sorted_query, orm.Query)
        self.assertIsNot(sorted_query, query)

    def test_get_object_url(self):
        self.pyramid_config.add_route('local_customers.view', '/local/customers/{uuid}')
        model = self.app.model
        enum = self.app.enum

        customer = model.LocalCustomer()
        self.session.add(customer)
        self.session.commit()

        typ = mod.LocalCustomerRef(self.request, session=self.session)
        url = typ.get_object_url(customer)
        self.assertIsNotNone(url)
        self.assertIn(f'/local/customers/{customer.uuid}', url)


class TestPendingCustomerRef(WebTestCase):

    def test_sort_query(self):
        typ = mod.PendingCustomerRef(self.request, session=self.session)
        query = typ.get_query()
        self.assertIsInstance(query, orm.Query)
        sorted_query = typ.sort_query(query)
        self.assertIsInstance(sorted_query, orm.Query)
        self.assertIsNot(sorted_query, query)

    def test_get_object_url(self):
        self.pyramid_config.add_route('pending_customers.view', '/pending/customers/{uuid}')
        model = self.app.model
        enum = self.app.enum

        user = model.User(username='barney')
        self.session.add(user)
        customer = model.PendingCustomer(status=enum.PendingCustomerStatus.PENDING,
                                         created_by=user)
        self.session.add(customer)
        self.session.commit()

        typ = mod.PendingCustomerRef(self.request, session=self.session)
        url = typ.get_object_url(customer)
        self.assertIsNotNone(url)
        self.assertIn(f'/pending/customers/{customer.uuid}', url)


class TestLocalProductRef(WebTestCase):

    def test_sort_query(self):
        typ = mod.LocalProductRef(self.request, session=self.session)
        query = typ.get_query()
        self.assertIsInstance(query, orm.Query)
        sorted_query = typ.sort_query(query)
        self.assertIsInstance(sorted_query, orm.Query)
        self.assertIsNot(sorted_query, query)

    def test_get_object_url(self):
        self.pyramid_config.add_route('local_products.view', '/local/products/{uuid}')
        model = self.app.model
        enum = self.app.enum

        product = model.LocalProduct()
        self.session.add(product)
        self.session.commit()

        typ = mod.LocalProductRef(self.request, session=self.session)
        url = typ.get_object_url(product)
        self.assertIsNotNone(url)
        self.assertIn(f'/local/products/{product.uuid}', url)


class TestPendingProductRef(WebTestCase):

    def test_sort_query(self):
        typ = mod.PendingProductRef(self.request, session=self.session)
        query = typ.get_query()
        self.assertIsInstance(query, orm.Query)
        sorted_query = typ.sort_query(query)
        self.assertIsInstance(sorted_query, orm.Query)
        self.assertIsNot(sorted_query, query)

    def test_get_object_url(self):
        self.pyramid_config.add_route('pending_products.view', '/pending/products/{uuid}')
        model = self.app.model
        enum = self.app.enum

        user = model.User(username='barney')
        self.session.add(user)
        product = model.PendingProduct(status=enum.PendingProductStatus.PENDING,
                                       created_by=user)
        self.session.add(product)
        self.session.commit()

        typ = mod.PendingProductRef(self.request, session=self.session)
        url = typ.get_object_url(product)
        self.assertIsNotNone(url)
        self.assertIn(f'/pending/products/{product.uuid}', url)
