import os
import json
import requests
from dotenv import load_dotenv
from auth import get_token

load_dotenv()

BASE_URL = os.getenv("SWIFT_BASE_URL", "https://sandbox.swift.com")

def get_headers():
    token = get_token()
    if not token:
        raise RuntimeError("Could not obtain access token.")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def list_messages():
    """List messages available to download from Alliance Cloud."""
    url = f"{BASE_URL}/swift-messaging-api/v1/messages"
    response = requests.get(url, headers=get_headers())
    print(f"\n[LIST MESSAGES] Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response

def get_message(message_id: str):
    """Download a specific message by ID."""
    url = f"{BASE_URL}/swift-messaging-api/v1/messages/{message_id}"
    response = requests.get(url, headers=get_headers())
    print(f"\n[GET MESSAGE {message_id}] Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response

def send_fin_message(payload: dict):
    """Upload/send a FIN (MT) message."""
    url = f"{BASE_URL}/swift-messaging-api/v1/messages"
    response = requests.post(url, headers=get_headers(), json=payload)
    print(f"\n[SEND MESSAGE] Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response

def get_reports():
    """Retrieve transmission/delivery reports."""
    url = f"{BASE_URL}/swift-messaging-api/v1/reports"
    response = requests.get(url, headers=get_headers())
    print(f"\n[REPORTS] Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response

# --- Sample FIN (MT103) message payload ---
SAMPLE_MT103_PAYLOAD = {
    "message_type": "fin",
    "service_id": "01",
    "content": (
        "{1:F01BANKBEBBAXXX0000000000}"
        "{2:I103BANKDEBBXXXXN}"
        "{4:\n"
        ":20:REFERENCE12345\n"
        ":23B:CRED\n"
        ":32A:230101EUR1000,00\n"
        ":50K:/123456789\nORDERING CUSTOMER NAME\n"
        ":59:/DE89370400440532013000\nBENEFICIARY NAME\n"
        ":71A:SHA\n"
        "-}"
    )
}

if __name__ == "__main__":
    print("=== SWIFT Messaging API - Sandbox Test ===\n")
    print("1. Listing available messages...")
    list_messages()

    print("\n2. Fetching delivery reports...")
    get_reports()

    print("\n3. Sending a sample MT103 FIN message...")
    send_fin_message(SAMPLE_MT103_PAYLOAD)
