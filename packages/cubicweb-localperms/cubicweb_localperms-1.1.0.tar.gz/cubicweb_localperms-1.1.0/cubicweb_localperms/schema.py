# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-localperms schema

client cubes should explicitly add 'X granted_permission CWPermission' and 'X
require_permission CWPermission' for each type that should have local
permission, the first one being explicitly granted and the other automatically
propagated.  Hence possible subjects of `granted_permission` should be a subset
of `require_permission` possible subjects.
"""

from cubicweb import _

from yams.buildobjs import EntityType, RelationType, RelationDefinition, String

from cubicweb.schema import PUB_SYSTEM_ENTITY_PERMS, PUB_SYSTEM_REL_PERMS


class CWPermission(EntityType):
    """entity type that may be used to construct some advanced security
    configuration
    """

    __permissions__ = PUB_SYSTEM_ENTITY_PERMS

    name = String(
        required=True,
        indexed=True,
        internationalizable=True,
        maxsize=100,
        description=_("name or identifier of the permission"),
    )
    label = String(
        required=True,
        internationalizable=True,
        maxsize=100,
        description=_(
            "distinct label to distinguate between other "
            "permission entity of the same name"
        ),
    )


class granted_permission(RelationType):
    """explicitly granted permission on an entity"""

    __permissions__ = PUB_SYSTEM_REL_PERMS
    # XXX cardinality = '*1'


class require_permission(RelationType):  # XXX rename me
    """link a permission to the entity. You should use this relation instead of
    granted_permission in your schema security definition, since this is the one
    which is automatically propagated.
    """

    __permissions__ = PUB_SYSTEM_REL_PERMS


class require_group(RelationDefinition):  # XXX rename me
    """groups to which the permission is granted"""

    __permissions__ = PUB_SYSTEM_REL_PERMS
    subject = "CWPermission"
    object = "CWGroup"
    # XXX cardinality = '+*'


class has_group_permission(RelationDefinition):
    """short cut relation for 'U in_group G, P require_group G' for efficiency
    reason. This relation is set automatically, you should not set this.
    """

    __permissions__ = PUB_SYSTEM_REL_PERMS
    subject = "CWUser"
    object = "CWPermission"
