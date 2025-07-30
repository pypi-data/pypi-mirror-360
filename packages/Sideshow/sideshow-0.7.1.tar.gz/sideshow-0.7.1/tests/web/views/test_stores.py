# -*- coding: utf-8; -*-

from unittest.mock import patch

import colander

from sideshow.testing import WebTestCase
from sideshow.web.views import stores as mod


class TestIncludeme(WebTestCase):

    def test_coverage(self):
        mod.includeme(self.pyramid_config)


class TestStoreView(WebTestCase):

    def make_view(self):
        return mod.StoreView(self.request)

    def test_configure_grid(self):
        model = self.app.model
        view = self.make_view()
        grid = view.make_grid(model_class=model.Store)
        self.assertNotIn('store_id', grid.linked_columns)
        self.assertNotIn('name', grid.linked_columns)
        view.configure_grid(grid)
        self.assertIn('store_id', grid.linked_columns)
        self.assertIn('name', grid.linked_columns)

    def test_grid_row_class(self):
        model = self.app.model
        view = self.make_view()

        store = model.Store()
        self.assertFalse(store.archived)
        self.assertIsNone(view.grid_row_class(store, {}, 0))

        store = model.Store(archived=True)
        self.assertTrue(store.archived)
        self.assertEqual(view.grid_row_class(store, {}, 0), 'has-background-warning')

    def test_configure_form(self):
        model = self.app.model
        view = self.make_view()

        # unique validators are set
        form = view.make_form(model_class=model.Store)
        self.assertNotIn('store_id', form.validators)
        self.assertNotIn('name', form.validators)
        view.configure_form(form)
        self.assertIn('store_id', form.validators)
        self.assertIn('name', form.validators)

    def test_unique_store_id(self):
        model = self.app.model
        view = self.make_view()

        store = model.Store(store_id='001', name='whatever')
        self.session.add(store)
        self.session.commit()

        with patch.object(view, 'Session', return_value=self.session):

            # invalid if same store_id in data
            node = colander.SchemaNode(colander.String(), name='store_id')
            self.assertRaises(colander.Invalid, view.unique_store_id, node, '001')

            # but not if store_id belongs to current store
            with patch.object(self.request, 'matchdict', new={'uuid': store.uuid}):
                with patch.object(view, 'editing', new=True):
                    node = colander.SchemaNode(colander.String(), name='store_id')
                    self.assertIsNone(view.unique_store_id(node, '001'))

    def test_unique_name(self):
        model = self.app.model
        view = self.make_view()

        store = model.Store(store_id='001', name='Acme Goods')
        self.session.add(store)
        self.session.commit()

        with patch.object(view, 'Session', return_value=self.session):

            # invalid if same name in data
            node = colander.SchemaNode(colander.String(), name='name')
            self.assertRaises(colander.Invalid, view.unique_name, node, 'Acme Goods')

            # but not if name belongs to current store
            with patch.object(self.request, 'matchdict', new={'uuid': store.uuid}):
                with patch.object(view, 'editing', new=True):
                    node = colander.SchemaNode(colander.String(), name='name')
                    self.assertIsNone(view.unique_name(node, 'Acme Goods'))
