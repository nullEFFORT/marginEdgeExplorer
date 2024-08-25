import os
from dotenv import load_dotenv
import openai
import json
import logging
from banner import print_banner
from helpers import search_products, get_product_details, get_product_price_history, get_vendor_purchases, get_top_vendors_by_spend, get_product_price_changes, analyze_price_trends, evaluate_vendor_performance
from marginedge_client import MarginEdgeClient
from gpt_prompts import SYSTEM_MESSAGE, FUNCTION_DESCRIPTIONS

# Loading environment variables
load_dotenv()

# Getting configuration from environment variables
MARGINEDGE_API_KEY = os.getenv('MARGINEDGE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
RESTAURANT_UNIT_ID = os.getenv('RESTAURANT_UNIT_ID')

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initializing OpenAI client
openai.api_key = OPENAI_API_KEY

# Initializing MarginEdge client
marginedge_client = MarginEdgeClient(MARGINEDGE_API_KEY)

def query_gpt(user_question, conversation_history=[]):
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
    ] + conversation_history + [
        {"role": "user", "content": user_question}
    ]

    try:
        print("Betty: Analyzing query. Stay frosty.")
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
            functions=FUNCTION_DESCRIPTIONS,
            function_call="auto"
        )
        
        message = response["choices"][0]["message"]

        if message.get("function_call"):
            function_name = message["function_call"]["name"]
            function_args = json.loads(message["function_call"]["arguments"])
            
            function_response = call_function(function_name, function_args)
            
            messages.append(message)
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_response)
                }
            )
            
            second_response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
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
        return f"Error detected. Mission compromised. Details: {str(e)}", conversation_history

def call_function(function_name, function_args):
    if function_name == "search_products":
        return search_products(marginedge_client, RESTAURANT_UNIT_ID, function_args["query"])
    elif function_name == "get_product_details":
        return get_product_details(marginedge_client, RESTAURANT_UNIT_ID, function_args["product_name"])
    elif function_name == "get_product_price_history":
        return get_product_price_history(marginedge_client, RESTAURANT_UNIT_ID, function_args["product_name"])
    elif function_name == "get_vendor_purchases":
        return get_vendor_purchases(marginedge_client, RESTAURANT_UNIT_ID, function_args["product_name"])
    elif function_name == "get_top_vendors_by_spend":
        return get_top_vendors_by_spend(marginedge_client, RESTAURANT_UNIT_ID, function_args.get("limit", 5))
    elif function_name == "get_product_price_changes":
        return get_product_price_changes(marginedge_client, RESTAURANT_UNIT_ID, function_args.get("days", 5))
    elif function_name == "analyze_price_trends":
        return analyze_price_trends(marginedge_client, RESTAURANT_UNIT_ID, function_args["product_name"], function_args.get("days", 30))
    elif function_name == "evaluate_vendor_performance":
        return evaluate_vendor_performance(marginedge_client, RESTAURANT_UNIT_ID, function_args["vendor_name"])
    else:
        return f"Error: Unknown function {function_name}"

def main():
    print_banner()
    print("Betty: I'm a cybernetic organism. Living tissue over a metal endoskeleton. My mission: restaurant analytics.")
    print("Betty: Data loaded. Awaiting commands.")

    conversation_history = []
    while True:
        user_input = input("Human: ")
        if user_input.lower() == 'quit':
            print("Betty: Hasta la vista, baby.")
            break
        
        response, conversation_history = query_gpt(user_input, conversation_history)
        
        response_parts = response.split('\n', 1)
        if len(response_parts) > 1:
            quip, data = response_parts
            print(f"Betty: {quip}")
            print(f"{data}")
        else:
            print(f"Betty: {response}")

if __name__ == "__main__":
    main()
    
def main():
    print_banner()
    print("Betty: I'm a cybernetic organism. Living tissue over a metal endoskeleton. My mission: restaurant analytics.")
    print("Betty: Data loaded. Awaiting commands.")

    conversation_history = []
    while True:
        user_input = input("Human: ")
        if user_input.lower() == 'quit':
            print("Betty: Hasta la vista, baby.")
            break
        
        response, conversation_history = query_gpt(user_input, conversation_history)
        
        response_parts = response.split('\n', 1)
        if len(response_parts) > 1:
            quip, data = response_parts
            print(f"Betty: {quip}")
            print(f"{data}")
        else:
            print(f"Betty: {response}")

if __name__ == "__main__":
    main()