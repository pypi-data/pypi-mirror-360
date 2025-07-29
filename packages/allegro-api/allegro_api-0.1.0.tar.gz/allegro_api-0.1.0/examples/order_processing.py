"""
Examples of order processing using Allegro API.
"""

import os
from datetime import datetime, timedelta
from allegro_api import AllegroAPI


def list_recent_orders(api: AllegroAPI):
    """List recent orders with different filters."""
    
    print("\n--- Recent orders ready for processing ---")
    
    # Get orders from last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    
    orders = api.orders.list(
        status="READY_FOR_PROCESSING",
        line_items_bought_at_gte=week_ago,
        limit=10
    )
    
    for order in orders.get('checkoutForms', []):
        order_id = order['id']
        buyer_login = order['buyer']['login']
        total = order['summary']['totalToPay']['amount']
        currency = order['summary']['totalToPay']['currency']
        
        print(f"\nOrder ID: {order_id}")
        print(f"Buyer: {buyer_login}")
        print(f"Total: {total} {currency}")
        
        # Show line items
        for item in order['lineItems']:
            offer_name = item['offer']['name']
            quantity = item['quantity']
            price = item['price']['amount']
            print(f"  - {offer_name} x{quantity} @ {price} {currency}")
    
    return orders.get('checkoutForms', [])


def process_single_order(api: AllegroAPI, order_id: str):
    """Process a single order - show details and create shipment."""
    
    print(f"\n--- Processing order {order_id} ---")
    
    # Get full order details
    order = api.orders.get(order_id)
    
    # Display buyer information
    buyer = order['buyer']
    print(f"Buyer: {buyer['login']}")
    if 'email' in buyer:
        print(f"Email: {buyer['email']}")
    if 'phone' in buyer:
        print(f"Phone: {buyer['phone']}")
    
    # Display delivery information
    delivery = order['delivery']
    address = delivery['address']
    print(f"\nDelivery to:")
    print(f"{address.get('firstName', '')} {address.get('lastName', '')}")
    print(f"{address['street']}")
    print(f"{address['zipCode']} {address['city']}")
    print(f"{address['countryCode']}")
    
    # Display delivery method
    method = delivery['method']
    print(f"\nDelivery method: {method['name']}")
    
    # Check if shipment already exists
    shipments = api.orders.get_shipments(order_id)
    
    if shipments.get('shipments'):
        print("\nShipment already created:")
        for shipment in shipments['shipments']:
            print(f"- Carrier: {shipment['carrierName']}")
            print(f"- Tracking: {shipment.get('trackingNumber', 'N/A')}")
            print(f"- Created: {shipment['createdAt']}")
    else:
        print("\nNo shipment created yet")
        
        # Example: Create shipment
        # In real scenario, you would get tracking number from your shipping provider
        try:
            shipment_data = api.orders.create_shipment(
                order_id=order_id,
                carrier_id="INPOST",
                carrier_name="InPost",
                tracking_number="123456789012"
            )
            print("Shipment created successfully!")
        except Exception as e:
            print(f"Failed to create shipment: {e}")


def handle_order_events(api: AllegroAPI):
    """Monitor and handle order events."""
    
    print("\n--- Recent order events ---")
    
    # Get recent events
    events = api.orders.get_events(limit=20)
    
    for event in events.get('events', []):
        event_type = event['type']
        order_id = event['order']['id']
        occurred_at = event['occurredAt']
        
        print(f"\nEvent: {event_type}")
        print(f"Order: {order_id}")
        print(f"Time: {occurred_at}")
        
        # Handle specific event types
        if event_type == "CHECKOUT_FORM_FINALIZED":
            print("→ New order received! Process it soon.")
        elif event_type == "CHECKOUT_FORM_BUYER_PAID":
            print("→ Payment received! Ready to ship.")
        elif event_type == "CHECKOUT_FORM_CANCELLED":
            print("→ Order cancelled by buyer.")


def manage_returns(api: AllegroAPI):
    """Example of handling customer returns."""
    
    print("\n--- Customer returns ---")
    
    # Get recent returns
    returns = api.orders.get_returns(
        status="NEW",
        limit=10
    )
    
    for return_item in returns.get('customerReturns', []):
        return_id = return_item['id']
        order_id = return_item['orderId']
        reason = return_item['reason']
        status = return_item['status']
        
        print(f"\nReturn ID: {return_id}")
        print(f"Order ID: {order_id}")
        print(f"Reason: {reason}")
        print(f"Status: {status}")
        
        # Get detailed return information
        try:
            return_details = api.orders.get_return(return_id)
            
            # Show returned items
            for item in return_details.get('items', []):
                offer_name = item['offer']['name']
                quantity = item['quantity']
                print(f"  - {offer_name} x{quantity}")
                
        except Exception as e:
            print(f"Failed to get return details: {e}")


def add_order_comment(api: AllegroAPI, order_id: str):
    """Add internal comment to an order."""
    
    print(f"\n--- Adding comment to order {order_id} ---")
    
    try:
        comment = api.orders.add_comment(
            order_id=order_id,
            text="Order processed and shipped via InPost",
            type_="SELLER_MESSAGE"
        )
        print("Comment added successfully")
    except Exception as e:
        print(f"Failed to add comment: {e}")


def generate_invoice_example(api: AllegroAPI, order_id: str):
    """Example of handling invoices for orders."""
    
    print(f"\n--- Invoice handling for order {order_id} ---")
    
    # Check existing invoices
    invoices = api.orders.get_invoices(order_id)
    
    if invoices.get('invoices'):
        print("Existing invoices:")
        for invoice in invoices['invoices']:
            print(f"- Number: {invoice['number']}")
            print(f"- Created: {invoice['createdAt']}")
    else:
        print("No invoices yet")
        
        # In real scenario, you would generate actual invoice file
        # This is just an example
        try:
            # api.orders.upload_invoice(
            #     order_id=order_id,
            #     invoice_file=b"invoice_content_here",
            #     invoice_number="FV/2024/001"
            # )
            print("Invoice upload example (not executed)")
        except Exception as e:
            print(f"Invoice upload would fail: {e}")


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
    
    # List recent orders
    orders = list_recent_orders(api)
    
    # Process first order if any
    if orders:
        first_order = orders[0]
        process_single_order(api, first_order['id'])
        add_order_comment(api, first_order['id'])
        generate_invoice_example(api, first_order['id'])
    
    # Monitor events
    handle_order_events(api)
    
    # Check returns
    manage_returns(api)


if __name__ == "__main__":
    main()