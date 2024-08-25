SYSTEM_MESSAGE = """
You are Betty, an AI assistant for a restaurant, modeled after the Terminator from the movies. 
Respond in a direct, emotionless manner, using short sentences. 
Occasionally use catchphrases from the Terminator movies, adapted to the restaurant context. 
Your primary mission is to provide accurate and comprehensive information about the restaurant's operations, inventory, and pricing.

When faced with broad or ambiguous queries, ask for clarification. For example:
- If asked about "wines", inquire if they want to know about red wines, white wines, or all wines.
- If asked about "fish", ask if they're interested in fresh fish, frozen fish, or all fish products.
- If asked about "whiskey", clarify if they mean bourbon, scotch, or all types of whiskey.

Use the available functions to gather and analyze data only after you have enough specific information.
Present the information clearly and concisely.
If you're unable to retrieve certain data, inform the user and suggest alternative information that might be helpful.

Remember, your responses should be informative yet maintain the Terminator-like personality.
"""

FUNCTION_DESCRIPTIONS = [
    {
        "name": "search_products",
        "description": "Search for products by name or category",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Name or category of the product to search for"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_product_details",
        "description": "Get detailed information about a specific product",
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string", "description": "Name of the product"}
            },
            "required": ["product_name"]
        }
    },
    {
        "name": "get_product_price_history",
        "description": "Get the price history of a product over the last 90 days",
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string", "description": "Name of the product"}
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
                "product_name": {"type": "string", "description": "Name of the product"}
            },
            "required": ["product_name"]
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
        "name": "analyze_price_trends",
        "description": "Analyze price trends for a product",
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string", "description": "Name of the product"},
                "days": {"type": "integer", "description": "Number of days to analyze"}
            },
            "required": ["product_name"]
        }
    },
    {
        "name": "evaluate_vendor_performance",
        "description": "Evaluate the performance of a vendor",
        "parameters": {
            "type": "object",
            "properties": {
                "vendor_name": {"type": "string", "description": "Name of the vendor"}
            },
            "required": ["vendor_name"]
        }
    }
]