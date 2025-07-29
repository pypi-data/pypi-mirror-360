from yams.buildobjs import (
    EntityType,
    SubjectRelation,
    RelationDefinition,
    String,
    Int,
    Date,
)
from cubicweb import _

from cubicweb_person.schema import Person


Person.add_relation(SubjectRelation("ExternalUri", cardinality="**"), name="same_as")


class Book(EntityType):
    title = String(
        required=False,  # handled by hook
        fulltextindexed=True,
        indexed=True,
        maxsize=255,
        description=_("book title"),
    )
    subtitle = String(fulltextindexed=True, maxsize=255, description=_("book subtitle"))
    isbn10 = String(
        unique=True,
        fulltextindexed=True,
        indexed=True,
        maxsize=10,
        description=_(
            "Old International Standard Book Number (10 chars, no spaces or dashes)"
        ),
    )
    isbn13 = String(
        unique=True,
        fulltextindexed=True,
        indexed=True,
        maxsize=13,
        description=_(
            "New International Standard Book Number (13 chars, no spaces or dashes)"
        ),
    )
    pages = Int(description=_("number of pages"))
    publish_date = Date(description=_("publication date"))
    language = String(
        fulltextindexed=True,
        indexed=True,
        maxsize=50,
        description=_("language of the book"),
    )
    summary = String(
        fulltextindexed=True, indexed=True, description=_("Short summary of the book")
    )
    content = String(
        fulltextindexed=True, indexed=True, description=_("table of contents")
    )
    # relations
    authors = SubjectRelation("Person", cardinality="**", description=_("book authors"))
    publisher = SubjectRelation(
        "Editor", cardinality="**", description=_("book publisher")
    )
    editor = SubjectRelation("Person", cardinality="**", description=_("book editor"))
    collection = SubjectRelation(
        "Collection", cardinality="*1", description=_("publisher's collection")
    )
    has_cover = SubjectRelation(
        "File", cardinality="**", composite="subject", description=_("book cover")
    )
    same_as = SubjectRelation("ExternalUri", cardinality="**", composite="subject")


class Collection(EntityType):
    name = String(required=True, fulltextindexed=True, indexed=True, maxsize=100)


class has_collection(RelationDefinition):
    subject = "Editor"
    object = "Collection"
    cardinality = "**"


class Editor(EntityType):  # XXX rename to Publisher
    name = String(required=True, fulltextindexed=True, indexed=True, maxsize=100)
    has_address = SubjectRelation("PostalAddress", cardinality="*1")


class same_as(RelationDefinition):
    subject = "Person"
    object = "ExternalUri"
    cardinality = "**"
    composite = "subject"
