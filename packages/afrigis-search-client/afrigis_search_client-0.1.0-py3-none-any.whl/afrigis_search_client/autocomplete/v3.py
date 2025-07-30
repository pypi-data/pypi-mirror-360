from typing import Optional, List
from pydantic import ValidationError
import aiohttp
from ..models.autocomplete import AutocompleteResponse
from ..endpoints import AutocompleteEndpoints

class AutocompleteV3:
    """
    Async client for Afrigis Autocomplete v3 API.
    Parameters:
        - query (str): The textual search term to be used for predictions (required)
        - max_results (Optional[int]): The maximum number of predictions (1-20, default 5)
        - include_types (Optional[List[str]]): Types of place results to return
        - exclude_types (Optional[List[str]]): Types of place results to exclude
    Returns:
        AutocompleteResponse: Pydantic model matching all documented response fields
    Raises:
        ValueError: For invalid input
        Exception: For API or validation errors
    """
    def __init__(self, authenticator):
        self.authenticator = authenticator
        self.endpoint = AutocompleteEndpoints.v3

    async def autocomplete(
        self,
        query: str,
        max_results: Optional[int] = None,
        include_types: Optional[List[str]] = None,
        exclude_types: Optional[List[str]] = None
    ) -> AutocompleteResponse:
        if not query or not query.strip():
            raise ValueError("Query must not be empty.")
        if max_results is not None and (max_results < 1 or max_results > 20):
            raise ValueError("max_results must be between 1 and 20.")
        params = {"query": query}
        if max_results is not None:
            params["max_results"] = max_results
        if include_types is not None:
            params["include_types"] = include_types
        if exclude_types is not None:
            params["exclude_types"] = exclude_types
        headers = await self.authenticator.get_headers()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.endpoint, params=params, headers=headers) as resp:
                data = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Autocomplete API error: {resp.status} {data}")
                try:
                    return AutocompleteResponse(**data)
                except ValidationError as e:
                    raise Exception(f"Response validation error: {e}")
