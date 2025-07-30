# copyright 2011-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-localperms specific hooks and operations"""

from cubicweb.server import hook

# sets to configure propagation hooks ##########################################

# relations where the "main" entity is the subject
S_RELS = set()
# relations where the "main" entity is the object
O_RELS = set(())

# relations where the "main" entity is the subject/object that should be skipped
# when propagating to entities linked through some particular relation
SKIP_S_RELS = set()
SKIP_O_RELS = set()

# granted_permission / require_permission synchronization hooks ################


class AddGrantedToSynchronizationHook(hook.Hook):
    __regid__ = "localperms.granted_permission_added"
    __select__ = hook.Hook.__select__ & hook.match_rtype(
        "granted_permission",
    )
    events = ("after_add_relation",)
    rql = (
        "SET P require_permission G WHERE P eid %(p)s, G eid %(g)s,"
        "NOT P require_permission G"
    )

    def __call__(self):
        self._cw.execute(self.rql, {"p": self.eidfrom, "g": self.eidto})


class DelGrantedToSynchronizationHook(AddGrantedToSynchronizationHook):
    __regid__ = "localperms.granted_permission_deleted"
    events = ("after_delete_relation",)
    rql = "DELETE P require_permission G WHERE P eid %(p)s, G eid %(g)s"


# require_permission propagation hooks #########################################


class AddEntitySecurityPropagationHook(hook.PropagateRelationHook):
    """propagate permissions when new entity are added"""

    __regid__ = "localperms.add_entity"
    __select__ = hook.PropagateRelationHook.__select__ & hook.match_rtype_sets(
        S_RELS, O_RELS
    )
    main_rtype = "require_permission"
    subject_relations = S_RELS
    object_relations = O_RELS


class AddPermissionSecurityPropagationHook(hook.PropagateRelationAddHook):
    __regid__ = "localperms.add_permission"
    __select__ = hook.PropagateRelationAddHook.__select__ & hook.match_rtype(
        "require_permission"
    )
    subject_relations = S_RELS
    object_relations = O_RELS
    skip_subject_relations = SKIP_S_RELS
    skip_object_relations = SKIP_O_RELS


class DelPermissionSecurityPropagationHook(hook.PropagateRelationDelHook):
    __regid__ = "localperms.del_permission"
    __select__ = hook.PropagateRelationDelHook.__select__ & hook.match_rtype(
        "require_permission"
    )
    subject_relations = S_RELS
    object_relations = O_RELS
    skip_subject_relations = SKIP_S_RELS
    skip_object_relations = SKIP_O_RELS


# has_group_permission propagation hooks #######################################


class AddGroupPermissionSecurityPropagationHook(hook.Hook):
    """propagate on group users when a permission is granted to a group"""

    __regid__ = "localperms.add_group_permission"
    __select__ = hook.Hook.__select__ & hook.match_rtype(
        "require_group",
    )
    events = ("after_add_relation",)
    rql = (
        "SET U has_group_permission P WHERE U in_group G, P eid %(p)s, G eid %(g)s,"
        "NOT U has_group_permission P"
    )

    def __call__(self):
        if self._cw.entity_type(self.eidfrom) != "CWPermission":
            return
        self._cw.execute(self.rql, {"p": self.eidfrom, "g": self.eidto})


class DelGroupPermissionSecurityPropagationHook(
    AddGroupPermissionSecurityPropagationHook
):
    """propagate on group users when a permission is removed to a group"""

    __regid__ = "localperms.del_group_permission"
    events = ("after_delete_relation",)
    rql = (
        "DELETE U has_group_permission P WHERE U in_group G, P eid %(p)s, G eid %(g)s,"
        "NOT EXISTS(U in_group G2, P require_group G2)"
    )


class AddInGroupSecurityPropagationHook(hook.Hook):
    """propagate group permission to users when a permission is granted to a group"""

    __regid__ = "localperms.add_in_group_permission"
    __select__ = hook.Hook.__select__ & hook.match_rtype(
        "in_group",
    )
    events = ("after_add_relation",)
    rql = (
        "SET U has_group_permission P WHERE U eid %(u)s, P require_group G, "
        "G eid %(g)s, NOT U has_group_permission P"
    )

    def __call__(self):
        self._cw.execute(self.rql, {"u": self.eidfrom, "g": self.eidto})


class DelInGroupSecurityPropagationHook(AddInGroupSecurityPropagationHook):
    """propagate on existing entities when a permission is deleted"""

    __regid__ = "localperms.del_in_group_permission"
    events = ("after_delete_relation",)
    rql = (
        "DELETE U has_group_permission P WHERE U eid %(u)s, P require_group G, "
        "G eid %(g)s, NOT EXISTS(U in_group G2, P require_group G2)"
    )


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)

    import os

    if os.environ.get("LOCALPERMS_INSTRUMENTALIZE"):
        from cubicweb.devtools.instrument import CubeTracerSet

        global S_RELS, O_RELS
        S_RELS = CubeTracerSet(vreg, S_RELS)
        O_RELS = CubeTracerSet(vreg, O_RELS)
