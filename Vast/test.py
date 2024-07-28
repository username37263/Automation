import requests
import json
import os

# Constants
API_KEY = ''
DISCORD_WEBHOOK_URL = ''
STATE_FILE = 'machine_state.json'
TIMEOUT_THRESHOLD = 300  # Minimum timeout in seconds to consider

def format_duration(seconds):
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    minutes = minutes % 60
    hours = hours % 24
    duration = []
    if days > 0:
        duration.append(f"{int(days)} days")
    if hours > 0:
        duration.append(f"{int(hours)} hours")
    if minutes > 0:
        duration.append(f"{int(minutes)} minutes")
    return ', '.join(duration) if duration else "0 minutes"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_state(state):
    with open(STATE_FILE, 'w') as file:
        json.dump(state, file)

def update_and_filter_machines(machines):
    state = load_state()
    new_state = {}
    filtered_machines = []

    print("Current state loaded:", state)  # Debug: Show loaded state

    for machine in machines:
        hostname = machine['hostname']
        if hostname in state:
            if state[hostname]['count'] == 0:
                state[hostname]['count'] = 1
            else:
                new_state[hostname] = state[hostname]
        else:
            new_state[hostname] = {'count': 0}
            filtered_machines.append(machine)

    for hostname in state:
        if hostname not in [m['hostname'] for m in machines]:
            state[hostname]['count'] += 1
            if state[hostname]['count'] <= 1:
                new_state[hostname] = state[hostname]

    save_state(new_state)
    print("New state saved:", new_state)  # Debug: Show new state

    return filtered_machines

def fetch_offline_machines():
    url = 'https://console.vast.ai/api/v0/machines/'
    headers = {'Accept': 'application/json', 'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        machines_data = response.json()['machines']
        timeout_machines = [
            {'hostname': m['hostname'], 'timeout': format_duration(m['timeout'])}
            for m in machines_data if 'timeout' in m and m['timeout'] >= TIMEOUT_THRESHOLD
        ]
        print("All detected timeouts:", timeout_machines)  # Debug: Log all detected timeouts
        return update_and_filter_machines(timeout_machines)
    else:
        print(f'Failed to fetch data: {response.status_code}')
        return []

def post_to_discord(machines):
    if machines:
        content = f"Timeout Machines: {len(machines)}"
        details = '\n'.join([f"Hostname: {machine['hostname']}, Timeout: {machine['timeout']}" for machine in machines])
        message = {"content": content + "\n" + details}
        response = requests.post(DISCORD_WEBHOOK_URL, json=message)
        if response.status_code == 204:
            print("Message successfully posted to Discord.")
        else:
            print(f"Failed to post to Discord: {response.status_code}, Response: {response.text}")
    else:
        print("No new or significant timeouts to report.")

def job():
    timeout_machines = fetch_offline_machines()
    if timeout_machines:
        print(f"Found {len(timeout_machines)} machines with significant timeouts.")
        post_to_discord(timeout_machines)
    else:
        print("No machines with significant timeouts found.")

# Execute the job
job()
