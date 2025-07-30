import os
import pytest
import asyncio
from afrigis_search_client import AfrigisSearchClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../integration_tests/.env"))

API_KEY = os.getenv("AFRIGIS_API_KEY")
CLIENT_ID = os.getenv("AFRIGIS_CLIENT_ID")
CLIENT_SECRET = os.getenv("AFRIGIS_CLIENT_SECRET")

@pytest.mark.asyncio
@pytest.mark.integration
async def test_geocode_v3_integration():
    """
    Integration test for geocode_address using real API key and token.
    """
    if not (API_KEY and CLIENT_ID and CLIENT_SECRET):
        pytest.skip("Integration credentials not set in environment variables.")
    client = AfrigisSearchClient(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, api_key=API_KEY)
    result = await client.geocode.v3.geocode_address(query="446 Rigel Avenue South, Pretoria")
    assert result.number_of_records > 0
    assert result.result[0].formatted_address
    print(f"[DEBUG] Geocode result: {result.result[0].formatted_address}")
