# src/afrigis_search_client/__init__.py

from .geocode import Geocode
from .token_manager import TokenManager
from .request_authenticator import RequestAuthenticator
from .autocomplete import Autocomplete
from .details import Details
from .delivery import Delivery

class AfrigisSearchClient:
    def __init__(self, client_id: str, client_secret: str, api_key: str):
        self._token_manager = TokenManager(client_id, client_secret)
        self._authenticator = RequestAuthenticator(api_key, self._token_manager)
        self.geocode = Geocode(self._authenticator)
        self.autocomplete = Autocomplete(self._authenticator)
        self.details = Details(self._authenticator)
        self.delivery = Delivery(self._authenticator)
