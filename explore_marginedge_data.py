# Because I didnt read the docs 
# "we used to be a proper society"

import os
from dotenv import load_dotenv
from marginedge_client import MarginEdgeClient
import json

# Load environment variables
load_dotenv()

# Initialize client
marginedge_client = MarginEdgeClient(os.getenv('MARGINEDGE_API_KEY'))
restaurant_unit_id = os.getenv('RESTAURANT_UNIT_ID')

# File to store our data
DATA_FILE = 'restaurant_data.json'

def update_data():
    """Fetch new data and update our stored data"""
    new_data = marginedge_client.get_all_data(restaurant_unit_id)
    with open(DATA_FILE, 'w') as f:
        json.dump(new_data, f, indent=2)
    print("Data updated successfully")

def load_data():
    """Load data from file"""
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def explore_data(data, path=[]):
    """Recursively explore the data structure"""
    while True:
        if isinstance(data, dict):
            print(f"\nCurrent path: /{'/'.join(path)}")
            options = list(data.keys())
            for i, key in enumerate(options, 1):
                print(f"{i}. {key}")
            print("0. Go back")
            choice = input("Enter your choice (or 'q' to quit): ")
            if choice.lower() == 'q':
                return 'quit'
            if choice == '0':
                return
            try:
                choice = int(choice)
                if 1 <= choice <= len(options):
                    key = options[choice-1]
                    result = explore_data(data[key], path + [key])
                    if result == 'quit':
                        return 'quit'
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif isinstance(data, list):
            print(f"\nCurrent path: /{'/'.join(path)}")
            print(f"This is a list with {len(data)} items.")
            while True:
                choice = input("Enter item index to view (or 'b' to go back): ")
                if choice.lower() == 'b':
                    return
                if choice.lower() == 'q':
                    return 'quit'
                try:
                    index = int(choice)
                    if 0 <= index < len(data):
                        result = explore_data(data[index], path + [f"[{index}]"])
                        if result == 'quit':
                            return 'quit'
                    else:
                        print("Invalid index. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        else:
            print(f"\nCurrent path: /{'/'.join(path)}")
            print(f"Value: {data}")
            input("Press Enter to go back...")
            return

def main():
    if not os.path.exists(DATA_FILE):
        update_data()
    
    while True:
        print("\nMarginEdge Data Explorer")
        print("1. Explore data")
        print("2. Update data")
        print("3. Quit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            data = load_data()
            explore_data(data)
        elif choice == '2':
            update_data()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()