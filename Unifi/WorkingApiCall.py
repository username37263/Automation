import requests
import urllib3

# Replace these with your UniFi credentials and host information
username = ''
password = ''
host = '192.168.0.1'  # Your UDM IP address
port = 443

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# The API endpoint URL
base_url = f'https://{host}:{port}/'

# Create a session to persist cookies across requests
session = requests.Session()
session.verify = False  # Ignore SSL verification

# Authentication payload
auth_payload = {
    'username': username,
    'password': password,
    'remember': True
}

# Attempt to authenticate
try:
    # UniFi Dream Machine's specific login endpoint
    login_url = f'{base_url}api/auth/login'
    response = session.post(login_url, json=auth_payload)

    # Raise an exception if the login failed
    response.raise_for_status()

    # Example: Get a list of clients
    clients_url = f'{base_url}proxy/network/api/s/default/stat/sta'
    clients_response = session.get(clients_url)

    clients_response.raise_for_status()
    clients = clients_response.json()['data']

    for client_info in clients:
        print(f"Client MAC: {client_info['mac']}, IP: {client_info.get('ip', 'N/A')}, Name: {client_info.get('hostname', 'N/A')}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
