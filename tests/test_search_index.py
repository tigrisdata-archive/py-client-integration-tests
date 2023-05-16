import time
from pprint import pprint
from unittest import TestCase

from tigrisdb.client import TigrisClient
from tigrisdb.errors import TigrisException
from tigrisdb.types.search import Query

from tests import shared_tigris_config


class SearchTestCase(TestCase):
    __client: TigrisClient
    index_name: str = "users"

    def setUp(self) -> None:
        self.__client = TigrisClient(config=shared_tigris_config)

    def test_execute(self):
        search = self.__client.get_search()
        # drop index if exists
        try:
            search.delete_index(self.index_name)
        except Exception as e:
            print(f"no index found, skipping.... {e}")

        schema = {
            "title": "users",
            "additionalProperties": False,
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "balance": {"type": "number"},
            }
        }
        search_index = search.create_or_update_index("users", schema)
        self.assertIsNotNone(search_index)

        # negative test on drop collection
        with self.assertRaises(TigrisException):
            search.delete_index("invalid_name")

        docs = [
            {"id": "1", "name": "Tom", "balance": 3.4},
            {"id": "2", "name": "List", "balance": 1.49},
            {"id": "3", "name": "Jack", "balance": 7.3},
            {"id": "4", "name": "Jenny", "balance": 3.15},
        ]
        # insert documents should succeed
        self.assertTrue(search_index.create_many(docs))

        time.sleep(1)  # wait
        found = search_index.get_many(list(doc["id"] for doc in docs))
        self.assertEqual(len(found), len(docs))
        pprint(found) # console.log

        # finally
        self.assertTrue(search.delete_index(self.index_name))
