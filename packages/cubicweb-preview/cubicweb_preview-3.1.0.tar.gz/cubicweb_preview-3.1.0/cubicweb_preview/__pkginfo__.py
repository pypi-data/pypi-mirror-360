# pylint: disable-msg=W0622
"""cubicweb-preview application packaging information"""

modname = "preview"
distname = "cubicweb-preview"

numversion = (3, 1, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "Enables adding a preview button in your forms"
web = "https://www.cubicweb.org/project/%s" % distname
classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: JavaScript",
]

__depends__ = {
    "cubicweb": ">=4.5.2,<6.0.0",
    "cubicweb-web": ">=1.0.0,<2.0.0",
}
