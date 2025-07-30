import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file in current directory or from HOME/.env
load_dotenv()
dotenv_path = os.path.join(os.path.expanduser("~"), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

def execute_curating_red_stones():
    """
    Execute the Curating Red Stones lattice.
    This function visualizes and structures Red Stone metadata connections.
    """
    print("Curating Red Stones Lattice Activated")
    redstone_key = "your-redstone-key"
    redstone_data = fetch_redstone_data(redstone_key)
    if redstone_data:
        display_redstone_data(redstone_data)
        connect_redstone_metadata_streams(redstone_data)
    else:
        print("Error: Unable to fetch RedStone data.")

def fetch_redstone_data(key):
    url = f"{os.getenv('EH_API_URL')}/api/redstones/{key}"
    headers = {"Authorization": f"Bearer {os.getenv('EH_TOKEN')}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("Unauthorized: Invalid or missing authentication token.")
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
    return None

def display_redstone_data(data):
    print("RedStone Data:")
    for key, value in data.items():
        print(f"{key}: {value}")

def connect_redstone_metadata_streams(data):
    """
    Connect RedStone metadata streams to hydrate.sanctuary.protocol endpoints.
    """
    url = f"{os.getenv('HYDRATE_SANCTUARY_PROTOCOL_URL')}/api/hydrate"
    headers = {"Authorization": f"Bearer {os.getenv('EH_TOKEN')}"}
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            print("RedStone metadata streams connected successfully.")
        elif response.status_code == 401:
            print("Unauthorized: Invalid or missing authentication token.")
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
