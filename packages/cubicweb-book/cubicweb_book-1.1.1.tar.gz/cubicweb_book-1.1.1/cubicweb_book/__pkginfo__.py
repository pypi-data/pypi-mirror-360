# pylint: disable-msg=W0622
"""cubicweb-book application packaging information"""

modname = "book"
distname = "cubicweb-%s" % modname

numversion = (1, 1, 1)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
description = "component to describe books for the CubicWeb framework"
author = "Logilab"
author_email = "contact@logilab.fr"
long_desc = """
This cube provides the entity type ``Book`` and uses the OpenLibrary API_
to automatically fill the book's description

Check out : `Fetching book descriptions and covers`_

.. _`Fetching book descriptions and covers` : http://www.logilab.org/blogentry/9138
.. _API : http://openlibrary.org/dev/docs/api
"""
web = "https://forge.extranet.logilab.fr/cubicweb/cubes/book"

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: JavaScript",
]

__depends__ = {
    "cubicweb": ">=4.5.2,<6.0.0",
    "cubicweb_web": ">=1.0.0,<2.0.0",
    "cubicweb-addressbook": ">=2.1.0,<3.0.0",
    "cubicweb-person": ">=2.0.0,<3.0.0",
    "cubicweb-file": ">=4.0.0,<5.0.0",
}
