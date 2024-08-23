import os
from dotenv import load_dotenv
from marginedge_client import MarginEdgeClient
import openai

# Load environment variables from .env file
load_dotenv()

# Load those keys from my dudes
marginedge_api_key = os.getenv('MARGINEDGE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
restaurant_unit_id = os.getenv('RESTAURANT_UNIT_ID')

# wake up biotch - time to work
marginedge_client = MarginEdgeClient(marginedge_api_key)

# Initialize OpenAI - the real mvp
openai.api_key = openai_api_key

def get_ai_insights(data):
    prompt = f"Analyze the following restaurant data and provide insights:\n\n{data}\n\nInsights:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a restaurant analytics expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        n=1,
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()

def main():
    # Get restaurant units
    print("Fetching restaurant units...")
    restaurant_units = marginedge_client.get_restaurant_units()
    print(f"Found {len(restaurant_units['restaurants'])} restaurant units.")

    print(f"Using restaurant unit ID: {restaurant_unit_id}")

    # Get categories
    print("\nFetching categories...")
    categories = marginedge_client.get_categories(restaurant_unit_id)
    print(f"Found {len(categories['categories'])} categories.")

    # Get recent orders
    print("\nFetching recent orders...")
    import datetime
    end_date = datetime.date.today().isoformat()
    start_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    orders = marginedge_client.get_orders(restaurant_unit_id, start_date, end_date)
    print(f"Found {len(orders['orders'])} orders in the last 30 days.")

    # Prepare data for AI analysis - samples because we haven't moved from the ghetto code to a 
    # real datastore
    data_for_analysis = {
        "restaurant_unit_id": restaurant_unit_id,
        "categories": categories['categories'][:5],  # First 5 categories
        "recent_orders": orders['orders'][:5]  # First 5 orders
    }

    # Get AI insights
    print("\nGenerating AI insights...")
    insights = get_ai_insights(str(data_for_analysis))
    print("\nAI Insights:")
    print(insights)

if __name__ == "__main__":
    main()