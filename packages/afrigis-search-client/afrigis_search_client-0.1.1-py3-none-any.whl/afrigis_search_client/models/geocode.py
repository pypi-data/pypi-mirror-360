# afrigis_search_client/models/geocode.py
from typing import List, Optional
from pydantic import BaseModel

class Confidence(BaseModel):
    confidence_id: int
    description: str

class Location(BaseModel):
    lat: float
    lng: float

class Address(BaseModel):
    place_id: str
    seoid: str
    sfid: str
    formatted_address: str
    confidence: Confidence
    location: Location
    types: List[str]
    country: str

class GeocodeResponse(BaseModel):
    number_of_records: int
    result: List[Address]
    code: int
    message: str
    source: str
