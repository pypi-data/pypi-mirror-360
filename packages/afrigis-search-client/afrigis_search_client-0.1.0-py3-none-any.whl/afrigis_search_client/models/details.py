from typing import Optional, List
from pydantic import BaseModel

class AddressComponent(BaseModel):
    long_name: str
    short_name: str
    types: Optional[List[str]]

class DetailsResult(BaseModel):
    place_id: str
    seoid: str
    sfid: str
    address_components: Optional[List[AddressComponent]]
    formatted_address: str
    confidence: Optional[dict]
    location: Optional[dict]
    name: Optional[str]
    types: Optional[List[str]]
    country: Optional[str]
    lifecyclestage: Optional[str]

class DetailsResponse(BaseModel):
    result: DetailsResult
    code: int
    message: Optional[str]
    source: Optional[str]
