"""
To use this script:
cubicweb-ctl shell appid import_dbpedia.py number_of_books_to_import

number_of_books_to_import is optionnal, if not provided, all books
will be imported
"""

from __future__ import print_function

import re

from lxml import etree
import six

from cubicweb.dataimport import CWImportController, RQLObjectStore

from cubicweb_book.migration.import_ol import gen_books, to_date

NAMESPACES = {
    "res": "http://www.w3.org/2005/sparql-results#",
    "dbpprop": "http://dbpedia.org/property/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
}

SPARQL = """select ?book, ?title, ?pages, ?isbn, ?authors, ?publish_date, ?publisher where {
  ?book rdf:type <http://dbpedia.org/class/Book>.
  ?book dbpprop:name ?title.
  ?book dbpprop:pages ?pages.
  ?book dbpedia-owl:isbn ?isbn.
  ?book dbpedia-owl:author ?authors.
  ?book dbpprop:releaseDate ?publish_date.
  ?book dbpprop:publisher ?publisher
} %s"""

AUTHOR_SPARQL = """select ?author where {
  ?author rdf:type <http://dbpedia.org/ontology/Person>.
  ?author foaf:name ?name
  FILTER regex(?name, "%s")
}"""

QUERY = """http://dbpedia.org/sparql?query=%s&format=application/rdf+xml""" % SPARQL


def get_books(limit):
    if limit:
        limit = "LIMIT %s" % limit
    else:
        limit = ""
    query = QUERY % limit
    tree = etree.parse(query)
    books = tree.xpath("/rdf:RDF/rdf:Description/res:solution", namespaces=NAMESPACES)
    for book in books:
        try:
            bookinfo = {}
            for binding in book.xpath("res:binding", namespaces=NAMESPACES):
                attr = binding.xpath("res:variable", namespaces=NAMESPACES)[0].text
                # author uri is store in attribute rdf:resource of res:value
                if attr in ("authors", "book"):
                    elt = binding.xpath("res:value", namespaces=NAMESPACES)[0]
                    value = six.text_type(elt.get("{%s}resource" % NAMESPACES["rdf"]))
                elif attr == "publisher":
                    # Publisher can either be an external resource or just plain text
                    elt = binding.xpath("res:value", namespaces=NAMESPACES)[0]
                    if elt.text:
                        value = six.text_type(elt.text)
                    else:
                        value = six.text_type(
                            elt.get("{%s}resource" % NAMESPACES["rdf"])
                        )
                else:
                    value = six.text_type(
                        binding.xpath("res:value", namespaces=NAMESPACES)[0].text
                    )
                bookinfo[attr] = value
            print("----------", bookinfo["book"])
            set_isbn(bookinfo)
            set_author(bookinfo)
            set_pages(bookinfo)
            set_publisher(bookinfo)
            bookinfo["cwuri"] = "http://dbpedia.org"
            bookinfo["externaluri"] = bookinfo["book"]
            bookinfo["publish_date"] = to_date(bookinfo["publish_date"])
            yield bookinfo
        except Exception as e:
            print("EXCEPTION in get_books:", e)


def set_isbn(bookinfo):
    # isbn numbers follow the pattern:
    # ISBN x-xx-xxxxxx-x (xxxxx)
    #
    # there can be multiple isbn separated by a / or ,
    # This function selects the number in order to set
    # attributes isbn10 or isbn13 accordingly.
    # Or even sometimes, the value is the isbn itself or
    # just x-xx-xxxxxx-x.
    # We match here those four cases.
    initial_isbn = bookinfo["isbn"]
    isbns = None
    if "/" in initial_isbn:
        isbns = initial_isbn.split("/")
    elif "," in initial_isbn:
        isbns = initial_isbn.split(",")
    else:
        isbns = [initial_isbn]
    bookinfo["isbn10"] = bookinfo["isbn13"] = ""
    for item in isbns:
        matchs = re.match(r".*ISBN\s([^\s]+)", item)
        if matchs:
            isbn = matchs.group(1)
            num = isbn.replace("-", "").strip()
            if len(num) == 10:
                bookinfo["isbn10"] = num
            elif len(num) == 13:
                bookinfo["isbn13"] = num
            else:
                print("Ignoring truncated ISBN number.")
        else:
            if "-" in item:
                item = item.replace("-", "")
            if len(item) == 10:
                bookinfo["isbn10"] = six.text_type(item)
            elif len(item) == 13:
                bookinfo["isbn13"] = six.text_type(item)
            else:
                print("Ignoring truncated ISBN number.")


def set_author(bookinfo):
    author_uri = bookinfo["authors"]
    url = "%s.rdf" % author_uri.replace("resource", "data")
    try:
        tree = etree.parse(url)
        # try load foaf:name, if not found, then we try rdfs:label
        auth_name = tree.xpath(
            "/rdf:RDF/rdf:Description/foaf:name", namespaces=NAMESPACES
        ) or tree.xpath("/rdf:RDF/rdf:Description/rdfs:label", namespaces=NAMESPACES)
        if len(auth_name) > 0:
            auth_name = auth_name[0].text

        author_infos = {}
        author_infos["name"] = six.text_type(auth_name)
        author_infos["cwuri"] = "http://dbpedia.org"
        author_infos["externaluri"] = six.text_type(author_uri)
        bookinfo["authors"] = [author_infos]
    except Exception as e:
        print("EXCEPTION in set_author:", e)


def set_publisher(bookinfo):
    # Publisher is either a uri or plain text
    # In case a uri is specified, we will look for the corresponding
    # name in its rdf representation.
    publisher_uri = bookinfo["publisher"]
    if publisher_uri.startswith("http"):
        url = "%s.rdf" % publisher_uri.replace("resource", "data")
        try:
            tree = etree.parse(url)
            publisher_name = tree.xpath(
                "/rdf:RDF/rdf:Description/rdfs:label", namespaces=NAMESPACES
            )
            if len(publisher_name) > 0:
                bookinfo["publisher"] = six.text_type(publisher_name[0].text[:50])
            else:
                bookinfo["publisher"] = ""
        except Exception as e:
            print("EXCEPTION in set_publisher:", e)


def set_pages(bookinfo):
    pages = bookinfo["pages"]
    number = pages.split()[0]
    if number.isdigit():
        bookinfo["pages"] = number
    else:
        bookinfo["pages"] = None


GENERATORS = []
CHK = []
GENERATORS.append((gen_books, CHK))

if __name__ == "__main__":
    import sys

    try:
        limit = sys.argv[4]
    except Exception:
        limit = None

    # create controller
    ctl = CWImportController(RQLObjectStore(session))
    ctl.askerror = 1
    ctl.generators = GENERATORS
    ctl.data["books"] = get_books(limit)
    # run
    ctl.run()
