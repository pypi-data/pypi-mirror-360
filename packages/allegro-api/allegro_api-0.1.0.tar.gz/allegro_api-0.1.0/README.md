# Allegro API Python

[![PyPI version](https://badge.fury.io/py/allegro-api.svg)](https://badge.fury.io/py/allegro-api)
[![Python versions](https://img.shields.io/pypi/pyversions/allegro-api.svg)](https://pypi.org/project/allegro-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://allegro-api-python.readthedocs.io)

A modern Python client library for the Allegro REST API with 100% API coverage.

## Features

- **100% API Coverage** - All Allegro REST API endpoints implemented
- Full OAuth2 authentication support (device flow, authorization code, client credentials)
- Automatic token refresh
- Type hints for better IDE support
- Comprehensive error handling
- Support for both production and sandbox environments
- Easy-to-use interface for common operations

## Installation

```bash
pip install allegro-api
```

## Quick Start

```python
from allegro_api import AllegroAPI

# Initialize client
api = AllegroAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",  # Optional for device flow
    sandbox=False  # Use True for sandbox environment
)

# Authenticate using device flow
api.authenticate()

# Get current user info
user = api.user.get_me()
print(f"Hello, {user['login']}!")

# Search for offers
results = api.search_offers(
    phrase="laptop",
    category_id="491",
    limit=10
)

for offer in results['offers']:
    print(f"{offer['name']} - {offer['sellingMode']['price']['amount']} PLN")
```

## Authentication

### Device Flow (Recommended for desktop applications)

```python
# Simple authentication - opens browser automatically
api.authenticate()

# Manual authentication - displays URL and code
api.authenticate(open_browser=False)
```

### Authorization Code Flow (For web applications)

```python
# Get authorization URL
auth_url = api.get_authorization_url(state="random_state")
# Redirect user to auth_url

# After user authorization, exchange code for token
api.authenticate(method="code", code="received_authorization_code")
```

### Client Credentials Flow (For server-to-server)

```python
api.authenticate(method="client_credentials")
```

### Using Existing Token

```python
api = AllegroAPI(
    access_token="existing_access_token",
    refresh_token="existing_refresh_token"
)
```

## Working with Offers

### List Your Offers

```python
# Get your active offers
my_offers = api.offers.list(
    publication_status=["ACTIVE"],
    limit=50
)

for offer in my_offers['offers']:
    print(f"{offer['name']} (ID: {offer['id']})")
```

### Create New Offer

```python
# Create offer from product
offer = api.offers.create_from_product(
    product_id="product_id_from_allegro",
    parameters={
        "price": {"amount": "99.99", "currency": "PLN"},
        "stock": {"available": 10},
        "publication": {"status": "ACTIVE"}
    }
)

# Create custom offer
offer_data = {
    "name": "My Product",
    "category": {"id": "491"},
    "parameters": [...],
    "images": [...],
    "sellingMode": {
        "format": "BUY_NOW",
        "price": {"amount": "99.99", "currency": "PLN"}
    },
    "stock": {"available": 10},
    "publication": {"status": "ACTIVE"}
}

offer = api.offers.create(offer_data)
```

### Update Offer

```python
# Update entire offer
updated_offer = api.offers.update(offer_id, updated_data)

# Update specific fields
api.offers.patch(offer_id, [
    {"op": "replace", "path": "/name", "value": "New Name"},
    {"op": "replace", "path": "/stock/available", "value": 5}
])

# Quick price update
api.offers.update_price(offer_id, amount=79.99)

# Quick stock update
api.offers.update_quantity(offer_id, quantity=20)
```

### Manage Offer Publication

```python
# Publish draft offer
api.offers.publish(offer_id)

# Unpublish offer
api.offers.unpublish(offer_id)

# End offer
api.offers.delete(offer_id)
```

## Working with Orders

```python
# List recent orders
orders = api.orders.list(
    status="READY_FOR_PROCESSING",
    limit=20
)

# Get order details
order = api.orders.get(order_id)

# Create shipment
api.orders.create_shipment(
    order_id=order_id,
    carrier_id="ALLEGRO_COURIER",
    carrier_name="Allegro Courier",
    tracking_number="123456789"
)
```

## Categories and Parameters

```python
# Browse categories
root_categories = api.categories.list()
subcategories = api.categories.list(parent_id="491")

# Get category details with parameters
category = api.categories.get("491")
parameters = api.categories.get_parameters("491")

# Search categories
matching = api.categories.search("laptop")
```

## Error Handling

```python
from allegro_api.exceptions import (
    AllegroAPIException,
    AuthenticationError,
    RateLimitError,
    ValidationError
)

try:
    api.offers.create(offer_data)
except ValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Details: {e.response_data}")
except RateLimitError as e:
    print(f"Rate limit hit, retry after {e.retry_after} seconds")
except AuthenticationError:
    # Token might be expired, try refreshing
    api.refresh_access_token()
except AllegroAPIException as e:
    print(f"API error: {e}")
```

## Advanced Usage

### Custom Request Configuration

```python
# Configure timeouts and retries
api = AllegroAPI(
    client_id="your_client_id",
    timeout=60,  # Request timeout in seconds
    max_retries=5,  # Maximum retry attempts
    backoff_factor=0.5  # Retry backoff factor
)
```

### Pagination

```python
# Manual pagination
all_offers = []
offset = 0
limit = 100

while True:
    response = api.offers.list(limit=limit, offset=offset)
    offers = response['offers']
    
    if not offers:
        break
        
    all_offers.extend(offers)
    offset += len(offers)
    
    if len(offers) < limit:
        break
```

### Batch Operations

```python
# Batch update multiple offers
operations = [
    {
        "offer": {"id": "offer1_id"},
        "modification": {
            "changeType": "PRICE",
            "price": {"amount": "99.99", "currency": "PLN"}
        }
    },
    {
        "offer": {"id": "offer2_id"},
        "modification": {
            "changeType": "QUANTITY",
            "quantity": {"available": 5}
        }
    }
]

result = api.offers.batch_update(operations)
command_id = result['id']

# Check batch status
status = api.offers.get_batch_status(command_id)
```

## Environment Variables

You can use environment variables for configuration:

```bash
export ALLEGRO_CLIENT_ID=your_client_id
export ALLEGRO_CLIENT_SECRET=your_client_secret
export ALLEGRO_SANDBOX=false
```

```python
import os
from allegro_api import AllegroAPI

api = AllegroAPI(
    client_id=os.getenv('ALLEGRO_CLIENT_ID'),
    client_secret=os.getenv('ALLEGRO_CLIENT_SECRET'),
    sandbox=os.getenv('ALLEGRO_SANDBOX', 'false').lower() == 'true'
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Resources

- [Official Allegro API Documentation](https://developer.allegro.pl/)
- [Library Documentation](https://allegro-api-python.readthedocs.io)
- [PyPI Package](https://pypi.org/project/allegro-api/)
- [GitHub Repository](https://github.com/yourusername/allegro-api-python)
- [Changelog](CHANGELOG.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## Support

For API-related issues, please check the [official Allegro API documentation](https://developer.allegro.pl/).

For library-specific issues, please [open an issue on GitHub](https://github.com/yourusername/allegro-api-python/issues).

## Author

Created and maintained by Marek Sybilak (marek.sybilak@neogento.com)