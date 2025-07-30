# afrigis_search_client/token_manager.py
import asyncio
import time
from .auth import TokenAcquisitionService
from .endpoints import AUTH_URL

class TokenManager:
    def __init__(self, client_id: str, client_secret: str):
        self._service = TokenAcquisitionService(
            url=AUTH_URL,
            client_id=client_id,
            client_secret=client_secret
        )
        self._token = None
        self._expires_at = 0  # epoch seconds
        self._lock = asyncio.Lock()

    async def get_token(self):
        async with self._lock:
            now = time.time()
            # Refresh if no token or token expires in <60s
            if not self._token or now >= self._expires_at - 60:
                token_response = await self._service.get_token()
                self._token = token_response.access_token
                self._expires_at = now + int(token_response.expires_in)
                self._refreshing = False
            return self._token

    async def get_token_threadsafe(self):
        # This method ensures only one token fetch for concurrent requests
        if not hasattr(self, '_refreshing'):
            self._refreshing = False
        if self._refreshing:
            # Wait for the lock to be released by the refresher
            async with self._lock:
                return self._token
        async with self._lock:
            now = time.time()
            if not self._token or now >= self._expires_at - 60:
                self._refreshing = True
                token_response = await self._service.get_token()
                self._token = token_response.access_token
                self._expires_at = now + int(token_response.expires_in)
                self._refreshing = False
            return self._token
