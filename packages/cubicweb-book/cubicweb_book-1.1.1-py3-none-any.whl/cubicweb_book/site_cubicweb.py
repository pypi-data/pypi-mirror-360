# XML <-> yams equivalence
from cubicweb.xy import xy

xy.register_prefix("bibo", "http://purl.org/ontology/bibo/")

xy.add_equivalence("Book", "bibo:Book")
xy.add_equivalence("Book title", "bibo:Book dc:title")
xy.add_equivalence("Book publish_date", "bibo:Book dc:date")
xy.add_equivalence("Book isbn10", "bibo:Book bibo:isbn10")
xy.add_equivalence("Book isbn13", "bibo:Book bibo:isbn13")
