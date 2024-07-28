from oauthlib.oauth1 import SIGNATURE_PLAINTEXT
from requests_oauthlib import OAuth1Session

# Set the MAAS host and port
MAAS_HOST = "http://IP of MAAS:5240/MAAS"
TAG_NAME = "Name of Tag"  # Replace "vast" with the name of the tag you want to retrieve nodes for

# Break the API key into its three components
CONSUMER_KEY, CONSUMER_TOKEN, SECRET = "API Token".split(":")

# Create an OAuth session for authentication
maas = OAuth1Session(CONSUMER_KEY, resource_owner_key=CONSUMER_TOKEN, resource_owner_secret=SECRET, signature_method=SIGNATURE_PLAINTEXT)

# Fetch nodes by tag
response = maas.get(f"{MAAS_HOST}/api/2.0/tags/{TAG_NAME}/op-nodes")

# Check response status code and content before parsing as JSON
if response.status_code != 200:
    print(f"Failed to fetch data: Status code {response.status_code}")
    print("Response text:", response.text)
else:
    try:
        # Parse the JSON response
        nodes = response.json()
        # Print IP addresses of each host
        for node in nodes:
            node_name = node.get('hostname')
            ips = node.get('ip_addresses')
            if ips:
                print(f"Hostname: {node_name}, IPs: {', '.join(ips)}")
            else:
                print(f"Hostname: {node_name}, IPs: None")
    except ValueError as e:
        print("Failed to decode JSON:", e)
