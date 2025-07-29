from __future__ import print_function

import six
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entity import EntityAdapter
from cubicweb.predicates import is_instance

from cubicweb_person.entities import Person

from lxml import etree

NAMESPACES = {
    "res": "http://www.w3.org/2005/sparql-results#",
    "dbpprop": "http://dbpedia.org/property/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dbpedia-owl": "http://dbpedia.org/ontology/",
}


class Book(AnyEntity):
    __regid__ = "Book"
    fetch_attrs, cw_fetch_order = fetch_config(["title", "isbn13", "isbn10", "pages"])


class BookICalendarableAdapter(EntityAdapter):
    __regid__ = "ICalendarable"
    __select__ = is_instance("Book")

    @property
    def start(self):
        return self.entity.publish_date

    stop = start


class Collection(AnyEntity):
    __regid__ = "Collection"

    fetch_attrs, cw_fetch_order = fetch_config(["name"])


class Editor(AnyEntity):
    __regid__ = "Editor"

    fetch_attrs, cw_fetch_order = fetch_config(["name"])


class Author(Person):
    def get_bibliographies(self):
        # yield bibliography and its related source
        # XXX for now, only dbpedia provides bibliography details by lang
        if self.same_as:
            for ext_uri in self.related("same_as", "object").entities():
                uri = "%s.rdf" % ext_uri.uri.replace("resource", "data")
                try:
                    tree = etree.parse(uri)
                    lang = self._cw.lang
                    # try to get bibliography in application lang otherwise en
                    biblio = tree.xpath(
                        '/rdf:RDF/rdf:Description/dbpedia-owl:abstract[@xml:lang="%s"]'
                        % lang,
                        namespaces=NAMESPACES,
                    )
                    if biblio:
                        yield (six.text_type(biblio[0].text), ext_uri.uri)
                    else:
                        biblio = tree.xpath(
                            '/rdf:RDF/rdf:Description/dbpedia-owl:abstract[@xml:lang="en"]',
                            namespaces=NAMESPACES,
                        )
                        if biblio:
                            yield (six.text_type(biblio[0].text), ext_uri.uri)
                        else:
                            continue

                except Exception as e:
                    print("EXCEPTION", e)
                    continue
