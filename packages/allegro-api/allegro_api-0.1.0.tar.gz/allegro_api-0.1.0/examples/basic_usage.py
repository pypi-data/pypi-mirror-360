"""
Basic usage examples for Allegro API Python library.
"""

import os
from allegro_api import AllegroAPI
from allegro_api.exceptions import AllegroAPIException, RateLimitError


def main():
    # Initialize API client
    # You can set these as environment variables or pass directly
    api = AllegroAPI(
        client_id=os.getenv("ALLEGRO_CLIENT_ID"),
        client_secret=os.getenv("ALLEGRO_CLIENT_SECRET"),
        sandbox=True  # Use sandbox for testing
    )
    
    try:
        # Authenticate using device flow
        print("Starting authentication...")
        api.authenticate()
        print("Authentication successful!")
        
        # Get user information
        user = api.user.get_me()
        print(f"\nLogged in as: {user['login']}")
        print(f"Company: {user.get('company', {}).get('name', 'N/A')}")
        
        # Search for offers
        print("\n--- Searching for laptops ---")
        search_results = api.search_offers(
            phrase="laptop",
            limit=5,
            sort="-withDeliveryPrice"  # Sort by price descending
        )
        
        for offer in search_results.get('offers', []):
            price = offer['sellingMode']['price']['amount']
            print(f"- {offer['name'][:50]}... - {price} PLN")
        
        # Get categories
        print("\n--- Top categories ---")
        categories = api.categories.list()
        for category in categories.get('categories', [])[:5]:
            print(f"- {category['name']} (ID: {category['id']})")
        
        # List user's offers (if any)
        print("\n--- Your offers ---")
        my_offers = api.offers.list(limit=5)
        
        if my_offers.get('offers'):
            for offer in my_offers['offers']:
                status = offer['publication']['status']
                print(f"- {offer['name']} (Status: {status})")
        else:
            print("No offers found")
        
        # Get user's active orders
        print("\n--- Recent orders ---")
        orders = api.orders.list(
            status="READY_FOR_PROCESSING",
            limit=5
        )
        
        if orders.get('checkoutForms'):
            for order in orders['checkoutForms']:
                buyer = order['buyer']['login']
                total = order['summary']['totalToPay']['amount']
                print(f"- Order from {buyer} - {total} PLN")
        else:
            print("No recent orders")
        
    except RateLimitError as e:
        print(f"Rate limit exceeded. Try again in {e.retry_after} seconds.")
    except AllegroAPIException as e:
        print(f"API Error: {e}")
        if e.response_data:
            print(f"Details: {e.response_data}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()