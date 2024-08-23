import json
from datetime import datetime, timedelta

def load_data(file_path='restaurant_data.json'):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_product_price_changes(days=5):
    data = load_data()
    products = data.get('products', {}).get('products', [])
    orders = data.get('orders', {}).get('orders', [])

    cutoff_date = datetime.now() - timedelta(days=days)
    recent_orders = [order for order in orders if datetime.fromisoformat(order.get('invoiceDate', '')) > cutoff_date]

    price_changes = []
    for product in products:
        product_id = product.get('companyConceptProductId')
        product_name = product.get('productName')
        recent_prices = [
            item['unitPrice']
            for order in recent_orders
            for item in order.get('lineItems', [])
            if item.get('companyConceptProductId') == product_id
        ]
        if len(set(recent_prices)) > 1:
            price_changes.append({
                'product': product_name,
                'old_price': min(recent_prices),
                'new_price': max(recent_prices)
            })

    return price_changes

def get_product_sales(product_name, days=7):
    data = load_data()
    orders = data.get('orders', {}).get('orders', [])

    cutoff_date = datetime.now() - timedelta(days=days)
    recent_orders = [order for order in orders if datetime.fromisoformat(order.get('invoiceDate', '')) > cutoff_date]

    total_sales = sum(
        item.get('quantity', 0)
        for order in recent_orders
        for item in order.get('lineItems', [])
        if product_name.lower() in item.get('vendorItemName', '').lower()
    )

    return total_sales

if __name__ == "__main__":
    # Test the functions
    print("Products with price changes in the last 5 days:")
    print(get_product_price_changes())
    
    print("\nSales of 'Martini' in the last 7 days:")
    print(get_product_sales('Martini'))