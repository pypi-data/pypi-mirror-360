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

import zope.interface
import zope.i18nmessageid
import zope.schema
import zope.location.interfaces
import zope.container.interfaces
import zope.schema.interfaces

from m01.mongo.tz_util import UTC

_ = zope.i18nmessageid.MessageFactory('p01')


class IMongoList(zope.schema.interfaces.IList):
    """Field containing a value that implements the API of a conventional
    Python list used in mogo item list.
    """


# class IMongoSubObjectConverter(zope.schema.interfaces.IObject):
#     """Mongo object converter field"""


class IMongoBinary(zope.schema.interfaces.IBytes):
    """Field which stores bson.binary.Binary data"""


class IMongoDate(zope.schema.interfaces.IDate):
    """Field which stores an ordinal integer as date."""


class IMongoDatetime(zope.schema.interfaces.IDatetime):
    """A field representing a timzone aware datetime."""

    tzinfo = zope.schema.Field(
        title=_("Timezone info"),
        description=_("Timezone info"),
        default=UTC
        )


class IMongoListData(zope.location.interfaces.ILocation):
    """Simple item list supporting ILocation"""

    def clear():
        """Clear data"""

    def dump():
        """Dump the list to json data"""

    def append(item):
        """Append an item to the list."""

    def insert(i, item):
        """Insert an item at the given position."""

    def pop(i=-1):
        """Pop an item from the list."""

    def remove(item):
        """Remove an item from the list."""

    def sort(*args, **kwargs):
        """Sort the list"""

    def __len__():
        """Returns the lenght."""

    def __contains__(item):
        """Returns True if the list contains the given item otherwise False."""

    def __getitem__(i):
        """Get an item from the list."""

    def __setitem__(i, item):
        """Add an item to the list."""

    def __delitem__(i):
        """Remove an item from the list."""

    def __cmp__(other):
        """compare"""

    def __repr__():
        """representation"""


class IMongoItemsData(zope.location.interfaces.ILocation):
    """Mongo item list supporting ILocation"""

    def clear():
        """Clear data"""

    def dump():
        """Dump the list to json data"""

    def locate(value):
        """Locate an object with parent but only if locatable."""

    def locateAndReturn(obj):
        """Locate and return an object with parent but only if locatable."""

    def reLocate(__parent__):
        """Update location, this is needed if we use LocationProxy."""

    def order(orderNames):
        """Order items by the given name order"""

    def fetch(idx):
        """Returns the item at the given position. Same as <type list>[idx]"""

    def append(item):
        """Append new item"""

    def insert(i, item):
        """Insert new item at given order"""

    def remove(item):
        """Remove an item"""

    def __len__():
        """Returns the lenght."""

    def __contains__(key):
        """Return True if item is a part of data"""

    def __getitem__(key):
        """Get item"""

    def __setitem__(key, item):
        """Set item"""

    def __delitem__(key):
        """Remove an item"""

    def get(key, default=None):
        """Get item by key"""

    def keys():
        """Get keys"""

    def values():
        """Get values"""

    def items():
        """Get items"""

    def __iter__():
        """Get iterator"""

    def __cmp__(other):
        """compare"""

    def __repr__():
        """representation"""


class ISecurityAware(zope.interface.Interface):
    """Security aware mixin."""

    # principal permission manager
    _ppmrow = zope.schema.Dict(
        title=u'Principal Permission byrow',
        default={})
    _ppmcol = zope.schema.Dict(
        title=u'Principal Permission bycol',
        default={})

    # principal role manager
    _prmrow = zope.schema.Dict(
        title=u'Principal Role byrow',
        default={})
    _prmcol = zope.schema.Dict(
        title=u'Principal Role bycol',
        default={})

    # role permission manager
    _rpmrow = zope.schema.Dict(
        title=u'Role Permission byrow',
        default={})
    _rpmcol = zope.schema.Dict(
        title=u'Role Permission bycol',
        default={})

#    principalPermissionManager = zope.interface.Attribute(
#        """Principal Permission Manager""")
#    principalRoleManager = zope.interface.Attribute(
#        """Principal Role Manager""")
#    rolePermissionManager = zope.interface.Attribute(
#        """Role Permission Manager""")


class IMongoTransactionAware(zope.interface.Interface):
    """Mongo transaction support."""

    # transaction data manager support methods
    def begin():
        """Beginn commit a transaction handling."""

    def commit():
        """Start commit transaction handling."""

    def vote():
        """Process MongoDB insert and update calls.

        Note, if something fails, this could leave inconsistent data in MongoDB.
        """

    def abort():
        """Abort transaction handling."""

    def finish():
        """Finish transaction commit."""


class IMongoCollectionAware(zope.interface.Interface):
    """Mongo item loader."""

    collection = zope.interface.Attribute("""A mongoDB collection.""")

    def doLoad(data):
        """Prepare data and load them into IMongoItem."""

    def load(data):
        """Load data into an IMongoStorageItem,

        Override this method if you need another mongo item.
        """


class IMongoBatchAware(zope.interface.Interface):
    """Batching support"""

    def getBatchData(query=None, page=1, size=25, sortName=None,
        sortOrder=None, searchText=None, fields=None, skipFilter=False):
        """Returns batched mongo data, current page, total items and page size.
        """

# setup, convert, dump
class ISetup(zope.interface.Interface):
    """Setup mixin"""

    def setup(data, dumpOriginalData=False):
        """Update object with given data key/values.

        The method returns the original data as dict including the original
        _m_changed and _version values. This could be usefull for revert
        changes.

        Note: this method can be used for update an object and commit changes
        ASAP to MongoDB. See update method in IMongoHandler for more info

        Note: this will change the _m_changed state if some key/value are using
        a MongoFieldProperty!
        """

class IConvert(zope.interface.Interface):
    """Setup mixin"""

    def convert(key, value):
        """This convert method knows how to handle nested converters.

        Normaly a converter can convert attribute values. If the attribute
        value is a list of items, then you can use amethod whihc knows how to
        handle each value type. Or you can use this converter method and
        define nested converter. If so, juset define a dict with _type/converter
        for a converter attr name.
        """

class IDump(zope.interface.Interface):
    """Setup mixin"""

    def dump(dumpNames=None, dictify=False):
        """Dump the object to bson.son.SON instance.

        Optional the values filtered by the given dumpNames can get dumped to
        a dict. This is usefull if you need partial data from an object as
        key/value dict.

        NOTE: the dictify argument forces to recoursive convert bson.son.SON
        instances to a plain dict.

        You can also use the dictify method from m01.mongo if you like to
        replace the SON instances with plain dicts. This is sometimes required
        e.g. if you need to convert the data to a json string.

        """


class ICreatedModified(zope.interface.Interface):
    """Created and modified mixin"""

    created = zope.schema.Datetime(
        title=_(u'created'),
        description=_(u'created'),
        default=None,
        required=True)

    modified = zope.schema.Datetime(
        title=_(u'modified'),
        description=_(u'modified'),
        default=None,
        required=False)


# mongo item
class IMongoSubItem(ISetup, IConvert, IDump, ICreatedModified):
    """Mongo sub item

    NOTE: this interface is the core interface for mongo sub items but this
    interface doens't provide ILocation or IContained. In most use case you
    need to provide ILocation in your own inherited interface. The missing
    ILocation interface in this interface makes it simpler for define correct
    permissions in ZCML.
    """

    _m_changed = zope.interface.Attribute(
        """The persistent state of the object.

        This is one of:

        None -- The object is loaded from the MongoDB

        False -- The obj get updated within the update method and set the False

        True -- The object has been modified since it was last saved

        """)


class IMongoUpdateMixin(zope.interface.Interface):
    """Optional update method mixin class usfull for adhoc key/value updates.
    """

    def update(data, raiseErrors=False):
        """Update an object with given data without using the built in
        transaction handling.

        This method is usefull for update key/values given in a data dict
        which need to get updated during processing. On a successfull update,
        True is returnd otherwise False.

        If raiseErrors is set to True, an error get raised.

        We will revert the changes on errors, doesn't matter if an error happens
        and get skipped. Our transaction is trying to cleanup/store the
        original data during commit.

        We also update the _version in MongoDB and the object itself and set
        the _m_changed marker to False which is a marker for calling this
        update method.

        Note, changed key/values before calling this method get also stored
        in MongoDB. And we do only revert to the data to the current state
        before we called the update method. This means you have to take care
        or you can messup your data.

        It is important to know that if you do not raise Errors and the return
        value is False, the data did not get updated.
        """


class IMongoParent(zope.interface.Interface):
    """Offers mongo object id (_mpid) support

    The _mpid get stored as _pid in a mongo item and is used as a __parent__
    reference.

    Normaly a mongo object _id get used as _mpid. By default the _id and
    _mpid are None. If a IMongoParent is used as a mixn in an IMongoItem, the
    mongo item will set this _mpid as the items _pid.
    """

    _id = zope.schema.Field(u"Mongo ObjectId.")
    _mpid = zope.schema.Field(u"Referencable mongo __parent__ ObjectId")


class IMongoParentAware(zope.interface.Interface):
    """Offers __parent__ id (_pid) reference support

    Normaly the IMongoParent _mpid get used as _pid.
    """

    _pid = zope.schema.Field(u"Items __parent__ ObjectId.")


class IMongoItem(ISetup, IConvert, IDump, ICreatedModified):
    """Mongo storage item schema without ILocation.

    NOTE: this interface is the core interface for mongo sub items but this
    interface doens't provide ILocation or IContained. In most use case you
    need to provide ILocation in your own inherited interface. The missing
    ILocation interface in this interface makes it simpler for define correct
    permissions in ZCML.
    """

    _id = zope.schema.Field(u"Mongo ObjectId.")

    _m_changed = zope.interface.Attribute(
        """The persistent state of the object.

        This is one of:

        None -- The object is loaded from the MongoDB

        False -- The obj get updated within the update method and set the False

        True -- The object has been modified since it was last saved

        """)

    _m_independent = zope.interface.Attribute("""Independent state""")

    _type = zope.schema.TextLine(
        title=u'Type',
        description=u'Mongo item type',
        default=None,
        required=True)

    _version = zope.schema.Int(
        title=u'Version',
        description=u'Mongo item version',
        default=0,
        required=True)

    def notifyRemove():
        """Notifies an item before dumped and removed from MongoDB.

        This allows us to cleanup the object before we remove from MongoDB.
        e.g. remove references from other databases. This let us add a remove
        marker for track file system references in m01.mongofs.
        """

class IMongoSubObject(ISetup, IConvert, IDump):
    """Mongo item base class.

    Note: only MongoFieldProperty attributes get observed and updated by our
    transaction handling. If you change other attributes, you have to set
    _m_changed to True by yourself.

    Note: We do not support manipulators known from pymongo. We use a converter
    pattern for ding the convertion, see converters
    """

    _m_changed = zope.interface.Attribute(
        """The persistent state of the object.

        This is one of:

        None -- The object is loaded from the MongoDB

        False -- The obj get updated within the update method and set the False

        True -- The object has been modified since it was last saved

        """)

    _type = zope.schema.TextLine(
        title=u'Type',
        description=u'Mongo item type',
        default=None,
        required=True)


class IMongoStorageItem(IMongoItem):
    """Mongo storage item."""


class IMongoContainerItem(IMongoItem):
    """Mongo container item."""


class ISecureMongoStorageItem(IMongoStorageItem, ISecurityAware):
    """Secure mongo storage item."""


class ISecureMongoContainerItem(IMongoContainerItem, ISecurityAware):
    """Secure mongo container item."""


class IMongoObjectAware(zope.interface.Interface):
    """Object that contains IMongoObject properties.

    This interface is optional. It just shows what an object must implement
    which uses a MongoObjectProperty for one or more attributes. The defined
    _moid is, together with a double point followed by the attribute name, used
    as a parent reference id in a MongoObject and exposed as _oid.

    An _moid could be a MongoDB _id or something like:

    ser43130chke34

    if such an object defines an attribute called myattr, the MongoObject _oid
    looks like:

    ser43130chke34:myattr

    The MongoFieldProperty is responsible for setup such _oid values based on
    the given instance _moid and field name.

    Attention: the _oid must be unique in your application, or at least unique
    in the MongoDB which the MongoObject get stored. Otherwise an
    IMongoAwareObject could get a wrong attribute value. Except if you like to
    share a MongoObject within different MongoObject __parent__ by using a
    shared _moid.

    We explicitly choosed this naming reference concept because this allows us
    to add new MongoObject without to write into the __parent__ object. Another
    concept would be to write the MongoObject _id into the MongoAwareObject
    which would force a write access to both the MongoAwareObject and
    MongoObject.

    """

    _moid = zope.schema.TextLine(
        title=u'Unique object ID',
        description=u'Unique ID used as MongoObject __parent__ reference',
        default=None,
        required=True,
        readonly=True)


class IMongoObject(IMongoItem, IMongoTransactionAware):
    """Mongo object without ILocation

    This mongo (item) object is observed by it's own transaction data manager.

    NOTE: this interface is the core interface for mongo sub items but this
    interface doens't provide ILocation or IContained. In most use case you
    need to provide ILocation in your own inherited interface. The missing
    ILocation interface in this interface makes it simpler for define correct
    permissions in ZCML.
    """

    _oid = zope.schema.TextLine(
        title=u'Mongo parent object ID including attribute name',
        description=u'Mongo parent object ID with including attribute name',
        default=None,
        required=True,
        readonly=True)

    # this is new since 0.6.0, the MongoObjectProperty will converte the items
    # during load and save them by it's _oid which does not change
    _field = zope.schema.TextLine(
        title=u'Name of parent field where this item is stored in',
        description=u'Name of parent field where this item is stored in',
        default=None,
        required=True)

    removed = zope.schema.Bool(
        title=u'Removed marker',
        description=u'Removed marker',
        default=False,
        required=True)

    def getCollection(parent):
        """Returns the right collection where the mongo object get stored.

        Note, this method must be a classmethod whihc makes it work with
        MongoObjectProperty
        """


# mongo mapping
class IMongoStorage(IMongoCollectionAware, IMongoBatchAware,
    zope.container.interfaces.IReadContainer):
    """Mongo storage without ILocation"""

    def add(obj):
        """items"""

    def __delitem__(name):
        """Delete the named object from the container."""


class IMongoContainer(IMongoCollectionAware, IMongoBatchAware,
    zope.container.interfaces.IContainer):
    """Mongo container without ILocation"""


# geo location support
class IGeoSchema(IDump):
    """Geo object base schema"""

    lon = zope.schema.Float(
        title=_(u'longitude'),
        description=_(u'longitude'),
        required=True)

    lat = zope.schema.Float(
        title=_(u'latitude'),
        description=_(u'latitude'),
        required=True)


class IGeoLocation(IGeoSchema):
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

    Note: The GeoLocation is registered with zope.Public permission. This is
    fine for ost use case since you will protect the property which is storing
    such a GeoLocation item. There is no need to explicit protect the lon/lat
    attributes. Just make sure npbody with the correct permission can access
    the GeoLocation item itself.

    """


class IGeoPoint(IGeoSchema):
    """Geo Point data wrapper, providing preserved lon/lat value order
    and supporting _m_changed marker concept.

    This item must get defined with a zope.schema.Object field and the
    MongoGeoPointProperty property. For more info see geo.txt and testing.py

    This implementation uses the order longitude, latitude as described in
    mongodb documentation because of unnamed lng/lat list values.

    """

    type = zope.schema.TextLine(
        title=u'Geo object type',
        description=u'Geo object type',
        default=u'Point',
        readonly=True,
        required=True)
