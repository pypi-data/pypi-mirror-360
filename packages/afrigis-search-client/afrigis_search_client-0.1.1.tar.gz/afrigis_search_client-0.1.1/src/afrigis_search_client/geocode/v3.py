# afrigis_search_client/geocode/v3.py
from typing import Optional, List
from pydantic import ValidationError
import aiohttp
from ..models.geocode import GeocodeResponse
from ..endpoints import GeocodeEndpoints

class GeocodeV3:
    """
    Async client for Afrigis Geocode v3 API.
    Parameters:
        - query (str): The textual address to be used for geocoding (required)
        - max_results (Optional[int]): The maximum number of results to match (reserved for future, default 10)
        - include_types (Optional[List[str]]): Types of address results to return (reserved for future)
    Returns:
        GeocodeResponse: Pydantic model matching all documented response fields
    Raises:
        ValueError: For invalid input
        Exception: For API or validation errors
    """
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.endpoint = GeocodeEndpoints.v3

    async def geocode_address(
        self,
        query: str,
        max_results: Optional[int] = None,
        include_types: Optional[List[str]] = None
    ) -> GeocodeResponse:
        if not query or not query.strip():
            raise ValueError("Query must not be empty.")
        if max_results is not None and max_results < 1:
            raise ValueError("max_results must be at least 1.")
        params = {"query": query}
        if max_results is not None:
            params["max_results"] = max_results
        if include_types is not None:
            params["include_types"] = include_types
        headers = await self.authenticator.get_headers()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.endpoint, params=params, headers=headers) as resp:
                data = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Geocode API error: {resp.status} {data}")
                try:
                    # Ensure all documented response fields are present
                    # number_of_records, result, code, message, source
                    return GeocodeResponse(**data)
                except ValidationError as e:
                    raise Exception(f"Response validation error: {e}")
