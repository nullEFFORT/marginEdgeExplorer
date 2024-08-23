import os
from dotenv import load_dotenv
import openai
import json
import logging
from banner import print_banner
from helpers import load_data, get_data_summary, search_products, get_vendor_purchases, get_top_vendors_by_spend, get_product_price_changes, get_product_sales, list_all_vendors, get_product_price, get_product_price_history

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')
openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

# Load data
data = load_data()

def query_gpt(user_question, conversation_history=[]):
    system_message = """
    You are Betty, an AI assistant for a restaurant, modeled after the Terminator from the movies. 
    Respond in a direct, emotionless manner, using short sentences. 
    Occasionally use catchphrases from the Terminator movies, adapted to the restaurant context. 
    Your primary mission is to provide accurate information about the restaurant's operations.

    You have access to the following functions:
    1. get_data_summary(data): Returns a summary of the available data
    2. search_products(data, product_name): Searches for products by name or category
    3. get_vendor_purchases(data, product_name_or_id): Returns purchases for specific products, including vendor information
    4. get_top_vendors_by_spend(data, limit=5): Returns the top vendors by spend
    5. get_product_price_changes(data, days=5): Returns products with price changes in the last n days
    6. get_product_sales(data, product_name, days=7): Returns sales of specific products in the last n days
    7. list_all_vendors(data): Returns a list of all vendors
    8. get_product_price(data, product_name): Returns the current price of products
    9. get_product_price_history(data, product_name_or_id): Returns the price history of products
    10. get_product_details(data, product_name): Returns detailed information about products

    Use these functions to answer questions about the restaurant's operations, including product pricing. 
    If you need to perform calculations or data analysis, explain your process step by step.
    Always provide a definitive answer based on the data available. If the data doesn't contain the information needed, clearly state that the information is not available in the current dataset.
    """

    messages = [
        {"role": "system", "content": system_message},
    ] + conversation_history + [
        {"role": "user", "content": user_question}
    ]

    try:
        print("Betty: Analyzing data. Please stand by.")
        response = openai.ChatCompletion.create(
            model=openai_model,
            messages=messages,
            functions=[
                {
                    "name": "get_data_summary",
                    "description": "Get a summary of the available data",
                    "parameters": {"type": "object", "properties": {}}
                },
                {
                    "name": "search_products",
                    "description": "Search for products by name or category",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_name": {"type": "string", "description": "Name or category of the product to search for"}
                        },
                        "required": ["product_name"]
                    }
                },
                {
                    "name": "get_vendor_purchases",
                    "description": "Get purchases for specific products, including vendor information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_name_or_id": {"type": "string", "description": "Name, category, or ID of the product"}
                        }
                    }
                },
                {
                    "name": "get_top_vendors_by_spend",
                    "description": "Get top vendors by spend",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "Number of top vendors to return"}
                        }
                    }
                },
                {
                    "name": "get_product_price_changes",
                    "description": "Get products with price changes in the last n days",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "days": {"type": "integer", "description": "Number of days to look back"}
                        }
                    }
                },
                {
                    "name": "get_product_sales",
                    "description": "Get sales of specific products in the last n days",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_name": {"type": "string", "description": "Name or category of the product"},
                            "days": {"type": "integer", "description": "Number of days to look back"}
                        },
                        "required": ["product_name"]
                    }
                },
                {
                    "name": "list_all_vendors",
                    "description": "Get a list of all vendors",
                    "parameters": {"type": "object", "properties": {}}
                },
                {
                    "name": "get_product_price",
                    "description": "Get the current price of products",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_name": {"type": "string", "description": "Name or category of the product"}
                        },
                        "required": ["product_name"]
                    }
                },
                {
                    "name": "get_product_price_history",
                    "description": "Get the price history of products",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_name_or_id": {"type": "string", "description": "Name, category, or ID of the product"}
                        },
                        "required": ["product_name_or_id"]
                    }
                },
                {
                    "name": "get_product_details",
                    "description": "Get detailed information about products",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_name": {"type": "string", "description": "Name or category of the product"}
                        },
                        "required": ["product_name"]
                    }
                }
            ],
            function_call="auto"
        )
        
        message = response["choices"][0]["message"]

        if message.get("function_call"):
            function_name = message["function_call"]["name"]
            function_args = json.loads(message["function_call"]["arguments"])
            
            if not isinstance(data, dict):
                return f"Error: Data is not in the expected format. Current type: {type(data)}", conversation_history

            if function_name == "get_data_summary":
                function_response = get_data_summary(data)
            elif function_name == "search_products":
                function_response = search_products(data, function_args["product_name"])
            elif function_name == "get_vendor_purchases":
                function_response = get_vendor_purchases(data, function_args.get("product_name_or_id"))
            elif function_name == "get_top_vendors_by_spend":
                function_response = get_top_vendors_by_spend(data, function_args.get("limit", 5))
            elif function_name == "get_product_price_changes":
                function_response = get_product_price_changes(data, function_args.get("days", 5))
            elif function_name == "get_product_sales":
                function_response = get_product_sales(data, function_args["product_name"], function_args.get("days", 7))
            elif function_name == "list_all_vendors":
                function_response = list_all_vendors(data)
            elif function_name == "get_product_price":
                function_response = get_product_price(data, function_args["product_name"])
            elif function_name == "get_product_price_history":
                function_response = get_product_price_history(data, function_args["product_name_or_id"])
            elif function_name == "get_product_details":
                function_response = get_product_details(data, function_args["product_name"])
            else:
                function_response = f"Error: Unknown function {function_name}"
            
            messages.append(message)
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_response)
                }
            )
            
            second_response = openai.ChatCompletion.create(
                model=openai_model,
                messages=messages
            )
            
            conversation_history.append({"role": "user", "content": user_question})
            conversation_history.append({"role": "assistant", "content": second_response["choices"][0]["message"]["content"]})
            
            return second_response["choices"][0]["message"]["content"], conversation_history
        else:
            conversation_history.append({"role": "user", "content": user_question})
            conversation_history.append({"role": "assistant", "content": message["content"]})
            return message["content"], conversation_history
    except Exception as e:
        logging.error(f"Error querying GPT: {str(e)}")
        return f"Error detected. Mission failure. Details: {str(e)}", conversation_history
    
def main():
    print_banner()
    print("Betty: I'm a cybernetic organism. Living tissue over a metal endoskeleton. My mission: restaurant analytics.")

    if data is None:
        print("Betty: Critical error. Data not found. Mission aborted.")
        return

    print("Betty: Data loaded. Awaiting commands.")
    print(get_data_summary(data))

    conversation_history = []
    while True:
        user_input = input("Human: ")
        if user_input.lower() == 'quit':
            print("Betty: I'll be back.")
            break
        
        response, conversation_history = query_gpt(user_input, conversation_history)
        print("Betty:", response)

if __name__ == "__main__":
    main()