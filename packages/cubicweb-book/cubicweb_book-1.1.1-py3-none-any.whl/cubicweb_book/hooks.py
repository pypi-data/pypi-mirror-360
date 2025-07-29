# -*- coding: utf-8 -*-
"""
:organization: Logilab
:copyright: 2009-2017 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import datetime

import six

from cubicweb import _
from cubicweb import Binary, ValidationError
from cubicweb.predicates import is_instance
from cubicweb.server import hook

from cubicweb_book import olapi


def set_if_unset(entity, key, book, otherkey):
    if "key" not in entity:
        if otherkey in book:
            value = book[otherkey]
            if isinstance(value, list):
                value = value[0]
            # NOTE: simplejson (v>=2.0.0) uses str for ascii strings
            entity[key] = six.text_type(value)


class BookCreationHook(hook.Hook):
    __regid__ = "book_fetchinfo"
    __select__ = hook.Hook.__select__ & is_instance("Book")

    events = ("before_add_entity",)

    def __call__(self):
        entity = self.entity
        book = None
        if "isbn13" in entity.cw_edited:
            try:
                book = olapi.get_bookinfo(isbn_13=entity.isbn13, cover_required=False)
            except olapi.OpenLibraryFailure:
                self._cw.info(
                    "failed to fetch book info from OpenLibrary for ISBN %s",
                    entity.isbn13,
                )

        elif "isbn10" in entity.cw_edited:
            try:
                book = olapi.get_bookinfo(isbn_10=entity.isbn10, cover_required=False)
            except olapi.OpenLibraryFailure:
                self._cw.info(
                    "failed to fetch book info from OpenLibrary for ISBN %s",
                    entity.isbn10,
                )

        if not book:
            self.check_required_fields()
        else:
            languages = []
            for lang in book.get("languages", []):
                langinfo = olapi.openlibrary_query("/type/language", **lang)
                if langinfo:
                    langinfo = langinfo[0]
                languages.append(langinfo.get("name", "?"))
            if entity.language is None:
                entity["language"] = ", ".join(languages)
            set_if_unset(entity, "title", book, "title")
            set_if_unset(entity, "pages", book, "number_of_pages")
            set_if_unset(entity, "isbn10", book, "isbn_10")
            if "publish_date" in book:
                date = book["publish_date"]
                try:
                    if "," in date:
                        date = datetime.strptime(date, "%B %d, %Y")
                    elif date.isdigit():
                        date = datetime(int(date), 1, 1)
                    else:
                        raise ValueError("unknown date format")
                    if not entity.get("publish_date"):
                        entity["publish_date"] = date
                except ValueError:
                    self._cw.info("failed to parse publish_date %s", date)
            BookRelationPreCommit(self._cw, entity=entity, book=book)

    def check_required_fields(self):
        entity = self.entity
        if not entity.title:
            raise ValidationError(
                entity.eid,
                {
                    "title": _(
                        "could not find the book in OpenLibrary. Please fill in "
                        "the title and other fields you know"
                    )
                },
            )


class BookRelationPreCommit(hook.Operation):

    def precommit_event(self):
        if not self.entity.has_cover and "cover" in self.book:
            name = "cover for %s" % self.book["title"]
            self.session.execute(
                "INSERT File F: F title %(n)s, F data %(d)s, "
                "F data_format %(f)s, F data_name %(dn)s, "
                "B has_cover F WHERE B eid %(x)s",
                {
                    "n": name,
                    "x": self.entity.eid,
                    "d": Binary(self.book["cover"]),
                    "f": "image/jpeg",
                    "dn": name,
                },
            )
        if not self.entity.publisher and "publishers" in self.book:
            for publisher in self.book["publishers"]:
                rset = self.session.execute(
                    "Any X WHERE X is Editor, X name %(name)s",
                    {"name": six.text_type(publisher)},
                )
                if rset:
                    for publisher in rset.entities(0):
                        publisher.set_relations(reverse_publisher=self.entity)
                else:
                    self.session.create_entity(
                        "Editor",
                        name=six.text_type(publisher),
                        reverse_publisher=self.entity,
                    )

        if not self.entity.authors and "authors" in self.book:
            for author_info in olapi.get_authors(self.book):
                uri = "http://openlibrary.org%s" % author_info["key"]
                rset = self.session.execute(
                    "Any U WHERE U is ExternalUri, U uri %(uri)s", {"uri": uri}
                )
                if rset:
                    author = rset.get_entity(0, 0).reverse_same_as[0]
                else:
                    author = self.session.create_entity(
                        "Person", surname=six.text_type(author_info["name"])
                    )
                author.set_relations(reverse_authors=self.entity)
