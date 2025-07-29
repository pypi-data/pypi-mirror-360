"""
to use this script:
cubicweb-ctl shell appid import_ol.py keywords to_search in_openlibrary
"""

from __future__ import print_function

import six

from cubicweb_book.olapi import search_books
from cubicweb.dataimport import CWImportController, RQLObjectStore, mk_entity
from datetime import datetime
from functools import partial
from lxml import etree

NAMESPACES = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "bibo": "http://purl.org/ontology/bibo/",
    "dcterms": "http://purl.org/dc/terms/",
    "ol": "http://openlibrary.org/type/author",
}


def get_node_value(tree, node_name):
    node = tree.xpath("/rdf:RDF/rdf:Description/%s" % node_name, namespaces=NAMESPACES)
    if len(node) > 0:
        return six.text_type(node[0].text)
    return ""


def get_externaluri(tree):
    externaluri = tree.xpath(
        "/rdf:RDF/rdf:Description[@rdf:about]", namespaces=NAMESPACES
    )
    if len(externaluri) > 0:
        return six.text_type(externaluri[0].get("{%s}about" % NAMESPACES["rdf"]))
    return ""


def get_authors(tree):
    authors = tree.xpath(
        "/rdf:RDF/rdf:Description/bibo:authorList/rdf:Description[@rdf:about]",
        namespaces=NAMESPACES,
    )
    authors_name = tree.xpath(
        "/rdf:RDF/rdf:Description/bibo:authorList/rdf:Description/rdf:value",
        namespaces=NAMESPACES,
    )
    if len(authors) > 0:
        authors_infos = []
        for author, author_name in zip(authors, authors_name):
            item = {}
            item["externaluri"] = six.text_type(
                author.get("{%s}about" % NAMESPACES["rdf"])
            )
            item["cwuri"] = six.text_type("http://openlibrary.org")
            item["name"] = six.text_type(author_name.text)
            authors_infos.append(item)
        return authors_infos
    return []


def uget(node, attr):
    value = node.get(attr)
    if isinstance(value, str):
        # if lxml returns a str value, it's a pure-ascii string
        value = six.text_type(value)
    return value


def to_date(date):
    if "," in date:
        return datetime.strptime(date, "%B %d, %Y")
    elif date.isdigit():
        return datetime(int(date), 1, 1)
    raise ValueError("unknown date format")


def fetch_book_rdf(bookid):
    """Work around bugs in OL's RDF"""
    from six.moves.urllib.request import urlopen

    bookid = bookid.replace("/b/", "/books/")
    url = "http://openlibrary.org%s.rdf" % bookid
    print("----------", url)
    data = urlopen(url).read()
    try:
        tree = etree.fromstring(data)
    except Exception as exc:
        print("Trying to work around", exc)
        data = data.replace("</rdf:RDF>", "</rdf:Description></rdf:RDF>")
        tree = etree.fromstring(data)
    return tree


def get_books(phrase):
    books = search_books(phrase)
    print("total, books", len(books))
    for book in books:
        if not book:
            print("empty book", book)
            continue
        try:
            tree = fetch_book_rdf(book)
        except Exception as exc:
            print("Failed. Ignoring this book", exc)
        bookinfo = {}
        bookinfo["isbn10"] = get_node_value(tree, "bibo:isbn10")
        bookinfo["isbn13"] = get_node_value(tree, "bibo:isbn13")
        bookinfo["cwuri"] = "http://openlibrary.org"
        bookinfo["externaluri"] = get_externaluri(tree)
        bookinfo["title"] = get_node_value(tree, "dcterms:title")[:128]
        bookinfo["publisher"] = get_node_value(tree, "dcterms:publisher")
        try:
            bookinfo["publish_date"] = to_date(get_node_value(tree, "dcterms:issued"))
        except Exception as exc:
            print("Failed to read publish_date because", exc)
            bookinfo["publish_date"] = None
        # authors is a list of urls leading to author external uri
        # from which we'll parse rdf content
        bookinfo["authors"] = get_authors(tree)
        yield bookinfo


def remove_book_same_id(id_type, id_value):
    beid = already_exists(ctl, "Book", id_type, id_value)
    if beid:
        ctl.store.rql("DELETE Book B WHERE B eid %s" % beid)


def already_exists(ctl, etype, attrname, attrvalue):
    rql = 'Any X WHERE X is %s, X %s "%s"' % (etype, attrname, attrvalue)
    rset = ctl.store.rql(rql)
    if rset:
        return rset[0][0]
    return None


def already_exists_relation(ctl, seid, rtype, oeid):
    rql = "Any X, Y WHERE X %s Y, X eid %s, Y eid %s" % (rtype, seid, oeid)
    rset = ctl.store.rql(rql)
    if rset:
        return True
    return False


# XXX move this to cw.dataimport ?


def _maxsize(size, text):
    if len(text) > size:
        print("Truncating from", len(text), "to size", size, text)
    return text[:size]


def maxsize(size):
    return partial(_maxsize, size)


GENERATORS = []

BOOKS = [
    ("title", "title", (maxsize(128),)),
    ("cwuri", "cwuri", ()),
]

AUTHORS = [("name", "surname", (maxsize(64),))]
PUBLISHERS = [("name", "name", (maxsize(100),))]
CHK = []


def gen_books(ctl):
    for bookinfo in ctl.get_data("books"):
        if already_exists(ctl, "Book", "isbn10", bookinfo["isbn10"]) or already_exists(
            ctl, "Book", "isbn13", bookinfo["isbn13"]
        ):
            beid = already_exists(
                ctl, "Book", "isbn10", bookinfo["isbn10"]
            ) or already_exists(ctl, "Book", "isbn13", bookinfo["isbn13"])
            book = ctl.store.rql("Any B WHERE B is Book, B eid %s" % beid).get_entity(
                0, 0
            )
            # update exsting book with new information
            book.update(bookinfo)
        else:
            entity = mk_entity(bookinfo, BOOKS)
            if bookinfo["isbn10"]:
                entity["isbn10"] = bookinfo["isbn10"]
            if bookinfo["isbn13"]:
                entity["isbn13"] = bookinfo["isbn13"]
            if "pages" in bookinfo:
                if bookinfo["pages"]:
                    entity["pages"] = bookinfo["pages"]
            ctl.store.add("Book", entity)
            beid = entity["eid"]
        # XXX cf datafeed.sget_externaluri()
        if not already_exists(ctl, "ExternalUri", "uri", bookinfo["externaluri"]):
            externaluri = mk_entity(
                {"uri": bookinfo["externaluri"]},
                [
                    ("uri", "uri", ()),
                ],
            )
            ctl.store.add("ExternalUri", externaluri)
            eueid = externaluri["eid"]
        else:
            eueid = already_exists(ctl, "ExternalUri", "uri", bookinfo["externaluri"])
        if not already_exists_relation(ctl, beid, "same_as", eueid):
            ctl.store.relate(beid, "same_as", eueid)
        if "authors" in bookinfo:
            for authorinfo in bookinfo.get("authors"):
                try:
                    # XXX ideally we want to collect author information from url
                    # but since RDF for author is invalid for now, we can not use it
                    # we have to wait until this is fixed.
                    # get author information from RDf source
                    # url = u'%s.rdf' % author
                    # tree = etree.parse(url)
                    if not already_exists(ctl, "Person", "surname", authorinfo["name"]):
                        author = mk_entity(authorinfo, AUTHORS)
                        ctl.store.add("Person", author)
                        aeid = author["eid"]
                    else:
                        aeid = already_exists(
                            ctl, "Person", "surname", authorinfo["name"]
                        )
                    if not already_exists_relation(ctl, beid, "authors", aeid):
                        ctl.store.relate(beid, "authors", aeid)
                    # Handle external URI
                    if not already_exists(
                        ctl, "ExternalUri", "uri", authorinfo["externaluri"]
                    ):
                        externaluri = mk_entity(
                            {"uri": authorinfo["externaluri"]},
                            [
                                ("uri", "uri", ()),
                            ],
                        )
                        ctl.store.add("ExternalUri", externaluri)
                        eueid = externaluri["eid"]
                    else:
                        eueid = already_exists(
                            ctl, "ExternalUri", "uri", authorinfo["externaluri"]
                        )
                    if not already_exists_relation(ctl, aeid, "same_as", eueid):
                        ctl.store.relate(aeid, "same_as", eueid)

                except Exception as e:
                    print("EXCEPTION:", e)
                    break
        if "publisher" in bookinfo:
            if not already_exists(ctl, "Editor", "name", bookinfo["publisher"]):
                editorinfo = {"name": bookinfo["publisher"]}
                editor = mk_entity(editorinfo, PUBLISHERS)
                ctl.store.add("Editor", editor)
                eeid = editor["eid"]
            else:
                eeid = already_exists(ctl, "Editor", "name", bookinfo["publisher"])
            if not already_exists_relation(ctl, beid, "publisher", eeid):
                ctl.store.relate(beid, "publisher", eeid)
        ctl.store.commit()


GENERATORS.append((gen_books, CHK))

if __name__ == "__main__":
    import sys

    phrase = " ".join(sys.argv[4:])
    # define data generators

    # create controller
    ctl = CWImportController(RQLObjectStore(session))
    ctl.askerror = 1
    ctl.generators = GENERATORS
    ctl.data["books"] = get_books(phrase)
    # run
    ctl.run()
