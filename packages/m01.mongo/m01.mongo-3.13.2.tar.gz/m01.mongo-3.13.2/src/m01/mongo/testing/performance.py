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
$Id: performance.py 5178 2025-03-18 15:08:21Z felipe.souza $
"""
from __future__ import absolute_import
from __future__ import print_function
from builtins import range
from six.moves import range
__docformat__ = "reStructuredText"

import time
import transaction
from ZODB.DB import DB
from ZODB.DemoStorage import DemoStorage

import m01.stub.testing
import m01.mongo.testing


timeResult = None


def timeTest(function, counter=10000, *args, **kw):
    """timer"""
    res = []
    append = res.append
    def wrapper(*args, **kw):
        start_time = time.time()
        for i in range(counter):
            append(function(*args, **kw))
        total_time = time.time() - start_time
        global timeResult
        timeResult = total_time
        # commit transaction forces indexer collector indexing our objects
        transaction.commit()
        return res
    return wrapper(*args, **kw)

###############################################################################
#
# test methods
#
###############################################################################

def runSave(collection, amountOfObjects=1000):
    for i in range(amountOfObjects):
        data = {'title': u'Title %s' % i,
                'description': u'Description %s' % i}
        collection.save(data)


def runSetup(storage, amountOfObjects=1000):
    """Only setup and dump object without any DB operation."""
    data = {'title': u'Title',
            'description': u'Description'}
    for i in range(amountOfObjects):
        m01.mongo.testing.SampleStorageItem(data)


def runSetupAndDump(storage, amountOfObjects=1000):
    """Only setup and dump object without any DB operation."""
    data = {'title': u'Title',
            'description': u'Description'}
    for i in range(amountOfObjects):
        item = m01.mongo.testing.SampleStorageItem(data)
        item.dump()


def runAdd(storage, amountOfObjects=1000):
    data = {'title': u'Title',
            'description': u'Description'}
    for i in range(amountOfObjects):
        item = m01.mongo.testing.SampleStorageItem(data)
        storage.add(item)


def runAddWithCommit(storage, amountOfObjects=1000):
    data = {'title': u'Title',
            'description': u'Description'}
    item = m01.mongo.testing.SampleStorageItem(data)
    for i in range(amountOfObjects):
        item = m01.mongo.testing.SampleStorageItem(data)
        storage.add(item)
    transaction.commit()


def runAddWithSingleCommit(storage, amountOfObjects=1000):
    data = {'title': u'Title',
            'description': u'Description'}
    item = m01.mongo.testing.SampleStorageItem(data)
    for i in range(amountOfObjects):
        item = m01.mongo.testing.SampleStorageItem(data)
        storage.add(item)
        transaction.commit()


def runObjectModified(obj, amountOfObjects=1000):
    for i in range(amountOfObjects):
        obj.title = u'Title %s' % i
        transaction.commit()


def runUpdate(storage, obj, amountOfObjects=1000):
    for i in range(amountOfObjects):
        data = {'title': u'Title %s' % i}
        obj.update(data)


def mongoCollections(storage, amountOfObjects=1000):
    for i in range(amountOfObjects):
        data = {'title': u'Title %s' % i,
                'description': u'Description %s' % i}
        collection.save(data)


###############################################################################
#
# performance test
#
###############################################################################

def getMongo():
    client = m01.mongo.testing.getTestClient()
    # tear down old database probably left over from aborted tests
    client.drop_database(m01.mongo.testing.TEST_DB_NAME)
    # setup new database
    mdb = client[m01.mongo.testing.TEST_DB_NAME]
    collection = mdb['performance']
    return mdb, collection


def runTest(repeatTimes, amountOfObjects):
    """Test methods

    Note, the ZODB is here for historical reason and shows that it is
    possible to store a container in ZODB whcih contains objects stored in
    mongodb. The transaction can handle the mixed environment.

    """

    # first setup mongo test database

    print("")
    print("Run test with")
    print("-------------")
    print("- %i x repeat tests" % repeatTimes)
    print("- %i objects" % amountOfObjects)

    # setup ZODB and storage
    zodb = DB(DemoStorage())
    conn = zodb.open()
    storage = m01.mongo.testing.SampleStorage()
    conn.root()['storage'] = storage
    transaction.commit()
    conn.close()

    # start test
    # setup mongo db and collection
    mdb, collection = getMongo()
    conn = zodb.open()
    storage = conn.root()['storage']
    timeTest(runSave, repeatTimes, collection, amountOfObjects)
    conn.close()
    print("save:  %.2f s" % timeResult)

    # setup mongo
    mdb, collection = getMongo()
    conn = zodb.open()
    storage = conn.root()['storage']
    timeTest(runSetup, repeatTimes, storage, amountOfObjects)
    conn.close()
    print("setup: %.2f s" % timeResult)

    # setup mongo
    mdb, collection = getMongo()
    conn = zodb.open()
    storage = conn.root()['storage']
    timeTest(runSetupAndDump, repeatTimes, storage, amountOfObjects)
    conn.close()
    print("setup and dump: %.2f s" % timeResult)

    # setup mongo
    mdb, collection = getMongo()
    conn = zodb.open()
    storage = conn.root()['storage']
    timeTest(runAdd, repeatTimes, storage, amountOfObjects)
    transaction.abort()
    conn.close()
    print("add:  %.2f s" % timeResult)

    # setup mongo
    mdb, collection = getMongo()
    conn = zodb.open()
    storage = conn.root()['storage']
    timeTest(runAddWithCommit, repeatTimes, storage, amountOfObjects)
    conn.close()
    print("add with commit:  %.2f s" % timeResult)

    # setup mongo
    mdb, collection = getMongo()
    conn = zodb.open()
    storage = conn.root()['storage']
    timeTest(runAddWithSingleCommit, repeatTimes, storage, amountOfObjects)
    conn.close()
    print("add with single commit:  %.2f s" % timeResult)

    # time object modified event
    # setup mongo
    mdb, collection = getMongo()
    conn = zodb.open()
    storage = conn.root()['storage']
    data = {'title': u'Title modified',
            'description': u'Description modified'}
    item = m01.mongo.testing.SampleStorageItem(data)
    storage.add(item)
    transaction.commit()
    timeTest(runObjectModified, repeatTimes, item, amountOfObjects)
    conn.close()
    print("object modified with single commit: %.2f s" % timeResult)

    # time object modified event
    # setup mongo
    mdb, collection = getMongo()
    conn = zodb.open()
    storage = conn.root()['storage']
    data = {'title': u'Title modified',
            'description': u'Description modified'}
    item = m01.mongo.testing.SampleStorageItem(data)
    storage.add(item)
    transaction.commit()
    timeTest(runUpdate, repeatTimes, storage, item, amountOfObjects)
    conn.close()
    print("object update: %.2f s" % timeResult)


def createCollection(mdb, amount):
    """Used for check how many collection we can add."""
    for i in range(amount):
        mdb.create_collection('collection-%i' % i)
        col = mdb['collection-%i' % i]
        for ii in range(25):
            col.ensure_index('idx-%i' % ii)


def dropCollection(mdb, amount):
    """Used for check how many collection we can add."""
    for i in range(amount):
        mdb.drop_collection('collection-%i' % i)


def runCollectionTest(amount):
    # first setup mongo test database
    setUpMongo()

    print("")
    print("Create collections")
    print("------------------")
    print("- %i collections" % amount)
    print("")
    # setup mongo
    mdb, collection = getMongo()
    timeTest(createCollection, 1, mdb, amount)
    print("create collection:  %.2f s" % timeResult)
    timeTest(dropCollection, 1, mdb, amount)
    print("drop collection:  %.2f s" % timeResult)


def main():
    error = None
    try:
        # m01.stub.testing.startMongoServer()
        m01.mongo.testing.setUpStubMongo()
        runTest(1, 100)
        runTest(1, 10000)
        # check the amount of collections. Note there is a limit of 24000
        # namspaces per collection. Each collection and index are counted as a
        # namespace. If you need more, you need to set the --nssize paramter.
        # You also need to use 64bit machine for test the namspace limit
        #runCollectionTest(24000)
    except Exception as e:
        error = e
    else:
        # m01.stub.testing.stopMongoServer(5.0)
        m01.mongo.testing.tearDownStubMongo()
    if error is not None:
        raise error
