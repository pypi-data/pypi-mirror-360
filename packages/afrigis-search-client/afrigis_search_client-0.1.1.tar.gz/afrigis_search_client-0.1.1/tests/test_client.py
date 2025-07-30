import unittest
from afrigis_search_client import AfrigisSearchClient

class TestAfrigisSearchClient(unittest.TestCase):
    def test_init(self):
        # Provide dummy credentials for unit test
        client = AfrigisSearchClient(
            client_id="dummy_id",
            client_secret="dummy_secret",
            api_key="dummy_api_key"
        )
        self.assertIsInstance(client, AfrigisSearchClient)

if __name__ == "__main__":
    unittest.main()
