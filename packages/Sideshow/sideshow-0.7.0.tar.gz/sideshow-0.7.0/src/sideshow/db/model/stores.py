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
Data models for Stores
"""

import sqlalchemy as sa

from wuttjamaican.db import model


class Store(model.Base):
    """
    Represents a physical location for the business.
    """
    __tablename__ = 'sideshow_store'

    uuid = model.uuid_column()

    store_id = sa.Column(sa.String(length=10), nullable=False, unique=True, doc="""
    Unique ID for the store.
    """)

    name = sa.Column(sa.String(length=100), nullable=False, unique=True, doc="""
    Display name for the store (must be unique!).
    """)

    archived = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Indicates the store has been "retired" essentially, and mostly
    hidden from view.
    """)

    def __str__(self):
        return self.get_display()

    def get_display(self):
        """
        Returns the display string for the store, e.g. "001 Acme Goods".
        """
        return ' '.join([(self.store_id or '').strip(),
                         (self.name or '').strip()])\
                  .strip()
