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
Static assets
"""

from fanstatic import Library, Resource


# # libcache
libcache = Library('sideshow_libcache', 'libcache')
vue_js = Resource(libcache, 'vue-2.6.14.min.js')
vue_resource_js = Resource(libcache, 'vue-resource-1.5.3.min.js')
buefy_js = Resource(libcache, 'buefy-0.9.25.min.js')
buefy_css = Resource(libcache, 'buefy-0.9.25.min.css')
fontawesome_js = Resource(libcache, 'fontawesome-5.3.1-all.min.js')
# bb_vue_js = Resource(libcache, 'vue.esm-browser-3.3.11.prod.js')
# bb_oruga_js = Resource(libcache, 'oruga-0.8.10.js')
# bb_oruga_bulma_js = Resource(libcache, 'oruga-bulma-0.3.0.js')
# bb_oruga_bulma_css = Resource(libcache, 'oruga-bulma-0.3.0.css')
# bb_fontawesome_svg_core_js = Resource(libcache, 'fontawesome-svg-core-6.5.2.js')
# bb_free_solid_svg_icons_js = Resource(libcache, 'free-solid-svg-icons-6.5.2.js')
# bb_vue_fontawesome_js = Resource(libcache, 'vue-fontawesome-3.0.6.index.es.js')


def includeme(config):
    config.include('wuttaweb.static')
    config.add_static_view('sideshow', 'sideshow.web:static', cache_max_age=3600)
