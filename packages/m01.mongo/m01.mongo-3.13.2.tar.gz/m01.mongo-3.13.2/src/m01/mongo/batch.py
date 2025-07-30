##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
from __future__ import division
from __future__ import absolute_import
from six import string_types
from past.utils import old_div
import six
__docformat__ = "reStructuredText"

import pymongo


def getBatchData(collection, query=None, page=1, size=25, sortName=None,
    sortOrder=None, fields=None):
    """Returns batched mongo cursor, current page, total items and page size.
    
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
    """
    # start with server, this allows us to approve the page position
    if query is None:
        query = {}
    cursor = collection.find(query, fields)

    # get overall total based on query
    total = cursor.count() 
    # calculate pages
    pages = old_div(total,size)
    if pages == 0 or total % size:
        pages += 1
    # as next we approve our page position
    if page > pages:
        # restart with pages number as page which is the last page
        page = pages
        return getBatchData(collection, query, page, size, sortName, sortOrder,
            fields)

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
