# -*- coding: utf-8; -*-
################################################################################
#
#  Sideshow -- Case/Special Order Tracker
#  Copyright © 2024-2025 Lance Edgar
#
#  This file is part of Sideshow.
#
#  Sideshow is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Sideshow is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Sideshow.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Sideshow - test utilities
"""

from wuttaweb import testing as base


class WebTestCase(base.WebTestCase):

    def make_config(self, **kwargs):
        config = super().make_config(**kwargs)
        config.setdefault('wutta.model_spec', 'sideshow.db.model')
        config.setdefault('wutta.enum_spec', 'sideshow.enum')
        config.setdefault(f'{config.appname}.batch.neworder.handler.default_spec',
                          'sideshow.batch.neworder:NewOrderBatchHandler')
        return config
