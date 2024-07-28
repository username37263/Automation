import requests
import schedule
import time
import json

# Constants
API_KEY = '015e0a2ebc6b134c57b9363e1842d656050eddfc909b8d4435e6d475c20d0990'
DISCORD_WEBHOOK_URL = ''

def fetch_machines_with_errors():
    # Define the API endpoint
    url = 'https://console.vast.ai/api/v0/machines/'

    # Setup the headers with the API key using 'Bearer'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    # Make the API request
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        machines_data = response.json()['machines']
        # Filter for machines with error descriptions
        machines_with_errors = [machine for machine in machines_data if machine.get('error_description')]
        return machines_with_errors
    else:
        print(f'Failed to fetch data: {response.status_code}')
        return []

def post_to_discord(machines):
    # Prepare the message
    if machines:
        content = f"Machines with Errors: {len(machines)}"
        details = '\n'.join([f"ID: {machine['id']}, Hostname: {machine['hostname']}, Error: {machine['error_description']}" for machine in machines])
        message = {"content": content + "\n" + details}
    else:
        message = {"content": "No machine errors found currently."}
    
    # Post the message to Discord
    requests.post(DISCORD_WEBHOOK_URL, json=message)

def job():
    machines_with_errors = fetch_machines_with_errors()
    if machines_with_errors:
        print(f"Found {len(machines_with_errors)} machines with errors.")
    else:
        print("No machines with errors found.")
    post_to_discord(machines_with_errors)

# Schedule the job every 15 minutes
schedule.every(1).minutes.do(job)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
