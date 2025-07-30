# -*- coding: utf-8; -*-

import datetime
import decimal
import json
from unittest.mock import patch

from sqlalchemy import orm
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from pyramid.response import Response

from wuttaweb.forms.schema import WuttaMoney

from sideshow.batch.neworder import NewOrderBatchHandler
from sideshow.orders import OrderHandler
from sideshow.testing import WebTestCase
from sideshow.web.views import orders as mod
from sideshow.web.forms.schema import OrderRef, PendingProductRef
from sideshow.config import SideshowConfig


class TestIncludeme(WebTestCase):

    def test_coverage(self):
        mod.includeme(self.pyramid_config)


class TestOrderView(WebTestCase):

    def make_config(self, **kw):
        config = super().make_config(**kw)
        SideshowConfig().configure(config)
        return config

    def make_view(self):
        return mod.OrderView(self.request)

    def make_handler(self):
        return NewOrderBatchHandler(self.config)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()

        # store_id hidden by default
        grid = view.make_grid(model_class=model.Order, columns=['store_id', 'order_id'])
        self.assertIn('store_id', grid.columns)
        view.configure_grid(grid)
        self.assertNotIn('store_id', grid.columns)

        # store_id is shown if configured
        self.config.setdefault('sideshow.orders.expose_store_id', 'true')
        grid = view.make_grid(model_class=model.Order, columns=['store_id', 'order_id'])
        self.assertIn('store_id', grid.columns)
        view.configure_grid(grid)
        self.assertIn('store_id', grid.columns)

    def test_create(self):
        self.pyramid_config.include('sideshow.web.views')
        self.config.setdefault('wutta.batch.neworder.handler.spec',
                               'sideshow.batch.neworder:NewOrderBatchHandler')
        self.config.setdefault('sideshow.orders.expose_store_id', 'true')
        self.config.setdefault('sideshow.orders.allow_item_discounts', 'true')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        store = model.Store(store_id='001', name='Acme Goods')
        self.session.add(store)
        store = model.Store(store_id='002', name='Acme Services')
        self.session.add(store)
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):
            with patch.object(self.request, 'current_route_url', return_value='/orders/new'):

                # this will require some perms
                with patch.multiple(self.request, create=True,
                                    user=user, is_root=True):

                    # fetch page to start things off
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 0)
                    response = view.create()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 1)
                    batch1 = self.session.query(model.NewOrderBatch).one()

                    # start over; deletes current batch
                    with patch.multiple(self.request, create=True,
                                        method='POST',
                                        POST={'action': 'start_over'}):
                        response = view.create()
                        self.assertIsInstance(response, HTTPFound)
                        self.assertIn('/orders/new', response.location)
                        self.assertEqual(self.session.query(model.NewOrderBatch).count(), 0)

                    # fetch again to get new batch
                    response = view.create()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 1)
                    batch2 = self.session.query(model.NewOrderBatch).one()
                    self.assertIsNot(batch2, batch1)

                    # set pending customer
                    with patch.multiple(self.request, create=True,
                                        method='POST',
                                        json_body={'action': 'set_pending_customer',
                                                   'first_name': 'Fred',
                                                   'last_name': 'Flintstone',
                                                   'phone_number': '555-1234',
                                                   'email_address': 'fred@mailinator.com'}):
                        response = view.create()
                        self.assertIsInstance(response, Response)
                        self.assertEqual(response.content_type, 'application/json')
                        self.assertEqual(response.json_body, {
                            'store_id': None,
                            'customer_is_known': False,
                            'customer_id': None,
                            'customer_name': 'Fred Flintstone',
                            'phone_number': '555-1234',
                            'email_address': 'fred@mailinator.com',
                            'new_customer_full_name': 'Fred Flintstone',
                            'new_customer_first_name': 'Fred',
                            'new_customer_last_name': 'Flintstone',
                            'new_customer_phone': '555-1234',
                            'new_customer_email': 'fred@mailinator.com',
                        })

                    # invalid action
                    with patch.multiple(self.request, create=True,
                                        method='POST',
                                        POST={'action': 'bogus'},
                                        json_body={'action': 'bogus'}):
                        response = view.create()
                        self.assertIsInstance(response, Response)
                        self.assertEqual(response.content_type, 'application/json')
                        self.assertEqual(response.json_body, {'error': 'unknown form action'})

                    # add item
                    with patch.multiple(self.request, create=True,
                                        method='POST',
                                        json_body={'action': 'add_item',
                                                   'product_info': {
                                                       'scancode': '07430500132',
                                                       'description': 'Vinegar',
                                                       'unit_price_reg': 5.99,
                                                   },
                                                   'order_qty': 1,
                                                   'order_uom': enum.ORDER_UOM_UNIT}):
                        response = view.create()
                        self.assertIsInstance(response, Response)
                        self.assertEqual(response.content_type, 'application/json')
                        data = response.json_body
                        self.assertEqual(sorted(data), ['batch', 'row'])

                    # add item, w/ error
                    with patch.object(NewOrderBatchHandler, 'add_item', side_effect=RuntimeError):
                        with patch.multiple(self.request, create=True,
                                            method='POST',
                                            json_body={'action': 'add_item',
                                                       'product_info': {
                                                           'scancode': '07430500116',
                                                           'description': 'Vinegar',
                                                           'unit_price_reg': 3.59,
                                                       },
                                                       'order_qty': 1,
                                                       'order_uom': enum.ORDER_UOM_UNIT}):
                            response = view.create()
                            self.assertIsInstance(response, Response)
                            self.assertEqual(response.content_type, 'application/json')
                            self.assertEqual(response.json_body, {'error': 'RuntimeError'})

    def test_get_current_batch(self):
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        # user is required
        self.assertRaises(HTTPForbidden, view.get_current_batch)

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):

                    # batch is auto-created
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 0)
                    batch = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 1)
                    self.assertIs(batch.created_by, user)

                    # same batch is returned subsequently
                    batch2 = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 1)
                    self.assertIs(batch2, batch)

    def test_customer_autocomplete(self):
        model = self.app.model
        handler = self.make_handler()
        view = self.make_view()
        view.batch_handler = handler

        with patch.object(view, 'Session', return_value=self.session):

            # empty results by default
            self.assertEqual(view.customer_autocomplete(), [])
            with patch.object(self.request, 'GET', new={'term': 'foo'}, create=True):
                self.assertEqual(view.customer_autocomplete(), [])

            # add a customer
            customer = model.LocalCustomer(full_name="Chuck Norris")
            self.session.add(customer)
            self.session.flush()

            # search for chuck finds chuck
            with patch.object(self.request, 'GET', new={'term': 'chuck'}, create=True):
                result = view.customer_autocomplete()
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0], {
                    'value': customer.uuid.hex,
                    'label': "Chuck Norris",
                })

            # search for sally finds nothing
            with patch.object(self.request, 'GET', new={'term': 'sally'}, create=True):
                result = view.customer_autocomplete()
                self.assertEqual(result, [])

            # external lookup not implemented by default
            with patch.object(handler, 'use_local_customers', return_value=False):
                with patch.object(self.request, 'GET', new={'term': 'sally'}, create=True):
                    self.assertRaises(NotImplementedError, view.customer_autocomplete)

    def test_product_autocomplete(self):
        model = self.app.model
        handler = self.make_handler()
        view = self.make_view()
        view.batch_handler = handler

        with patch.object(view, 'Session', return_value=self.session):

            # empty results by default
            self.assertEqual(view.product_autocomplete(), [])
            with patch.object(self.request, 'GET', new={'term': 'foo'}, create=True):
                self.assertEqual(view.product_autocomplete(), [])

            # add a product
            product = model.LocalProduct(brand_name="Bragg's", description="Vinegar")
            self.session.add(product)
            self.session.flush()

            # search for vinegar finds product
            with patch.object(self.request, 'GET', new={'term': 'vinegar'}, create=True):
                result = view.product_autocomplete()
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0], {
                    'value': product.uuid.hex,
                    'label': "Bragg's Vinegar",
                })

            # search for brag finds product
            with patch.object(self.request, 'GET', new={'term': 'brag'}, create=True):
                result = view.product_autocomplete()
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0], {
                    'value': product.uuid.hex,
                    'label': "Bragg's Vinegar",
                })

            # search for juice finds nothing
            with patch.object(self.request, 'GET', new={'term': 'juice'}, create=True):
                result = view.product_autocomplete()
                self.assertEqual(result, [])

            # external lookup not implemented by default
            with patch.object(handler, 'use_local_products', return_value=False):
                with patch.object(self.request, 'GET', new={'term': 'juice'}, create=True):
                    self.assertRaises(NotImplementedError, view.product_autocomplete)

    def test_get_pending_product_required_fields(self):
        model = self.app.model
        view = self.make_view()

        # only description is required by default
        fields = view.get_pending_product_required_fields()
        self.assertEqual(fields, ['description'])

        # but config can specify otherwise
        self.config.setdefault('sideshow.orders.unknown_product.fields.brand_name.required', 'true')
        self.config.setdefault('sideshow.orders.unknown_product.fields.description.required', 'false')
        self.config.setdefault('sideshow.orders.unknown_product.fields.size.required', 'true')
        self.config.setdefault('sideshow.orders.unknown_product.fields.unit_price_reg.required', 'true')
        fields = view.get_pending_product_required_fields()
        self.assertEqual(fields, ['brand_name', 'size', 'unit_price_reg'])

    def test_get_dept_item_discounts(self):
        model = self.app.model
        view = self.make_view()

        with patch.object(view, 'Session', return_value=self.session):

            # empty list by default
            discounts = view.get_dept_item_discounts()
            self.assertEqual(discounts, [])

            # mock settings
            self.app.save_setting(self.session, 'sideshow.orders.departments.5.name', 'Bulk')
            self.app.save_setting(self.session, 'sideshow.orders.departments.5.default_item_discount', '15')
            self.app.save_setting(self.session, 'sideshow.orders.departments.6.name', 'Produce')
            self.app.save_setting(self.session, 'sideshow.orders.departments.6.default_item_discount', '5')
            discounts = view.get_dept_item_discounts()
            self.assertEqual(len(discounts), 2)
            self.assertEqual(discounts[0], {
                'department_id': '5',
                'department_name': 'Bulk',
                'default_item_discount': '15',
            })
            self.assertEqual(discounts[1], {
                'department_id': '6',
                'department_name': 'Produce',
                'default_item_discount': '5',
            })

            # invalid setting
            self.app.save_setting(self.session, 'sideshow.orders.departments.I.N.V.A.L.I.D.name', 'Bad News')
            self.app.save_setting(self.session, 'sideshow.orders.departments.I.N.V.A.L.I.D.default_item_discount', '42')
            discounts = view.get_dept_item_discounts()
            self.assertEqual(len(discounts), 2)
            self.assertEqual(discounts[0], {
                'department_id': '5',
                'department_name': 'Bulk',
                'default_item_discount': '15',
            })
            self.assertEqual(discounts[1], {
                'department_id': '6',
                'department_name': 'Produce',
                'default_item_discount': '5',
            })

    def test_get_context_customer(self):
        self.pyramid_config.add_route('orders', '/orders/')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()
        view.batch_handler = handler

        user = model.User(username='barney')
        self.session.add(user)

        # with external customer
        with patch.object(handler, 'use_local_customers', return_value=False):
            batch = handler.make_batch(self.session, created_by=user,
                                       customer_id=42, customer_name='Fred Flintstone',
                                       phone_number='555-1234', email_address='fred@mailinator.com')
            self.session.add(batch)
            self.session.flush()
            context = view.get_context_customer(batch)
            self.assertEqual(context, {
                'store_id': None,
                'customer_is_known': True,
                'customer_id': 42,
                'customer_name': 'Fred Flintstone',
                'phone_number': '555-1234',
                'email_address': 'fred@mailinator.com',
            })

        # with local customer
        local = model.LocalCustomer(full_name="Betty Boop")
        self.session.add(local)
        batch = handler.make_batch(self.session, created_by=user,
                                   local_customer=local, customer_name='Betty Boop',
                                   phone_number='555-8888')
        self.session.add(batch)
        self.session.flush()
        context = view.get_context_customer(batch)
        self.assertEqual(context, {
            'store_id': None,
            'customer_is_known': True,
            'customer_id': local.uuid.hex,
            'customer_name': 'Betty Boop',
            'phone_number': '555-8888',
            'email_address': None,
        })

        # with pending customer
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        handler.set_customer(batch, dict(
            full_name="Fred Flintstone",
            first_name="Fred", last_name="Flintstone",
            phone_number='555-1234', email_address='fred@mailinator.com',
        ))
        self.session.flush()
        context = view.get_context_customer(batch)
        self.assertEqual(context, {
            'store_id': None,
            'customer_is_known': False,
            'customer_id': None,
            'customer_name': 'Fred Flintstone',
            'phone_number': '555-1234',
            'email_address': 'fred@mailinator.com',
            'new_customer_full_name': 'Fred Flintstone',
            'new_customer_first_name': 'Fred',
            'new_customer_last_name': 'Flintstone',
            'new_customer_phone': '555-1234',
            'new_customer_email': 'fred@mailinator.com',
        })

        # with no customer
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.session.flush()
        context = view.get_context_customer(batch)
        self.assertEqual(context, {
            'store_id': None,
            'customer_is_known': True, # nb. this is for UI default
            'customer_id': None,
            'customer_name': None,
            'phone_number': None,
            'email_address': None,
        })

    def test_start_over(self):
        self.pyramid_config.add_route('orders.create', '/orders/new')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):

                    batch = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 1)
                    result = view.start_over(batch)
                    self.assertIsInstance(result, HTTPFound)
                    self.session.flush()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 0)

    def test_cancel_order(self):
        self.pyramid_config.add_route('orders', '/orders/')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):

                    batch = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 1)
                    result = view.cancel_order(batch)
                    self.assertIsInstance(result, HTTPFound)
                    self.session.flush()
                    self.assertEqual(self.session.query(model.NewOrderBatch).count(), 0)

    def test_set_store(self):
        model = self.app.model
        view = self.make_view()
        handler = NewOrderBatchHandler(self.config)

        user = model.User(username='barney')
        self.session.add(user)
        self.session.flush()

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):

                    batch = view.get_current_batch()
                    self.assertIsNone(batch.store_id)

                    # store_id is required
                    result = view.set_store(batch, {})
                    self.assertEqual(result, {'error': "Must provide store_id"})
                    result = view.set_store(batch, {'store_id': ''})
                    self.assertEqual(result, {'error': "Must provide store_id"})

                    # store_id is set on batch
                    result = view.set_store(batch, {'store_id': '042'})
                    self.assertEqual(batch.store_id, '042')
                    self.assertIn('store_id', result)
                    self.assertEqual(result['store_id'], '042')

    def test_assign_customer(self):
        self.pyramid_config.add_route('orders.create', '/orders/new')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        weirdal = model.LocalCustomer(full_name="Weird Al")
        self.session.add(weirdal)
        self.session.flush()

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()

                    # normal
                    self.assertIsNone(batch.local_customer)
                    self.assertIsNone(batch.pending_customer)
                    context = view.assign_customer(batch, {'customer_id': weirdal.uuid.hex})
                    self.assertIsNone(batch.pending_customer)
                    self.assertIs(batch.local_customer, weirdal)
                    self.assertEqual(context, {
                        'store_id': None,
                        'customer_is_known': True,
                        'customer_id': weirdal.uuid.hex,
                        'customer_name': 'Weird Al',
                        'phone_number': None,
                        'email_address': None,
                    })

                    # missing customer_id
                    context = view.assign_customer(batch, {})
                    self.assertEqual(context, {'error': "Must provide customer_id"})

    def test_unassign_customer(self):
        self.pyramid_config.add_route('orders.create', '/orders/new')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.flush()

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()
                    view.set_pending_customer(batch, {'first_name': 'Jack',
                                                      'last_name': 'Black'})

                    # normal
                    self.assertIsNone(batch.local_customer)
                    self.assertIsNotNone(batch.pending_customer)
                    self.assertEqual(batch.customer_name, 'Jack Black')
                    context = view.unassign_customer(batch, {})
                    # nb. pending record remains, but not used
                    self.assertIsNotNone(batch.pending_customer)
                    self.assertIsNone(batch.customer_name)
                    self.assertIsNone(batch.local_customer)
                    self.assertEqual(context, {
                        'store_id': None,
                        'customer_is_known': True,
                        'customer_id': None,
                        'customer_name': None,
                        'phone_number': None,
                        'email_address': None,
                        'new_customer_full_name': 'Jack Black',
                        'new_customer_first_name': 'Jack',
                        'new_customer_last_name': 'Black',
                        'new_customer_phone': None,
                        'new_customer_email': None,
                    })

    def test_set_pending_customer(self):
        self.pyramid_config.add_route('orders.create', '/orders/new')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        data = {
            'first_name': 'Fred',
            'last_name': 'Flintstone',
            'phone_number': '555-1234',
            'email_address': 'fred@mailinator.com',
        }

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()
                    self.session.flush()

                    # normal
                    self.assertIsNone(batch.pending_customer)
                    context = view.set_pending_customer(batch, data)
                    self.assertIsInstance(batch.pending_customer, model.PendingCustomer)
                    self.assertEqual(context, {
                        'store_id': None,
                        'customer_is_known': False,
                        'customer_id': None,
                        'customer_name': 'Fred Flintstone',
                        'phone_number': '555-1234',
                        'email_address': 'fred@mailinator.com',
                        'new_customer_full_name': 'Fred Flintstone',
                        'new_customer_first_name': 'Fred',
                        'new_customer_last_name': 'Flintstone',
                        'new_customer_phone': '555-1234',
                        'new_customer_email': 'fred@mailinator.com',
                    })

    def test_get_product_info(self):
        model = self.app.model
        handler = self.make_handler()
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        local = model.LocalProduct(scancode='07430500132',
                                   brand_name='Bragg',
                                   description='Vinegar',
                                   size='32oz',
                                   case_size=12,
                                   unit_price_reg=decimal.Decimal('5.99'))
        self.session.add(local)
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):
            with patch.object(view, 'batch_handler', create=True, new=handler):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()

                    # typical, for local product
                    context = view.get_product_info(batch, {'product_id': local.uuid.hex})
                    self.assertEqual(context['product_id'], local.uuid.hex)
                    self.assertEqual(context['scancode'], '07430500132')
                    self.assertEqual(context['brand_name'], 'Bragg')
                    self.assertEqual(context['description'], 'Vinegar')
                    self.assertEqual(context['size'], '32oz')
                    self.assertEqual(context['full_description'], 'Bragg Vinegar 32oz')
                    self.assertEqual(context['case_size'], 12)
                    self.assertEqual(context['unit_price_reg'], 5.99)

                    # error if no product_id
                    context = view.get_product_info(batch, {})
                    self.assertEqual(context, {'error': "Must specify a product ID"})

                    # error if product not found
                    mock_uuid = self.app.make_true_uuid()
                    self.assertRaises(ValueError, view.get_product_info,
                                      batch, {'product_id': mock_uuid.hex})

                    with patch.object(handler, 'use_local_products', return_value=False):

                        # external lookup not implemented by default
                        self.assertRaises(NotImplementedError, view.get_product_info,
                                          batch, {'product_id': '42'})

                        # external lookup may return its own error
                        with patch.object(handler, 'get_product_info_external',
                                          return_value={'error': "something smells fishy"}):
                            context = view.get_product_info(batch, {'product_id': '42'})
                            self.assertEqual(context, {'error': "something smells fishy"})

    def test_get_past_products(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        handler = view.batch_handler

        user = model.User(username='barney')
        self.session.add(user)
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.session.flush()

        # (nb. this all assumes local customers and products)

        # error if no customer
        self.assertRaises(ValueError, view.get_past_products, batch, {})

        # empty history for customer
        customer = model.LocalCustomer(full_name='Fred Flintstone')
        batch.local_customer = customer
        self.session.flush()
        products = view.get_past_products(batch, {})
        self.assertEqual(len(products), 0)

        # mock historical order
        order = model.Order(order_id=42, local_customer=customer, created_by=user)
        product = model.LocalProduct(scancode='07430500132', description='Vinegar',
                                     unit_price_reg=5.99, case_size=12)
        item = model.OrderItem(local_product=product, order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                               status_code=enum.ORDER_ITEM_STATUS_READY)
        order.items.append(item)
        self.session.add(order)
        self.session.flush()
        self.session.refresh(product)

        # that should now be returned
        products = view.get_past_products(batch, {})
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['product_id'], product.uuid.hex)
        self.assertEqual(products[0]['scancode'], '07430500132')
        self.assertEqual(products[0]['description'], 'Vinegar')
        # nb. this is a float, since result is JSON-safe
        self.assertEqual(products[0]['case_price_quoted'], 71.88)
        self.assertEqual(products[0]['case_price_quoted_display'], '$71.88')

    def test_add_item(self):
        model = self.app.model
        enum = self.app.enum
        self.config.setdefault('sideshow.orders.allow_item_discounts', 'true')
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        data = {
            'product_info': {
                'scancode': '07430500132',
                'brand_name': 'Bragg',
                'description': 'Vinegar',
                'size': '32oz',
                'unit_price_reg': 5.99,
            },
            'order_qty': 1,
            'order_uom': enum.ORDER_UOM_UNIT,
            'discount_percent': 10,
        }

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(len(batch.rows), 0)

                    # normal pending product
                    result = view.add_item(batch, data)
                    self.assertIn('batch', result)
                    self.assertIn('row', result)
                    self.session.flush()
                    self.assertEqual(len(batch.rows), 1)
                    row = batch.rows[0]
                    self.assertIsInstance(row.pending_product, model.PendingProduct)

                    # external product not yet supported
                    with patch.object(handler, 'use_local_products', return_value=False):
                        with patch.dict(data, product_info='42'):
                            self.assertRaises(NotImplementedError, view.add_item, batch, data)

    def test_update_item(self):
        model = self.app.model
        enum = self.app.enum
        self.config.setdefault('sideshow.orders.allow_item_discounts', 'true')
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        data = {
            'product_info': {
                'scancode': '07430500132',
                'brand_name': 'Bragg',
                'description': 'Vinegar',
                'size': '32oz',
                'unit_price_reg': 5.99,
                'case_size': 12,
            },
            'order_qty': 1,
            'order_uom': enum.ORDER_UOM_CASE,
            'discount_percent': 15,
        }

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(len(batch.rows), 0)

                    # add row w/ pending product
                    view.add_item(batch, data)
                    self.session.flush()
                    row = batch.rows[0]
                    self.assertIsInstance(row.pending_product, model.PendingProduct)
                    self.assertEqual(row.unit_price_quoted, decimal.Decimal('5.99'))

                    # missing row uuid
                    result = view.update_item(batch, data)
                    self.assertEqual(result, {'error': "Must specify row UUID"})

                    # row not found
                    with patch.dict(data, uuid=self.app.make_true_uuid()):
                        result = view.update_item(batch, data)
                        self.assertEqual(result, {'error': "Row not found"})

                    # row for wrong batch
                    batch2 = handler.make_batch(self.session, created_by=user)
                    self.session.add(batch2)
                    row2 = handler.make_row(order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
                    handler.add_row(batch2, row2)
                    self.session.flush()
                    with patch.dict(data, uuid=row2.uuid):
                        result = view.update_item(batch, data)
                        self.assertEqual(result, {'error': "Row is for wrong batch"})

                    # true product not yet supported
                    with patch.object(handler, 'use_local_products', return_value=False):
                        self.assertRaises(NotImplementedError, view.update_item, batch, {
                            'uuid': row.uuid,
                            'product_info': '42',
                            'order_qty': 1,
                            'order_uom': enum.ORDER_UOM_UNIT,
                        })

                    # update row, pending product
                    with patch.dict(data, uuid=row.uuid, order_qty=2):
                        with patch.dict(data['product_info'], scancode='07430500116'):
                            self.assertEqual(row.product_scancode, '07430500132')
                            self.assertEqual(row.order_qty, 1)
                            result = view.update_item(batch, data)
                            self.assertEqual(sorted(result), ['batch', 'row'])
                            self.assertEqual(row.product_scancode, '07430500116')
                            self.assertEqual(row.order_qty, 2)
                            self.assertEqual(row.pending_product.scancode, '07430500116')
                            self.assertEqual(result['row']['product_scancode'], '07430500116')
                            self.assertEqual(result['row']['order_qty'], 2)

    def test_delete_item(self):
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        data = {
            'product_info': {
                'scancode': '07430500132',
                'brand_name': 'Bragg',
                'description': 'Vinegar',
                'size': '32oz',
                'unit_price_reg': 5.99,
                'case_size': 12,
            },
            'order_qty': 1,
            'order_uom': enum.ORDER_UOM_CASE,
        }

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()
                    self.session.flush()
                    self.assertEqual(len(batch.rows), 0)

                    # add row w/ pending product
                    view.add_item(batch, data)
                    self.session.flush()
                    row = batch.rows[0]
                    self.assertIsInstance(row.pending_product, model.PendingProduct)
                    self.assertEqual(row.unit_price_quoted, decimal.Decimal('5.99'))

                    # missing row uuid
                    result = view.delete_item(batch, data)
                    self.assertEqual(result, {'error': "Must specify a row UUID"})

                    # row not found
                    with patch.dict(data, uuid=self.app.make_true_uuid()):
                        result = view.delete_item(batch, data)
                        self.assertEqual(result, {'error': "Row not found"})

                    # row for wrong batch
                    batch2 = handler.make_batch(self.session, created_by=user)
                    self.session.add(batch2)
                    row2 = handler.make_row(order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
                    handler.add_row(batch2, row2)
                    self.session.flush()
                    with patch.dict(data, uuid=row2.uuid):
                        result = view.delete_item(batch, data)
                        self.assertEqual(result, {'error': "Row is for wrong batch"})

                    # row is deleted
                    data['uuid'] = row.uuid
                    self.assertEqual(len(batch.rows), 1)
                    self.assertEqual(batch.row_count, 1)
                    result = view.delete_item(batch, data)
                    self.assertEqual(sorted(result), ['batch'])
                    self.session.refresh(batch)
                    self.assertEqual(len(batch.rows), 0)
                    self.assertEqual(batch.row_count, 0)

    def test_submit_order(self):
        self.pyramid_config.add_route('orders.view', '/orders/{uuid}')
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        self.session.commit()

        data = {
            'product_info': {
                'scancode': '07430500132',
                'brand_name': 'Bragg',
                'description': 'Vinegar',
                'size': '32oz',
                'unit_price_reg': 5.99,
                'case_size': 12,
            },
            'order_qty': 1,
            'order_uom': enum.ORDER_UOM_CASE,
        }

        with patch.object(view, 'batch_handler', create=True, new=handler):
            with patch.object(view, 'Session', return_value=self.session):
                with patch.object(self.request, 'user', new=user):
                    batch = view.get_current_batch()
                    self.assertEqual(len(batch.rows), 0)

                    # add row w/ pending product
                    view.add_item(batch, data)
                    self.assertEqual(len(batch.rows), 1)
                    row = batch.rows[0]
                    self.assertIsInstance(row.pending_product, model.PendingProduct)
                    self.assertEqual(row.unit_price_quoted, decimal.Decimal('5.99'))

                    # execute not allowed yet (no customer)
                    result = view.submit_order(batch, {})
                    self.assertEqual(result, {'error': "Must assign the customer"})

                    # execute not allowed yet (no phone number)
                    view.set_pending_customer(batch, {'full_name': 'John Doe'})
                    result = view.submit_order(batch, {})
                    self.assertEqual(result, {'error': "Customer phone number is required"})

                    # submit/execute ok
                    view.set_pending_customer(batch, {'full_name': 'John Doe',
                                                      'phone_number': '555-1234'})
                    result = view.submit_order(batch, {})
                    self.assertEqual(sorted(result), ['next_url'])
                    self.assertIn('/orders/', result['next_url'])

                    # error (already executed)
                    result = view.submit_order(batch, {})
                    self.assertEqual(result, {
                        'error': f"ValueError: batch has already been executed: {batch}",
                    })

    def test_normalize_batch(self):
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        pending = {
            'scancode': '07430500132',
            'brand_name': 'Bragg',
            'description': 'Vinegar',
            'size': '32oz',
            'unit_price_reg': 5.99,
            'case_size': 12,
        }
        row = handler.add_item(batch, pending, 1, enum.ORDER_UOM_CASE)
        self.session.commit()

        data = view.normalize_batch(batch)
        self.assertEqual(data, {
            'uuid': batch.uuid.hex,
            'total_price': '71.880',
            'total_price_display': '$71.88',
            'status_code': None,
            'status_text': None,
        })

    def test_normalize_row(self):
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()
        view.batch_handler = handler

        user = model.User(username='barney')
        self.session.add(user)
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        self.session.flush()

        # add 1st row w/ pending product
        pending = {
            'scancode': '07430500132',
            'brand_name': 'Bragg',
            'description': 'Vinegar',
            'size': '32oz',
            'unit_price_reg': 5.99,
            'case_size': 12,
            'vendor_name': 'Acme Warehouse',
            'vendor_item_code': '1234',
        }
        row1 = handler.add_item(batch, pending, 2, enum.ORDER_UOM_CASE)

        # typical, pending product
        data = view.normalize_row(row1)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['uuid'], row1.uuid.hex)
        self.assertEqual(data['sequence'], 1)
        self.assertIsNone(data['product_id'])
        self.assertEqual(data['product_scancode'], '07430500132')
        self.assertEqual(data['product_full_description'], 'Bragg Vinegar 32oz')
        self.assertEqual(data['case_size'], 12)
        self.assertEqual(data['vendor_name'], 'Acme Warehouse')
        self.assertEqual(data['order_qty'], 2)
        self.assertEqual(data['order_uom'], 'CS')
        self.assertEqual(data['order_qty_display'], '2 Cases (&times; 12 = 24 Units)')
        self.assertEqual(data['unit_price_reg'], 5.99)
        self.assertEqual(data['unit_price_reg_display'], '$5.99')
        self.assertNotIn('unit_price_sale', data)
        self.assertNotIn('unit_price_sale_display', data)
        self.assertNotIn('sale_ends', data)
        self.assertNotIn('sale_ends_display', data)
        self.assertEqual(data['unit_price_quoted'], 5.99)
        self.assertEqual(data['unit_price_quoted_display'], '$5.99')
        self.assertEqual(data['case_price_quoted'], 71.88)
        self.assertEqual(data['case_price_quoted_display'], '$71.88')
        self.assertEqual(data['total_price'], 143.76)
        self.assertEqual(data['total_price_display'], '$143.76')
        self.assertIsNone(data['special_order'])
        self.assertEqual(data['status_code'], row1.STATUS_OK)
        self.assertEqual(data['pending_product'], {
            'uuid': row1.pending_product_uuid.hex,
            'scancode': '07430500132',
            'brand_name': 'Bragg',
            'description': 'Vinegar',
            'size': '32oz',
            'department_id': None,
            'department_name': None,
            'unit_price_reg': 5.99,
            'vendor_name': 'Acme Warehouse',
            'vendor_item_code': '1234',
            'unit_cost': None,
            'case_size': 12.0,
            'notes': None,
            'special_order': None,
        })

        # the next few tests will morph 1st row..

        # unknown case size
        row1.pending_product.case_size = None
        handler.refresh_row(row1)
        self.session.flush()
        data = view.normalize_row(row1)
        self.assertIsNone(data['case_size'])
        self.assertEqual(data['order_qty_display'], '2 Cases (&times; ?? = ?? Units)')

        # order by unit
        row1.order_uom = enum.ORDER_UOM_UNIT
        handler.refresh_row(row1)
        self.session.flush()
        data = view.normalize_row(row1)
        self.assertEqual(data['order_uom'], enum.ORDER_UOM_UNIT)
        self.assertEqual(data['order_qty_display'], '2 Units')

        # item on sale
        row1.pending_product.case_size = 12
        row1.unit_price_sale = decimal.Decimal('5.19')
        row1.sale_ends = datetime.datetime(2099, 1, 5, 20, 32)
        handler.refresh_row(row1)
        self.session.flush()
        data = view.normalize_row(row1)
        self.assertEqual(data['unit_price_sale'], 5.19)
        self.assertEqual(data['unit_price_sale_display'], '$5.19')
        self.assertEqual(data['sale_ends'], '2099-01-05 20:32:00')
        self.assertEqual(data['sale_ends_display'], '2099-01-05')
        self.assertEqual(data['unit_price_quoted'], 5.19)
        self.assertEqual(data['unit_price_quoted_display'], '$5.19')
        self.assertEqual(data['case_price_quoted'], 62.28)
        self.assertEqual(data['case_price_quoted_display'], '$62.28')

        # add 2nd row w/ local product
        local = model.LocalProduct(brand_name="Lay's",
                                   description="Potato Chips",
                                   vendor_name='Acme Distribution',
                                   unit_price_reg=3.29)
        self.session.add(local)
        self.session.flush()
        row2 = handler.add_item(batch, local.uuid.hex, 1, enum.ORDER_UOM_UNIT)

        # typical, local product
        data = view.normalize_row(row2)
        self.assertEqual(data['uuid'], row2.uuid.hex)
        self.assertEqual(data['sequence'], 2)
        self.assertEqual(data['product_id'], local.uuid.hex)
        self.assertIsNone(data['product_scancode'])
        self.assertEqual(data['product_full_description'], "Lay's Potato Chips")
        self.assertIsNone(data['case_size'])
        self.assertEqual(data['vendor_name'], 'Acme Distribution')
        self.assertEqual(data['order_qty'], 1)
        self.assertEqual(data['order_uom'], 'EA')
        self.assertEqual(data['order_qty_display'], '1 Units')
        self.assertEqual(data['unit_price_reg'], 3.29)
        self.assertEqual(data['unit_price_reg_display'], '$3.29')
        self.assertNotIn('unit_price_sale', data)
        self.assertNotIn('unit_price_sale_display', data)
        self.assertNotIn('sale_ends', data)
        self.assertNotIn('sale_ends_display', data)
        self.assertEqual(data['unit_price_quoted'], 3.29)
        self.assertEqual(data['unit_price_quoted_display'], '$3.29')
        self.assertIsNone(data['case_price_quoted'])
        self.assertEqual(data['case_price_quoted_display'], '')
        self.assertEqual(data['total_price'], 3.29)
        self.assertEqual(data['total_price_display'], '$3.29')
        self.assertIsNone(data['special_order'])
        self.assertEqual(data['status_code'], row2.STATUS_OK)
        self.assertNotIn('pending_product', data)

        # the next few tests will morph 2nd row..

        def refresh_external(row):
            row.product_scancode = '012345'
            row.product_brand = 'Acme'
            row.product_description = 'Bricks'
            row.product_size = '1 ton'
            row.product_weighed = True
            row.department_id = 1
            row.department_name = "Bricks & Mortar"
            row.special_order = False
            row.vendor_name = 'Acme Distributors'
            row.vendor_item_code = '1234'
            row.case_size = None
            row.unit_cost = decimal.Decimal('599.99')
            row.unit_price_reg = decimal.Decimal('999.99')

        # typical, external product
        with patch.object(handler, 'use_local_products', return_value=False):
            with patch.object(handler, 'refresh_row_from_external_product', new=refresh_external):
                handler.update_item(row2, '42', 1, enum.ORDER_UOM_UNIT)
                data = view.normalize_row(row2)
        self.assertEqual(data['uuid'], row2.uuid.hex)
        self.assertEqual(data['sequence'], 2)
        self.assertEqual(data['product_id'], '42')
        self.assertEqual(data['product_scancode'], '012345')
        self.assertEqual(data['product_full_description'], 'Acme Bricks 1 ton')
        self.assertIsNone(data['case_size'])
        self.assertEqual(data['vendor_name'], 'Acme Distributors')
        self.assertEqual(data['vendor_item_code'], '1234')
        self.assertEqual(data['order_qty'], 1)
        self.assertEqual(data['order_uom'], 'EA')
        self.assertEqual(data['order_qty_display'], '1 Units')
        self.assertEqual(data['unit_price_reg'], 999.99)
        self.assertEqual(data['unit_price_reg_display'], '$999.99')
        self.assertNotIn('unit_price_sale', data)
        self.assertNotIn('unit_price_sale_display', data)
        self.assertNotIn('sale_ends', data)
        self.assertNotIn('sale_ends_display', data)
        self.assertEqual(data['unit_price_quoted'], 999.99)
        self.assertEqual(data['unit_price_quoted_display'], '$999.99')
        self.assertIsNone(data['case_price_quoted'])
        self.assertEqual(data['case_price_quoted_display'], '')
        self.assertEqual(data['total_price'], 999.99)
        self.assertEqual(data['total_price_display'], '$999.99')
        self.assertFalse(data['special_order'])
        self.assertEqual(data['status_code'], row2.STATUS_OK)
        self.assertNotIn('pending_product', data)

    def test_get_instance_title(self):
        model = self.app.model
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        self.session.add(order)
        self.session.flush()

        title = view.get_instance_title(order)
        self.assertEqual(title, "#42 for Fred Flintstone")

    def test_configure_form(self):
        model = self.app.model
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        self.session.commit()

        # viewing (no customer)
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=order)
            # nb. this is to avoid include/exclude ambiguity
            form.remove('items')
            # nb. store_id gets hidden by default
            form.append('store_id')
            self.assertIn('store_id', form)
            view.configure_form(form)
            self.assertNotIn('store_id', form)
            schema = form.get_schema()
            self.assertIn('pending_customer', form)
            self.assertIsInstance(schema['total_price'].typ, WuttaMoney)

        # assign local customer
        local = model.LocalCustomer(first_name='Jack', last_name='Black',
                                    phone_number='555-1234')
        self.session.add(local)
        self.session.flush()

        # nb. from now on we include store_id
        self.config.setdefault('sideshow.orders.expose_store_id', 'true')

        # viewing (local customer)
        with patch.object(view, 'viewing', new=True):
            with patch.object(order, 'local_customer', new=local):
                form = view.make_form(model_instance=order)
                # nb. this is to avoid include/exclude ambiguity
                form.remove('items')
                # nb. store_id will now remain
                form.append('store_id')
                self.assertIn('store_id', form)
                view.configure_form(form)
                self.assertIn('store_id', form)
                self.assertNotIn('pending_customer', form)
                schema = form.get_schema()
                self.assertIsInstance(schema['total_price'].typ, WuttaMoney)

        # local customer is hidden if missing when customer_id is set
        with patch.object(view, 'viewing', new=True):
            with patch.object(order, 'customer_id', new='42'):
                form = view.make_form(model_instance=order)
                # nb. this is to avoid include/exclude ambiguity
                form.remove('items')
                view.configure_form(form)
                self.assertNotIn('local_customer', form)

    def test_get_xref_buttons(self):
        self.pyramid_config.add_route('neworder_batches.view', '/batch/neworder/{uuid}')
        model = self.app.model
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):

            # nb. this requires perm to view batch
            with patch.object(self.request, 'is_root', new=True):

                # order has no batch, so no buttons
                buttons = view.get_xref_buttons(order)
                self.assertEqual(buttons, [])

                # mock up a batch to get a button
                batch = handler.make_batch(self.session,
                                           id=order.order_id,
                                           created_by=user,
                                           executed=datetime.datetime.now(),
                                           executed_by=user)
                self.session.add(batch)
                self.session.flush()
                buttons = view.get_xref_buttons(order)
                self.assertEqual(len(buttons), 1)
                button = buttons[0]
                self.assertIn("View the Batch", button)

    def test_get_row_grid_data(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        self.session.flush()
        order.items.append(model.OrderItem(product_id='07430500132',
                                           product_scancode='07430500132',
                                           order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                           status_code=enum.ORDER_ITEM_STATUS_INITIATED))
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):
            query = view.get_row_grid_data(order)
            self.assertIsInstance(query, orm.Query)
            items = query.all()
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].product_scancode, '07430500132')

    def test_configure_row_grid(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        self.session.flush()
        order.items.append(model.OrderItem(product_id='07430500132',
                                           product_scancode='07430500132',
                                           order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                           status_code=enum.ORDER_ITEM_STATUS_INITIATED))
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):
            grid = view.make_grid(model_class=model.OrderItem, data=order.items)
            self.assertNotIn('product_scancode', grid.linked_columns)
            view.configure_row_grid(grid)
            self.assertIn('product_scancode', grid.linked_columns)

    def test_row_grid_row_class(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        # typical
        item = model.OrderItem(status_code=enum.ORDER_ITEM_STATUS_READY)
        self.assertIsNone(view.row_grid_row_class(item, {}, 1))

        # warning
        item = model.OrderItem(status_code=enum.ORDER_ITEM_STATUS_CANCELED)
        self.assertEqual(view.row_grid_row_class(item, {}, 1), 'has-background-warning')

    def test_render_status_code(self):
        enum = self.app.enum
        view = self.make_view()
        result = view.render_status_code(None, None, enum.ORDER_ITEM_STATUS_INITIATED)
        self.assertEqual(result, "initiated")
        self.assertEqual(result, enum.ORDER_ITEM_STATUS[enum.ORDER_ITEM_STATUS_INITIATED])

    def test_get_row_action_url_view(self):
        self.pyramid_config.add_route('order_items.view', '/order-items/{uuid}')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        self.session.flush()
        item = model.OrderItem(product_id='07430500132',
                               product_scancode='07430500132',
                               order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                               status_code=enum.ORDER_ITEM_STATUS_INITIATED)
        order.items.append(item)
        self.session.flush()

        url = view.get_row_action_url_view(item, 0)
        self.assertIn(f'/order-items/{item.uuid}', url)

    def test_configure(self):
        self.pyramid_config.add_route('home', '/')
        self.pyramid_config.add_route('login', '/auth/login')
        self.pyramid_config.add_route('orders', '/orders/')
        model = self.app.model
        view = self.make_view()

        self.app.save_setting(self.session, 'sideshow.orders.departments.5.name', 'Bulk')
        self.app.save_setting(self.session, 'sideshow.orders.departments.5.default_item_discount', '15')
        self.app.save_setting(self.session, 'sideshow.orders.departments.6.name', 'Produce')
        self.app.save_setting(self.session, 'sideshow.orders.departments.6.default_item_discount', '5')
        self.session.commit()

        with patch.object(view, 'Session', return_value=self.session):
            with patch.multiple(self.config, usedb=True, preferdb=True):

                # sanity check
                allowed = self.config.get_bool('sideshow.orders.allow_unknown_products',
                                               session=self.session)
                self.assertIsNone(allowed)
                self.assertEqual(self.session.query(model.Setting).count(), 4)
                discounts = view.get_dept_item_discounts()
                self.assertEqual(len(discounts), 2)
                self.assertEqual(discounts[0], {
                    'department_id': '5',
                    'department_name': 'Bulk',
                    'default_item_discount': '15',
                })
                self.assertEqual(discounts[1], {
                    'department_id': '6',
                    'department_name': 'Produce',
                    'default_item_discount': '5',
                })

                # fetch initial page
                response = view.configure()
                self.assertIsInstance(response, Response)
                self.assertNotIsInstance(response, HTTPFound)
                self.session.flush()
                allowed = self.config.get_bool('sideshow.orders.allow_unknown_products',
                                               session=self.session)
                self.assertIsNone(allowed)
                self.assertEqual(self.session.query(model.Setting).count(), 4)

                # post new settings
                with patch.multiple(self.request, create=True,
                                    method='POST',
                                    POST={
                                        'sideshow.orders.allow_unknown_products': 'true',
                                        'dept_item_discounts': json.dumps([{
                                            'department_id': '5',
                                            'department_name': 'Grocery',
                                            'default_item_discount': 10,
                                        }])
                                    }):
                    response = view.configure()
                self.assertIsInstance(response, HTTPFound)
                self.session.flush()
                allowed = self.config.get_bool('sideshow.orders.allow_unknown_products',
                                               session=self.session)
                self.assertTrue(allowed)
                self.assertTrue(self.session.query(model.Setting).count() > 1)
                discounts = view.get_dept_item_discounts()
                self.assertEqual(len(discounts), 1)
                self.assertEqual(discounts[0], {
                    'department_id': '5',
                    'department_name': 'Grocery',
                    'default_item_discount': '10',
                })


class OrderItemViewTestMixin:

    def test_common_get_fallback_templates(self):
        view = self.make_view()

        templates = view.get_fallback_templates('view')
        self.assertEqual(templates, ['/order-items/view.mako',
                                     '/master/view.mako'])

    def test_common_get_query(self):
        view = self.make_view()
        query = view.get_query(session=self.session)
        self.assertIsInstance(query, orm.Query)

    def test_common_configure_grid(self):
        model = self.app.model
        view = self.make_view()

        # store_id is removed by default
        grid = view.make_grid(model_class=model.OrderItem)
        grid.append('store_id')
        self.assertIn('store_id', grid.columns)
        view.configure_grid(grid)
        self.assertNotIn('store_id', grid.columns)

        # store_id is shown if configured
        self.config.setdefault('sideshow.orders.expose_store_id', 'true')
        grid = view.make_grid(model_class=model.OrderItem)
        grid.append('store_id')
        self.assertIn('store_id', grid.columns)
        view.configure_grid(grid)
        self.assertIn('store_id', grid.columns)

    def test_common_render_order_attr(self):
        model = self.app.model
        view = self.make_view()
        order = model.Order(order_id=42)
        item = model.OrderItem()
        order.items.append(item)
        self.assertEqual(view.render_order_attr(item, 'order_id', None), 42)

    def test_common_render_status_code(self):
        enum = self.app.enum
        view = self.make_view()
        self.assertEqual(view.render_status_code(None, None, enum.ORDER_ITEM_STATUS_INITIATED),
                         'initiated')

    def test_common_grid_row_class(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        # typical
        item = model.OrderItem(status_code=enum.ORDER_ITEM_STATUS_READY)
        self.assertIsNone(view.grid_row_class(item, {}, 1))

        # warning
        item = model.OrderItem(status_code=enum.ORDER_ITEM_STATUS_CANCELED)
        self.assertEqual(view.grid_row_class(item, {}, 1), 'has-background-warning')

    def test_common_configure_form(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        item = model.OrderItem(status_code=enum.ORDER_ITEM_STATUS_INITIATED)

        # viewing, w/ pending product
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=item)
            view.configure_form(form)
            schema = form.get_schema()
            self.assertIsInstance(schema['order'].typ, OrderRef)
            self.assertIn('pending_product', form)
            self.assertIsInstance(schema['pending_product'].typ, PendingProductRef)

        # viewing, w/ local product
        local = model.LocalProduct()
        item.local_product = local
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=item)
            view.configure_form(form)
            schema = form.get_schema()
            self.assertIsInstance(schema['order'].typ, OrderRef)
            self.assertNotIn('pending_product', form)

    def test_common_get_template_context(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        order = model.Order()
        item = model.OrderItem(order_qty=2, order_uom=enum.ORDER_UOM_CASE, case_size=8)
        order.items.append(item)

        with patch.object(self.request, 'is_root', new=True):
            with patch.object(view, 'viewing', new=True):
                form = view.make_model_form(model_instance=item)
                context = view.get_template_context({'instance': item, 'form': form})
                self.assertIn('item', context)
                self.assertIs(context['item'], item)
                self.assertIn('order', context)
                self.assertIs(context['order'], order)
                self.assertIn('order_qty_uom_text', context)
                self.assertEqual(context['order_qty_uom_text'], "2 Cases (&times; 8 = 16 Units)")

    def test_common_render_event_note(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        # typical
        event = model.OrderItemEvent(type_code=enum.ORDER_ITEM_EVENT_READY, note='testing')
        result = view.render_event_note(event, 'note', 'testing')
        self.assertEqual(result, 'testing')

        # user note
        event = model.OrderItemEvent(type_code=enum.ORDER_ITEM_EVENT_NOTE_ADDED, note='testing2')
        result = view.render_event_note(event, 'note', 'testing2')
        self.assertNotEqual(result, 'testing2')
        self.assertIn('<span', result)
        self.assertIn('class="has-background-info-light"', result)
        self.assertIn('testing2', result)

    def test_common_get_xref_buttons(self):
        self.pyramid_config.add_route('orders.view', '/orders/{uuid}')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        item = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                               status_code=enum.ORDER_ITEM_STATUS_INITIATED)
        order.items.append(item)
        self.session.flush()

        # nb. this requires perms
        with patch.object(self.request, 'is_root', new=True):

            # one button by default
            buttons = view.get_xref_buttons(item)
            self.assertEqual(len(buttons), 1)
            self.assertIn("View the Order", buttons[0])

    def test_common_add_note(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        self.pyramid_config.add_route(f'{view.get_route_prefix()}.view',
                                      f'{view.get_url_prefix()}/{{uuid}}')

        user = model.User(username='barney')
        self.session.add(user)

        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        item = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                               status_code=enum.ORDER_ITEM_STATUS_INITIATED)
        order.items.append(item)
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):
            with patch.object(self.request, 'matchdict', new={'uuid': item.uuid}):
                with patch.object(self.request, 'POST', new={'note': 'testing'}):
                    self.assertEqual(len(item.events), 0)
                    result = view.add_note()
                    self.assertEqual(len(item.events), 1)
                    self.assertEqual(item.events[0].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)
                    self.assertEqual(item.events[0].note, 'testing')

    def test_common_change_status(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        self.pyramid_config.add_route(f'{view.get_route_prefix()}.view',
                                      f'{view.get_url_prefix()}/{{uuid}}')

        user = model.User(username='barney')
        self.session.add(user)

        order = model.Order(order_id=42, created_by=user)
        self.session.add(order)
        item = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                               status_code=enum.ORDER_ITEM_STATUS_INITIATED)
        order.items.append(item)
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):
            with patch.object(self.request, 'user', new=user):
                with patch.object(self.request, 'matchdict', new={'uuid': item.uuid}):

                    # just status change, no note
                    with patch.object(self.request, 'POST', new={
                            'new_status': enum.ORDER_ITEM_STATUS_PLACED}):
                        self.assertEqual(len(item.events), 0)
                        result = view.change_status()
                        self.assertIsInstance(result, HTTPFound)
                        self.assertFalse(self.request.session.peek_flash('error'))
                        self.assertEqual(len(item.events), 1)
                        self.assertEqual(item.events[0].type_code, enum.ORDER_ITEM_EVENT_STATUS_CHANGE)
                        self.assertEqual(item.events[0].note,
                                         'status changed from "initiated" to "placed"')

                    # status change plus note
                    with patch.object(self.request, 'POST', new={
                            'new_status': enum.ORDER_ITEM_STATUS_RECEIVED,
                            'note': 'check it out'}):
                        self.assertEqual(len(item.events), 1)
                        result = view.change_status()
                        self.assertIsInstance(result, HTTPFound)
                        self.assertFalse(self.request.session.peek_flash('error'))
                        self.assertEqual(len(item.events), 3)
                        self.assertEqual(item.events[0].type_code, enum.ORDER_ITEM_EVENT_STATUS_CHANGE)
                        self.assertEqual(item.events[0].note,
                                         'status changed from "initiated" to "placed"')
                        self.assertEqual(item.events[1].type_code, enum.ORDER_ITEM_EVENT_STATUS_CHANGE)
                        self.assertEqual(item.events[1].note,
                                         'status changed from "placed" to "received"')
                        self.assertEqual(item.events[2].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)
                        self.assertEqual(item.events[2].note, "check it out")

                    # invalid status
                    with patch.object(self.request, 'POST', new={'new_status': 23432143}):
                        self.assertEqual(len(item.events), 3)
                        result = view.change_status()
                        self.assertIsInstance(result, HTTPFound)
                        self.assertTrue(self.request.session.peek_flash('error'))
                        self.assertEqual(len(item.events), 3)


class TestOrderItemView(OrderItemViewTestMixin, WebTestCase):

    def make_view(self):
        return mod.OrderItemView(self.request)

    def test_get_order_items(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        self.pyramid_config.add_route('order_items', '/order-items/')

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_READY)
        order.items.append(item1)
        item2 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_READY)
        order.items.append(item2)
        self.session.add(order)
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):

            # no items found
            self.assertRaises(HTTPFound, view.get_order_items, None)
            self.assertRaises(HTTPFound, view.get_order_items, '')
            self.assertRaises(HTTPFound, view.get_order_items, [])
            self.assertRaises(HTTPFound, view.get_order_items, 'invalid')

            # list of UUID
            items = view.get_order_items([item1.uuid, item2.uuid])
            self.assertEqual(len(items), 2)
            self.assertIs(items[0], item1)
            self.assertIs(items[1], item2)

            # list of str
            items = view.get_order_items([item1.uuid.hex, item2.uuid.hex])
            self.assertEqual(len(items), 2)
            self.assertIs(items[0], item1)
            self.assertIs(items[1], item2)

            # comma-delimited str
            items = view.get_order_items(','.join([item1.uuid.hex, item2.uuid.hex]))
            self.assertEqual(len(items), 2)
            self.assertIs(items[0], item1)
            self.assertIs(items[1], item2)


class TestPlacementView(OrderItemViewTestMixin, WebTestCase):

    def make_view(self):
        return mod.PlacementView(self.request)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.OrderItem)

        # nothing added without perms
        self.assertEqual(len(grid.tools), 0)
        view.configure_grid(grid)
        self.assertFalse(grid.checkable)
        self.assertEqual(len(grid.tools), 0)

        # button added with perm
        with patch.object(self.request, 'is_root', new=True):
            view.configure_grid(grid)
            self.assertTrue(grid.checkable)
            self.assertEqual(len(grid.tools), 1)
            self.assertIn('process_placement', grid.tools)
            tool = grid.tools['process_placement']
            self.assertIn('<b-button ', tool)
            self.assertIn('Order Placed', tool)

    def test_process_placement(self):
        self.pyramid_config.add_route('order_items_placement', '/placement/')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        grid = view.make_grid(model_class=model.OrderItem)

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_READY)
        order.items.append(item1)
        item2 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_READY)
        order.items.append(item2)
        item3 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_READY)
        order.items.append(item3)
        self.session.add(order)
        self.session.flush()

        # view only configured for POST
        with patch.multiple(self.request, method='POST', user=user):
            with patch.object(view, 'Session', return_value=self.session):

                # redirect if items not specified
                with patch.object(view.order_handler, 'process_placement') as process_placement:
                    self.assertRaises(HTTPFound, view.process_placement)
                    process_placement.assert_not_called()
                    self.assertTrue(self.request.session.pop_flash('warning'))
                    self.assertFalse(self.request.session.peek_flash())

                # two items are updated
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_READY)
                self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_READY)
                self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_READY)
                self.assertEqual(len(item1.events), 0)
                self.assertEqual(len(item2.events), 0)
                self.assertEqual(len(item3.events), 0)
                with patch.object(self.request, 'POST', new={
                        'item_uuids': ','.join([item1.uuid.hex, item2.uuid.hex]),
                        'vendor_name': 'Acme Dist',
                        'po_number': 'ACME123',
                }):
                    view.process_placement()
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_PLACED)
                self.assertEqual(item2.status_code, enum.ORDER_ITEM_STATUS_PLACED)
                self.assertEqual(item3.status_code, enum.ORDER_ITEM_STATUS_READY)
                self.assertEqual(len(item1.events), 1)
                self.assertEqual(len(item2.events), 1)
                self.assertEqual(len(item3.events), 0)
                self.assertEqual(item1.events[0].note, "PO ACME123 for vendor Acme Dist")
                self.assertEqual(item2.events[0].note, "PO ACME123 for vendor Acme Dist")
                self.assertFalse(self.request.session.peek_flash('warning'))
                self.assertTrue(self.request.session.pop_flash())


class TestReceivingView(OrderItemViewTestMixin, WebTestCase):

    def make_view(self):
        return mod.ReceivingView(self.request)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.OrderItem)

        # nothing added without perms
        self.assertEqual(len(grid.tools), 0)
        view.configure_grid(grid)
        self.assertFalse(grid.checkable)
        self.assertEqual(len(grid.tools), 0)

        # buttons added with perm
        with patch.object(self.request, 'is_root', new=True):
            view.configure_grid(grid)
            self.assertEqual(len(grid.tools), 2)
            self.assertTrue(grid.checkable)

            self.assertIn('process_receiving', grid.tools)
            tool = grid.tools['process_receiving']
            self.assertIn('<b-button ', tool)
            self.assertIn('Received', tool)

            self.assertIn('process_reorder', grid.tools)
            tool = grid.tools['process_reorder']
            self.assertIn('<b-button ', tool)
            self.assertIn('Re-Order', tool)

    def test_process_receiving(self):
        self.pyramid_config.add_route('order_items_receiving', '/receiving/')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        grid = view.make_grid(model_class=model.OrderItem)

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_PLACED)
        order.items.append(item1)
        self.session.add(order)
        self.session.flush()

        # view only configured for POST
        with patch.multiple(self.request, method='POST', user=user):
            with patch.object(view, 'Session', return_value=self.session):

                # redirect if items not specified
                with patch.object(view.order_handler, 'process_receiving') as process_receiving:
                    self.assertRaises(HTTPFound, view.process_receiving)
                    process_receiving.assert_not_called()
                    self.assertTrue(self.request.session.pop_flash('warning'))
                    self.assertFalse(self.request.session.peek_flash())

                # all info provided
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_PLACED)
                self.assertEqual(len(item1.events), 0)
                with patch.object(self.request, 'POST', new={
                        'item_uuids': item1.uuid.hex,
                        'vendor_name': "Acme Dist",
                        'invoice_number': 'INV123',
                        'po_number': '123',
                        'note': 'extra note',
                }):
                    view.process_receiving()
                self.assertFalse(self.request.session.peek_flash('warning'))
                self.assertTrue(self.request.session.pop_flash())
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
                self.assertEqual(len(item1.events), 2)
                self.assertEqual(item1.events[0].note, "invoice INV123 (PO 123) from vendor Acme Dist")
                self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_RECEIVED)
                self.assertEqual(item1.events[1].note, "extra note")
                self.assertEqual(item1.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)

    def test_process_reorder(self):
        self.pyramid_config.add_route('order_items_receiving', '/receiving/')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        grid = view.make_grid(model_class=model.OrderItem)

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_PLACED)
        order.items.append(item1)
        self.session.add(order)
        self.session.flush()

        # view only configured for POST
        with patch.multiple(self.request, method='POST', user=user):
            with patch.object(view, 'Session', return_value=self.session):

                # redirect if items not specified
                with patch.object(view.order_handler, 'process_reorder') as process_reorder:
                    self.assertRaises(HTTPFound, view.process_reorder)
                    process_reorder.assert_not_called()
                    self.assertTrue(self.request.session.pop_flash('warning'))
                    self.assertFalse(self.request.session.peek_flash())

                # all info provided
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_PLACED)
                self.assertEqual(len(item1.events), 0)
                with patch.object(self.request, 'POST', new={
                        'item_uuids': item1.uuid.hex,
                        'note': 'extra note',
                }):
                    view.process_reorder()
                self.assertFalse(self.request.session.peek_flash('warning'))
                self.assertTrue(self.request.session.pop_flash())
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_READY)
                self.assertEqual(len(item1.events), 2)
                self.assertIsNone(item1.events[0].note)
                self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_REORDER)
                self.assertEqual(item1.events[1].note, "extra note")
                self.assertEqual(item1.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)


class TestContactView(OrderItemViewTestMixin, WebTestCase):

    def make_view(self):
        return mod.ContactView(self.request)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.OrderItem)

        # nothing added without perms
        self.assertEqual(len(grid.tools), 0)
        view.configure_grid(grid)
        self.assertFalse(grid.checkable)
        self.assertEqual(len(grid.tools), 0)

        # buttons added with perm
        with patch.object(self.request, 'is_root', new=True):
            view.configure_grid(grid)
            self.assertEqual(len(grid.tools), 2)
            self.assertTrue(grid.checkable)

            self.assertIn('process_contact_success', grid.tools)
            tool = grid.tools['process_contact_success']
            self.assertIn('<b-button ', tool)
            self.assertIn('Contact Success', tool)

            self.assertIn('process_contact_failure', grid.tools)
            tool = grid.tools['process_contact_failure']
            self.assertIn('<b-button ', tool)
            self.assertIn('Contact Failure', tool)

    def test_process_contact_success(self):
        self.pyramid_config.add_route('order_items_contact', '/contact/')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        grid = view.make_grid(model_class=model.OrderItem)

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item1)
        self.session.add(order)
        self.session.flush()

        # view only configured for POST
        with patch.multiple(self.request, method='POST', user=user):
            with patch.object(view, 'Session', return_value=self.session):

                # redirect if items not specified
                with patch.object(view.order_handler, 'process_contact_success') as process_contact_success:
                    self.assertRaises(HTTPFound, view.process_contact_success)
                    process_contact_success.assert_not_called()
                    self.assertTrue(self.request.session.pop_flash('warning'))
                    self.assertFalse(self.request.session.peek_flash())

                # all info provided
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
                self.assertEqual(len(item1.events), 0)
                with patch.object(self.request, 'POST', new={
                        'item_uuids': item1.uuid.hex,
                        'note': 'extra note',
                }):
                    view.process_contact_success()
                self.assertFalse(self.request.session.peek_flash('warning'))
                self.assertTrue(self.request.session.pop_flash())
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_CONTACTED)
                self.assertEqual(len(item1.events), 2)
                self.assertIsNone(item1.events[0].note)
                self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_CONTACTED)
                self.assertEqual(item1.events[1].note, "extra note")
                self.assertEqual(item1.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)

    def test_process_contact_failure(self):
        self.pyramid_config.add_route('order_items_contact', '/contact/')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        grid = view.make_grid(model_class=model.OrderItem)

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_RECEIVED)
        order.items.append(item1)
        self.session.add(order)
        self.session.flush()

        # view only configured for POST
        with patch.multiple(self.request, method='POST', user=user):
            with patch.object(view, 'Session', return_value=self.session):

                # redirect if items not specified
                with patch.object(view.order_handler, 'process_contact_failure') as process_contact_failure:
                    self.assertRaises(HTTPFound, view.process_contact_failure)
                    process_contact_failure.assert_not_called()
                    self.assertTrue(self.request.session.pop_flash('warning'))
                    self.assertFalse(self.request.session.peek_flash())

                # all info provided
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_RECEIVED)
                self.assertEqual(len(item1.events), 0)
                with patch.object(self.request, 'POST', new={
                        'item_uuids': item1.uuid.hex,
                        'note': 'extra note',
                }):
                    view.process_contact_failure()
                self.assertFalse(self.request.session.peek_flash('warning'))
                self.assertTrue(self.request.session.pop_flash())
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_CONTACT_FAILED)
                self.assertEqual(len(item1.events), 2)
                self.assertIsNone(item1.events[0].note)
                self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_CONTACT_FAILED)
                self.assertEqual(item1.events[1].note, "extra note")
                self.assertEqual(item1.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)


class TestDeliveryView(OrderItemViewTestMixin, WebTestCase):

    def make_view(self):
        return mod.DeliveryView(self.request)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.OrderItem)

        # nothing added without perms
        self.assertEqual(len(grid.tools), 0)
        view.configure_grid(grid)
        self.assertFalse(grid.checkable)
        self.assertEqual(len(grid.tools), 0)

        # buttons added with perm
        with patch.object(self.request, 'is_root', new=True):
            view.configure_grid(grid)
            self.assertEqual(len(grid.tools), 2)
            self.assertTrue(grid.checkable)

            self.assertIn('process_delivery', grid.tools)
            tool = grid.tools['process_delivery']
            self.assertIn('<b-button ', tool)
            self.assertIn('Delivered', tool)

            self.assertIn('process_restock', grid.tools)
            tool = grid.tools['process_restock']
            self.assertIn('<b-button ', tool)
            self.assertIn('Restocked', tool)

    def test_process_delivery(self):
        self.pyramid_config.add_route('order_items_delivery', '/delivery/')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        grid = view.make_grid(model_class=model.OrderItem)

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_CONTACTED)
        order.items.append(item1)
        self.session.add(order)
        self.session.flush()

        # view only configured for POST
        with patch.multiple(self.request, method='POST', user=user):
            with patch.object(view, 'Session', return_value=self.session):

                # redirect if items not specified
                with patch.object(view.order_handler, 'process_delivery') as process_delivery:
                    self.assertRaises(HTTPFound, view.process_delivery)
                    process_delivery.assert_not_called()
                    self.assertTrue(self.request.session.pop_flash('warning'))
                    self.assertFalse(self.request.session.peek_flash())

                # all info provided
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_CONTACTED)
                self.assertEqual(len(item1.events), 0)
                with patch.object(self.request, 'POST', new={
                        'item_uuids': item1.uuid.hex,
                        'note': 'extra note',
                }):
                    view.process_delivery()
                self.assertFalse(self.request.session.peek_flash('warning'))
                self.assertTrue(self.request.session.pop_flash())
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_DELIVERED)
                self.assertEqual(len(item1.events), 2)
                self.assertIsNone(item1.events[0].note)
                self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_DELIVERED)
                self.assertEqual(item1.events[1].note, "extra note")
                self.assertEqual(item1.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)

    def test_process_restock(self):
        self.pyramid_config.add_route('order_items_delivery', '/delivery/')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()
        grid = view.make_grid(model_class=model.OrderItem)

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_name="Fred Flintstone", created_by=user)
        item1 = model.OrderItem(order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                status_code=enum.ORDER_ITEM_STATUS_CONTACTED)
        order.items.append(item1)
        self.session.add(order)
        self.session.flush()

        # view only configured for POST
        with patch.multiple(self.request, method='POST', user=user):
            with patch.object(view, 'Session', return_value=self.session):

                # redirect if items not specified
                with patch.object(view.order_handler, 'process_restock') as process_restock:
                    self.assertRaises(HTTPFound, view.process_restock)
                    process_restock.assert_not_called()
                    self.assertTrue(self.request.session.pop_flash('warning'))
                    self.assertFalse(self.request.session.peek_flash())

                # all info provided
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_CONTACTED)
                self.assertEqual(len(item1.events), 0)
                with patch.object(self.request, 'POST', new={
                        'item_uuids': item1.uuid.hex,
                        'note': 'extra note',
                }):
                    view.process_restock()
                self.assertFalse(self.request.session.peek_flash('warning'))
                self.assertTrue(self.request.session.pop_flash())
                self.assertEqual(item1.status_code, enum.ORDER_ITEM_STATUS_RESTOCKED)
                self.assertEqual(len(item1.events), 2)
                self.assertIsNone(item1.events[0].note)
                self.assertEqual(item1.events[0].type_code, enum.ORDER_ITEM_EVENT_RESTOCKED)
                self.assertEqual(item1.events[1].note, "extra note")
                self.assertEqual(item1.events[1].type_code, enum.ORDER_ITEM_EVENT_NOTE_ADDED)
