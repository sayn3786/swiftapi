"""
SWIFT OAuth Diagnostic v3 — correct grant_type=password with License ID/Secret.
Run: python debug_auth.py
"""
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY    = os.getenv("SWIFT_CONSUMER_KEY", "")
CONSUMER_SECRET = os.getenv("SWIFT_CONSUMER_SECRET", "")
LICENSE_ID      = os.getenv("SWIFT_LICENSE_ID", "")
LICENSE_SECRET  = os.getenv("SWIFT_LICENSE_SECRET", "")
URL             = "https://sandbox.swift.com/oauth2/v1/token"

encoded_basic = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()

print("=" * 60)
print("CREDENTIAL CHECK")
print("=" * 60)
print(f"Consumer Key    : {CONSUMER_KEY}")
print(f"Consumer Secret : {CONSUMER_SECRET[:4]}{'*'*12}")
print(f"License ID      : {LICENSE_ID or '❌ NOT SET'}")
print(f"License Secret  : {LICENSE_SECRET[:4]+'*'*12 if LICENSE_SECRET else '❌ NOT SET'}")

print("\n" + "=" * 60)
print("AUTH ATTEMPTS")
print("=" * 60)

attempts = [
    {
        "label": "1. PASSWORD grant — Basic auth + License ID/Secret in body",
        "headers": {
            "Authorization": f"Basic {encoded_basic}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        "data": {
            "grant_type": "password",
            "username": LICENSE_ID,
            "password": LICENSE_SECRET,
        },
    },
    {
        "label": "2. PASSWORD grant — Basic auth + License ID/Secret + scope",
        "headers": {
            "Authorization": f"Basic {encoded_basic}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        "data": {
            "grant_type": "password",
            "username": LICENSE_ID,
            "password": LICENSE_SECRET,
            "scope": "swift.swiftref",
        },
    },
    {
        "label": "3. PASSWORD grant — Consumer Key/Secret as username/password (no Basic auth)",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        "data": {
            "grant_type": "password",
            "username": CONSUMER_KEY,
            "password": CONSUMER_SECRET,
        },
    },
    {
        "label": "4. CLIENT CREDENTIALS — Basic auth header (original approach)",
        "headers": {
            "Authorization": f"Basic {encoded_basic}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        "data": {"grant_type": "client_credentials"},
    },
]

success = False
for a in attempts:
    print(f"\n{a['label']}")
    try:
        r = requests.post(URL, headers=a["headers"], data=a["data"], timeout=10)
        print(f"  Status  : {r.status_code}")
        print(f"  Response: {r.text[:300]}")
        if r.ok:
            print("  ✅ SUCCESS!")
            print(f"  Token   : {r.json().get('access_token','')[:80]}...")
            success = True
            break
    except Exception as e:
        print(f"  ❌ Exception: {e}")

print("\n" + "=" * 60)
if not success:
    print("❌ All attempts failed.\n")
    print("WHAT YOU NEED:")
    print("  SWIFT uses TWO separate credentials:")
    print()
    print("  1. Consumer Key + Secret  →  from developer.swift.com (you have these)")
    print("     Used in: Authorization: Basic header")
    print()
    print("  2. License ID + License Secret  →  from swift.com account")
    print("     Used in: grant body as username + password")
    print()
    print("HOW TO GET License ID & Secret:")
    print("  Option A: Log into swift.com → My Profile → License Management")
    print("  Option B: If no swift.com account, email: developer-support@swift.com")
    print("            and ask for sandbox License ID and License Secret")
    print()
    print("Then add to your .env:")
    print("  SWIFT_LICENSE_ID=your_license_id")
    print("  SWIFT_LICENSE_SECRET=your_license_secret")
