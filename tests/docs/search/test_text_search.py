import time
from unittest import TestCase

from tigrisdb.client import TigrisClient
from tigrisdb.search import Search
from tigrisdb.search_index import SearchIndex
from tigrisdb.types import sort
from tigrisdb.types.filters import Eq, And, LTE, GTE
from tigrisdb.types.search import Query, DocStatus, Result

from main import tigris_conf

CATALOG_SCHEMA = {
    "title": "catalog",
    "additionalProperties": False,
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "price": {"type": "number"},
        "brand": {"type": "string", "facet": True},
        "labels": {"type": "string", "facet": True},
        "popularity": {"type": "number"},
        "review": {
            "type": "object",
            "properties": {
                "author": {"type": "string"},
                "rating": {"type": "number"}

            }
        }
    }
}

DOCS = [
    {"id": "1", "name": "fiona handbag", "price": 99.9, "brand": "michael kors", "labels": "purses", "popularity": 8,
     "review": {"author": "alice", "rating": 7}},
    {"id": "2", "name": "tote bag", "price": 49, "brand": "coach", "labels": "handbags", "popularity": 9,
     "review": {"author": "olivia", "rating": 8.3}},
    {"id": "3", "name": "sling bag", "price": 75, "brand": "coach", "labels": "purses", "popularity": 9,
     "review": {"author": "alice", "rating": 9.2}},
    {"id": "4", "name": "sneakers shoes", "price": 40, "brand": "adidas", "labels": "shoes", "popularity": 10,
     "review": {"author": "olivia", "rating": 9}},
    {"id": "5", "name": "running shoes", "price": 89, "brand": "nike", "labels": "shoes", "popularity": 10,
     "review": {"author": "olivia", "rating": 8.5}},
    {"id": "6", "name": "running shorts", "price": 35, "brand": "adidas", "labels": "clothing", "popularity": 7,
     "review": {"author": "olivia", "rating": 7.5}},
]


class TextSearchTest(TestCase):
    client: Search = None
    index: SearchIndex = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TigrisClient(config=tigris_conf).get_search()

        # create search index
        cls.index = cls.client.create_or_update_index("catalog", schema=CATALOG_SCHEMA)
        # index some documents
        res: list[DocStatus] = cls.index.create_many(DOCS)

        # validating that all insertions succeed without any error
        for r in res:
            assert not r.error
        time.sleep(1)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.delete_index("catalog")

    # Searching for documents with a basic query
    def test_basic_search(self):
        query = Query(q="running")
        results: Result = self.index.search(query)
        # print(json.dumps(dataclasses.asdict(results), indent=2, default=str))
        self.assertEqual(2, len(results.hits))
        self.assertEqual(2, results.meta.found)

    # Searching on specific fields
    def test_search_on_specific_fields(self):
        query = Query(
            q="running",
            search_fields=["name", "labels"]
        )
        results: Result = self.index.search(query)
        # print(json.dumps(dataclasses.asdict(results), indent=2, default=str))
        self.assertEqual(2, len(results.hits))
        self.assertEqual(2, results.meta.found)

    # Refine the search results using filters
    def test_search_using_filters(self):
        query = Query(
            q="running",
            search_fields=["name", "labels"],
            filter_by=Eq("brand", "nike")
        )
        results: Result = self.index.search(query)
        # print(json.dumps(dataclasses.asdict(results), indent=2, default=str))
        self.assertEqual(1, len(results.hits))
        self.assertEqual(1, results.meta.found)

    # Applying complex filter on search results
    def test_search_using_complex_filters(self):
        query = Query(
            q="running",
            search_fields=["name", "labels"],
            filter_by=And(GTE("price", 40), LTE("price", 90))
        )
        results: Result = self.index.search(query)
        # print(json.dumps(dataclasses.asdict(results), indent=2, default=str))
        self.assertEqual(1, len(results.hits))
        self.assertEqual(1, results.meta.found)
        for hit in results.hits:
            price = hit.doc["price"]
            self.assertGreaterEqual(price, 40)
            self.assertLessEqual(price, 90)

    # Faceted search
    def test_faceted_search(self):
        query = Query(
            q="running",
            search_fields=["name", "labels"],
            filter_by=And(GTE("price", 40), LTE("price", 90)),
            facet_by=["brand", "labels"]
        )
        results: Result = self.index.search(query)
        # print(json.dumps(dataclasses.asdict(results), indent=2, default=str))
        self.assertEqual(1, len(results.hits))
        self.assertEqual(1, results.meta.found)

    # Sorting the search results with single sort order
    def test_with_single_sort(self):
        query = Query(
            q="running",
            search_fields=["name", "labels"],
            sort_by=sort.Descending("popularity")
        )
        results: Result = self.index.search(query)
        # print(json.dumps(dataclasses.asdict(results), indent=2, default=str))
        self.assertEqual(2, len(results.hits))
        self.assertEqual(2, results.meta.found)
        prev = None
        for hit in results.hits:
            if prev:
                self.assertGreaterEqual(prev.doc["popularity"], hit.doc["popularity"])
            prev = hit

    # Sorting the search results with multiple sort orders
    def test_with_tie_breaker_sort(self):
        query = Query(
            sort_by=[sort.Descending("popularity"), sort.Descending("review.rating")]
        )
        results: Result = self.index.search(query)
        # print(json.dumps(dataclasses.asdict(results), indent=2, default=str))
        self.assertEqual(len(DOCS), len(results.hits))
        self.assertEqual(len(DOCS), results.meta.found)
        prev = results.hits[0].doc
        for hit in results.hits[1:]:
            current = hit.doc
            if current["popularity"] == prev["popularity"]:
                self.assertGreaterEqual(prev["review"]["rating"], current["review"]["rating"])
            else:
                self.assertGreaterEqual(prev["popularity"], current["popularity"])
            prev = current

    # Specifying the document fields to retrieve
    def test_retrieve_doc_fields(self):
        query = Query(
            q="running",
            include_fields=["name", "price", "brand"]
        )
        results: Result = self.index.search(query)
        # print(json.dumps(dataclasses.asdict(results), indent=2, default=str))
        self.assertEqual(2, len(results.hits))
        self.assertEqual(2, results.meta.found)
        for hit in results.hits:
            self.assertCountEqual(query.include_fields, hit.doc.keys())

    # Excluding document fields
    def test_with_exclude_fields(self):
        query = Query(
            q="running",
            exclude_fields=["id", "price"]
        )
        results: Result = self.index.search(query)
        # print(json.dumps(dataclasses.asdict(results), indent=2, default=str))
        self.assertEqual(2, len(results.hits))
        self.assertEqual(2, results.meta.found)
        for hit in results.hits:
            doc_keys = hit.doc.keys()
            for f in query.exclude_fields:
                self.assertNotIn(f, doc_keys)