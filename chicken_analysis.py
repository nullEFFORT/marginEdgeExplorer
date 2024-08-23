import os
from dotenv import load_dotenv
from marginedge_client import MarginEdgeClient
from datetime import datetime, timedelta
import json
import time

# Load environment variables
load_dotenv()

# Initialize client
marginedge_client = MarginEdgeClient(os.getenv('MARGINEDGE_API_KEY'))
restaurant_unit_id = os.getenv('RESTAURANT_UNIT_ID')

def find_chicken_products(products):
    return [p for p in products if 'chicken' in p.get('productName', '').lower()]

def get_chicken_vendors_and_prices(orders, chicken_products):
    vendors = set()
    price_history = {p['productName']: [] for p in chicken_products}
    chicken_product_ids = set(p['companyConceptProductId'] for p in chicken_products)
    
    for order in orders[:5]:  # Limit to first 5 orders
        try:
            order_details = marginedge_client.get_order_detail(restaurant_unit_id, order['orderId'])
            print(f"Processing order {order['orderId']}...")
            for item in order_details.get('lineItems', []):
                if item.get('companyConceptProductId') in chicken_product_ids:
                    vendors.add(order.get('vendorName'))
                    product_name = next(p['productName'] for p in chicken_products if p['companyConceptProductId'] == item.get('companyConceptProductId'))
                    price_history[product_name].append({
                        'date': order.get('invoiceDate'),
                        'price': item.get('unitPrice'),
                        'vendor': order.get('vendorName')
                    })
            time.sleep(1)  # Add a 1-second delay between requests to avoid rate limiting
        except Exception as e:
            print(f"Error fetching details for order {order['orderId']}: {str(e)}")
    
    # Sort price history by date
    for product in price_history:
        price_history[product] = sorted(price_history[product], key=lambda x: datetime.fromisoformat(x['date']))
    
    return list(vendors), price_history

def main():
    # Fetch data from API
    print("Fetching products...")
    products = marginedge_client.get_products(restaurant_unit_id)
    print(f"Received {len(products)} products")
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)  # Get 90 days of order history
    print(f"\nFetching orders from {start_date} to {end_date}...")
    orders = marginedge_client.get_orders(restaurant_unit_id, start_date.isoformat(), end_date.isoformat())
    print(f"Received {len(orders)} orders")

    # 1. What chicken products do we buy?
    chicken_products = find_chicken_products(products)
    print("\nChicken products:")
    for product in chicken_products:
        print(f"- {product['productName']} (Latest price: ${product.get('latestPrice', 'N/A')}, ID: {product['companyConceptProductId']})")
    
    print("\n" + "="*50 + "\n")
    
    # 2 & 3. Who do we buy chicken from and what's the price history?
    print("Fetching detailed order information (limited to first 5 orders)...")
    chicken_vendors, price_history = get_chicken_vendors_and_prices(orders, chicken_products)
    
    print("\nChicken vendors:")
    if chicken_vendors:
        for vendor in chicken_vendors:
            print(f"- {vendor}")
    else:
        print("No vendors found for chicken products in the processed orders")
    
    print("\n" + "="*50 + "\n")
    
    print("Price history for chicken products (based on processed orders):")
    for product, history in price_history.items():
        print(f"\n{product}:")
        if history:
            for entry in history:
                print(f"  {entry['date']}: ${entry['price']} (Vendor: {entry['vendor']})")
        else:
            print("  No price history available in the processed orders")

if __name__ == "__main__":
    main()