# afrigis_search_client/endpoints.py

# Centralized endpoint and AUTH_URL management

# Base URL for authentication (OAuth2)
AUTH_URL = "https://auth.afrigis.services/"

GEOCODE_BASE_URL = "https://Afrigis.services/geocode"
AUTOCOMPLETE_BASE_URL = "https://Afrigis.services/places-autocomplete"
DETAILS_BASE_URL = "https://Afrigis.services/places-details"
DELIVERY_BASE_URL = "https://Afrigis.services/places-delivery"

class GeocodeEndpoints:
    v3 = f"{GEOCODE_BASE_URL}/api/v3/address"
    # v4 = f"{GEOCODE_BASE_URL}/api/v4/address"  # Example for future version

class AutocompleteEndpoints:
    v3 = f"{AUTOCOMPLETE_BASE_URL}/api/v3/autocomplete"

class DetailsEndpoints:
    v3 = f"{DETAILS_BASE_URL}/api/v3/details"

class DeliveryEndpoints:
    v1 = f"{DELIVERY_BASE_URL}/api/v1/delivery"
