from datetime import datetime, timedelta

def search_products(client, restaurant_unit_id, query):
    query = query.lower()
    all_products = client.get_products(restaurant_unit_id)
    
    matching_products = []
    for product in all_products:
        product_name = product["productName"].lower()
        product_category = product["categories"][0].get("categoryName", "").lower() if product.get("categories") else ""
        
        # Check for wines
        if query == "all wines" and ("wine" in product_name or "wine" in product_category):
            matching_products.append(product)
        # Check for other queries
        elif query in product_name or query in product_category:
            matching_products.append(product)
    
    return [
        {
            "name": p["productName"],
            "category": p["categories"][0].get("categoryName", "Unknown") if p.get("categories") else "Unknown",
            "latest_price": p.get("latestPrice", "Unknown"),
            "unit": p.get("reportByUnit", "Unknown"),
            "id": p.get("companyConceptProductId", "Unknown")
        }
        for p in matching_products
    ]
    
    return matching_products

def get_product_details(client, restaurant_unit_id, product_name):
    products = search_products(client, restaurant_unit_id, product_name)
    if not products:
        return "Product not found."
    
    product = products[0]
    details = client.get_product_details(restaurant_unit_id, product["id"])
    
    return {
        "name": details["productName"],
        "category": details["categories"][0]["categoryName"] if details["categories"] else "Unknown",
        "latest_price": details["latestPrice"],
        "unit": details.get("reportByUnit", "Unknown"),
        "tax_exempt": details["taxExempt"],
        "on_inventory": details["onInventory"]
    }

def get_product_price_history(client, restaurant_unit_id, product_name):
    products = search_products(client, restaurant_unit_id, product_name)
    if not products:
        return "Product not found."
    
    product = products[0]
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    try:
        history = client.get_product_price_history(
            restaurant_unit_id,
            product["id"],
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        return [
            {"date": entry["date"], "price": entry["price"]}
            for entry in history
        ]
    except Exception as e:
        return f"Unable to retrieve price history. Error: {str(e)}"

def get_vendor_purchases(client, restaurant_unit_id, product_name):
    products = search_products(client, restaurant_unit_id, product_name)
    if not products:
        return "Product not found."
    
    product = products[0]
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    orders = client.get_orders(restaurant_unit_id, start_date.isoformat(), end_date.isoformat())
    
    purchases = []
    for order in orders:
        order_details = client.get_order_detail(restaurant_unit_id, order["orderId"])
        for item in order_details.get("lineItems", []):
            if item["companyConceptProductId"] == product["id"]:
                purchases.append({
                    "date": order["invoiceDate"],
                    "vendor": order["vendorName"],
                    "quantity": item["quantity"],
                    "unit_price": item["unitPrice"],
                    "total_price": item["quantity"] * item["unitPrice"]
                })
    
    return purchases

def get_top_vendors_by_spend(client, restaurant_unit_id, limit=5):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    orders = client.get_orders(restaurant_unit_id, start_date.isoformat(), end_date.isoformat())
    
    vendor_spend = {}
    for order in orders:
        vendor_name = order["vendorName"]
        order_total = order["orderTotal"]
        vendor_spend[vendor_name] = vendor_spend.get(vendor_name, 0) + order_total
    
    sorted_vendors = sorted(vendor_spend.items(), key=lambda x: x[1], reverse=True)
    return sorted_vendors[:limit]

def get_product_price_changes(client, restaurant_unit_id, days=5):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    products = client.get_products(restaurant_unit_id)
    
    price_changes = []
    for product in products:
        try:
            history = client.get_product_price_history(
                restaurant_unit_id,
                product["companyConceptProductId"],
                start_date.isoformat(),
                end_date.isoformat()
            )
            if len(history) > 1 and history[0]["price"] != history[-1]["price"]:
                price_changes.append({
                    "name": product["productName"],
                    "old_price": history[0]["price"],
                    "new_price": history[-1]["price"],
                    "change": history[-1]["price"] - history[0]["price"]
                })
        except Exception:
            continue
    
    return price_changes

def analyze_price_trends(client, restaurant_unit_id, product_name, days=30):
    products = search_products(client, restaurant_unit_id, product_name)
    if not products:
        return "Product not found."
    
    product = products[0]
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    try:
        history = client.get_product_price_history(
            restaurant_unit_id,
            product["id"],
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        if not history:
            return "No price history available for this product."

        oldest_price = history[0]["price"]
        newest_price = history[-1]["price"]
        price_change = newest_price - oldest_price
        percent_change = (price_change / oldest_price) * 100

        trend = "increasing" if price_change > 0 else "decreasing" if price_change < 0 else "stable"

        return {
            "product": product_name,
            "trend": trend,
            "price_change": price_change,
            "percent_change": percent_change,
            "oldest_price": oldest_price,
            "newest_price": newest_price
        }
    except Exception as e:
        return f"Unable to analyze price trends. Error: {str(e)}"

def evaluate_vendor_performance(client, restaurant_unit_id, vendor_name):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    orders = client.get_orders(restaurant_unit_id, start_date.isoformat(), end_date.isoformat())
    
    vendor_orders = [order for order in orders if order["vendorName"] == vendor_name]
    
    if not vendor_orders:
        return "No orders found for this vendor."

    total_orders = len(vendor_orders)
    total_spend = sum(order["orderTotal"] for order in vendor_orders)
    avg_order_value = total_spend / total_orders if total_orders > 0 else 0

    on_time_deliveries = sum(1 for order in vendor_orders if order["status"] == "CLOSED")
    on_time_rate = (on_time_deliveries / total_orders) * 100 if total_orders > 0 else 0

    return {
        "vendor": vendor_name,
        "total_orders": total_orders,
        "total_spend": total_spend,
        "avg_order_value": avg_order_value,
        "on_time_rate": on_time_rate
    }