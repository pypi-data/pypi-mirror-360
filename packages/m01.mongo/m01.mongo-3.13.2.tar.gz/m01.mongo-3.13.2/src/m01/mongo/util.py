###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
from __future__ import absolute_import
from past.builtins import cmp
from zope.interface import implementer
__docformat__ = "reStructuredText"

import zope.location
import zope.interface

from m01.mongo import interfaces


@implementer(interfaces.IMongoItemsData)
class MongoItemsData(zope.location.location.Location):
    """Mongo item list with _m_changed and location handling support."""


    def __init__(self, data=[]):
        self.clear()
        for obj in data:
            __name__, obj = self.locateAndReturn(obj)
            self.data[__name__] = obj
            self._order.append(__name__)

    def clear(self):
        """Clear data"""
        self.data = {}
        self._order = []

    def _m_changed():
        def get(self):
            raise AttributeError("_m_changed is a write only property")
        def set(self, value):
            if value == True:
                self.__parent__._m_changed = True
            else:
                raise ValueError("Can only dispatch True to __parent__")
        return property(get, set)

    _m_changed = _m_changed()
    def dump(self):
        items = []
        for obj in list(self.values()):
            if hasattr(obj, 'dump'):
                # dump mongo sub items
                items.append(obj.dump())
            else:
                # store simple value
                items.append(obj)
        return items

    def locate(self, value):
        """Locate an object with parent but only if locatable."""
        try:
            value.__parent__ = self
        except AttributeError as e:
            pass

    def locateAndReturn(self, obj):
        """Locate and return an object with parent but only if locatable."""
        self.locate(obj)
        return obj.__name__, obj

    def reLocate(self, __parent__):
        """Update location, this is needed if we use LocationProxy."""
        for item in list(self.values()):
            item.__parent__ = __parent__

    def order(self, orderNames):
        """Order items by the given name order"""
        if set(self._order) != set(orderNames):
            raise ValueError("Not all names used for order items")
        self._order = orderNames
        self._m_changed = True

    def fetch(self, idx):
        key = self._order[idx]
        return self.data[key]

    def append(self, item):
        """Append new item"""
        if item.__name__ in self._order:
            raise ValueError("Given item already appended", item.__name__)
        self._order.append(item.__name__)
        self.data[item.__name__] = item
        self.locate(item)
        self._m_changed = True

    def insert(self, i, item):
        """Insert new item at given order"""
        if item.__name__ in self._order:
            raise ValueError("Given item already inserted", item.__name__)
        self._order.insert(i, item.__name__)
        self.data[item.__name__] = item
        self.locate(item)
        self._m_changed = True

    def remove(self, item):
        """Remove an item"""
        del self.data[item.__name__]
        self._order.remove(item.__name__)
        self._m_changed = True

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, item):
        if key != item.__name__:
            raise KeyError("Only item __name__ are allowed as names")
        self.append(item)

    def __delitem__(self, key):
        item = self.data[key]
        self.remove(item)

    def get(self, key, default=None):
        """Get item by key"""
        return self.data.get(key, default)

    def keys(self):
        return self._order

    def values(self):
        for key in self._order:
            yield self.data[key]

    def items(self):
        for key in self._order:
            yield key, self.data[key]

    def __iter__(self):
        for key in self._order:
            yield self.data[key]

    def __cast(self, other):
        """Allows to compare other MongoItemsData lists."""
        if isinstance(other, MongoItemsData):
            return other.data
        else:
            return other

    def __cmp__(self, other):
        return cmp(self.data, self.__cast(other))

    def __repr__(self):
        """Represent this item as list of values"""
        return repr(list(self.data.values()))


@implementer(interfaces.IMongoListData)
class MongoListData(zope.location.location.Location):
    """Mongo item list with _m_changed support."""


    def __init__(self, data=[]):
        """Initialize given values in a new list

        IMPORTANT, it's absolutly required that we copy the values from the
        data list because it could be a global default value!. If we do not
        copy the data list, we would reference the default value from the
        schema field. eeek
        """
        self.data = list(data)

    def clear(self):
        """Clear data"""
        self.data = []

    def _m_changed():
        def get(self):
            raise AttributeError("_m_changed is a write only property")
        def set(self, value):
            if value == True:
                self.__parent__._m_changed = True
            else:
                raise ValueError("Can only dispatch True to __parent__")
        return property(get, set)

    _m_changed = _m_changed()
    def dump(self):
        items = []
        for obj in self:
            if hasattr(obj, 'dump'):
                # dump mongo sub items
                items.append(obj.dump())
            else:
                # store simple value
                items.append(obj)
        return items

    def append(self, item):
        self.data.append(item)
        self._m_changed = True

    def insert(self, i, item):
        self.data.insert(i, item)
        self._m_changed = True

    def pop(self, i=-1):
        rtn = self.data.pop(i)
        self._m_changed = True
        return rtn

    def remove(self, item):
        self.data.remove(item)
        self._m_changed = True

    def sort(self, *args, **kwargs):
        self.data.sort(*args, **kwds)
        self._m_changed = True

    def __len__(self):
        return len(self.data)

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, i, item):
        self.data[i] = item
        self._m_changed = True

    def __delitem__(self, i):
        del self.data[i]
        self._m_changed = True

    def __cast(self, other):
        """Allows to compare other MongoListData lists."""
        if isinstance(other, MongoListData):
            return other.data
        else:
            return other

    def __cmp__(self, other):
        return cmp(self.data, self.__cast(other))

    def __repr__(self):
        return repr(self.data)
