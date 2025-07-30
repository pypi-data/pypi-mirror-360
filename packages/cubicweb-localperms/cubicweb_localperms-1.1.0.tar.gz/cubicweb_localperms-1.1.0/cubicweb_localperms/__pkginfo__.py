# pylint: disable=W0622
"""cubicweb-localperms application packaging information"""

modname = "localperms"
distname = "cubicweb-localperms"

numversion = (1, 1, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "allow definition of local permissions"
web = "http://www.cubicweb.org/project/%s" % distname
classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
]

__depends__ = {
    "cubicweb": ">= 4.5.2, < 6.0.0",
    "cubicweb-web": ">= 1.0.0, < 2.0.0",
}
__recommends__ = {}
