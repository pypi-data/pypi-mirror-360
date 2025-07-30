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
See also: :ref:`sideshow-install`
"""

import typer

from .base import sideshow_typer


@sideshow_typer.command()
def install(
        ctx: typer.Context,
):
    """
    Install the Sideshow app
    """
    config = ctx.parent.wutta_config
    app = config.get_app()
    install = app.get_install_handler(pkg_name='sideshow',
                                      app_title="Sideshow",
                                      pypi_name='Sideshow',
                                      egg_name='Sideshow')
    install.run()
