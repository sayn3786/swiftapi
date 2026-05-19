"""
SWIFT OAuth Diagnostic — tries every known request format.
Run: python debug_auth.py
"""
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

KEY    = os.getenv("SWIFT_CONSUMER_KEY")
SECRET = os.getenv("SWIFT_CONSUMER_SECRET")

URLS = [
    "https://sandbox.swift.com/oauth2/v1/token",
    "https://sandbox.swift.com/oauth2/v2/token",
]

encoded = base64.b64encode(f"{KEY}:{SECRET}".encode()).decode()

attempts = [
    {
        "label": "1. Basic auth header, no scope, form body",
        "url": URLS[0],
        "headers": {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        "data": "grant_type=client_credentials",
    },
    {
        "label": "2. Credentials in body (client_id/client_secret), no scope",
        "url": URLS[0],
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": f"grant_type=client_credentials&client_id={KEY}&client_secret={SECRET}",
    },
    {
        "label": "3. Basic auth + scope=swift.messaging.api",
        "url": URLS[0],
        "headers": {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        "data": "grant_type=client_credentials&scope=swift.messaging.api",
    },
    {
        "label": "4. v2 endpoint, Basic auth, no scope",
        "url": URLS[1],
        "headers": {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        "data": "grant_type=client_credentials",
    },
    {
        "label": "5. Basic auth + Accept header + no scope",
        "url": URLS[0],
        "headers": {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        "data": "grant_type=client_credentials",
    },
    {
        "label": "6. Credentials in body + scope=swift.messaging.api",
        "url": URLS[0],
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": f"grant_type=client_credentials&client_id={KEY}&client_secret={SECRET}&scope=swift.messaging.api",
    },
]

print(f"Consumer Key : {KEY}")
print(f"Secret set   : {'YES' if SECRET and SECRET != 'your_consumer_secret_here' else '❌ NO — fill in .env'}\n")
print("=" * 60)

for a in attempts:
    print(f"\n{a['label']}")
    try:
        r = requests.post(a["url"], headers=a["headers"], data=a["data"], timeout=10)
        print(f"  Status : {r.status_code}")
        print(f"  Body   : {r.text[:200]}")
        if r.ok:
            print("  ✅ SUCCESS")
            print(f"  Token  : {r.json().get('access_token', '')[:60]}...")
            break
    except Exception as e:
        print(f"  ❌ Exception: {e}")

print("\n" + "=" * 60)
print("Copy the successful attempt number and share it.")
