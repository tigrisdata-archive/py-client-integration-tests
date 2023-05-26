import json
import time
from typing import TypedDict, Dict, List
from unittest import TestCase

from tigrisdb.client import TigrisClient
from tigrisdb.search import Search
from tigrisdb.search_index import SearchIndex
from tigrisdb.types import ClientConfig
from tigrisdb.types.filters import Eq
from tigrisdb.types.search import Query, VectorField

from main import tigris_conf
from tests.utils import pretty

VECTOR_SCHEMA = {
    "title": "my_embeddings",
    "additionalProperties": False,
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "document": {"type": "string"},
        "metadata": {"type": "object"},
        "embeddings": {
            "type": "array",
            "format": "vector",
            "dimensions": 3
        }
    }
}


class Document(TypedDict):
    id: str
    document: str
    metadata: Dict
    embeddings: List[float]


DOCS: List[Document] = [
    Document(id="id_1", document="First document", metadata={"category": "shoes"}, embeddings=[1.2, 2.3, 4.5]),
    Document(id="id_2", document="Another document", metadata={"category": "clothing"}, embeddings=[6.7, 8.2, 9.2])
]


class VectorConceptDocs(TestCase):
    client: Search = None
    index: SearchIndex = None

    @classmethod
    def setUpClass(cls) -> None:
        # cls.client = TigrisClient(config=tigris_conf).get_search()
        cls.client = TigrisClient(
            config=ClientConfig(
                server_url=tigris_conf.server_url,
                project_name=tigris_conf.project_name,
                client_id=tigris_conf.client_id,
                client_secret=tigris_conf.client_secret
            )).get_search()
        # create search index
        cls.index = cls.client.create_or_update_index("my_embeddings", schema=VECTOR_SCHEMA)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.delete_index("my_embeddings")

    def test_create_docs(self):
        res = self.index.create_many(DOCS)
        for r in res:
            self.assertIsNone(r.error)
        time.sleep(1)

    def test_similarity(self):
        q = Query(
            vector_query=VectorField(field="embeddings", vector=[1.0, 2.1, 3.2]),
        )
        result = self.index.search(q)
        pretty(result)
        self.assertEqual(len(DOCS), len(result.hits))
        hit = result.hits[0]
        print(json.dumps(hit.doc, indent=2))
        print(hit.meta.text_match.vector_distance)

    def test_filter(self):
        q = Query(
            vector_query=VectorField(field="embeddings", vector=[1.0, 2.1, 3.2]),
            filter_by=Eq("metadata.category", "shoes")
        )
        result = self.index.search(q)
        self.assertEqual(1, len(result.hits))
        pretty(result)
