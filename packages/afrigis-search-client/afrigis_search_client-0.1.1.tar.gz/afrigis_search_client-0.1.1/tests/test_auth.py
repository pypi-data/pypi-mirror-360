import pytest
import asyncio
from afrigis_search_client.auth import TokenAcquisitionService, TokenAcquisitionError
from unittest.mock import AsyncMock
from afrigis_search_client import AfrigisSearchClient
from afrigis_search_client.token_manager import TokenManager

class DummyResponse:
    def __init__(self, status, json_data):
        self.status = status
        self._json = json_data
    async def json(self):
        return self._json
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass

class DummySession:
    def __init__(self, base_url):
        self.base_url = base_url
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    def post(self, url, data):
        if data["client_id"] == "valid" and data["client_secret"] == "valid":
            return DummyResponse(200, {"access_token": "token123", "expires_in": 3600})
        return DummyResponse(400, {})

@pytest.mark.asyncio
async def test_token_acquisition_success(monkeypatch):
    service = TokenAcquisitionService(
        url="https://api.example.com",
        client_id="valid",
        client_secret="valid"
    )
    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **kw: DummySession(service._url))
    token = await service.get_token()
    assert token.access_token == "token123"
    assert token.expires_in == 3600

@pytest.mark.asyncio
async def test_token_acquisition_failure(monkeypatch):
    service = TokenAcquisitionService(
        url="https://api.example.com",
        client_id="bad",
        client_secret="bad"
    )
    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **kw: DummySession(service._url))
    with pytest.raises(TokenAcquisitionError):
        await service.get_token()

@pytest.mark.asyncio
async def test_token_acquisition_missing_url():
    with pytest.raises(ValueError):
        TokenAcquisitionService(url="", client_id="id", client_secret="secret")

@pytest.mark.asyncio
async def test_token_acquisition_missing_client_id():
    with pytest.raises(ValueError):
        TokenAcquisitionService(url="url", client_id="", client_secret="secret")

@pytest.mark.asyncio
async def test_token_acquisition_missing_client_secret():
    with pytest.raises(ValueError):
        TokenAcquisitionService(url="url", client_id="id", client_secret="")

@pytest.mark.asyncio
async def test_token_acquisition_whitespace_client_secret():
    with pytest.raises(ValueError):
        TokenAcquisitionService(url="url", client_id="id", client_secret="   ")

@pytest.mark.asyncio
async def test_token_manager_refresh(monkeypatch):
    class DummyTokenService:
        def __init__(self):
            self.calls = 0
        async def get_token(self):
            self.calls += 1
            return type('Token', (), {"access_token": f"token{self.calls}", "expires_in": 1})()  # expires in 1s
    tm = TokenManager("id", "secret")
    tm._service = DummyTokenService()
    # First call, should fetch token
    token1 = await tm.get_token()
    await asyncio.sleep(1.1)  # Wait for expiry
    # Second call, should refresh
    token2 = await tm.get_token()
    assert token1 != token2
    assert tm._service.calls >= 2

@pytest.mark.asyncio
async def test_token_manager_concurrent(monkeypatch):
    class DummyTokenService:
        def __init__(self):
            self.calls = 0
        async def get_token(self):
            self.calls += 1
            await asyncio.sleep(0.1)
            return type('Token', (), {"access_token": "token123", "expires_in": 60})()
    tm = TokenManager("id", "secret")
    tm._service = DummyTokenService()
    # Many concurrent requests using the threadsafe method
    tokens = await asyncio.gather(*[tm.get_token_threadsafe() for _ in range(10)])
    assert all(t == "token123" for t in tokens)
    assert tm._service.calls == 1
