from typing import Optional
from pydantic import ValidationError
import aiohttp
from ..models.details import DetailsResponse
from ..endpoints import DetailsEndpoints

class DetailsV3:
    """
    Async client for Afrigis Details v3 API.
    Parameters:
        - reference (str): The reference identifier (seoid or place_id) (required)
    Returns:
        DetailsResponse: Pydantic model matching all documented response fields
    Raises:
        ValueError: For invalid input
        Exception: For API or validation errors
    """
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.endpoint = DetailsEndpoints.v3

    async def get_details(self, reference: str) -> DetailsResponse:
        if not reference or not reference.strip():
            raise ValueError("Reference must not be empty.")
        params = {"reference": reference}
        headers = await self.authenticator.get_headers()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.endpoint, params=params, headers=headers) as resp:
                data = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Details API error: {resp.status} {data}")
                try:
                    return DetailsResponse(**data)
                except ValidationError as e:
                    raise Exception(f"Response validation error: {e}")
