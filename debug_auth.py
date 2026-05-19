"""
SWIFT OAuth Diagnostic v2 — properly URL-encodes credentials, shows exact payload.
Run: python debug_auth.py
"""
import os
import base64
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

KEY    = os.getenv("SWIFT_CONSUMER_KEY", "")
SECRET = os.getenv("SWIFT_CONSUMER_SECRET", "")
URL    = "https://sandbox.swift.com/oauth2/v1/token"

# ── Credential sanity check ──────────────────────────────────────────────────
print("=" * 60)
print("CREDENTIAL CHECK")
print("=" * 60)
print(f"Consumer Key    : {KEY}")
print(f"Secret length   : {len(SECRET)} chars")
print(f"Secret preview  : {SECRET[:4]}{'*' * (len(SECRET)-4) if len(SECRET) > 4 else '(too short!)'}")
print(f"Secret set      : {'YES' if SECRET and SECRET != 'your_consumer_secret_here' else '❌ NO'}")

special_chars = [c for c in '&=+#%@ ' if c in SECRET]
if special_chars:
    print(f"⚠ Special chars in secret: {special_chars} — must be URL-encoded in body")
else:
    print("Secret chars    : No special chars detected")

# Build properly URL-encoded values
encoded_basic = base64.b64encode(f"{KEY}:{SECRET}".encode()).decode()
key_enc    = quote_plus(KEY)
secret_enc = quote_plus(SECRET)

print(f"\nBase64 basic    : {encoded_basic[:30]}...")
print(f"URL-encoded key : {key_enc[:30]}")
print(f"URL-encoded sec : {secret_enc[:4]}{'*'*10}")

# ── Attempts (all using dict so requests handles encoding) ───────────────────
print("\n" + "=" * 60)
print("AUTH ATTEMPTS")
print("=" * 60)

attempts = [
    {
        "label": "1. Body dict — client_id/secret, no scope [PROPER ENCODING]",
        "headers": {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        "data": {"grant_type": "client_credentials", "client_id": KEY, "client_secret": SECRET},
    },
    {
        "label": "2. Body dict — client_id/secret + scope=swift.messaging.api",
        "headers": {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        "data": {"grant_type": "client_credentials", "client_id": KEY, "client_secret": SECRET,
                 "scope": "swift.messaging.api"},
    },
    {
        "label": "3. Basic auth dict — no scope [PROPER ENCODING]",
        "headers": {"Authorization": f"Basic {encoded_basic}",
                    "Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        "data": {"grant_type": "client_credentials"},
    },
    {
        "label": "4. Basic auth dict — scope=swift.messaging.api",
        "headers": {"Authorization": f"Basic {encoded_basic}",
                    "Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        "data": {"grant_type": "client_credentials", "scope": "swift.messaging.api"},
    },
    {
        "label": "5. requests HTTPBasicAuth — no scope",
        "headers": {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        "data": {"grant_type": "client_credentials"},
        "auth": (KEY, SECRET),
    },
]

success = False
for a in attempts:
    print(f"\n{a['label']}")
    try:
        kwargs = {"headers": a["headers"], "data": a["data"], "timeout": 10}
        if "auth" in a:
            kwargs["auth"] = a["auth"]
        r = requests.post(URL, **kwargs)
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
    print("NEXT STEPS:")
    print("1. Go to developer.swift.com → Apps → Your App → Credentials")
    print("2. Click 'Regenerate Secret' and copy the new value carefully")
    print("3. Paste into .env as SWIFT_CONSUMER_SECRET=<value>  (no quotes)")
    print("4. Make sure the app has at least one API product subscribed")
    print("5. Run this script again")
