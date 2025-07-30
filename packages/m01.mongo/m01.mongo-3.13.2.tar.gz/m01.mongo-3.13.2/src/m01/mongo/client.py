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
"""A pymongo client with environment based setup
$Id: client.py 5178 2025-03-18 15:08:21Z felipe.souza $
"""
from __future__ import absolute_import
from builtins import str
__docformat__ = "reStructuredText"

import pymongo


###############################################################################
#
# pymongo client setup

client = None

# TODO: implement all options defined in pymongo/common.py
# TODO: support **kwargs and update options at the end for override existing
#       or define undefined options given from new mongo versions

def getMongoClient(settings=None, connect=True, retry=True):
    global client
    if client is not None:
        # force to close monitor thread
        client.close()
    # setup client
    if settings is None:
        from m01.mongo import settings
    uri = settings.MONGODB_URI
    if uri == 'testing' or settings.P01_CDN_RECIPE_PROCESS or \
        settings.I18N_EXTRACT:
        # testing or resource extraction, just a dummy client using testing port
        return pymongo.MongoClient('localhost:45017')
    else:
        uri = str(uri)
        if settings.MONGODB_SSL and \
            settings.MONGODB_SSL_CERT_REQUIRED is None:
            # if undefined use ssl.CERT_REQUIRED
            import ssl
            ssl_cert_reqs = ssl.CERT_REQUIRED
        else:
            ssl_cert_reqs = settings.MONGODB_SSL_CERT_REQUIRED
        if not settings.MONGODB_CONNECT:
            connect = False
        options = {
            'connect': connect,
            'tz_aware': settings.MONGODB_TZ_AWARE,
        }
        if settings.MONGODB_REPLICA_SET:
            options['replicaSet'] = settings.MONGODB_REPLICA_SET
        if settings.MONGODB_APP_NAME:
            options['appname'] = settings.MONGODB_APP_NAME
        if settings.MONGODB_MIN_POOL_SIZE:
            options['minPoolSize'] = settings.MONGODB_MIN_POOL_SIZE
        if settings.MONGODB_MAX_POOL_SIZE:
            options['maxPoolSize'] = settings.MONGODB_MAX_POOL_SIZE
        if settings.MONGODB_CONNECT_TIMEOUT:
            options['connectTimeoutMS'] = \
                settings.MONGODB_CONNECT_TIMEOUT
        if settings.MONGODB_SERVER_SELECTION_TIMEOUT:
            options['serverSelectionTimeoutMS'] = \
                settings.MONGODB_SERVER_SELECTION_TIMEOUT
        if settings.MONGODB_SOCKET_TIMEOUT:
            options['socketTimeoutMS'] = settings.MONGODB_SOCKET_TIMEOUT
        if settings.MONGODB_WAIT_QUEUE_TIMEOUT:
            options['waitQueueTimeoutMS'] = \
                settings.MONGODB_WAIT_QUEUE_TIMEOUT
        if settings.MONGODB_MAX_IDLE_TIME_MS:
            options['maxIdleTimeMS'] = \
                settings.MONGODB_MAX_IDLE_TIME_MS
        if settings.MONGODB_WAIT_QUEUE_MULTIPLE:
            options['waitQueueMultiple'] = \
                settings.MONGODB_WAIT_QUEUE_MULTIPLE
        if settings.MONGODB_HEARTBEAT_FREQUENCY:
            options['heartbeatFrequencyMS'] = \
                settings.MONGODB_HEARTBEAT_FREQUENCY
        # auth options
        if settings.MONGODB_AUTH_MECHNISM:
            options['authMechanism'] = settings.MONGODB_AUTH_MECHNISM
        if settings.MONGODB_USERNAME:
            options['username'] = settings.MONGODB_USERNAME
        if settings.MONGODB_PASSWORD:
            options['password'] = settings.MONGODB_PASSWORD
        # ssl options
        if settings.MONGODB_SSL:
            options['ssl'] = settings.MONGODB_SSL
            if ssl_cert_reqs:
                options['ssl_cert_reqs'] = ssl_cert_reqs
            if settings.MONGODB_CA_CERT:
                options['ssl_ca_certs'] = settings.MONGODB_CA_CERT
            if settings.MONGODB_CLIENT_CERT:
                options['ssl_certfile'] = settings.MONGODB_CLIENT_CERT
            if settings.MONGODB_CLIENT_CERT_KEY_FILE:
                options['ssl_keyfile'] = settings.MONGODB_CLIENT_CERT_KEY_FILE
            if settings.MONGODB_PEM_PASSPHRASE:
                options['ssl_pem_passphrase'] = settings.MONGODB_PEM_PASSPHRASE
            if settings.MONGODB_REVOCATION_LIST:
                options['ssl_crlfile'] = settings.MONGODB_REVOCATION_LIST
            if settings.MONGODB_SSL_MATCH_HOSTNAME:
                options['ssl_match_hostname'] = \
                    settings.MONGODB_SSL_MATCH_HOSTNAME
        # tls options
        if settings.MONGODB_TLS:
            options['tls'] = settings.MONGODB_TLS
            if settings.MONGODB_TLS_CA_FILE:
                options['tlsCAFile'] = settings.MONGODB_TLS_CA_FILE
            if settings.MONGODB_TLS_CERT_KEY_FILE:
                options['tlsCertificateKeyFile'] = \
                    settings.MONGODB_TLS_CERT_KEY_FILE
            if settings.MONGODB_TLS_CERT_KEY_FILE_PASSWORD:
                options['tlsCertificateKeyFilePassword'] = \
                    settings.MONGODB_TLS_CERT_KEY_FILE_PASSWORD
            if settings.MONGODB_TLS_CRL_FILE:
                options['tlsCRLFile'] = settings.MONGODB_TLS_CRL_FILE
            if settings.MONGODB_TLS_ALLOW_INVALID_CERT:
                options['tlsAllowInvalidCertificates'] = \
                    settings.MONGODB_TLS_ALLOW_INVALID_CERT
            if settings.MONGODB_TLS_ALLOW_INVALID_HOSTNAME:
                options['tlsAllowInvalidHostnames'] = \
                    settings.MONGODB_TLS_ALLOW_INVALID_HOSTNAME
            if settings.MONGODB_TLS_CERTIFICATE_SELECTOR:
                options['tlsCertificateSelector'] = \
                    settings.MONGODB_TLS_CERTIFICATE_SELECTOR
        try:
            client = pymongo.MongoClient(uri, **options)
            if connect:
                client.admin.command('ismaster')
            return client
        except pymongo.errors.ConnectionFailure as e:
            # ensure client, try again without connect
            if retry:
                return getMongoClient(settings, connect=False, retry=False)
            else:
                raise e
