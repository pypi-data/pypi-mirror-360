# -*- coding: utf-8 -*-
"""
Boxes for books

:organization: Logilab
:copyright: 2009-2017 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.predicates import is_instance, score_entity
from cubicweb_web.component import EntityCtxComponent


def has_isbn(entity):
    return entity.isbn13 is not None


class BookSeeAlso(EntityCtxComponent):
    __regid__ = "book_seealso_box"
    __select__ = (
        EntityCtxComponent.__select__ & is_instance("Book") & score_entity(has_isbn)
    )
    context = "navcontentbottom"

    order = 25  # display order of the box (25=display it last)

    def render_title(self, w):
        w(self._cw._("This book on other sites"))

    def render_body(self, w):
        entity = self.cw_rset.get_entity(0, 0)
        isbn = entity.isbn13 or ""
        self.append(self.link("OpenLibrary", "http://openlibrary.org/isbn/%s" % isbn))
        self.append(
            self.link("Google Books", "http://books.google.com/books?q=isbn:%s" % isbn)
        )
        self.append(
            self.link(
                "Amazon Books",
                "http://www.amazon.com/gp/search/ref=sr_adv_b/?field-isbn=%s" % isbn,
            )
        )
        self.render_items(w)
