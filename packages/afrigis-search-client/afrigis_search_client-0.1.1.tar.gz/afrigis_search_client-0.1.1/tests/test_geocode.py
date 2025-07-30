import pytest
from unittest.mock import AsyncMock
from afrigis_search_client import AfrigisSearchClient

@pytest.mark.asyncio
async def test_geocode_v3_success(monkeypatch):
    class DummyResponse:
        status = 200
        async def json(self):
            return {
                "number_of_records": 1,
                "result": [
                    {
                        "place_id": "abc123",
                        "seoid": "abc123",
                        "sfid": "xyz789",
                        "formatted_address": "123 Main St, City, Country",
                        "confidence": {"confidence_id": 1, "description": "High"},
                        "location": {"lat": -25.0, "lng": 28.0},
                        "types": ["street_address_level_1"],
                        "country": "South Africa"
                    }
                ],
                "code": 200,
                "message": "OK",
                "source": "geocode.api-address"
            }
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    class DummySession:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        def get(self, url, params=None, headers=None):
            return DummyResponse()
    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **kw: DummySession())
    client = AfrigisSearchClient(client_id="id", client_secret="secret", api_key="dummy")
    # Patch token manager to avoid real token acquisition
    client._token_manager.get_token = AsyncMock(return_value="token123")
    result = await client.geocode.v3.geocode_address(query="123 Main St")
    assert result.number_of_records == 1
    assert result.result[0].formatted_address == "123 Main St, City, Country"

@pytest.mark.asyncio
async def test_geocode_v3_error(monkeypatch):
    class DummyResponse:
        status = 400
        async def json(self):
            return {"error": "Bad request"}
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    class DummySession:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        def get(self, url, params=None, headers=None):
            return DummyResponse()
    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **kw: DummySession())
    client = AfrigisSearchClient(client_id="id", client_secret="secret", api_key="dummy")
    client._token_manager.get_token = AsyncMock(return_value="token123")
    with pytest.raises(Exception):
        await client.geocode.v3.geocode_address(query="123 Main St")

@pytest.mark.asyncio
async def test_geocode_v3_edge_cases(monkeypatch):
    class DummyResponse:
        status = 200
        async def json(self):
            return {
                "number_of_records": 1,
                "result": [
                    {
                        "place_id": "abc123",
                        "seoid": "abc123",
                        "sfid": "xyz789",
                        "formatted_address": "Edge Case Address",
                        "confidence": {"confidence_id": 1, "description": "High"},
                        "location": {"lat": -90.0, "lng": 180.0},
                        "types": ["street_address_level_1"],
                        "country": "South Africa"
                    }
                ],
                "code": 200,
                "message": "OK",
                "source": "geocode.api-address"
            }
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    class DummySession:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        def get(self, url, params=None, headers=None):
            return DummyResponse()
    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **kw: DummySession())
    client = AfrigisSearchClient(client_id="id", client_secret="secret", api_key="dummy")
    client._token_manager.get_token = AsyncMock(return_value="token123")
    # Special characters
    await client.geocode.v3.geocode_address(query="!@#$%^&*()_+-=[]{}|;':,.<>/?")
    # Unicode
    await client.geocode.v3.geocode_address(query="東京タワー, Москва, München, القاهرة")
    # Very long string
    await client.geocode.v3.geocode_address(query="A"*1000)
    # Edge coordinates (simulate in result)
    result = await client.geocode.v3.geocode_address(query="-90,180")
    assert result.result[0].location.lat == -90.0
    assert result.result[0].location.lng == 180.0
