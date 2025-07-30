# afrigis_search_client/request_authenticator.py
class RequestAuthenticator:
    def __init__(self, api_key: str, token_manager):
        self.api_key = api_key
        self.token_manager = token_manager

    async def get_headers(self):
        token = await self.token_manager.get_token()
        return {
            "x-api-key": self.api_key,
            "Authorization": f"Bearer {token}"
        }
