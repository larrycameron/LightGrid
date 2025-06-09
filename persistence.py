import csv
import os
from datetime import datetime

# File paths (can be moved to config if needed)
BATTERY_STATE_FILE = 'battery_state.csv'
BATTERY_HISTORY_FILE = 'battery_history.csv'
USERS_FILE = 'users.csv'
SESSIONS_FILE = 'sessions.csv'
EVENT_LOG_FILE = 'event_log.csv'
MESH_STATUS_HISTORY_FILE = 'mesh_status_history.csv'

# --- Battery State ---
def save_battery_state(current_charge_Ah):
    with open(BATTERY_STATE_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['current_charge_Ah'])
        writer.writerow([current_charge_Ah])

def load_battery_state():
    if not os.path.exists(BATTERY_STATE_FILE):
        return 0.0
    with open(BATTERY_STATE_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            return float(row['current_charge_Ah'])
    return 0.0

# --- Battery History ---
def append_battery_history(timestamp, voltage, current, charge_pct):
    file_exists = os.path.exists(BATTERY_HISTORY_FILE)
    with open(BATTERY_HISTORY_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'voltage', 'current', 'charge_pct'])
        writer.writerow([timestamp, voltage, current, charge_pct])

def load_battery_history():
    if not os.path.exists(BATTERY_HISTORY_FILE):
        return []
    with open(BATTERY_HISTORY_FILE, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

# --- Users ---
def save_users(users):
    # users: dict username -> hashed_password
    with open(USERS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['username', 'hashed_password'])
        for username, hashed in users.items():
            writer.writerow([username, hashed])

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    users = {}
    with open(USERS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users[row['username']] = row['hashed_password']
    return users

# --- Sessions ---
def save_sessions(sessions):
    # sessions: dict session_id -> username
    with open(SESSIONS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['session_id', 'username'])
        for sid, username in sessions.items():
            writer.writerow([sid, username])

def load_sessions():
    if not os.path.exists(SESSIONS_FILE):
        return {}
    sessions = {}
    with open(SESSIONS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sessions[row['session_id']] = row['username']
    return sessions

# --- Event Log ---
def append_event_log(event):
    file_exists = os.path.exists(EVENT_LOG_FILE)
    with open(EVENT_LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'event'])
        writer.writerow([datetime.now().isoformat(), event])

def load_event_log():
    if not os.path.exists(EVENT_LOG_FILE):
        return []
    with open(EVENT_LOG_FILE, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def append_mesh_status(node_statuses):
    # node_statuses: dict of node_id -> (status, power_mode, bandwidth)
    import json
    file_exists = os.path.exists(MESH_STATUS_HISTORY_FILE)
    with open(MESH_STATUS_HISTORY_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'node_statuses'])
        writer.writerow([datetime.now().isoformat(), json.dumps(node_statuses)])

def load_mesh_status_history():
    import json
    if not os.path.exists(MESH_STATUS_HISTORY_FILE):
        return []
    with open(MESH_STATUS_HISTORY_FILE, 'r') as f:
        reader = csv.DictReader(f)
        records = []
        for row in reader:
            row['node_statuses'] = json.loads(row['node_statuses'])
            records.append(row)
        return records 