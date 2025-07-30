import aiohttp
from typing import Optional
from dataclasses import dataclass

@dataclass
class TokenResponse:
    access_token: str
    expires_in: int

class TokenAcquisitionError(Exception):
    pass

class TokenAcquisitionService:
    def __init__(self, url: str, client_id: str, client_secret: str):
        if not url:
            raise ValueError("url must be provided")
        if not client_id:
            raise ValueError("client_id must be provided")
        if not client_secret or not str(client_secret).strip():
            raise ValueError("client_secret must be provided")
        self._url = url
        self._client_id = client_id
        self._client_secret = client_secret

    async def get_token(self) -> TokenResponse:
        data = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        async with aiohttp.ClientSession(base_url=self._url) as session:
            async with session.post("/oauth2/token", data=data) as resp:
                if resp.status != 200:
                    raise TokenAcquisitionError(f"Failed to acquire token: {resp.status}")
                result = await resp.json()
                access_token = result.get("access_token")
                expires_in = result.get("expires_in")
                if not access_token:
                    raise TokenAcquisitionError("No access_token in response")
                return TokenResponse(access_token=access_token, expires_in=expires_in)
