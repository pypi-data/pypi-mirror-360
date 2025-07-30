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
from __future__ import division
from __future__ import absolute_import
from zope.interface import implementer
from future import standard_library
import six
standard_library.install_aliases()
from builtins import str
from six import string_types
from past.utils import old_div
from future.utils import PY2
from future.types import newstr

import _thread
import datetime

import pymongo
import pymongo.errors
import bson.objectid
import bson.son

import transaction
import zope.interface
import zope.location.location
from zope.security.proxy import removeSecurityProxy

import m01.mongo
from m01.mongo import UTC
from m01.mongo import LOCAL
from m01.mongo import interfaces
from m01.mongo import util
from m01.mongo.fieldproperty import MongoFieldProperty
from m01.mongo.tm import ensureMongoTransaction

_marker = object()


class MongoObjectAware(object):
    """Offers _moid (mongo object id) referencable for IMongoObject as _oid"""

    # mongo id, built in attrs
    _id = None

    # mongo object _id (_moid) used as a _oid reference in IMongoObject, by
    # default None. This additional _moid (_id) to _oid mapping offers a hook
    # for custom _moid concepts independent from other _id refences like _mpid.
    # See IMongoItemAware for more info.
    @property
    def _moid(self):
        return self._id


class MongoItemAware(object):
    """Offers _mpid (mongo parent id) referencable for IMongoParentAware item"""

    # mongo id, built in attrs
    _id = None

    # mongo _id used as __parent__ reference, by default None. This additional
    # _id to _mpid mapping offers a hook for custom _pid concepts. Which means
    # you can use a similar _mpid in different containers for sharing items.
    # Note: no _mpid means no __parent__ filter and all items in the same
    # collection get shared as long as no other filters get used. See doFind
    # doFindOne etc. methods how we filter by default
    @property
    def _mpid(self):
        if self._id is not None:
            return self._id


class MongoParentAware(object):
    """References IMongoParent item by it's _mpid stored as _pid

    Used for restrict an item to a given __parent__ using a _mpid attribute.

    If no _mpid is given, the items belong to any container which will load
    items without additional filters. See doFind, doFindOne etc. methods for
    more information about filter items.
    """

    # built in attrs
    _pid = None
    _m_parent = None

    def __parent__():
        def fget(self):
            return self._m_parent
        def fset(self, __parent__):
            self._m_parent = __parent__
            # only set _pid the first time
            if self._pid is None:
                try:
                    self._pid = __parent__._mpid
                except AttributeError as e:
                    pass
        return property(fget, fset)

    __parent__ = __parent__()


class SetupConvert(zope.location.location.Location):
    """Mixin class for setup, update and dump item and subitems.

    Note: a converter dict can contain a converter method which returns a
    converted value or a class. A class can be used if we need to create sub
    items values. e.g. embeded mongo array data
    """

    # built in attrs without change observation. Note: this base class does not
    # support _pid (__parent__) reference. See MongoItemBase for _pid support
    __parent__ = None
    __name__ = None
    _m_initialized = False
    _m_changed = None

    # _skipNames defines which attribute/valus will not get stored containd in
    # the datat from mongodb. The _skipNames list will get overriden with the
    # default skipped attribute names from the base class which implements this
    # class. Don't customize this in your custom implementation or if so, make
    # sure you will define every skipped attribute name even those which will
    # get added in future release.
    _skipNames = []

    # customize this in your implementation
    skipNames = [] # attribute names
    converters = {} # attr-name/converter
    defaults = {} # attr-name/value

    def convert(self, key, value):
        """This convert method knows how to handle nested converters.

        A converter can convert attribute values if the attribute
        value is a list of items. You can use a method which knows how to
        handle each value type.

        You can define a converter method which knows to convert all kind
        of items like:

        def toMyItems(value):
            _type = value.get('_type')
            if _type == 'Car':
                return Car(value)
            elif _type == 'House':
                return House(value)
            else:
                return value

        converters = {'myItems': toMyItems}

        IMPORTANT; this converter can NOT convert a nested data structure, it
        is NOT possible to define converters like this:

        e.g.
        def toCar(value):
            return Car(value)

        converters = {'myItems': {'house': toHouse, 'car': toCar}}

        """
        converter = self.converters.get(key)
        if converter is not None:
            if isinstance(value, (list, tuple)):
                # convert list values
                value = [converter(d) for d in value]
            elif isinstance(value, dict):
                # convert mapping values
                if hasattr(value, '__parent__') and value.__parent__ is None:
                    # apply __parent__ if value.__parent__ is None
                    value.__parent__ = self
                value = converter(value)
        return value

    def setup(self, data, dumpOriginalData=False):
        """Setup object with given data key/values. See IMongoHandler"""
        if dumpOriginalData:
            orgData = {'_m_changed': self._m_changed, '_version': self._version}
        else:
            orgData = None

        # setup key/values
        skipNames = self._skipNames + self.skipNames
        for k, v in list(data.items()):
            # skip names if given in data dict
            if k not in skipNames:
                # dump old data
                if orgData is not None:
                    if isinstance(getattr(self, k), (list, tuple)):
                        orgData[k] = [obj.dump() for obj in getattr(self, k, [])]
                    else:
                        orgData[k] = getattr(self, k)
                # convert value
                v = self.convert(k, v)
                # set value
                try:
                    setattr(self, k, v)
                except zope.interface.Invalid as e:
                    pass
                except (AttributeError, ValueError) as e:
                    raise AttributeError(
                        "Can't set value %s %s for attr %s: %r on %r" % (
                            v, type(v), k, str(e), self))

        # this allows to ensure default values or even converter instances
        for k, v in list(self.defaults.items()):
            if getattr(self, k, None) is None:
                # convert value or return an initial empty converter instance
                v = self.convert(k, v)
                setattr(self, k, v)

        # mark the item as initialized. This allows us to implement attribtues
        # with apply decorator which act different for an initialized object
        self._m_initialized = True

        # return original data or None
        return orgData

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)

NO_VALUE_MARKER = object()

class Dump(object):
    """Mixin class for dump item and subitems."""

    # _dumpNames defines which attributes will get stored in mongodb. This
    # list of attribute names will get overriden with default names from the
    # base class which implements this class. Don't customize this list in your
    # custom implementation or if so, make sure you will define every attribute even those which will
    # name which will get added in future release.
    _dumpNames = []
    # customize this in your implementation
    dumpNames = [] # attribute names

    def dump(self, dumpNames=None, dictify=False):
        """Dump the object to json data dict providing a sorted order."""
        if dumpNames is None:
            dumpNames = self._dumpNames + self.dumpNames
        # allways preserve order in mongodb
        data = bson.son.SON()
        to_lower = lambda x: x.lower() if isinstance(x, str) else x.decode('utf-8').lower()
        for k in sorted(dumpNames, key=to_lower):
            # get value from __dict__, this will ensure that we catch values
            # converted by field properties e.g. MongoDateProperty
            v = self.__dict__.get(k, NO_VALUE_MARKER)
            if v is NO_VALUE_MARKER:
                # this will make sure that we catch values which are not stored
                # in our __dict__ like object properties and schema default
                # values
                v = getattr(self, k, NO_VALUE_MARKER)
            # if we found a value dump and/or store it
            if v is not NO_VALUE_MARKER:
                # found a value or default schema value
                if hasattr(v, 'dump'):
                    # dump MongoSubItem, MongoDubObject, MongoItemsData or
                    # MongoListData
                    data[k] = v.dump()
                else:
                    # store simple value including None if None is given
                    data[k] = v
        if dictify:
            data = m01.mongo.dictify(data)
        return data


class SetupConvertDump(SetupConvert, Dump):
    """Mixin class for update items without transaction support"""


@implementer(interfaces.IMongoUpdateMixin)
class MongoUpdateMixin(object):
    """Optional update method mixin class.

    This mixin class offers a method which allows to update a MongoItem without
    a transaction process. You can use this mixin class for update counters or
    other not so important values. Not, this get probably called more then once
    if the transaction runs into a retry loop.
    """


    def update(self, data, raiseErrors=False, **kwargs):
        """Update an object with given data without using the built in
        transaction handling. This method calls setup which makes sure that
        we do not mark the object as _m_changed.
        """
        # prevent changes if tansaction is doomed
        t  = transaction.get()
        if t.isDoomed():
            return False

        # updated object data
        orgData = self.setup(data, dumpOriginalData=True)

        # update the data in MongoDB
        collection = self.__parent__.collection
        try:
            if self._version == 0:
                dump = self.__parent__.doInsertDump(self)
                self.__parent__.doInsert(collection, dump)
            else:
                dump = self.__parent__.doUpdateDump(self)
                self.__parent__.doUpdate(collection, dump, upsert=False)
        except (TypeError, pymongo.errors.ConnectionFailure,
            pymongo.errors.AutoReconnect, pymongo.errors.InvalidName) as e:
            # revert data, the transaction will try to store them later
            self.setup(orgData)
            if raiseErrors:
                raise e
            else:
                return False

        # mark _m_changed with False and not None like we do in load method
        # otherwise the item get processed again with our transaction handling
        self._m_changed = False
        return True


class MongoItemBase(MongoParentAware, SetupConvertDump):
    """Mongo item base class.

    Note: only MongoFieldProperty attributes get observed and updated by our
    transaction handling. If you change other attributes, you have to set
    _m_changed to True by yourself.

    Note: We do not support manipulators known from pymongo. We use a converter
    pattern for ding the convertion, see converters
    """

    # built in attrs
    _id = None
    _type = None
    _version = None
    _m_independent = False

    # built in skip and dump names
    _skipNames = []
    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified']

    # attrs with default values
    created = MongoFieldProperty(interfaces.IMongoItem['created'])
    modified = MongoFieldProperty(interfaces.IMongoItem['modified'])

    def __init__(self, data):
        """Initialize a mongo item with given data.

        This method will also make sure that the __parent__ and other values
        get set before we call setup.

        Note: if you enhance your own MongoItem __init__ method, don't forget
        to set_m_changed to None. Otherwise it will end in write access on
        each read.
        """
        # set given or None _pid (__parent__._id) reference
        self._pid = data.pop('_pid', None)
        # set given or None __parent__
        self.__parent__ = data.pop('__parent__', None)

        # set given or new _id
        _id = data.pop('_id', _marker)
        if _id is _marker:
            _id = bson.objectid.ObjectId()
        self.__dict__['_id'] = _id

        # set given or new _type if not already set as built-in
        if self._type is None:
            _type = data.pop('_type', self.__class__.__name__)
            if _type != self.__class__.__name__:
                raise TypeError("Wrong mongo item _type used")
            self.__dict__['_type'] = str(_type)

        # set given or 0 (zero) _version
        self.__dict__['_version'] = data.pop('_version', 0)

        # set given or new created datetime
        created = data.pop('created', _marker)
        if created is _marker:
            created = m01.mongo.now(UTC)
        self.__dict__['created'] = created

        # setup object with given (non IMongoItem) key/value data
        self.setup(data)

        # it is very important to set _m_changed to None, otherwise each read
        # access will end in a write access.
        self._m_changed = None

    def notifyRemove(self):
        """Notifies an item before dumped and removed from MongoDB."""
        pass


class SecureMongoItemBase(MongoItemBase):
    """Secure mongo item base class."""

    # built in skip and dump names
    _skipNames = []
    _dumpNames = ['_id', '_pid', '_type', '_version', '__name__',
                  'created', 'modified',
                  '_ppmrow', '_ppmcol',
                  '_prmrow', '_prmcol',
                  '_rpmrow', '_rpmcol',
                  ]

    def __init__(self, data):
        self._ppmrow = {}
        self._ppmcol = {}
        self._prmrow = {}
        self._prmcol = {}
        self._rpmrow = {}
        self._rpmcol = {}
        super(SecureMongoItemBase, self).__init__(data)


class MongoSubObjectBase(MongoParentAware, SetupConvertDump):
    """Mongo item base class.

    Note: only MongoFieldProperty attributes get observed and updated by our
    transaction handling. If you change other attributes, you have to set
    _m_changed to True by yourself.

    Note: We do not support manipulators known from pymongo. We use a converter
    pattern for ding the convertion, see converters
    """

    # built in attrs
    _type = None
    __m_changed = None

    # built in skip and dump names
    _skipNames = []
    _dumpNames = ['_type', '__name__']

    def __init__(self, data):
        """Initialize a mongo sub object with given data.

        This method will also make sure that the __name__ and __parent__ and
        other values get set before we call setup.

        Note: if you enhance your own MongoSubObjectBase __init__ method, don't
        forget to set_m_changed to None if you change value. Otherwise it will
        end in write access on each read access.
        """
        # set given or None __name__ and __parent__
        self.__name__ = data.pop('__name__', None)
        self.__parent__ = data.pop('__parent__', None)
        # set given or new _type if not already set as built-in
        if self._type is None:
            _type = data.pop('_type', self.__class__.__name__)
            if _type != self.__class__.__name__:
                raise TypeError("Wrong mongo item _type used")
            self.__dict__['_type'] = str(_type)
        # setup object with given (non IMongoItem) key/value data
        self.setup(data)
        # it is very important to set _m_changed to None, otherwise each read
        # access will end in a write access.
        self._m_changed = None

    def _m_changed():
        def get(self):
            return self.__m_changed
        def set(self, value):
            self.__m_changed = value
            if self.__parent__ is not None and value == True:
                self.__parent__._m_changed = True
        return property(get, set)

    _m_changed = _m_changed()


@implementer(interfaces.IMongoTransactionAware)
class MongoMappingBase(MongoItemAware, zope.location.location.Location):
    """Mongo mapping base class with thread save transaction and caching
    support.

    Note: right now we do not support manipulators. If we add suport for
    manipulators, check/change collection update and insert calls.

    Note: the databaseName and collectionName are not exposed in the API this
    is only use in our default implementation. You just have to make sure to
    define a collection and a cacheKey.

    Note: if you define a custom load method, you can use the built-in _type
    value where each Montoitem will use. By default the MongoItem uses it's
    class.__name__ as _type.

    """


    @property
    def collection(self):
        """Returns a mongodb collection"""
        raise NotImplementedError(
            "Subclass must implement collection attribute")

    @property
    def cacheKey(self):
        """Provide a thread local and unique cache key.

        Note: It's very important that you define a unique cache key which does
        not conflict with other instances or you will get into trouble because
        2 object whould begin the transaction before vote them. Then the first
        transaction will move the items to the transaction cache and the second
        object whould remove the transaction cache because of the same cache
        key before any vore call get processed which whould add items to the
        mongodb. The id(self) will make sure that we use unique cache keys per
        instance.
        """
        return '%s.%i.%i' % (self.collection.full_name, id(self),
            _thread.get_ident())

    def load(self, data):
        """Load data into a IMongoItem

        Since the default MongoContainerItem and MongoStorageItem are useless,
        we do not provide a default implementation.

        Implement this method if you need another mongo item. If you override
        the doLoad method which normaly calls this method, take care that your
        items get marked as not _m_changed. Otherwise it will end in write
        access on each read operation. Also see what else we do in doLoad
        method an do the same if needed. e.g. locate items etc.
        """
        raise NotImplementedError("Subclass must implement load")

    def doLoad(self, data):
        """Prepare data and load them into IMongoItem.

        This method calls the load method and will make sure that we
        inject a __parent__ and mark the loaded object as not _m_changed

        BIG NOTE: never ever load partial data or the transaction will write
        only this partial data back to mongo. This means never load data if
        they get loaded with the doFind method using a fields argument within
        a subset of the items fields!
        """
        # first validate data
        assert data['_id'] is not None
        # the __setitem__ or add methods are responsible that a _pid get
        # added. This means we can just assert them if an _mpid is given
        if self._mpid is not None:
            assert data['_pid'] == self._mpid

        __name__ = data.get('__name__')
        # make sure we never load removed data
        if __name__ in self._cache_removed:
            raise KeyError(__name__)
        # ensure that we never load objects by data twice, allways return our
        # objects from cache first, otherwise we will have two instances
        # representing the same object which will make troubles if we commit
        # our transaction
        obj = self._cache_loaded.get(__name__)
        # only load if not cached
        if obj is not None:
            # this only fails if we do not provide unique cacheKey
            assert obj.__parent__ is self
            assert obj._id == data['_id']
            # return the cached obj
            return obj
        # locate without to set _pid
        data['__parent__'] = self
        obj = self.load(data)
        # cache
        self._cache_loaded[obj.__name__] = obj
        # mark as NOT changed
        obj._m_changed = False
        # return located obj
        return obj

    # filter
    def doFilter(self, spec):
        """Base filter for all do* methods if not overriden"""
        if self._mpid is not None:
            spec['_pid'] = self._mpid
        return spec

    def doCountFilter(self, spec):
        """Filter for doCount method"""
        return self.doFilter(spec)

    def doFindOneFilter(self, spec):
        return self.doFilter(spec)

    def doFindFilter(self, spec):
        return self.doFilter(spec)

    def doBatchDataFilter(self, spec):
        return self.doFilter(spec)

    # dump methods (including validation)
    def doInsertDump(self, obj):
        assert obj._version == 0
        obj._version += 1
        data = obj.dump()
        assert data['_id'] is not None
        assert data['_version'] == 1
        if self._mpid is not None:
            assert data['_pid'] == self._mpid
        return data

    def doUpdateDump(self, obj):
        assert obj._version  > 0
        curVersion = obj._version
        obj._version += 1
        data = obj.dump()
        assert data['_id'] is not None
        if self._mpid is not None:
            assert data['_pid'] == self._mpid
        assert data['_version'] > 1
        # has version and not independent, check if not changed
        if not obj._m_independent:
            spec = {'_id': data['_id'], '_version': curVersion}
            if self.collection.find_one(spec) is None:
                raise ValueError(
                    "MongoItem version does not compare")
        return data

    def doRemoveDump(self, obj):
        assert obj._version  > 0
        curVersion = obj._version
        obj._version += 1
        data = obj.dump()
        assert data['_id'] is not None
        if self._mpid is not None:
            assert data['_pid'] == self._mpid
        assert data['_version'] > 1
        # has version and not independent, check if not changed
        if not obj._m_independent:
            spec = {'_id': data['_id'], '_version': curVersion}
            if self.collection.find_one(spec) is None:
                raise ValueError(
                    "MongoItem version does not compare")
        return data

    # mongo commiter
    def doCount(self, collection, spec=None, skipFilter=False):
        if spec is None:
            spec = bson.son.SON()
        if not skipFilter:
            spec = self.doCountFilter(spec)
        return collection.count_documents(spec)

    def doFindOne(self, collection, spec=None, fields=None, skipFilter=False):
        if spec is None:
            spec = bson.son.SON()
        if not skipFilter:
            spec = self.doFindOneFilter(spec)
        return collection.find_one(spec, fields)

    def doFind(self, collection, spec=None, fields=None, skipFilter=False):
        if spec is None:
            spec = bson.son.SON()
        if not skipFilter:
            spec = self.doFindFilter(spec)
        return collection.find(spec, fields)

    def doInsert(self, collection, data):
        if not isinstance(data, list):
            data = [data]
        for d in data:
            collection.insert_one(d)

    def doUpdate(self, collection, data, upsert=False):
        if not isinstance(data, list):
            data = [data]
        for d in data:
            # doUpdateDump is allowed to return None for block item update
            if d is not None:
                # very critical error, never update items without an _id
                assert d['_id'] is not None
                filter = {'_id': d['_id']}
                # skip _id with $set, OperationFailure: Mod on _id not allowed
                d.pop('_id', None)
                collection.update_one(filter, {'$set': d}, upsert=upsert)

    def doRemove(self, collection, data):
        if not isinstance(data, list):
            data = [data]
        for d in data:
            # doRemoveDump is allowed to return None for block item remove
            if d is not None:
                # very critical error, never remove items without an _id
                assert d['_id'] is not None
                collection.delete_one({'_id': d['_id']})

    # caches
    @property
    def _cache(self):
        """Thread local cache for objects."""
        return LOCAL.__dict__.setdefault(self.cacheKey, {})

    @property
    def _cache_added(self):
        return self._cache.setdefault('added', {})

    @property
    def _cache_loaded(self):
        return self._cache.setdefault('loaded', {})

    @property
    def _cache_removed(self):
        return self._cache.setdefault('removed', {})

    @property
    def _t_cache_insert(self):
        return self._cache.setdefault('insert', [])

    @property
    def _t_cache_update(self):
        return self._cache.setdefault('update', [])

    @property
    def _t_cache_remove(self):
        return self._cache.setdefault('remove', [])

    def resetLoadCache(self):
        """Reset thread local load caches."""
        _cache = self._cache
        if 'added' in _cache:
            del _cache['added']
        if 'loaded' in _cache:
            del _cache['loaded']
        if 'removed' in _cache:
            del _cache['removed']

    def resetTransactionCache(self):
        """Reset thread local transaction caches."""
        _cache = self._cache
        if 'insert' in _cache:
            del _cache['insert']
        if 'update' in _cache:
            del _cache['update']
        if 'remove' in _cache:
            del _cache['remove']

    def resetCache(self):
        """Reset thread local cache."""
        if self.cacheKey in LOCAL.__dict__:
            del LOCAL.__dict__[self.cacheKey]

    # IContainer API
    def __len__(self):
        # also take as removed and added cached items into account
        counts = self.doCount(self.collection)
        return counts - len(self._cache_removed) + len(self._cache_added)

    def items(self):
        # join transaction handling
        self.ensureTransaction()
        for data in self.doFind(self.collection):
            __name__ = data['__name__']
            if __name__ in self._cache_removed:
                # skip removed items
                continue
            obj = self._cache_loaded.get(__name__)
            if obj is None:
                try:
                    # load, locate and cache if not cached
                    obj = self.doLoad(data)
                except (KeyError, TypeError):
                    continue
            yield __name__, obj
        # also return keys/items not stored in MongoDB yet
        for k, v in list(self._cache_added.items()):
            yield k, v

    def keys(self):
        for data in self.doFind(self.collection, {}, ['__name__']):
            __name__ = data['__name__']
            if __name__ in self._cache_removed:
                # skip removed items
                continue
            else:
                yield __name__
        # also return keys not stored in MongoDB yet
        for k, v in list(self._cache_added.items()):
            yield k

    def values(self):
        # join transaction handling
        self.ensureTransaction()
        for data in self.doFind(self.collection):
            __name__ = data['__name__']
            if __name__ in self._cache_removed:
                # skip removed items
                continue
            obj = self._cache_loaded.get(__name__)
            if obj is None:
                try:
                    # load, locate and cache if not cached
                    obj = self.doLoad(data)
                except (KeyError, TypeError):
                    continue
            yield obj
        # also return items not stored in MongoDB yet
        for k, v in list(self._cache_added.items()):
            yield v

    def __iter__(self):
        """Return an iterator for the keys of the mapping object.
        """
        return iter(list(self.keys()))

    def __getitem__(self, key):
        """get item"""
        raise NotImplementedError("Subclass must implement __getitem__")

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError as e:
            pass
        return default

    def __delitem__(self, key):
        """delete item"""
        # load object
        obj = self[key]
        # notify remove
        obj.notifyRemove()
        # cleanup cache
        if key in self._cache_added:
            # remove new items
            del self._cache_added[key]
        else:
            # import pdb; pdb.set_trace()
            # or add to remove cache but only if not yet added
            self._cache_removed[key] = obj
        # also remove from loaded items
        if key in self._cache_loaded:
            del self._cache_loaded[key]

    def getBatchData(self, query=None, page=1, size=25, sortName=None,
        sortOrder=None, searchText=None, fields=None, skipFilter=False):
        """Returns batched mongo data, current page, total items and page size.

        Note: this method will not return loaded IMongoItems. If you need to
        load the given mongo data you can simply iterate the given cursor and
        call doLoad(data). The doLoad method also takes care of all the cached
        items. But take care, since mongo returns removed items and doesn't
        know about new added items till a transaction commits, this method
        could return bad items. And if you like to skip removed items from
        the curser by yourself, the page and pages counter could get messed up.
        If you like to bypass this troubles, I highly recommend only call
        doLoad based on cursor data if you didn't add or remove items from a
        container in the same transaction.
        (response.redirect or transaction.commit are your friends)

        Note: the page can get recalculated if the page position doesn't fit
        into the batch. This means the page in the reult can be different as
        the given page input. This is usefull if we use a larger page number
        as we realy have, e.g. after remove an item.

        Note: this method will call doBatchDataFilter which could enhance
        the given query specification

        Note: take care, this method will ignore cached (removed, added) items
        till we commit the transaction. You can eighter commit the transaction
        or use a response redirect in your request before using this method
        after remove or add items.

        NOTE: searchText is not used in this method. But this method signature
        allows to implement a search pattern in your own implementation.
        IF you use a pure mongo $text index, simply provide the right $text
        query part in the query argument. If you use elasticsearch or other
        text indexing server simply implement your own concept. This method
        signature makes it possible to implement generic search APIs in UI
        like we use for livesearch etc.
        """
        # start with server, this allows us to approve the page position
        if query is None:
            query = bson.son.SON()
        if not skipFilter:
            # skip batch data filter
            query = self.doBatchDataFilter(query)
        cursor = self.collection.find(query, fields)

        # get overall total based on query
        total = self.collection.count_documents({})
        # calculate pages
        pages = old_div(total,size)
        if pages == 0 or total % size:
            pages += 1
        # as next we approve our page position
        if page > pages:
            # restart with pages number as page which is the last page
            page = pages
            return self.getBatchData(query, page, size, sortName, sortOrder,
                searchText, fields, skipFilter)

        # calculate start size
        start = (page-1) * size
        cursor = cursor.skip(start)
        # sort result
        if sortName is not None:
            if sortOrder is None:
                if isinstance(sortName, six.string_types):
                    sortName = [(sortName, pymongo.ASCENDING)]
                elif not isinstance(sortName, list):
                    raise TypeError("if no sortOrder is specified, "
                                    "sortName must be an instance of list")
            cursor = cursor.sort(sortName, sortOrder)
        # limit result
        cursor = cursor.limit(size)
        # return data including probably adjusted page number
        return (cursor, page, pages, total)

    # transaction API
    def ensureTransaction(self):
        """Ensure that a transaction data manager observes our modification.

        Note: tis method is not exposed in our interface API.

        Note: we do not know if we return objects if they get modified. This
        means we observe all container which return items.

        Our transaction is not responsible for cleanup our thread local caches.
        We use an EndRequestEvent handler for cleanup our thread local cached
        items. Take care if you do testing, normaly the cache cleanup subscriber
        is not a part of the testing setup. But you can cleanup the caches by
        just call m01.mongo.clearThreadLocalCache(None) if you need to.
        """
        ensureMongoTransaction(self)

    def begin(self):
        """Prepare commit transaction handling.

        We move all relevant items from the load caches to the commit caches.
        This will give us empty load caches if the transactions runs into the
        retry loop.

        Note, prevent to load other mongo items which will run into ensure other
        transactions. This will fail if we join such new transactions during
        our commit phase.
        """
        self.resetTransactionCache()
        ci = self._t_cache_insert
        cu = self._t_cache_update
        dt = m01.mongo.now(UTC)
        for obj in list(self._cache_loaded.values()):
            if obj._m_changed:
                # set modified
                obj.modified = dt
                if obj._version == 0:
                    # has no version, add to insert cache
                    ci.append(self.doInsertDump(obj))
                else:
                    # has version, add to update cache
                    cu.append(self.doUpdateDump(obj))

        # add removed objects specification to transaction remove cache
        cr = self._t_cache_remove
        for obj in list(self._cache_removed.values()):
            cr.append(self.doRemoveDump(obj))

        # reset load cache which will support a clean retry
        self.resetLoadCache()

    def commit(self):
        """Start commit transaction handling."""
        pass

    def vote(self):
        """Process MongoDB insert and update calls.

        Note, if something fails, this could leave inconsistent data in MongoDB.

        """
        collection = self.collection
        # first remove removed items
        if len(self._t_cache_remove):
            self.doRemove(collection, self._t_cache_remove)
        # insert new items
        if len(self._t_cache_insert):
            self.doInsert(collection, self._t_cache_insert)
        # update existing items
        if len(self._t_cache_update):
            self.doUpdate(collection, self._t_cache_update, upsert=False)
        # reset transaction cache
        self.resetTransactionCache()

    def abort(self):
        """Abort transaction handling."""
        self.resetTransactionCache()
        self.resetLoadCache()
        self.resetCache()

    def finish(self):
        """Finish transaction commit."""
        self.resetTransactionCache()
        self.resetLoadCache()
        self.resetCache()


class MongoStorageBase(MongoMappingBase):
    """Mongo storage base class using mongo_id as __name__"""

    def __contains__(self, key):
        """Checks for an item by the given key without to load them"""
        if key in self._cache_removed:
            # NOTE: your implementation must make sure what should be done
            # for removed items, we just return False here
            return False
        elif self._cache_loaded.get(key):
            return True
        else:
            try:
                if PY2 and isinstance(key, newstr):
                    key_str = "{}".format(key)  # ObjectId requires a simple str
                else:
                    key_str = str(key)  # Standard conversion in Python 3

                data = self.doFindOne(self.collection,
                    {'_id': bson.objectid.ObjectId(key_str)})
                if data is not None:
                    return True
            except(pymongo.errors.InvalidId, TypeError) as e:
                pass

        return False

    def add(self, obj):
        """Add an item."""
        assert obj.__name__ is not None
        if obj.__name__ in self:
            # duplicated item
            raise KeyError(obj.__name__)
        # join transaction handling
        self.ensureTransaction()

        # set the parent
        obj = removeSecurityProxy(obj)
        # locate and set _pid if None
        obj.__parent__ = self

        # mark as changed
        obj._m_changed = True

        self._cache_added[obj.__name__] = obj
        self._cache_loaded[obj.__name__] = obj
        return obj.__name__

    def __getitem__(self, key):
        """get item"""
        if key in self._cache_removed:
            raise KeyError(key)
        obj = self._cache_loaded.get(key)
        if obj is None:
            try:
                if PY2 and isinstance(key, newstr):
                    key_str = "{}".format(key)  # ObjectId requires a simple str
                else:
                    key_str = str(key)  # Standard conversion in Python 3

                data = self.doFindOne(self.collection,
                    {'_id': bson.objectid.ObjectId(key_str)})
                if data is None:
                    raise KeyError(key)
            except(pymongo.errors.InvalidId, TypeError) as e:
                raise KeyError(key)
            obj = self.doLoad(data)
            # join transaction handling
            self.ensureTransaction()
        return obj


class MongoContainerBase(MongoMappingBase):
    """Mongo container base class using _id and __name__ as unique index."""

    def __contains__(self, key):
        """Checks for an item by the given key without to load them"""
        if key in self._cache_removed:
            # NOTE: your implementation must make sure what should be done
            # for removed items, we just return False here
            return False
        elif self._cache_loaded.get(key):
            return True
        else:
            try:
                data = self.doFindOne(self.collection, {'__name__': key})
                if data is not None:
                    return True
            except(pymongo.errors.InvalidId, TypeError) as e:
                pass

        return False

    def __setitem__(self, key, obj):
        """Set item"""
        if obj.__name__ is not None and obj.__name__ != key:
            raise KeyError("Key %r does not compare with object.__name__" % key,
                obj.__name__)
        if key in self:
            # duplicated item
            raise KeyError(key)
        # join transaction handling
        self.ensureTransaction()

        # set the name and parent
        obj = removeSecurityProxy(obj)
        # locate and set _pid if None
        obj.__parent__ = self
        obj.__name__ = key

        # mark as changed
        obj._m_changed = True

        self._cache_added[obj.__name__] = obj
        self._cache_loaded[obj.__name__] = obj

    def __getitem__(self, key):
        """get item"""
        if key in self._cache_removed:
            raise KeyError(key)
        obj = self._cache_loaded.get(key)
        if obj is None:
            try:
                data = self.doFindOne(self.collection, {'__name__': key})
                if data is None:
                    raise KeyError(key)
            except(pymongo.errors.InvalidId, TypeError) as e:
                raise KeyError(key)
            obj = self.doLoad(data)
            # join transaction handling
            self.ensureTransaction()
        return obj
