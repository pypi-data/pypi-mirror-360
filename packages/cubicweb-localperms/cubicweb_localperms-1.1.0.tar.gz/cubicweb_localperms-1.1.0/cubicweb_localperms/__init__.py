"""cubicweb-localperms application package

allow definition of local permissions
"""

from rql.utils import quote
from cubicweb.schema import ERQLExpression, RRQLExpression


def _perm(names):
    if isinstance(names, (list, tuple)):
        if len(names) == 1:
            names = quote(names[0])
        else:
            names = "IN (%s)" % (",".join(quote(name) for name in names))
    else:
        names = quote(names)
    # return u' require_permission P, P name %s, U in_group G, P require_group G' % names
    return " require_permission P, P name %s, U has_group_permission P" % names


def xperm(*names):
    return "X" + _perm(names)


def xexpr(*names):
    return ERQLExpression(xperm(*names))


_XREXPR_OPTIONS = frozenset(("role", "etype"))


def xrexpr(relation, *names, **options):
    """return an :class:`ERQLExpression` where X is related to an Y variable
    through `relation`, by default as subject, but you can specify 'object using
    the `role` keyword argument. The Y variable is itself linked to a
    :class:`CWPermission` entity which should have one of the given `names`.

    You can also specify the entity type for X using the `etype` keyword
    argument.

    Examples:

    >>> xrexpr('a_relation', 'read', 'write').expression
    u'X a_relation Y, Y require_permission P, P name IN ("read", "write"), \
    U has_group_permission P'
    >>> xrexpr('a_relation', 'read', role='object').expression
    u'Y a_relation X, Y require_permission P, P name "read", \
    U has_group_permission P'
    >>> xrexpr('a_relation', 'read', etype='MyEType').expression
    u'X a_relation Y, X is MyEType, Y require_permission P, P name "read", \
    U has_group_permission P'
    """
    assert not (set(options) - _XREXPR_OPTIONS), "unknown option specified: %s" % (
        set(options) - _XREXPR_OPTIONS
    )
    role = options.get("role", "subject")
    assert role in ("subject", "object"), "bad role %s" % role
    if role == "subject":
        rql = "X %s Y" % relation
    else:
        rql = "Y %s X" % relation
    if options.get("etype"):
        rql += ", X is %s" % options.get("etype")
    return ERQLExpression("%s, Y %s" % (rql, _perm(names)))


def sexpr(*names):
    return RRQLExpression("S" + _perm(names), "S")


def restricted_sexpr(restriction, *names):
    rql = "%s, %s" % (restriction, "S" + _perm(names))
    return RRQLExpression(rql, "S")


def restricted_oexpr(restriction, *names):
    rql = "%s, %s" % (restriction, "O" + _perm(names))
    return RRQLExpression(rql, "O")


def oexpr(*names):
    return RRQLExpression("O" + _perm(names), "O")


def relxperm(rel, role, *names):
    assert role in ("subject", "object")
    if role == "subject":
        zxrel = ", X %s Z" % rel
    else:
        zxrel = ", Z %s X" % rel
    return "Z" + _perm(names) + zxrel


def relxexpr(rel, role, *names):
    return ERQLExpression(relxperm(rel, role, *names))
