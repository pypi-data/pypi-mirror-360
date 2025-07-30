# afrigis_search_client/geocode/__init__.py
from .v3 import GeocodeV3

class Geocode:
    def __init__(self, authenticator):
        self.v3 = GeocodeV3(authenticator)
        # self.v4 = GeocodeV4(authenticator)  # For future versioning
