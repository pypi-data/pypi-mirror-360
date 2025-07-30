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
Sideshow web app
"""

from wuttaweb import app as base


def main(global_config, **settings):
    """
    Make and return the WSGI app (Paste entry point).
    """
    # prefer Sideshow templates over wuttaweb
    settings.setdefault('mako.directories', [
        'sideshow.web:templates',
        'wuttaweb:templates',
    ])

    # make config objects
    wutta_config = base.make_wutta_config(settings)
    pyramid_config = base.make_pyramid_config(settings)

    # bring in the rest of Sideshow
    pyramid_config.include('sideshow.web')

    return pyramid_config.make_wsgi_app()


def make_wsgi_app(config=None):
    """
    Make and return the WSGI app (generic entry point).
    """
    return base.make_wsgi_app(main, config=config)


def make_asgi_app(config=None):
    """
    Make and return the ASGI app.
    """
    return base.make_asgi_app(main, config=config)
