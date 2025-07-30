"""install some monkey patches to ease API"""

from logilab.common.decorators import monkeypatch

from cubicweb import schema


schema.INTERNAL_TYPES.add("CWPermission")
schema.SYSTEM_RTYPES.add("require_group")
schema.SYSTEM_RTYPES.add("require_permission")
schema.SYSTEM_RTYPES.add("has_group_permission")
schema.NO_I18NCONTEXT.add("require_permission")


try:
    from cubicweb.server import repository, session
except ImportError:
    pass
else:
    # cubicweb-server configuration / monkey-patching

    repository.NO_CACHE_RELATIONS.add(("require_permission", "object"))

    @monkeypatch(session.InternalManager, "has_permission")
    @staticmethod
    def has_permission(self, pname, contexteid=None):
        return True


try:
    from cubicweb import devtools
except ImportError:
    pass
else:
    # cubicweb-dev configuration
    devtools.SYSTEM_ENTITIES.add("CWPermission")
    devtools.SYSTEM_RELATIONS.add("require_group")
    devtools.SYSTEM_RELATIONS.add("require_permission")
