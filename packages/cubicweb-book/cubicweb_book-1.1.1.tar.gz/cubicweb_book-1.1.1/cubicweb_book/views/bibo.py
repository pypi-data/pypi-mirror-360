__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb import _
from cubicweb_web.view import EntityView
from cubicweb.predicates import is_instance


class BiboView(EntityView):
    __regid__ = "bibo"
    __select__ = is_instance("Book")

    title = _("bibo rdf")
    templatable = False
    content_type = "application/rdf+xml"
    item_vid = "bibo_item"

    def call(self):
        self.w('<?xml version="1.0" encoding="%s"?>\n' % self._cw.encoding)
        self.w(
            """<rdf:RDF
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
            xmlns:owl="http://www.w3.org/2002/07/owl#"
            xmlns:foaf="http://xmlns.com/foaf/0.1/"
            xmlns:bibo='http://purl.org/ontology/bibo/'
            xmlns:dcterms='http://purl.org/dc/terms/'
            xmlns:dc='http://purl.org/dc/elements/1.1/'
            >\n"""
        )
        for i in range(self.cw_rset.rowcount):
            self.cell_call(row=i, col=0)
        self.w("</rdf:RDF>\n")

    def cell_call(self, row, col):
        self.wview(self.item_vid, self.cw_rset, row=row, col=col)


class BiboItemView(EntityView):
    __regid__ = "bibo_item"
    __select__ = is_instance("Book")

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        self.w('<bibo:Book rdf:about="%s">\n' % xml_escape(entity.absolute_url()))
        self.w(" <dc:title>%s</dc:title>" % xml_escape(entity.dc_title()))
        if entity.publish_date:
            self.w(" <dc:date>%s</dc:date>" % xml_escape(entity.dc_date("%Y-%m-%d")))
        for same in entity.same_as:
            self.w(" <owl:sameAs>%s</owl:sameAs>" % xml_escape(same.uri))
        if entity.isbn10:
            self.w(" <bibo:isbn10>%s</bibo:isbn10>" % xml_escape(entity.isbn10))
        if entity.isbn13:
            self.w(" <bibo:isbn13>%s</bibo:isbn13>" % xml_escape(entity.isbn13))
        for pub in entity.publisher:
            self.w(
                " <dcterms:publisher>%s</dcterms:publisher>"
                % xml_escape(pub.dc_title())
            )
        self.w("</bibo:Book>\n")
