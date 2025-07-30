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
"""cubicweb-localperms entity's classes"""

from logilab.common.decorators import monkeypatch

from cubicweb import Unauthorized
from cubicweb.entities import AnyEntity, fetch_config, authobjs


@monkeypatch(authobjs.CWGroup)
def grant_permission(self, entity, pname, plabel=None):
    """grant local `pname` permission on `entity` to this group using
    :class:`CWPermission`.

    If a similar permission already exists, add the group to it, else create
    a new one.
    """
    if not self._cw.execute(
        "SET X require_group G WHERE E eid %(e)s, G eid %(g)s, "
        "E granted_permission X, X name %(name)s, X label %(label)s",
        {"e": entity.eid, "g": self.eid, "name": pname, "label": plabel},
    ):
        self._cw.create_entity(
            "CWPermission",
            name=pname,
            label=plabel,
            require_group=self,
            reverse_granted_permission=entity,
        )


@monkeypatch(authobjs.CWUser)
def has_permission(self, pname, contexteid=None):
    rql = "Any P WHERE P is CWPermission, P name %(name)s, U has_group_permission P, U eid %(u)s"
    kwargs = {"name": pname, "u": self.eid}
    if contexteid is not None:
        rql += ", X require_permission P, X eid %(x)s"
        kwargs["x"] = contexteid
    try:
        return self._cw.execute(rql, kwargs)
    except Unauthorized:
        return False


class CWPermission(AnyEntity):
    __regid__ = "CWPermission"
    fetch_attrs, cw_fetch_order = fetch_config(["name", "label"])

    def dc_title(self):
        if self.label:
            return "%s (%s)" % (self._cw._(self.name), self.label)
        return self._cw._(self.name)
