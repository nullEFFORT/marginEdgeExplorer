import json
from collections import defaultdict

def load_data(file_path='restaurant_data.json'):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_vendor_purchases(vendor_name):
    data = load_data()
    vendor_purchases = defaultdict(float)
    
    for order in data.get('orders', {}).get('orders', []):
        if order.get('vendorName', '').lower() == vendor_name.lower():
            for item in order.get('lineItems', []):
                product_name = item.get('vendorItemName', 'Unknown Product')
                quantity = item.get('quantity', 0)
                unit_price = item.get('unitPrice', 0)
                vendor_purchases[product_name] += quantity * unit_price
    
    return dict(vendor_purchases)

def get_top_vendors_by_spend(limit=5):
    data = load_data()
    vendor_spend = defaultdict(float)
    
    for order in data.get('orders', {}).get('orders', []):
        vendor_name = order.get('vendorName', 'Unknown Vendor')
        order_total = float(order.get('orderTotal', 0))
        vendor_spend[vendor_name] += order_total
    
    sorted_vendors = sorted(vendor_spend.items(), key=lambda x: x[1], reverse=True)
    return sorted_vendors[:limit]

if __name__ == "__main__":
    # Test the functions
    print("Top 5 vendors by spend:")
    print(get_top_vendors_by_spend())
    
    print("\nPurchases from 'Inland Foods':")
    print(get_vendor_purchases('Inland Foods'))