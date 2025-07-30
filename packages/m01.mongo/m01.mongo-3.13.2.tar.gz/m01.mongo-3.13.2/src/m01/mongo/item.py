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
try:
    unicode
except NameError:
    # Python 3
    unicode = str

__docformat__ = "reStructuredText"

import datetime
import bson.objectid

import zope.interface
import zope.location.interfaces

import m01.mongo
from m01.mongo import UTC
from m01.mongo import LOCAL
from m01.mongo import interfaces
from m01.mongo import base
from m01.mongo.fieldproperty import MongoFieldProperty
from zope.interface import implementer

_marker = object()


class MongoSubItem(base.SetupConvertDump):
    """Mongo sub item base class usable for MongoList schema items.

    A mongo sub item get used in a MongoItems (list) and is a part off a
    MongoItem which is stored in a MongoDB. Such a mongo sub item provide an
    own object _id reference which is stored in the sub items container like
    we use with MongoItemsData by default. As you can see in MongoFieldProperty,
    we need a MongoList schema for setup such a MongoItemsData container.

    """

    _id = None
    _type = None
    _m_changed_value = None

    # built in skip and dump names
    _skipNames = ['__name__']
    _dumpNames = ['_id', '_type', 'created', 'modified']

    # customize this in your implementation
    skipNames = []
    dumpNames = []

    created = MongoFieldProperty(interfaces.IMongoSubItem['created'])
    modified = MongoFieldProperty(interfaces.IMongoSubItem['modified'])

    def __init__(self, data):
        """Initialize a MongoSubItem with given data."""
        # set given or new _id
        _id = data.pop('_id', _marker)
        if _id is _marker:
            _id = bson.objectid.ObjectId()
        self.__dict__['_id'] = _id

        # set given or None __parent__
        __parent__ = data.pop('__parent__', None)
        if __parent__ is not None:
            self.__parent__ = __parent__

        # set given or new _type
        _type = data.pop('_type', self.__class__.__name__)
        if _type != self.__class__.__name__:
            raise TypeError("Wrong mongo item _type used")
        self.__dict__['_type'] = unicode(_type)

        # set given or new created datetime
        created = data.pop('created', _marker)
        if created is _marker:
            created = m01.mongo.now(UTC)
        self.__dict__['created'] = created

        # update object with given key/value data
        self.setup(data)

        # it is very important to set _m_changed_value to None, otherwise each
        # read access will end in a write access.
        self._m_changed_value = None

    @property
    def __name__(self):
        return unicode(self._id)

    def _m_changed():
        def fget(self):
            return self._m_changed_value
        def fset(self, value):
            if value == True:
                self._m_changed_value = value
                if self.__parent__ is not None:
                    self.__parent__._m_changed = value
            elif value != True:
                raise ValueError("Can only dispatch True to __parent__")
        return property(fget, fset)

    _m_changed = _m_changed()

# TODO: this is not the best contept. Use a comit marker and implement this
#       in Dump mixin:
#    def dump(self, dumpNames=None, dictify=False, commit=False):
#        # prevent write access
#        if self._m_changed and commit:
#            self.modified = m01.mongo.now(UTC)
#        return super(MongoSubItem, self).dump(dumpNames, commit)
# or even better use a private attr for modified e.g. _m_modified and write to
# this attr in _m_changed. This would write _m_modified on each _m_changed but
# it would only write the new changed date if we commit the parent obj.
# probably use a _m_modified_original and keep a reference to it and reset the
# _m_modified if we set _m_changed to None again which also could happen
    def dump(self, dumpNames=None, dictify=False):
        if self._m_changed and (dumpNames is None or 'modified' in dumpNames):
            self.modified = m01.mongo.now(UTC)
        return super(MongoSubItem, self).dump(dumpNames)


@implementer(interfaces.IMongoContainerItem, interfaces.IMongoParentAware, zope.location.interfaces.ILocation)
class MongoContainerItem(base.MongoItemBase):
    """Simple mongo container item.

    Implement your own IMongoContainerItem with the attributes you need.
    """

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(zope.location.interfaces.ILocation['__name__'])


@implementer(interfaces.IMongoStorageItem, interfaces.IMongoParentAware, zope.location.interfaces.ILocation)
class MongoStorageItem(base.MongoItemBase):
    """Simple mongo storage item.

    This MongoItem will use the mongo ObjectId as the __name__. This means
    you can't set an own __name__ value for this object.

    Implement your own IMongoStorageItem with the attributes you need.
    """

    _skipNames = ['__name__']

    @property
    def __name__(self):
        return unicode(self._id)


@implementer(interfaces.ISecureMongoContainerItem, interfaces.IMongoParentAware, zope.location.interfaces.ILocation)
class SecureMongoContainerItem(base.SecureMongoItemBase):
    """Security aware MongoContainerItem."""

    # validate __name__ and observe to set _m_changed
    __name__ = MongoFieldProperty(zope.location.interfaces.ILocation['__name__'])


@implementer(interfaces.ISecureMongoStorageItem, interfaces.IMongoParentAware, zope.location.interfaces.ILocation)
class SecureMongoStorageItem(base.SecureMongoItemBase):
    """Security aware MongoStorageItem."""

    _skipNames = ['__name__']

    @property
    def __name__(self):
        return unicode(self._id)


@implementer(interfaces.IMongoSubObject, zope.location.interfaces.ILocation)
class MongoSubObject(base.MongoSubObjectBase):
    """Mongo sub Object class"""


@implementer(interfaces.IMongoObject, zope.location.interfaces.ILocation)
class MongoObject(base.MongoItemBase):
    """Mongo object used for store as object value on persistent or non
    persistent objects.

    This mongo object is used as object value and must provide an own
    collection method. This means such an object get not stored in the same
    collection as the __parent__ object .The __parent__ could be a mongo item,
    sub item or container etc.

    The attribute name is used as the mongo object _field. This _field
    is together with the mongo object parent id (_moid) used as unique id.
    This unique id is exposed as _oid value. Also see MongoObjectProperty

    The __parent__ object which contains such MongoObject items needs to
    provide an _moid attribute with a unique object id. This _moid is used as a
    part of unique mongo id (_oid). You can use the p01.oid package which
    provides such a unique id for peristent __parent__ objects if you mix ZODB
    and ZODB less databases or you can use the MongoObjectAware class for non
    persistent items. If you use the p01.oid package, you need to expose the
    oid as _moid in your implementation. See how we did it in MongoObjectAware

    Note: If you enhance your own MongoObject __init__ method, don't forget
    to set_m_changed to None. Otherwise it will end in write access on
    each read.

    Changes:
    Since version 0.6.0 we will use the _field value as the MongoObject part
    for _oid. Previous version where using the __name__ instead. For older
    MongoObject items stored in mongodb we will support boths. This means if
    a _field valu is given we use them if not we use the __name__.

    New items must set the __name__ explict if they need one. Note, a __name__
    allows to traverser the MongoObject item within a different container
    by it's __name__. This is the reason why we changed the implementation.
    Now it's possible to store the MongoObject as property valu in a parent
    item and at the same time to implement a container or storage and traverse
    them as container item. This is a core pattern for gridfs files implemented
    in m01.grid (see m01.grid.item.FileObject)

    Note:
    The MongoObject implementation can't get mixed into one class with
    MongoContainerItem, MongoStorageItem or MongoItem beacause of the
    transaction commit process API.

    We currently only use the MongoObject items with read container which only
    allow to traverse to the MongoObject items. We have not checked if it is
    possible to implement a container or storage which is able to write changes
    in MongoObject items to the collection like we do with MongoContainerItem
    or MongoStorageItem.

    The current API looks like it should be possible to implement a MongoObject
    as item. If we do so in the future, we probably offer a IMongoObjectStorage
    and MongoObjectContainer. The big question is does such a container
    implementation support to store items in different collections?
    """

    # write concern markers (empty dict means connection settings get used)
    _m_insert_write_concern = {}
    _m_update_write_concern = {}
    _m_remove_write_concern = {}

    _m_independent = False

    # marker for remove handling
    _field = MongoFieldProperty(interfaces.IMongoObject['_field'])
    removed = MongoFieldProperty(interfaces.IMongoObject['removed'])

    _skipNames = ['_oid']
    _dumpNames = ['_id', '_oid', '__name__', '_type', '_version',
                  '_field',
                  'created', 'modified', 'removed']

    @classmethod
    def getCollection(cls, parent):
        """Note, this method must be a classmethod and return the collection."""
        raise NotImplementedError(
            "Subclass must implement classmethod getCollection")

    @property
    def collection(self):
        return self.getCollection(self.__parent__)

    @property
    def _oid(self):
        try:
            # BBB before 0.6.0, never remove
            # the _field value is new since 0.6.0. Previous version where using
            # the __name__ instead. Support both
            _field = self._field and self._field or self.__name__
            return u'%s:%s' % (self.__parent__._moid, _field)
        except AttributeError as e:
            if self.__parent__ is None:
                raise AttributeError("Missing __parent__ object")
            else:
                raise AttributeError(
                    '__parent__ "%s" does not provide an _moid' % (
                        self.__parent__))

    # MongoDB handler methods
    def doInsert(self):
        self.modified = m01.mongo.now(UTC)
        self.collection.insert_one(self.dump())

    def doUpdate(self, upsert=False):
        self.modified = m01.mongo.now(UTC)
        data = self.dump()
        # skip _id with $set, OperationFailure: Mod on _id not allowed
        data.pop('_id', None)
        self.collection.update_one({'_id': self._id}, {'$set': data},
            upsert=upsert)

    def doRemove(self):
        # never call remove without an _id
        if self._id is None:
            raise ValueError("Empty _id given, this would remove all objects")
        self.collection.delete_one({'_id': self._id})
        if self._oid in LOCAL.__dict__:
            del LOCAL.__dict__[self._oid]

    def begin(self):
        """Beginn commit a transaction handling."""
        # compare not independent items by it's _id and version number
        if self._version > 0 and not self._m_independent \
            and not self.collection.find_one(
            {'_id':self._id, '_version':self._version}):
            raise ValueError("MongoItem version does not compare")

    # transaction management methods
    def commit(self):
        """Start commit transaction handling."""
        pass

    def vote(self):
        """Process MongoDB insert and update calls.

        Note, if something fails, this could leave inconsistent data in MongoDB.
        """
        if self._m_changed:
            # remove marked item
            if self.removed:
                self.doRemove(**self._m_remove_write_concern)
            else:
                # handle not removed item
                self._version += 1
                if self._version == 1:
                    # insert new item
                    self.doInsert(**self._m_insert_write_concern)
                else:
                    # update existing items
                    self.doUpdate(**self._m_update_write_concern)

    def abort(self):
        """Abort transaction handling."""
        pass

    def finish(self):
        """Finish transaction commit."""
        if self._oid in LOCAL.__dict__:
            del LOCAL.__dict__[self._oid]
