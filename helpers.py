import json
from datetime import datetime, timedelta

def load_data(file_path='marginedge_api_full_data.json'):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        print(f"Loaded data from {file_path}")
        print(f"Keys in data: {list(data.keys())}")
        for key, value in data.items():
            if isinstance(value, dict) and 'nextPage' in value and value.get(key.lower()):
                print(f"Number of {key}: {len(value.get(key.lower(), []))}")
            elif isinstance(value, list):
                print(f"Number of {key}: {len(value)}")
            else:
                print(f"{key}: Unable to determine count")
        return data
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Please ensure the file exists.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file.")
        return None

def get_data_summary(data):
    if not data:
        return "No data available."
    
    summary = []
    if 'restaurant_units' in data:
        summary.append(f"Restaurant Units: {len(data['restaurant_units'].get('restaurants', []))} units")
    if 'categories' in data:
        summary.append(f"Categories: {len(data['categories'].get('categories', []))} categories")
    if 'products' in data:
        summary.append(f"Products: {len(data['products'].get('products', []))} products")
    if 'vendors' in data:
        summary.append(f"Vendors: {len(data['vendors'].get('vendors', []))} vendors")
    if 'orders' in data:
        summary.append(f"Orders: {len(data['orders'].get('orders', []))} orders")
    
    return "\n".join(summary)

def search_products(data, product_name):
    products = data.get('products', {}).get('products', [])
    matching_products = [p for p in products if product_name.lower() in p.get('productName', '').lower()]
    
    if not matching_products:
        # If no exact matches, look for partial matches
        matching_products = [p for p in products if any(word.lower() in p.get('productName', '').lower() for word in product_name.split())]
    
    return matching_products

def get_vendor_purchases(data, product_name_or_id=None):
    products = search_products(data, product_name_or_id) if product_name_or_id else data.get('products', {}).get('products', [])
    orders = data.get('orders', {}).get('orders', [])

    vendor_purchases = {}
    for product in products:
        product_id = product['companyConceptProductId']
        product_name = product['productName']
        vendor_purchases[product_name] = {
            'product_id': product_id,
            'vendors': {},
            'total_quantity': 0,
            'total_spend': 0
        }

        for order in orders:
            vendor_name = order.get('vendorName', 'Unknown Vendor')
            for item in order.get('lineItems', []):
                if item.get('companyConceptProductId') == product_id:
                    if vendor_name not in vendor_purchases[product_name]['vendors']:
                        vendor_purchases[product_name]['vendors'][vendor_name] = {
                            'quantity': 0,
                            'total_spend': 0,
                            'last_purchase_date': None
                        }
                    
                    quantity = item.get('quantity', 0)
                    unit_price = item.get('unitPrice', 0)
                    total = quantity * unit_price
                    
                    vendor_purchases[product_name]['vendors'][vendor_name]['quantity'] += quantity
                    vendor_purchases[product_name]['vendors'][vendor_name]['total_spend'] += total
                    vendor_purchases[product_name]['vendors'][vendor_name]['last_purchase_date'] = order.get('invoiceDate')
                    vendor_purchases[product_name]['total_quantity'] += quantity
                    vendor_purchases[product_name]['total_spend'] += total

    return vendor_purchases

def get_top_vendors_by_spend(data, limit=5):
    vendor_spend = {}
    for order in data.get('orders', {}).get('orders', []):
        vendor_name = order.get('vendorName', 'Unknown Vendor')
        order_total = float(order.get('orderTotal', 0))
        vendor_spend[vendor_name] = vendor_spend.get(vendor_name, 0) + order_total
    
    sorted_vendors = sorted(vendor_spend.items(), key=lambda x: x[1], reverse=True)
    return sorted_vendors[:limit]

def get_product_price_changes(data, days=5):
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

def get_product_sales(data, product_name, days=7):
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

def list_all_vendors(data):
    return [vendor.get('vendorName', 'Unknown Vendor') for vendor in data.get('vendors', {}).get('vendors', [])]

def get_product_price(data, product_name):
    products = search_products(data, product_name)
    if products:
        return [(p['productName'], p['latestPrice']) for p in products]
    return []

def get_product_price_history(data, product_name_or_id):
    products = search_products(data, product_name_or_id)
    orders = data.get('orders', {}).get('orders', [])

    if not products:
        return f"No products found matching '{product_name_or_id}'."

    price_histories = {}
    for product in products:
        product_id = product['companyConceptProductId']
        product_name = product['productName']

        price_history = []
        for order in sorted(orders, key=lambda x: x.get('invoiceDate', ''), reverse=True):
            for item in order.get('lineItems', []):
                if item.get('companyConceptProductId') == product_id:
                    price_history.append({
                        'date': order.get('invoiceDate'),
                        'price': item.get('unitPrice'),
                        'vendor': order.get('vendorName')
                    })

        if price_history:
            price_histories[product_name] = {
                'product_id': product_id,
                'price_history': price_history
            }

    if not price_histories:
        return f"No price history found for products matching '{product_name_or_id}'."

    return price_histories

def get_product_details(data, product_name):
    products = data.get('products', {}).get('products', [])
    matching_products = [p for p in products if product_name.lower() in p.get('productName', '').lower()]
    
    if matching_products:
        return [{
            'name': p.get('productName'),
            'id': p.get('companyConceptProductId'),
            'central_id': p.get('centralProductId'),
            'latest_price': p.get('latestPrice'),
            'report_by_unit': p.get('reportByUnit'),
            'tax_exempt': p.get('taxExempt'),
            'categories': [cat.get('categoryId') for cat in p.get('categories', [])]
        } for p in matching_products]
    return []