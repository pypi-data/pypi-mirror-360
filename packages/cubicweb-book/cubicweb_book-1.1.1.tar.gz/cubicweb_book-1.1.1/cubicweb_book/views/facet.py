from cubicweb.predicates import is_instance
from cubicweb_web.facet import (
    RangeFacet,
    DateRangeFacet,
    HasRelationFacet,
    AttributeFacet,
)


class BookPagesFacet(RangeFacet):
    __regid__ = "priority-facet"
    __select__ = RangeFacet.__select__ & is_instance("Book")
    rtype = "pages"


class BookPubdateFacet(DateRangeFacet):
    __regid__ = "pubdate-facet"
    __select__ = DateRangeFacet.__select__ & is_instance("Book")
    rtype = "publish_date"


class HasCoverFacet(HasRelationFacet):
    __regid__ = "hascover-facet"
    __select__ = HasRelationFacet.__select__ & is_instance("Book")
    rtype = "has_cover"


class CWUriFacet(AttributeFacet):
    __regid__ = "cwuri-facet"
    __select__ = AttributeFacet.__select__ & is_instance("Book")
    rtype = "cwuri"
