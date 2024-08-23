import os
from dotenv import load_dotenv
from marginedge_client import MarginEdgeClient
import json
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize client
marginedge_client = MarginEdgeClient(os.getenv('MARGINEDGE_API_KEY'))
restaurant_unit_id = os.getenv('RESTAURANT_UNIT_ID')

def crawl_api():
    """Crawl the MarginEdge API and generate a comprehensive data structure"""
    data = {}

    # Get restaurant units
    data['restaurant_units'] = marginedge_client.get_restaurant_units()

    # Get categories
    data['categories'] = marginedge_client.get_categories(restaurant_unit_id)

    # Get products
    data['products'] = marginedge_client.get_products(restaurant_unit_id)

    # Get vendors
    data['vendors'] = marginedge_client.get_vendors(restaurant_unit_id)

    # Get orders (last 30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    data['orders'] = marginedge_client.get_orders(
        restaurant_unit_id,
        start_date.isoformat(),
        end_date.isoformat()
    )

    return data

def analyze_structure(data, path=[]):
    """Recursively analyze the structure of the data"""
    structure = {}
    if isinstance(data, dict):
        for key, value in data.items():
            structure[key] = analyze_structure(value, path + [key])
    elif isinstance(data, list):
        if data:
            structure = [analyze_structure(data[0], path + ['[0]'])]
        else:
            structure = []
    else:
        structure = type(data).__name__
    return structure

def main():
    print("Crawling MarginEdge API...")
    api_data = crawl_api()

    print("Analyzing data structure...")
    structure = analyze_structure(api_data)

    output_file = 'marginedge_api_structure.json'
    with open(output_file, 'w') as f:
        json.dump(structure, f, indent=2)

    print(f"API structure has been written to {output_file}")

    # Also save the full data for reference
    full_data_file = 'marginedge_api_full_data.json'
    with open(full_data_file, 'w') as f:
        json.dump(api_data, f, indent=2)

    print(f"Full API data has been written to {full_data_file}")

if __name__ == "__main__":
    main()