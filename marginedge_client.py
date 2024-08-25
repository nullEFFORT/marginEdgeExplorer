import requests
from datetime import datetime, timedelta
import time

class MarginEdgeClient:
    def __init__(self, api_key):
        self.base_url = "https://api.marginedge.com/public"
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.rate_limit_delay = 1
        self.product_cache = {}

    def _make_request(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 429:  # Too Many Requests
            time.sleep(self.rate_limit_delay)
            self.rate_limit_delay *= 2  # Exponential backoff
            return self._make_request(endpoint, params)
        self.rate_limit_delay = 1  # Reset delay if request was successful
        response.raise_for_status()
        return response.json()

    def _get_all_pages(self, endpoint, params=None):
        if params is None:
            params = {}
        all_data = []
        next_page = None

        while True:
            if next_page:
                params['nextPage'] = next_page
            data = self._make_request(endpoint, params)
            
            for key in data.keys():
                if isinstance(data[key], list):
                    all_data.extend(data[key])
                    break
            
            next_page = data.get('nextPage')
            if not next_page:
                break

        return all_data

    def get_restaurant_units(self):
        return self._get_all_pages("restaurantUnits")

    def get_categories(self, restaurant_unit_id):
        return self._get_all_pages("categories", {"restaurantUnitId": restaurant_unit_id})

    def get_products(self, restaurant_unit_id, category=None, search_term=None):
        cache_key = f"{category}_{search_term}"
        if cache_key in self.product_cache:
            return self.product_cache[cache_key]

        params = {"restaurantUnitId": restaurant_unit_id}
        if category:
            params["category"] = category
        if search_term:
            params["search"] = search_term

        products = self._get_all_pages("products", params)
        self.product_cache[cache_key] = products
        return products

    def get_vendors(self, restaurant_unit_id):
        return self._get_all_pages("vendors", {"restaurantUnitId": restaurant_unit_id})

    def get_orders(self, restaurant_unit_id, start_date, end_date, order_status=None):
        params = {
            "restaurantUnitId": restaurant_unit_id,
            "startDate": start_date,
            "endDate": end_date
        }
        if order_status:
            params["orderStatus"] = order_status
        return self._get_all_pages("orders", params)

    def get_order_detail(self, restaurant_unit_id, order_id):
        return self._make_request(f"orders/{order_id}", {"restaurantUnitId": restaurant_unit_id})

    def get_product_details(self, restaurant_unit_id, product_id):
        return self._make_request(f"products/{product_id}", {"restaurantUnitId": restaurant_unit_id})

    def get_product_price_history(self, restaurant_unit_id, product_id, start_date, end_date):
        params = {
            "restaurantUnitId": restaurant_unit_id,
            "startDate": start_date,
            "endDate": end_date
        }
        return self._make_request(f"products/{product_id}/priceHistory", params)