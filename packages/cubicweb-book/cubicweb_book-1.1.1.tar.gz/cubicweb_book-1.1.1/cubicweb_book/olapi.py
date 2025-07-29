"""
Simple API for OpenLibrary <http://openlibrary.org/dev/docs>

Try running::

  $ python olapi.py search tom sawyer

:organization: Logilab
:copyright: 2009-2017 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from six.moves.urllib.request import urlopen
from six.moves.urllib.error import HTTPError, URLError
from six.moves.urllib.parse import urlencode
from json import loads, dumps


class OpenLibraryFailure(Exception):
    """raised on API failure"""


def openlibrary_fetch(url):
    try:
        result = loads(urlopen(url).read().decode("utf8"))  # XXX handle timeouts
    except URLError as exc:
        raise OpenLibraryFailure(str(exc))
    # depending on the type of request, result is not identically structured
    # result from a search will have a status key, otherwise result is the
    # set of result itself
    if "result" in result:
        if result["status"] != "ok":
            raise OpenLibraryFailure(result["message"])
        return result["result"]
    else:
        return result


def openlibrary_query(type, **kwargs):
    query = dict(type=type, **kwargs)
    # required parameter * empty to collect all properties from books
    # objects
    query["*"] = ""
    url = "http://openlibrary.org/query.json?%s" % urlencode(query)
    return openlibrary_fetch(url)


def search_books(phrase):
    query = dict(query=phrase)
    url = "http://openlibrary.org/api/search?%s" % urlencode({"q": dumps(query)})
    return openlibrary_fetch(url)


def get_bookcover(coverid, size="M"):
    try:
        url = "http://covers.openlibrary.org/w/id/%s-%s.jpg" % (coverid, size)
        data = urlopen(url).read()
    except HTTPError as exc:
        raise OpenLibraryFailure(str(exc))
    return data


def get_authors(bookinfo):
    authors = []
    for author_key in bookinfo.get("authors", []):
        authinfo = openlibrary_query("/type/author", **author_key)
        authors += authinfo
    return authors


def set_bookinfo_cover(bookinfo, cover_required=False):
    coverids = bookinfo.get("covers", [])
    for coverid in coverids:
        try:
            bookinfo["cover"] = get_bookcover(coverid)
        except OpenLibraryFailure as exc:
            if cover_required:
                raise exc


def get_bookinfo(cover_required=False, **kwargs):
    infos = openlibrary_query("/type/edition", **kwargs)
    if infos:
        bookinfo = infos[0]
        set_bookinfo_cover(bookinfo, cover_required)
        return bookinfo
    return {}


if __name__ == "__main__":
    import sys
    import pprint

    if sys.argv[1] == "search":
        pprint.pprint(search_books(sys.argv[2]))
