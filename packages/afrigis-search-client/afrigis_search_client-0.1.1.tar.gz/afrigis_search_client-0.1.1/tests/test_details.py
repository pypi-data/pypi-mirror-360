import pytest
from unittest.mock import AsyncMock
from afrigis_search_client import AfrigisSearchClient

@pytest.mark.asyncio
async def test_details_v3_success(monkeypatch):
    class DummyResponse:
        status = 200
        async def json(self):
            return {
                "result": {
                    "place_id": "abc123",
                    "seoid": "abc123",
                    "sfid": "xyz789",
                    "address_components": [],
                    "formatted_address": "123 Main St, City, Country",
                    "confidence": {},
                    "location": {},
                    "name": "Test Place",
                    "types": ["street_address_level_1"],
                    "country": "South Africa",
                    "lifecyclestage": "Active"
                },
                "code": 200,
                "message": "OK",
                "source": "details.api"
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
    result = await client.details.v3.get_details(reference="abc123")
    assert result.code == 200
    assert result.result.place_id == "abc123"
    assert result.result.formatted_address == "123 Main St, City, Country"

@pytest.mark.asyncio
async def test_details_v3_invalid_reference(monkeypatch):
    client = AfrigisSearchClient(client_id="id", client_secret="secret", api_key="dummy")
    client._token_manager.get_token = AsyncMock(return_value="token123")
    with pytest.raises(ValueError):
        await client.details.v3.get_details(reference=" ")
    with pytest.raises(ValueError):
        await client.details.v3.get_details(reference=None)

@pytest.mark.asyncio
async def test_details_v3_auth_error(monkeypatch):
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
        await client.details.v3.get_details(reference="abc123")
