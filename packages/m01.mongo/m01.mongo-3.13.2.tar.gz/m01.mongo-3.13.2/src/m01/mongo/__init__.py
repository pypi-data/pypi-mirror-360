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
__docformat__ = "reStructuredText"

import calendar
import time
import datetime
import struct
import threading
import zope.component

import bson.son
import bson.objectid

from m01.mongo.tz_util import UTC


###############################################################################
#
# threading

LOCAL = threading.local()

def clearThreadLocalCache(event=None):
    """A subscriber to EndRequestEvent

    Cleans up the thread local cache on each end request.
    """
    for key in list(LOCAL.__dict__.keys()):
        del LOCAL.__dict__[key]


###############################################################################
#
# datetime hook

_tzmarker = object()

# testing hook for datetime
# allows to set the current date/time
NOW = None

def now(tz=_tzmarker):
    global NOW
    if tz is _tzmarker:
        tz = UTC
    if NOW is not None:
        return NOW(tz)
    else:
        return datetime.datetime.now(tz)

def setNOW(value=None):
    global NOW
    if value is None:
        NOW = None
    elif callable(value):
        NOW = value
    else:
        NOW = lambda tz: value.replace(tzinfo=tz)

def getNOW():
    global NOW
    return NOW

def today():
    return now().date()


###############################################################################
#
# SON to dict converter
def dictify(data):
    """Recursive replace SON items with dict in the given data structure.

    Compared to the SON.to_dict method, this method will also handle tuples
    and keep them intact.

    """
    if isinstance(data, bson.son.SON):
        data = dict(data)
    if isinstance(data, dict):
        d = {}
        for k, v in list(data.items()):
            # replace nested SON items
            d[k] = dictify(v)
    elif isinstance(data, (tuple, list)):
        d = []
        for v in data:
            # replace nested SON items
            d.append(dictify(v))
        if isinstance(data, tuple):
            # keep tuples intact
            d = tuple(d)
    else:
        d = data
    return d


###############################################################################
#
# object id generation

def getObjectId(secs=0):
    """Knows how to generate similar ObjectId based on integer (counter)

    Note: this method can get used if you need to define similar ObjectId
    in a non persistent environment if need to bootstrap mongo containers.
    """
    time_tuple = time.gmtime(secs)
    ts = calendar.timegm(time_tuple)
    oid = struct.pack(">i", int(ts)) + b"\x00" * 8
    return bson.objectid.ObjectId(oid)


def getObjectIdByTimeStr(tStr, frmt="%Y-%m-%d %H:%M:%S"):
    """Knows how to generate similar ObjectId based on a time string

    The time string format used by default is ``%Y-%m-%d %H:%M:%S``.
    Use the current development time which could prevent duplicated
    ObjectId. At least some kind of ;-)
    """
    time.strptime(tStr, frmt)
    ts = time.mktime(tStr)
    oid = struct.pack(">i", int(ts)) + b"\x00" * 8
    return bson.objectid.ObjectId(oid)
