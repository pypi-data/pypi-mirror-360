# AfriGIS Python Search Client

## Overview
AfriGIS Python Search Client is a modern, async Python SDK for seamless integration with the AfriGIS Search suite of APIs. It provides robust, versioned, and strongly-typed access to [Autocomplete](https://developers.afrigis.co.za/portfolio/autocomplete/), [Geocode](https://developers.afrigis.co.za/portfolio/search/), [Place Details](https://developers.afrigis.co.za/portfolio/place-details/), and [Delivery Address Format](https://developers.afrigis.co.za/portfolio/delivery-address-format/) APIs, handling authentication, request formatting, and error mapping for you.

- Token-based authentication (OAuth2)
- API key support
- Strongly-typed request/response models (Pydantic)
- Async API for scalable apps
- Comprehensive error handling
- Thread/async-safe and production-ready
- Versioned endpoints for future compatibility

## Installation
Install via pip (after building or from PyPI):

```pwsh
pip install afrigis-search-client
```

## Configuration
You can provide credentials via environment variables, .env file, or directly as parameters. Example `.env`:

```
AFRIGIS_AUTH_URL=https://auth.afrigis.services
AFRIGIS_CLIENT_ID=your-client-id
AFRIGIS_CLIENT_SECRET=your-client-secret
AFRIGIS_API_KEY=your-api-key
```

## Client Initialization
```python
from afrigis_search_client import AfrigisSearchClient
import os

client = AfrigisSearchClient(
    client_id=os.getenv("AFRIGIS_CLIENT_ID"),
    client_secret=os.getenv("AFRIGIS_CLIENT_SECRET"),
    api_key=os.getenv("AFRIGIS_API_KEY")
)
```

## Usage Examples
All endpoints are async and raise exceptions for error conditions. See below for details on which exceptions are raised and when.

### Autocomplete
```python
result = await client.autocomplete.v3.autocomplete(query="446 Rigel", max_results=5)
for suggestion in result.result:
    print(f"{suggestion.description} ({suggestion.country})")
```

### Geocoding
```python
result = await client.geocode.v3.geocode_address(query="446 Rigel Avenue South, Erasmusrand", max_results=5)
for address in result.result:
    print(f"{address.formatted_address} - {address.location}")
```

### Place Details
```python
result = await client.details.v3.get_details(reference="2XIAs5De9f_eEXNFubwV-ZXI41F281017")
print(result.result.formatted_address)
print(result.result.location)
```

### Delivery Address Lookup
```python
result = await client.delivery.v1.get_delivery(reference="2XIAs5De9f_eEXNFubwV-ZXI41F281017")
print(result.result.formatted_address)
print(result.result.delivery)
```

### Autocomplete/Geocode with IncludeTypes/ExcludeTypes
```python
result = await client.autocomplete.v3.autocomplete(
    query="446 Rigel",
    max_results=5,
    include_types=["street_address_level_1", "locality"],
    exclude_types=["administrative_area_level_1"]
)
```

## Exception Handling
All endpoints raise exceptions for error conditions:
- `ValueError`: For invalid input (e.g., empty query)
- `Exception`: For API errors, network errors, or response validation errors

## Thread Safety & Token Management
- The client is async/thread-safe and manages authentication tokens automatically.
- Tokens are refreshed as needed; you do not need to handle this yourself.

## API Reference
- [Autocomplete v3](https://developers.afrigis.co.za/portfolio/autocomplete/)
- [Geocode v3](https://developers.afrigis.co.za/portfolio/search/)
- [Place Details v3](https://developers.afrigis.co.za/portfolio/place-details/)
- [Delivery Address Format v1](https://developers.afrigis.co.za/portfolio/delivery-address-format/)

## Support & Further Resources
- Contact [AfriGIS](https://www.afrigis.co.za/) for production support and API documentation
