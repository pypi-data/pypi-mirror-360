from typing import Optional
from pydantic import BaseModel

class StructuredAddress(BaseModel):
    address_line_1: Optional[str]
    address_line_2: Optional[str]
    address_line_3: Optional[str]
    address_line_4: Optional[str]
    address_line_5: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]

class DeliveryResult(BaseModel):
    place_id: str
    seoid: str
    sfid: str
    delivery: StructuredAddress
    formatted_address: str
    confidence: Optional[dict]
    location: Optional[dict]
    types: Optional[list]
    country: Optional[str] = None  # Default to None
    lifecyclestage: Optional[str]

class DeliveryResponse(BaseModel):
    result: DeliveryResult
    code: int
    message: Optional[str]
    source: Optional[str]
