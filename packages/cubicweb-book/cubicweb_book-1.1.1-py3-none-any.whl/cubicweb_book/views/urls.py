"""
Url rewriting for books.

:organization: Logilab
:copyright: 2009-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb_web.views.urlrewrite import SimpleReqRewriter, rgx


class BookReqRewriter(SimpleReqRewriter):
    rules = [
        (
            rgx(r"/book/(\d+)\.rdf"),
            dict(
                rql="Any B WHERE B is Book, B eid %(eid)s" % {"eid": r"\1"}, vid="bibo"
            ),
        ),
        (
            rgx(r"/book/(\d+)\.html"),
            dict(rql="Any B WHERE B is Book, B eid %(eid)s" % {"eid": r"\1"}),
        ),
        (
            rgx(r"/book/isbn/(.*)"),
            dict(
                rql='Any B WHERE B is Book, (B isbn13 "%(isbn)s") OR (B isbn10 "%(isbn)s")'
                % {"isbn": r"\1"}
            ),
        ),
    ]
