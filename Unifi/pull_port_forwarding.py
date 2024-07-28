# Direct import from Auth.py
import requests
from Auth import get_authenticated_session, base_url

# Function to retrieve port forwarding rules
def fetch_port_forwarding_rules():
    session = get_authenticated_session()
    if not session:
        print("Unable to authenticate")
        return []

    try:
        # The endpoint to retrieve port forwarding rules
        port_forwarding_url = f'{base_url}proxy/network/api/s/default/rest/portforward'
        response = session.get(port_forwarding_url)
        response.raise_for_status()

        # Extract port forwarding rules information
        rules = response.json()['data']
        return rules

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during API request: {e}")
        return []

# Function to print port forwarding information
def print_port_forwarding_info(rules):
    if not rules:
        print("No port forwarding rules found.")
        return

    for rule in rules:
        name = rule.get('name', 'Unnamed Rule')
        src_ip = rule.get('src', 'All')
        dst_ip = rule.get('dst', 'N/A')
        dst_port = rule.get('dst_port', 'N/A')
        fwd_port = rule.get('fwd_port', 'N/A')
        enabled = rule.get('enabled', False)

        print(f"Rule: {name}")
        print(f"  Source IP: {src_ip}")
        print(f"  Destination IP: {dst_ip}")
        print(f"  Destination Port: {dst_port}")
        print(f"  Forward Port: {fwd_port}")
        print(f"  Enabled: {'Yes' if enabled else 'No'}\n")

# Fetch and print the port forwarding rules
port_forwarding_rules = fetch_port_forwarding_rules()
print_port_forwarding_info(port_forwarding_rules)
