import json
import time
from typing import List
from unittest import TestCase

from tigrisdb.client import TigrisClient
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
        "brand": {"type": "string"},
        "labels": {"type": "string"},
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


class TextSearch(TestCase):

    def setUp(self) -> None:
        self.client = TigrisClient(config=tigris_conf).get_search()
        # create search index
        self.index = self.client.create_or_update_index("catalog", schema=CATALOG_SCHEMA)
        # index some documents
        res: list[DocStatus] = self.index.create_many(DOCS)
        # validating that all insertions succeed without any error
        for r in res:
            self.assertIsNone(r.error)
        time.sleep(1)

    def tearDown(self) -> None:
        self.client.delete_index("catalog")

    # Searching for documents with a basic query
    def test_basic_search(self):
        query = Query(q="running")
        results: Result = self.index.search(query)
        print(results)
        self.assertEqual(2, len(results.hits))
        self.assertEqual(2, results.meta.found)
