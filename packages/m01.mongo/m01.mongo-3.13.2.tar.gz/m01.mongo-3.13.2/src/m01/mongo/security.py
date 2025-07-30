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
from builtins import object
from zope.interface import implementer
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.security.proxy import removeSecurityProxy
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.securitypolicy.interfaces import IRolePermissionManager
from zope.securitypolicy.interfaces import IGrantInfo
from zope.securitypolicy.interfaces import Allow
from zope.securitypolicy.interfaces import Deny
from zope.securitypolicy.interfaces import Unset
from zope.security.management import queryInteraction

from m01.mongo import interfaces


class SecurityMap(object):
    """SecurityMap adapter base class."""

    def __init__(self, context):
        self.context = context

    def __bool__(self):
        return bool(self._byrow)

    def addCell(self, rowentry, colentry, value):
        row = self._byrow.get(rowentry)
        if row:
            if row.get(colentry) is value:
                return False
        else:
            row = self._byrow[rowentry] = {}

        col = self._bycol.get(colentry)
        if not col:
            col = self._bycol[colentry] = {}

        row[colentry] = value
        col[rowentry] = value

        self._invalidated_interaction_cache()
        self.context._m_changed = True
        return True

    def _invalidated_interaction_cache(self):
        # Invalidate this threads interaction cache
        interaction = queryInteraction()
        if interaction is not None:
            try:
                invalidate_cache = interaction.invalidate_cache
            except AttributeError:
                pass
            else:
                invalidate_cache()

    def delCell(self, rowentry, colentry):
        row = self._byrow.get(rowentry)
        if row and (colentry in row):
            del row[colentry]
            if not row:
                del self._byrow[rowentry]
            col = self._bycol[colentry]
            del col[rowentry]
            if not col:
                del self._bycol[colentry]

            self._invalidated_interaction_cache()
            self.context._m_changed = True
            return True

        return False

    def queryCell(self, rowentry, colentry, default=None):
        row = self._byrow.get(rowentry)
        if row:
            return row.get(colentry, default)
        else:
            return default

    def getCell(self, rowentry, colentry):
        marker = object()
        cell = self.queryCell(rowentry, colentry, marker)
        if cell is marker:
            raise KeyError('Not a valid row and column pair.')
        return cell

    def getRow(self, rowentry):
        row = self._byrow.get(rowentry)
        if row:
            return list(row.items())
        else:
            return []

    def getCol(self, colentry):
        col = self._bycol.get(colentry)
        if col:
            return list(col.items())
        else:
            return []

    def getAllCells(self):
        res = []
        for r in list(self._byrow.keys()):
            for c in list(self._byrow[r].items()):
                res.append((r,) + c)
        return res


class PPMSecurityMap(SecurityMap):

    @property
    def _byrow(self):
        return self.context._ppmrow

    @property
    def _bycol(self):
        return self.context._ppmcol


class PRMSecurityMap(SecurityMap):

    @property
    def _byrow(self):
        return self.context._prmrow

    @property
    def _bycol(self):
        return self.context._prmcol


class RPMSecurityMap(SecurityMap):

    @property
    def _byrow(self):
        return self.context._rpmrow

    @property
    def _bycol(self):
        return self.context._rpmcol


@implementer(IPrincipalPermissionManager)
class PrincipalPermissionManager(PPMSecurityMap):
    """Mappings between principals and permissions."""


    def grantPermissionToPrincipal(self, permission_id, principal_id):
        self.addCell(permission_id, principal_id, True)

    def denyPermissionToPrincipal(self, permission_id, principal_id):
        self.addCell(permission_id, principal_id, False)

    unsetPermissionForPrincipal = PPMSecurityMap.delCell
    getPrincipalsForPermission = PPMSecurityMap.getRow
    getPermissionsForPrincipal = PPMSecurityMap.getCol

    def getSetting(self, permission_id, principal_id, default=None):
        return self.queryCell(permission_id, principal_id, default)

    getPrincipalsAndPermissions = PPMSecurityMap.getAllCells


@implementer(IPrincipalRoleManager)
class PrincipalRoleManager(PRMSecurityMap):
    """Mappings between principals and roles."""


    def assignRoleToPrincipal(self, role_id, principal_id):
        self.addCell(role_id, principal_id, True)

    def removeRoleFromPrincipal(self, role_id, principal_id):
        self.addCell(role_id, principal_id, False)

    unsetRoleForPrincipal = PRMSecurityMap.delCell
    getPrincipalsForRole = PRMSecurityMap.getRow
    getRolesForPrincipal = PRMSecurityMap.getCol

    def getSetting(self, role_id, principal_id):
        return self.queryCell(role_id, principal_id, default=None)

    getPrincipalsAndRoles = PRMSecurityMap.getAllCells


@implementer(IRolePermissionManager)
class RolePermissionManager(RPMSecurityMap):
    """Provide adapter that manages role permission data in an object attribute
    """


    def grantPermissionToRole(self, permission_id, role_id):
        self.addCell(permission_id, role_id, True)

    def denyPermissionToRole(self, permission_id, role_id):
        self.addCell(permission_id, role_id, False)

    unsetPermissionFromRole = RPMSecurityMap.delCell
    getRolesForPermission = RPMSecurityMap.getRow
    getPermissionsForRole = RPMSecurityMap.getCol
    getRolesAndPermissions = RPMSecurityMap.getAllCells

    def getSetting(self, permission_id, role_id):
        return self.queryCell(permission_id, role_id, default=None)


@implementer(IGrantInfo)
class GrantInfoAdapter(object):
    """Grant info adapter.

    Right now we do not provide special pages whihc use the GrantInfo adapter.
    This means we return Allow, Deny and Unset as grant info. Later we will
    probably implement custom grant info pages and use True, False and None as
    grant info values.
    """

    zope.component.adapts(interfaces.ISecurityAware)

    prinper = {}
    prinrole = {}
    permrole = {}

    def __init__(self, context):
        self.context = removeSecurityProxy(context)
        self.prinper = self.context.ppmcol
        self.prinrole = self.context.prmcol
        self.permrole = self.context.rpmrow

    def __bool__(self):
        return bool(self.prinper or self.prinrole or self.permrole)

    def principalPermissionGrant(self, principal, permission):
        """This is the only method which uses Allo, Deny and Unset.

        All other adapter and the security policy use True, False and None.
        """
        prinper = self.prinper.get(principal)
        if prinper:
            grant = prinper.get(permission, Unset)
            if grant is False:
                return Deny
            elif grant is True:
                return Allow
        return Unset

    def getRolesForPermission(self, permission):
        permrole = self.permrole.get(permission)
        if permrole:
            return list(permrole.items())
        return ()

    def getRolesForPrincipal(self, principal):
        prinrole = self.prinrole.get(principal)
        if prinrole:
            return list(prinrole.items())
        return ()

