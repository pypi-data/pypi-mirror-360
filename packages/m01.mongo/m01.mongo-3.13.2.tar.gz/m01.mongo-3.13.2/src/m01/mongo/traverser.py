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
from builtins import map
from zope.interface import implementer
from builtins import object
from six.moves import map
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.publisher.interfaces
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces import IDefaultViewName
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher

from m01.mongo import interfaces


class BrowserDefaultMixin(object):
    """Browser default mixin class.

    Note: we don't use the @@ prefix for IDefaultViewName because @@ prefixed
    view names force to bypass our IBrowserPublisher traverser and use the view
    namespace for lookup views.
    """

    def browserDefault(self, request):
        """See zope.publisher.browser.interfaces.IBrowserPublisher"""
        view_name = zope.component.getSiteManager(None).adapters.lookup(
            list(map(zope.interface.providedBy, (self.context, request))),
                IDefaultViewName)
        if view_name is None:
            raise zope.component.ComponentLookupError(
                "Couldn't find default view name", self.context, request)
        return self.context, (view_name,)


@implementer(IBrowserPublisher)
class MongoTraverserMixin(BrowserDefaultMixin):
    """MongoTraverser mixin class"""


    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""
        raise NotImplementedError("Subclass must implement publishTraverse")


class MongoStorageTraverser(MongoTraverserMixin):
    """MongoStorageTraverser"""

    zope.component.adapts(interfaces.IMongoStorage, IHTTPRequest)

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""

        # check storage if we get a valid MongoDB object id.
        if len(name) == 12 or len(name) == 24:
            try:
                return self.context[name]
            except KeyError:
                pass

        view = zope.component.queryMultiAdapter((self.context, request),
            name=name)
        if view is not None:
            return view

        raise zope.publisher.interfaces.NotFound(self.context, name, request)


class MongoContainerTraverser(MongoTraverserMixin):
    """MongoContainerTraverser"""

    zope.component.adapts(interfaces.IMongoContainer, IHTTPRequest)

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""

        # Note: we changed the order of lookup because we do not like to
        # force the storage to lookup MongoDB if we need a view. But take
        # care, this means a view name will override a item key if you don't
        # use a @@ view marker prefix.
        view = zope.component.queryMultiAdapter((self.context, request),
            name=name)
        if view is not None:
            return view

        # this will force a MongoDB lookup
        try:
            return self.context[name]
        except KeyError:
            pass

        raise zope.publisher.interfaces.NotFound(self.context, name, request)


@implementer(IBrowserPublisher)
class MongoItemsDataTraverser(object):
    """MongoItemsTraverser"""

    zope.component.adapts(interfaces.IMongoItemsData, IHTTPRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""
        try:
            return self.context[name]
        except TypeError as e:
            pass

        raise zope.publisher.interfaces.NotFound(self.context, name, request)
