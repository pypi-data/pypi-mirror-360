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
from __future__ import print_function

__docformat__ = "reStructuredText"

import unittest
import doctest

import m01.mongo.testing


def test_suite():
    suites = []
    append = suites.append

    # fake database tests. our fake database does not support ensure_index and
    # special prefixed commands like ($near). This menas we can't run all tests
    # with our fake database
    fakeTestNames = [
        'client.txt',
        'container.txt',
        'object.txt',
        'shared.txt',
        'storage.txt',
        'usecase.txt',
        'util.txt',
        'zope.schema.txt',
    ]
    for name in fakeTestNames:
        append(
            doctest.DocFileSuite(name,
                globs={
                    'print_function': print_function,
                    'absolute_import': absolute_import
                },
                setUp=m01.mongo.testing.setUpFakeMongo,
                tearDown=m01.mongo.testing.tearDownFakeMongo,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                checker=m01.mongo.testing.reNormalizer),
        )
    append(
        doctest.DocFileSuite('testing.txt',
            globs={
                'print_function': print_function,
                'absolute_import': absolute_import
            },
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            checker=m01.mongo.testing.reNormalizer),
    )

    # real mongo database tests using m01.stub using level 2 tests (--all or -a2)
    testNames = [
        '../README.txt',
        'batching.txt',
        'container.txt',
        'geo.txt',
        'geopoint.txt',
        'object.txt',
        'shared.txt',
        'storage.txt',
        'usecase.txt',
        'zope.schema.txt',
    ]
    for name in testNames:
        suite = unittest.TestSuite((
            doctest.DocFileSuite(name,
                globs={
                    'print_function': print_function,
                    'absolute_import': absolute_import
                },
                setUp=m01.mongo.testing.setUpStubMongo,
                tearDown=m01.mongo.testing.tearDownStubMongo,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                checker=m01.mongo.testing.reNormalizer),
        ))
        suite.level = 2
        append(suite)

    # return test suite
    return unittest.TestSuite(suites)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
