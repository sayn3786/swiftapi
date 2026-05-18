import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY    = os.getenv("SWIFT_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("SWIFT_CONSUMER_SECRET")
TOKEN_URL       = os.getenv("SWIFT_TOKEN_URL", "https://sandbox.swift.com/oauth2/v1/token")
SCOPE           = os.getenv("SWIFT_SCOPE", "swift.messaging.api")

def get_token() -> str:
    credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    response = requests.post(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "client_credentials",
            "scope": SCOPE,
        },
    )

    if response.status_code != 200:
        print(f"[ERROR] Token request failed: {response.status_code}")
        print(response.text)
        return None

    token_data = response.json()
    print(f"[OK] Token obtained. Expires in: {token_data.get('expires_in')}s")
    return token_data["access_token"]

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"\nAccess Token:\n{token[:60]}...")
