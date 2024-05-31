#
# Copyright (C) Stanislaw Adaszewski <s DOT adaszewski AT gmail DOT com>, 2024.
#
# This file is part of PyDeclarative.
#
# PyDeclarative is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# PyDeclarative is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more 
# details.
#
# You should have received a copy of the GNU Lesser General Public License along 
# with PyDeclarative. If not, see <https://www.gnu.org/licenses/>.
#


from collections import namedtuple
from .signal import Signal


class ListModel:
    def __init__(self, items=[]):
        self.items = items
        self.item_added = Signal()
        self.item_removed = Signal()
        self.item_updated = Signal()
        self.model_reseted = Signal()

    def append(self, data):
        self.insert(len(self.items), data)

    def insert(self, row, data):
        self.items.insert(row, data)
        self.item_added(row)

    def remove(self, row):
        self.items.pop(row)
        self.item_removed(row)

    def clear(self):
        self.items = []
        self.model_reseted()

    def get(self, row):
        return self.items[row]

    def set(self, row, data):
        self.items[row].update(data)
        self.item_updated(row)

    def __len__(self):
        return len(self.items)
