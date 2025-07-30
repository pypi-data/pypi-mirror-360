# -*- coding: utf-8; -*-

import datetime
from unittest.mock import patch

from pyramid.httpexceptions import HTTPFound

from sideshow.testing import WebTestCase
from sideshow.web.views import products as mod
from sideshow.batch.neworder import NewOrderBatchHandler


class TestIncludeme(WebTestCase):

    def test_coverage(self):
        mod.includeme(self.pyramid_config)


class TestLocalProductView(WebTestCase):

    def make_view(self):
        return mod.LocalProductView(self.request)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.LocalProduct)
        self.assertNotIn('scancode', grid.linked_columns)
        self.assertNotIn('brand_name', grid.linked_columns)
        self.assertNotIn('description', grid.linked_columns)
        view.configure_grid(grid)
        self.assertIn('scancode', grid.linked_columns)
        self.assertIn('brand_name', grid.linked_columns)
        self.assertIn('description', grid.linked_columns)

    def test_configure_form(self):
        model = self.app.model
        view = self.make_view()

        # creating
        with patch.object(view, 'creating', new=True):
            form = view.make_form(model_class=model.LocalProduct)
            self.assertIn('external_id', form)
            view.configure_form(form)
            self.assertNotIn('external_id', form)

        user = model.User(username='barney')
        self.session.add(user)
        product = model.LocalProduct()
        self.session.add(product)
        self.session.commit()

        # viewing
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=product)
            self.assertNotIn('external_id', form.readonly_fields)
            self.assertNotIn('local_products.view.orders', form.grid_vue_context)
            view.configure_form(form)
            self.assertIn('external_id', form.readonly_fields)
            self.assertIn('local_products.view.orders', form.grid_vue_context)

    def test_make_orders_grid(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_id=42, created_by=user)
        product = model.LocalProduct()
        self.session.add(product)
        item = model.OrderItem(local_product=product,
                               order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                               status_code=enum.ORDER_ITEM_STATUS_INITIATED)
        order.items.append(item)
        self.session.add(order)
        self.session.commit()

        # no view perm
        grid = view.make_orders_grid(product)
        self.assertEqual(len(grid.actions), 0)

        # with view perm
        with patch.object(self.request, 'is_root', new=True):
            grid = view.make_orders_grid(product)
            self.assertEqual(len(grid.actions), 1)
            self.assertEqual(grid.actions[0].key, 'view')

    def test_make_new_order_batches_grid(self):
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        product = model.LocalProduct()
        self.session.add(product)
        row = handler.make_row(local_product=product,
                               order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
        handler.add_row(batch, row)
        self.session.commit()

        # no view perm
        grid = view.make_new_order_batches_grid(product)
        self.assertEqual(len(grid.actions), 0)

        # with view perm
        with patch.object(self.request, 'is_root', new=True):
            grid = view.make_new_order_batches_grid(product)
            self.assertEqual(len(grid.actions), 1)
            self.assertEqual(grid.actions[0].key, 'view')


class TestPendingProductView(WebTestCase):

    def make_view(self):
        return mod.PendingProductView(self.request)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        # nb. mostly just getting coverage here
        grid = view.make_grid(model_class=model.PendingProduct)
        self.assertNotIn('scancode', grid.linked_columns)
        self.assertNotIn('brand_name', grid.linked_columns)
        self.assertNotIn('description', grid.linked_columns)
        view.configure_grid(grid)
        self.assertIn('scancode', grid.linked_columns)
        self.assertIn('brand_name', grid.linked_columns)
        self.assertIn('description', grid.linked_columns)

    def test_grid_row_class(self):
        enum = self.app.enum
        model = self.app.model
        view = self.make_view()
        product = model.PendingProduct()

        # null by default
        self.assertIsNone(view.grid_row_class(product, {}, 1))

        # warning for ignored
        product.status = enum.PendingProductStatus.IGNORED
        self.assertEqual(view.grid_row_class(product, {}, 1), 'has-background-warning')

    def test_configure_form(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        # creating
        with patch.object(view, 'creating', new=True):
            form = view.make_form(model_class=model.PendingProduct)
            view.configure_form(form)
            self.assertNotIn('created', form)
            self.assertNotIn('created_by', form)

        user = model.User(username='barney')
        self.session.add(user)
        product = model.PendingProduct(status=enum.PendingProductStatus.PENDING,
                                         created_by=user)
        self.session.add(product)
        self.session.commit()

        # viewing
        with patch.object(view, 'viewing', new=True):
            form = view.make_form(model_instance=product)
            view.configure_form(form)
            self.assertIn('status', form)
            self.assertIn('created', form)
            self.assertIn('created_by', form)

    def test_make_orders_grid(self):
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        order = model.Order(order_id=42, customer_id=42, created_by=user)
        product = model.PendingProduct(status=enum.PendingProductStatus.PENDING,
                                         created_by=user)
        self.session.add(product)
        item = model.OrderItem(pending_product=product,
                               order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                               status_code=enum.ORDER_ITEM_STATUS_INITIATED)
        order.items.append(item)
        self.session.add(order)
        self.session.commit()

        # no view perm
        grid = view.make_orders_grid(product)
        self.assertEqual(len(grid.actions), 0)

        # with view perm
        with patch.object(self.request, 'is_root', new=True):
            grid = view.make_orders_grid(product)
            self.assertEqual(len(grid.actions), 1)
            self.assertEqual(grid.actions[0].key, 'view')

    def test_make_new_order_batches_grid(self):
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        product = model.PendingProduct(status=enum.PendingProductStatus.PENDING,
                                         created_by=user)
        self.session.add(product)
        row = handler.make_row(pending_product=product,
                               order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
        handler.add_row(batch, row)
        self.session.commit()

        # no view perm
        grid = view.make_new_order_batches_grid(product)
        self.assertEqual(len(grid.actions), 0)

        # with view perm
        with patch.object(self.request, 'is_root', new=True):
            grid = view.make_new_order_batches_grid(product)
            self.assertEqual(len(grid.actions), 1)
            self.assertEqual(grid.actions[0].key, 'view')

    def test_get_template_context(self):
        enum = self.app.enum
        model = self.app.model
        view = self.make_view()
        product = model.PendingProduct(status=enum.PendingProductStatus.PENDING)
        orig_context = {'instance': product}

        # local setting omitted by default
        context = view.get_template_context(orig_context)
        self.assertNotIn('use_local_products', context)

        # still omitted even though 'viewing'
        with patch.object(view, 'viewing', new=True):
            context = view.get_template_context(orig_context)
            self.assertNotIn('use_local_products', context)

            # still omitted even though correct status
            product.status = enum.PendingProductStatus.READY
            context = view.get_template_context(orig_context)
            self.assertNotIn('use_local_products', context)

            # no longer omitted if user has perm
            with patch.object(self.request, 'is_root', new=True):
                context = view.get_template_context(orig_context)
                self.assertIn('use_local_products', context)
                # nb. true by default
                self.assertTrue(context['use_local_products'])

                # accurately reflects config
                self.config.setdefault('sideshow.orders.use_local_products', 'false')
                context = view.get_template_context(orig_context)
                self.assertFalse(context['use_local_products'])

    def test_delete_instance(self):
        self.pyramid_config.add_route('pending_products.view', '/pending/products/{uuid}')
        model = self.app.model
        enum = self.app.enum
        handler = NewOrderBatchHandler(self.config)
        view = self.make_view()

        user = model.User(username='barney')
        self.session.add(user)

        # 1st product is standalone, will be deleted
        product = model.PendingProduct(status=enum.PendingProductStatus.PENDING,
                                       created_by=user)
        self.session.add(product)
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingProduct).count(), 1)
        view.delete_instance(product)
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingProduct).count(), 0)

        # 2nd product is attached to new order batch, will not be deleted
        batch = handler.make_batch(self.session, created_by=user)
        self.session.add(batch)
        product = model.PendingProduct(status=enum.PendingProductStatus.PENDING,
                                         created_by=user)
        self.session.add(product)
        row = handler.make_row(pending_product=product,
                               order_qty=1, order_uom=enum.ORDER_UOM_UNIT)
        handler.add_row(batch, row)
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingProduct).count(), 1)
        self.assertRaises(HTTPFound, view.delete_instance, product)
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingProduct).count(), 1)

        # but after batch is executed, 2nd product can be deleted
        batch.executed = datetime.datetime.now()
        batch.executed_by = user
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingProduct).count(), 1)
        view.delete_instance(product)
        self.session.flush()
        self.assertEqual(self.session.query(model.PendingProduct).count(), 0)

    def test_resolve(self):
        self.pyramid_config.add_route('pending_products.view', '/pending/products/{uuid}')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        product = model.PendingProduct(status=enum.PendingProductStatus.PENDING,
                                       created_by=user)
        self.session.add(product)
        self.session.flush()

        info = {
            'product_id': '07430500132',
            'scancode': '07430500132',
            'brand_name': "Bragg's",
            'description': "Apple Cider Vinegar",
            'size': "32oz",
            'weighed': False,
            'department_id': None,
            'department_name': None,
            'special_order': False,
            'vendor_name': None,
            'vendor_item_code': None,
            'case_size': 12,
            'unit_cost': 2.99,
            'unit_price_reg': 5.99,
        }

        with patch.object(view, 'Session', return_value=self.session):
            with patch.object(self.request, 'user', new=user):
                with patch.object(self.request, 'matchdict', new={'uuid': product.uuid}):

                    # flash error if wrong status
                    result = view.resolve()
                    self.assertIsInstance(result, HTTPFound)
                    self.assertTrue(self.request.session.peek_flash('error'))
                    self.assertEqual(self.request.session.pop_flash('error'),
                                     ["pending product does not have 'ready' status!"])

                    # flash error if product_id not specified
                    product.status = enum.PendingProductStatus.READY
                    result = view.resolve()
                    self.assertIsInstance(result, HTTPFound)
                    self.assertTrue(self.request.session.peek_flash('error'))
                    self.assertEqual(self.request.session.pop_flash('error'),
                                     ["must specify valid product_id"])

                    # more sample data
                    order = model.Order(order_id=100, created_by=user,
                                        customer_name="Fred Flintstone")
                    item = model.OrderItem(pending_product=product,
                                           order_qty=1, order_uom=enum.ORDER_UOM_UNIT,
                                           status_code=enum.ORDER_ITEM_STATUS_READY)
                    order.items.append(item)
                    self.session.add(order)

                    # product + order items updated
                    self.assertIsNone(product.product_id)
                    self.assertEqual(product.status, enum.PendingProductStatus.READY)
                    self.assertIsNone(item.product_id)
                    batch_handler = NewOrderBatchHandler(self.config)
                    with patch.object(batch_handler, 'get_product_info_external',
                                      return_value=info):
                        with patch.object(self.app, 'get_batch_handler',
                                          return_value=batch_handler):
                            with patch.object(self.request, 'POST',
                                              new={'product_id': '07430500132'}):
                                with patch.object(batch_handler, 'get_product_info_external',
                                                  return_value=info):
                                    result = view.resolve()
                    self.assertIsInstance(result, HTTPFound)
                    self.assertFalse(self.request.session.peek_flash('error'))
                    self.assertEqual(product.product_id, '07430500132')
                    self.assertEqual(product.status, enum.PendingProductStatus.RESOLVED)
                    self.assertEqual(item.product_id, '07430500132')

    def test_ignore(self):
        self.pyramid_config.add_route('pending_products.view', '/pending/products/{uuid}')
        model = self.app.model
        enum = self.app.enum
        view = self.make_view()

        # sample data
        user = model.User(username='barney')
        self.session.add(user)
        product = model.PendingProduct(status=enum.PendingProductStatus.PENDING,
                                       created_by=user)
        self.session.add(product)
        self.session.flush()

        with patch.object(view, 'Session', return_value=self.session):
            with patch.object(self.request, 'user', new=user):
                with patch.object(self.request, 'matchdict', new={'uuid': product.uuid}):

                    # flash error if wrong status
                    result = view.ignore()
                    self.assertIsInstance(result, HTTPFound)
                    self.assertTrue(self.request.session.peek_flash('error'))
                    self.assertEqual(self.request.session.pop_flash('error'),
                                     ["pending product does not have 'ready' status!"])

                    # product updated
                    product.status = enum.PendingProductStatus.READY
                    self.assertIsNone(product.product_id)
                    self.assertEqual(product.status, enum.PendingProductStatus.READY)
                    result = view.ignore()
                    self.assertIsInstance(result, HTTPFound)
                    self.assertFalse(self.request.session.peek_flash('error'))
                    self.assertIsNone(product.product_id)
                    self.assertEqual(product.status, enum.PendingProductStatus.IGNORED)
