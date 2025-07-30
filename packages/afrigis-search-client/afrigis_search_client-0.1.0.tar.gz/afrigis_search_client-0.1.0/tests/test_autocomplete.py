import pytest
from unittest.mock import AsyncMock
from afrigis_search_client import AfrigisSearchClient

@pytest.mark.asyncio
async def test_autocomplete_v3_success(monkeypatch):
    class DummyResponse:
        status = 200
        async def json(self):
            return {
                "result": [
                    {
                        "place_id": "abc123",
                        "seoid": "abc123",
                        "sfid": "xyz789",
                        "description": "123 Main St, City, Country",
                        "title": "123 Main St",
                        "types": ["street_address_level_1"],
                        "country": "South Africa"
                    }
                ],
                "code": 200,
                "message": "OK",
                "source": "autocomplete.api"
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
    # Minimal
    result = await client.autocomplete.v3.autocomplete(query="123 Main St")
    assert result.code == 200
    assert result.result[0].description == "123 Main St, City, Country"
    # All params
    result = await client.autocomplete.v3.autocomplete(
        query="123 Main St",
        max_results=5,
        include_types=["street_address_level_1"],
        exclude_types=["premise_level_1"]
    )
    assert result.code == 200
    assert result.result[0].types == ["street_address_level_1"]

@pytest.mark.asyncio
async def test_autocomplete_v3_invalid_query(monkeypatch):
    client = AfrigisSearchClient(client_id="id", client_secret="secret", api_key="dummy")
    client._token_manager.get_token = AsyncMock(return_value="token123")
    with pytest.raises(ValueError):
        await client.autocomplete.v3.autocomplete(query=" ")
    with pytest.raises(ValueError):
        await client.autocomplete.v3.autocomplete(query=None)

@pytest.mark.asyncio
async def test_autocomplete_v3_invalid_max_results(monkeypatch):
    client = AfrigisSearchClient(client_id="id", client_secret="secret", api_key="dummy")
    client._token_manager.get_token = AsyncMock(return_value="token123")
    with pytest.raises(ValueError):
        await client.autocomplete.v3.autocomplete(query="Pretoria", max_results=0)
    with pytest.raises(ValueError):
        await client.autocomplete.v3.autocomplete(query="Pretoria", max_results=21)

@pytest.mark.asyncio
async def test_autocomplete_v3_include_types(monkeypatch):
    class DummyResponse:
        status = 200
        async def json(self):
            return {
                "result": [
                    {
                        "place_id": "abc123",
                        "seoid": "abc123",
                        "sfid": "xyz789",
                        "description": "123 Main St, City, Country",
                        "title": "123 Main St",
                        "types": ["street_address_level_1"],
                        "country": "South Africa"
                    }
                ],
                "code": 200,
                "message": "OK",
                "source": "autocomplete.api"
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
    result = await client.autocomplete.v3.autocomplete(query="123 Main St", include_types=["street_address_level_1"])
    assert result.result[0].types == ["street_address_level_1"]

@pytest.mark.asyncio
async def test_autocomplete_v3_exclude_types(monkeypatch):
    class DummyResponse:
        status = 200
        async def json(self):
            return {
                "result": [
                    {
                        "place_id": "abc123",
                        "seoid": "abc123",
                        "sfid": "xyz789",
                        "description": "123 Main St, City, Country",
                        "title": "123 Main St",
                        "types": ["premise_level_1"],
                        "country": "South Africa"
                    }
                ],
                "code": 200,
                "message": "OK",
                "source": "autocomplete.api"
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
    result = await client.autocomplete.v3.autocomplete(query="123 Main St", exclude_types=["premise_level_1"])
    assert result.result[0].types == ["premise_level_1"]

@pytest.mark.asyncio
async def test_autocomplete_v3_auth_error(monkeypatch):
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
        await client.autocomplete.v3.autocomplete(query="123 Main St")

@pytest.mark.asyncio
async def test_autocomplete_v3_edge_cases(monkeypatch):
    class DummyResponse:
        status = 200
        async def json(self):
            return {
                "result": [
                    {
                        "place_id": "abc123",
                        "seoid": "abc123",
                        "sfid": "xyz789",
                        "description": "Edge Case Result",
                        "title": "Edge Case",
                        "types": ["street_address_level_1"],
                        "country": "South Africa"
                    }
                ],
                "code": 200,
                "message": "OK",
                "source": "autocomplete.api"
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
    result = await client.autocomplete.v3.autocomplete(query="!@#$%^&*()_+-=[]{}|;':,.<>/?")
    assert result.code == 200
    # Unicode
    result = await client.autocomplete.v3.autocomplete(query="東京タワー, Москва, München, القاهرة")
    assert result.code == 200
    # Very long string
    result = await client.autocomplete.v3.autocomplete(query="A"*1000)
    assert result.code == 200
