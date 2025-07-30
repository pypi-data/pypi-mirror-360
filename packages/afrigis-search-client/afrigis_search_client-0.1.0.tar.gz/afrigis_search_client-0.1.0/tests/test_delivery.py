import pytest
from unittest.mock import AsyncMock
from afrigis_search_client import AfrigisSearchClient

@pytest.mark.asyncio
async def test_delivery_v1_success(monkeypatch):
    class DummyResponse:
        status = 200
        async def json(self):
            return {
                "result": {
                    "place_id": "abc123",
                    "seoid": "abc123",
                    "sfid": "xyz789",
                    "delivery": {
                        "address_line_1": "123 Main St",
                        "address_line_2": None,
                        "address_line_3": "Suburb",
                        "address_line_4": "City",
                        "address_line_5": "Province",
                        "country": "South Africa",
                        "postal_code": "0001"
                    },
                    "formatted_address": "123 Main St, City, Province, 0001",
                    "confidence": {},
                    "location": {},
                    "types": ["street_address_level_1"],
                    "country": "South Africa",
                    "lifecyclestage": "Active"
                },
                "code": 200,
                "message": "OK",
                "source": "delivery.api"
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
    result = await client.delivery.v1.get_delivery(reference="abc123")
    assert result.code == 200
    assert result.result.place_id == "abc123"
    assert result.result.delivery.address_line_1 == "123 Main St"

@pytest.mark.asyncio
async def test_delivery_v1_invalid_reference(monkeypatch):
    client = AfrigisSearchClient(client_id="id", client_secret="secret", api_key="dummy")
    client._token_manager.get_token = AsyncMock(return_value="token123")
    with pytest.raises(ValueError):
        await client.delivery.v1.get_delivery(reference=" ")
    with pytest.raises(ValueError):
        await client.delivery.v1.get_delivery(reference=None)

@pytest.mark.asyncio
async def test_delivery_v1_auth_error(monkeypatch):
    class DummyResponse:
        status = 403
        async def json(self):
            return {"error": "Unauthorized"}
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    class DummySession:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        def get(self, url, params=None, headers=None):
            return DummyResponse()
    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **kw: DummySession())
    client = AfrigisSearchClient(client_id="id", client_secret="secret", api_key="badkey")
    client._token_manager.get_token = AsyncMock(return_value="token123")
    with pytest.raises(Exception):
        await client.delivery.v1.get_delivery(reference="abc123")
