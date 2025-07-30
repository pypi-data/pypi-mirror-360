from typing import List, Optional
from pydantic import BaseModel

class AutocompleteResult(BaseModel):
    place_id: str
    seoid: str
    sfid: str
    description: str
    title: Optional[str]
    types: Optional[List[str]]
    country: Optional[str]

class AutocompleteResponse(BaseModel):
    result: List[AutocompleteResult]
    code: int
    message: Optional[str]
    source: Optional[str]
