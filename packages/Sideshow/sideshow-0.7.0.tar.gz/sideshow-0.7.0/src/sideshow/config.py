# -*- coding: utf-8; -*-
################################################################################
#
#  Sideshow -- Case/Special Order Tracker
#  Copyright © 2024 Lance Edgar
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
Sideshow config extension
"""

from wuttjamaican.conf import WuttaConfigExtension


class SideshowConfig(WuttaConfigExtension):
    """
    Config extension for Sideshow.

    This establishes some config defaults specific to Sideshow.
    """
    key = 'sideshow'

    def configure(self, config):
        """ """

        # app info
        config.setdefault(f'{config.appname}.app_title', "Sideshow")
        config.setdefault(f'{config.appname}.app_dist', "Sideshow")

        # app model, enum
        config.setdefault(f'{config.appname}.model_spec', 'sideshow.db.model')
        config.setdefault(f'{config.appname}.enum_spec', 'sideshow.enum')

        # batch handlers
        config.setdefault(f'{config.appname}.batch.neworder.handler.default_spec',
                          'sideshow.batch.neworder:NewOrderBatchHandler')

        # web app menu
        config.setdefault(f'{config.appname}.web.menus.handler.default_spec',
                          'sideshow.web.menus:SideshowMenuHandler')

        # web app libcache
        config.setdefault('wuttaweb.static_libcache.module', 'sideshow.web.static')
