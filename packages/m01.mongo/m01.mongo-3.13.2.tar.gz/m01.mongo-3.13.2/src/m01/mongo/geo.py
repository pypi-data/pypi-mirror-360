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
"""Geo location item
$Id:$
"""
from __future__ import absolute_import
__docformat__ = "reStructuredText"
from zope.interface import implementer


import bson.son

import zope.interface
import zope.location.location
from zope.security.proxy import removeSecurityProxy

from m01.mongo import interfaces
from m01.mongo.fieldproperty import MongoFieldProperty


class GeoBase(zope.location.location.Location):
    """Geo base class"""

    __parent__ = None
    __name__ = None
    _m_initialized = False
    _m_changed_value = None

    _lon = MongoFieldProperty(interfaces.IGeoSchema['lon'])
    _lat = MongoFieldProperty(interfaces.IGeoSchema['lat'])

    def _m_changed():
        def get(self):
            return self._m_changed_value
        def set(self, value):
            if value == True:
                self._m_changed_value = value
                if self.__parent__ is not None:
                    removeSecurityProxy(self.__parent__)._m_changed = value
            elif value != True:
                raise ValueError("Can only dispatch True to __parent__")
        return property(get, set)

    _m_changed = _m_changed()

    def lat():
        def fget(self):
            return self._lat
        def fset(self, value):
            if self._lat != value:
                # prevent write access if not changed
                self._lat = value
        return property(fget, fset)

    lat = lat()

    def lon():
        def fget(self):
            return self._lon
        def fset(self, value):
            if self._lon != value:
                # prevent write access if not changed
                self._lon = value
        return property(fget, fset)

    lon = lon()

    def __repr__(self):
        return u'<%s lon:%s, lat:%s>' % (self.__class__.__name__, self.lon,
            self.lat)


# IGeoLocation
@implementer(interfaces.IGeoLocation)
class GeoLocation(GeoBase):
    """Geo location data wrapper, providing preserved lon/lat value order
    and supporting _m_changed marker concept.

    This item must get defined with a zope.schema.Object field and the
    MongoGeoLocationProperty property. for more info see geo.txt and testing.py

    IMPORTANT:
    we use the order latitude, longitude and (NOT lon, lat) like described in
    mongodb documentation

    A more detailed description about the lon/lat order thema:

    looking at the Geographic Coordinate System, you'll notice that longitude
    counts left to right, while latitude counts bottom to top. Translating that
    into x/y this would mean the Longitude/Latitude approach is the only one
    that makes sense logically.

    In english, coordinates are usually referred to as latitude/longitude in a
    term. This is due to 2 reasons: a precedents o in the alphabet and in
    Navigation, in the days of sextants Latitude was easier, and more exactly
    determined, so that was the first thing to determine/write down.

    From OGC Specs, lon/lat is the correct way to interpret them. You can
    easily see that from how those that where participants in creating the
    Specs (Oracle/Informix/ESRI/IBM) implemented them, and those that did
    their own stuff (MS/Google).

    """


    asDict = True

    def __init__(self, data):
        """Initialize a MongoSubItem with given data."""
        if (isinstance(data, list) and len(data) == 2):
            self.asDict = False
            # set lon, lat
            lon = data[0]
            lat = data[1]
        else:
            self.asDict = True
            # set given or None __parent__, we will set the __parent__ later
            # within the field property if not given yet.
            self.__parent__ = data.pop('__parent__', None)
            # set lon, lat
            lon = data.get('lon', None)
            lat = data.get('lat', None)

        # set lon, lat values and ensure float values
        if lon is not None:
            self.lon = float(lon)
        if lat is not None:
            self.lat = float(lat)
        # mark as not changed
        self._m_changed_value = None
        # mark the item as initialized. This allows us to implement attribtues
        # with apply decorator which act different for an initialized object
        self._m_initialized = True

    def dump(self, dumpNames=None, dictify=False):
        """Dump to data dict prevent lon/lat order by using SON """
        if self.asDict or dictify:
            # bson.son.SON will ensure the order in the dict
            data = bson.son.SON()
            if self.lon is not None:
                data['lon'] = self.lon
            if self.lat is not None:
                data['lat'] = self.lat
            return data
        else:
            return [self.lon, self.lat]


@implementer(interfaces.IGeoPoint)
class GeoPoint(GeoBase):
    """Geo Point data wrapper, providing preserved lon/lat value order
    and supporting _m_changed marker concept.

    This item must get defined with a zope.schema.Object field and the
    MongoGeoPointProperty property. For more info see geo.txt and testing.py

    This implementation uses the order longitude, latitude as described in
    mongodb documentation because of unnamed lng/lat list values.

    """


    def __init__(self, data):
        """Initialize a MongoSubItem with given data."""
        lon = None
        lat = None
        if isinstance(data, (dict, bson.son.SON)):
            if data.get('coordinates'):
                # GeoJSON format from mongodb
                type = data.get('type')
                if type is not None and type != self.type:
                    raise TypeError("Wrong GoePoint type given", type)
                # set given or None __parent__, we will set the __parent__ later
                # within the field property if not given yet.
                self.__parent__ = data.pop('__parent__', None)
                # set coordinates if given
                coordinates = data.get('coordinates')
                if coordinates and len(coordinates) == 2:
                    # set lon, lat
                    lon = coordinates[0]
                    lat = coordinates[1]
            else:
                # simple dict with lon, lat given (see MongoGeoPointProperty)
                self.__parent__ = data.pop('__parent__', None)
                # set lon, lat
                lon = data.get('lon', None)
                lat = data.get('lat', None)
        elif (isinstance(data, list) and len(data) == 2):
            # simple lon, lat list given (see MongoGeoPointProperty)
            self.asDict = False
            # set lon, lat
            lon = data[0]
            lat = data[1]

        # set lon, lat values and ensure float values
        if lon is not None and lat is not None:
            self.lon = float(lon)
            self.lat = float(lat)
        # mark as not changed
        self._m_changed_value = None
        # mark the item as initialized. This allows us to implement attribtues
        # with apply decorator which act different for an initialized object
        self._m_initialized = True

    def dump(self, dumpNames=None, dictify=False):
        """Dump to data dict prevent lon/lat order by using SON """
        # bson.son.SON will ensure the order in the dict
        data = bson.son.SON()
        data['type'] = self.type
        if self.lon is not None and self.lat is not None:
            data['coordinates'] = [self.lon, self.lat]
        if dictify:
            data = m01.mongo.dictify(data)
        return data

    @property
    def type(self):
        return u'Point'