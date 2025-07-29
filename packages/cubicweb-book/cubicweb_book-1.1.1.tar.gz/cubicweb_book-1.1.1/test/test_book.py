"""template automatic tests"""

import random
import os
from cubicweb import devtools
from cubicweb.devtools.fill import ValueGenerator
from cubicweb_web.devtools.testlib import (
    AutomaticWebTest,
    WebPostgresApptestConfiguration,
    WebCWTC,
)


def setUpModule():
    """Ensure a PostgreSQL cluster is running and configured

    If PGHOST environment variable is defined, use existing PostgreSQL cluster
    running on PGHOST and PGPORT (default 5432).

    Or start a dedicated PostgreSQL cluster by using
    cubicweb.devtools.startpgcluster()
    """
    config = devtools.DEFAULT_PSQL_SOURCES["system"]
    if config["db-host"] != "REPLACEME":
        return
    if "PGHOST" in os.environ:
        config["db-host"] = os.environ["PGHOST"]
        config["db-port"] = os.environ.get("PGPORT", 5432)
        return
    devtools.startpgcluster(__file__)
    import atexit

    atexit.register(devtools.stoppgcluster, __file__)


def random_numbers(size):
    return "".join(random.choice("0123456789") for i in range(size))


class MyValueGenerator(ValueGenerator):
    def generate_Book_isbn10(self, entity, index):
        return random_numbers(10)

    def generate_Book_isbn13(self, entity, index):
        return random_numbers(13)


class AutomaticWebTest(AutomaticWebTest):
    configcls = WebPostgresApptestConfiguration

    def to_test_etypes(self):
        return set(("Book", "Collection", "Editor"))

    def list_startup_views(self):
        return ()


class ViewTC(WebCWTC):
    configcls = WebPostgresApptestConfiguration

    def test_author_view(self):
        with self.admin_access.web_request() as req:
            jdoe = req.create_entity("Person", surname="jdoe")
            req.create_entity("Book", title="book", authors=jdoe)
            # should not raise
            jdoe.view("author-biblio")


if __name__ == "__main__":
    import unittest

    unittest.main()
