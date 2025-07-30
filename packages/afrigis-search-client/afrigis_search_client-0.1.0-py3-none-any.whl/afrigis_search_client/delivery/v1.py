from typing import Optional
from pydantic import ValidationError
import aiohttp
from ..models.delivery import DeliveryResponse
from ..endpoints import DeliveryEndpoints

class DeliveryV1:
    """
    Async client for Afrigis Delivery v1 API.
    Parameters:
        - reference (str): The reference identifier (seoid or place_id) (required)
    Returns:
        DeliveryResponse: Pydantic model matching all documented response fields
    Raises:
        ValueError: For invalid input
        Exception: For API or validation errors
    """
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.endpoint = DeliveryEndpoints.v1

    async def get_delivery(self, reference: str) -> DeliveryResponse:
        if not reference or not reference.strip():
            raise ValueError("Reference must not be empty.")
        params = {"reference": reference}
        headers = await self.authenticator.get_headers()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.endpoint, params=params, headers=headers) as resp:
                data = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Delivery API error: {resp.status} {data}")
                try:
                    return DeliveryResponse(**data)
                except ValidationError as e:
                    raise Exception(f"Response validation error: {e}")
