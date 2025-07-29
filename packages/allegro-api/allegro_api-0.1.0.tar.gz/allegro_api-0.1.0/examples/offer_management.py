"""
Examples of offer management using Allegro API.
"""

import os
from datetime import datetime
from allegro_api import AllegroAPI
from allegro_api.exceptions import ValidationError


def create_offer_example(api: AllegroAPI):
    """Example of creating a new offer."""
    
    # First, let's find a suitable category
    # Category 491 is "Laptopy" (Laptops)
    category_id = "491"
    
    # Get category parameters to know what's required
    parameters = api.categories.get_parameters(category_id)
    print(f"Category parameters: {len(parameters.get('parameters', []))} available")
    
    # Create offer data
    offer_data = {
        "name": "Test Laptop - Dell Latitude E7450",
        "category": {
            "id": category_id
        },
        "parameters": [
            # Add required parameters based on category
            # This is simplified - real implementation would use actual parameter IDs
        ],
        "images": [
            {
                "url": "https://example.com/laptop.jpg"  # Replace with actual image URL
            }
        ],
        "sellingMode": {
            "format": "BUY_NOW",
            "price": {
                "amount": "1999.99",
                "currency": "PLN"
            }
        },
        "stock": {
            "available": 5
        },
        "publication": {
            "status": "INACTIVE"  # Start as draft
        },
        "delivery": {
            "shippingTime": {
                "from": 1,
                "to": 3
            },
            "shippingCost": {
                "amount": "15.00",
                "currency": "PLN"
            }
        },
        "payments": {
            "invoice": "VAT"
        },
        "location": {
            "countryCode": "PL",
            "stateCode": "PL-MZ",
            "postCode": "00-001",
            "city": "Warszawa"
        },
        "aftersalesServices": {
            "impliedWarranty": {
                "length": "TWO_YEARS"
            },
            "returnPolicy": {
                "isAccepted": True,
                "length": "FOURTEEN_DAYS"
            }
        }
    }
    
    try:
        # Create the offer
        print("\nCreating new offer...")
        offer = api.offers.create(offer_data)
        print(f"Offer created with ID: {offer['id']}")
        
        return offer['id']
        
    except ValidationError as e:
        print(f"Validation error: {e}")
        print(f"Details: {e.response_data}")
        return None


def update_offer_example(api: AllegroAPI, offer_id: str):
    """Example of updating an existing offer."""
    
    print(f"\nUpdating offer {offer_id}...")
    
    # Method 1: Update specific fields with patch
    patch_operations = [
        {
            "op": "replace",
            "path": "/name",
            "value": "Updated - Dell Latitude E7450 i5 8GB"
        },
        {
            "op": "replace",
            "path": "/stock/available",
            "value": 3
        }
    ]
    
    try:
        api.offers.patch(offer_id, patch_operations)
        print("Offer patched successfully")
    except Exception as e:
        print(f"Patch failed: {e}")
    
    # Method 2: Update price directly
    try:
        api.offers.update_price(offer_id, amount=1799.99)
        print("Price updated to 1799.99 PLN")
    except Exception as e:
        print(f"Price update failed: {e}")
    
    # Method 3: Update quantity
    try:
        api.offers.update_quantity(offer_id, quantity=10, operation="set")
        print("Quantity updated to 10")
    except Exception as e:
        print(f"Quantity update failed: {e}")


def publish_offer_example(api: AllegroAPI, offer_id: str):
    """Example of publishing an offer."""
    
    print(f"\nPublishing offer {offer_id}...")
    
    try:
        # Publish the offer
        api.offers.publish(offer_id)
        print("Offer published successfully!")
        
        # Check offer status
        offer = api.offers.get(offer_id)
        status = offer['publication']['status']
        print(f"Current status: {status}")
        
    except Exception as e:
        print(f"Publishing failed: {e}")


def monitor_offer_events(api: AllegroAPI):
    """Example of monitoring offer events."""
    
    print("\nMonitoring offer events...")
    
    try:
        # Get recent offer events
        events = api.offers.get_events(limit=10)
        
        for event in events.get('events', []):
            event_type = event['type']
            offer_id = event['offer']['id']
            occurred_at = event['occurredAt']
            
            print(f"- {event_type} for offer {offer_id} at {occurred_at}")
            
    except Exception as e:
        print(f"Failed to get events: {e}")


def batch_update_example(api: AllegroAPI):
    """Example of batch updating multiple offers."""
    
    print("\nBatch updating offers...")
    
    # Get some offers to update
    my_offers = api.offers.list(limit=5)
    offer_ids = [offer['id'] for offer in my_offers.get('offers', [])]
    
    if not offer_ids:
        print("No offers to update")
        return
    
    # Prepare batch operations
    operations = []
    
    for i, offer_id in enumerate(offer_ids[:2]):  # Update first 2 offers
        operations.append({
            "offer": {"id": offer_id},
            "modification": {
                "changeType": "PRICE",
                "price": {
                    "amount": f"{1500 + i * 100}.00",
                    "currency": "PLN"
                }
            }
        })
    
    try:
        # Submit batch update
        result = api.offers.batch_update(operations)
        command_id = result['id']
        print(f"Batch update submitted, command ID: {command_id}")
        
        # Check status
        import time
        time.sleep(2)  # Wait a bit
        
        status = api.offers.get_batch_status(command_id)
        print(f"Batch status: {status['status']}")
        
        if status.get('errors'):
            for error in status['errors']:
                print(f"Error: {error}")
                
    except Exception as e:
        print(f"Batch update failed: {e}")


def main():
    # Initialize API
    api = AllegroAPI(
        client_id=os.getenv("ALLEGRO_CLIENT_ID"),
        client_secret=os.getenv("ALLEGRO_CLIENT_SECRET"),
        sandbox=True
    )
    
    # Authenticate
    print("Authenticating...")
    api.authenticate()
    
    # Run examples
    offer_id = create_offer_example(api)
    
    if offer_id:
        update_offer_example(api, offer_id)
        publish_offer_example(api, offer_id)
    
    monitor_offer_events(api)
    batch_update_example(api)


if __name__ == "__main__":
    main()