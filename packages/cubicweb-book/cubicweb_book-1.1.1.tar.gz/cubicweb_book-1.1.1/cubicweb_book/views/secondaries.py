"""Secondaries views for Book.

:organization: Logilab
:copyright: 2009-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance, score_entity
from cubicweb.uilib import cut
from cubicweb_web.view import EntityView


class BookListView(EntityView):
    __regid__ = "listitem"
    __select__ = is_instance("Book")

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<div class="container clear">')
        self.w('<div class="left">')
        self.render_cover(entity)
        self.w("</div>")
        self.w("<div>")
        self.w(
            '<h2><a href="%s">%s</a></h2>'
            % (entity.absolute_url(), xml_escape(entity.dc_title()))
        )
        self.w("<p>%s - " % (entity.printable_value("publish_date") or ""))
        self.w("%s" % self._cw._("by"))
        self.wview("csv", entity.related("authors"), "null")
        self.w("</p></div></div><br />")

    def render_cover(self, entity):
        if entity.has_cover:
            imgs = [
                (image.absolute_url(vid="download"), image.data_name)
                for image in entity.has_cover
            ]
        else:
            imgs = [(self._cw.uiprops["PICTO_NOCOVER"], self._cw._("no cover"))]
        for src, alt in imgs:
            self.w(
                '<a href="%s">'
                '<img alt="%s" src="%s" width="50" style="align:right; width:30; height:50" />'
                "</a>" % (entity.absolute_url(), xml_escape(alt), xml_escape(src))
            )


class AuthorBibliographyView(EntityView):
    __regid__ = "author-biblio"
    __select__ = is_instance("Person") & score_entity(lambda x: x.reverse_authors)

    def entity_call(self, entity):
        desc = cut(entity.dc_description(), 50)
        self.w(
            '<a href="%s" title="%s">'
            % (xml_escape(entity.absolute_url()), xml_escape(desc))
        )
        self.w(xml_escape(self._cw.view("textincontext", rset=entity.cw_rset)))
        self.w("</a>")
        for biblio, source in entity.get_bibliographies():
            if source.startswith("http://dbpedia.org"):
                title = "dbpedia"
            elif source.startswith("http://openlibrary.org"):
                title = "openlibrary"
            else:
                title = self._cw._("unknown source")
            self.w(
                '<div>%s<br/>(%s: <a href="%s">%s</a>)</div>'
                % (biblio, self._cw._("Source"), source, self._cw._(title))
            )
