# pylint: disable=W0622
"""cubicweb-geocoding application packaging information"""

modname = "geocoding"
distname = "cubicweb-geocoding"

numversion = (1, 1, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "geocoding views such as google maps"
web = f"https://forge.extranet.logilab.fr/cubicweb/cubes/{distname}"

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: JavaScript",
]

__depends__ = {
    "cubicweb": ">= 4.10.0, < 6.0.0",
    "cubicweb-web": ">= 1.4.2, < 2.0.0",
}
__recommends__ = {}
