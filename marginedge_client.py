import requests
from datetime import datetime, timedelta

class MarginEdgeClient:
    def __init__(self, api_key):
        self.base_url = "https://api.marginedge.com/public"
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _get_all_pages(self, endpoint, params=None):
        if params is None:
            params = {}
        all_data = []
        next_page = None

        while True:
            if next_page:
                params['nextPage'] = next_page
            response = requests.get(f"{self.base_url}/{endpoint}", headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Assuming the actual data is always in a list under some key
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

    def get_products(self, restaurant_unit_id):
        return self._get_all_pages("products", {"restaurantUnitId": restaurant_unit_id})

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

    def get_all_data(self, restaurant_unit_id):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        return {
            "restaurant_units": self.get_restaurant_units(),
            "categories": self.get_categories(restaurant_unit_id),
            "products": self.get_products(restaurant_unit_id),
            "vendors": self.get_vendors(restaurant_unit_id),
            "orders": self.get_orders(restaurant_unit_id, start_date.isoformat(), end_date.isoformat())
        }
    
    def get_order_detail(self, restaurant_unit_id, order_id):
        response = requests.get(f"{self.base_url}/orders/{order_id}", headers=self.headers, params={"restaurantUnitId": restaurant_unit_id})
        response.raise_for_status()
        return response.json()    