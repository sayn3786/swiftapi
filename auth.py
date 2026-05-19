import os
import base64
import time
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY    = os.getenv("SWIFT_CONSUMER_KEY", "")
CONSUMER_SECRET = os.getenv("SWIFT_CONSUMER_SECRET", "")
LICENSE_ID      = os.getenv("SWIFT_LICENSE_ID", "")
LICENSE_SECRET  = os.getenv("SWIFT_LICENSE_SECRET", "")
TOKEN_URL       = os.getenv("SWIFT_TOKEN_URL", "https://sandbox.swift.com/oauth2/v1/token")
SCOPE           = os.getenv("SWIFT_SCOPE", "")

# ── Token cache (avoid re-requesting within the 30-min window) ──
_cached_token     = None
_token_expires_at = 0


def _is_token_valid() -> bool:
    return _cached_token is not None and time.time() < _token_expires_at - 30


# ── Mode 1: Password grant (primary SWIFT sandbox method) ──────────────────
# Requires: Consumer Key/Secret (Basic header) + License ID/Secret (body)

def get_token_password(scope: str = SCOPE) -> str:
    if not LICENSE_ID or not LICENSE_SECRET:
        print("[SKIP] Password grant: SWIFT_LICENSE_ID or SWIFT_LICENSE_SECRET not set in .env")
        return None

    encoded = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()

    data = {
        "grant_type": "password",
        "username": LICENSE_ID,
        "password": LICENSE_SECRET,
    }
    if scope:
        data["scope"] = scope

    response = requests.post(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        data=data,
    )

    if not response.ok:
        print(f"[ERROR] Password grant failed: {response.status_code} — {response.text}")
        return None

    token_data = response.json()
    _store_token(token_data)
    print(f"[OK] Token via password grant. Expires in: {token_data.get('expires_in')}s")
    return token_data["access_token"]


# ── Mode 2: JWT Bearer (for Messaging API / production PKI flows) ──────────
# Requires: SWIFT_CERT_PATH + SWIFT_KEY_PATH pointing to SWIFT-issued PKI cert

def get_token_jwt_bearer(scope: str = SCOPE) -> str:
    cert_path = os.getenv("SWIFT_CERT_PATH")
    key_path  = os.getenv("SWIFT_KEY_PATH")

    if not cert_path or not key_path:
        print("[SKIP] JWT Bearer: SWIFT_CERT_PATH or SWIFT_KEY_PATH not set in .env")
        return None

    try:
        import jwt as pyjwt
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        from cryptography.x509 import load_pem_x509_certificate
    except ImportError:
        print("[ERROR] Run: pip install PyJWT cryptography")
        return None

    with open(key_path, "rb") as f:
        private_key = load_pem_private_key(f.read(), password=None)
    with open(cert_path, "rb") as f:
        cert_pem = f.read()
        cert_b64 = base64.b64encode(cert_pem).decode()
        cert_subject = load_pem_x509_certificate(cert_pem).subject.rfc4514_string()

    now = int(time.time())
    assertion = pyjwt.encode(
        payload={
            "iat": now, "nbf": now, "exp": now + 300,
            "jti": uuid.uuid4().hex,
            "iss": CONSUMER_KEY,
            "sub": cert_subject,
            "aud": TOKEN_URL.replace("https://", ""),
        },
        headers={"alg": "RS256", "x5c": [cert_b64], "typ": "JWT"},
        key=private_key,
        algorithm="RS256",
    )

    encoded = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()

    response = requests.post(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
            "scope": scope,
        },
    )

    if not response.ok:
        print(f"[ERROR] JWT Bearer failed: {response.status_code} — {response.text}")
        return None

    token_data = response.json()
    _store_token(token_data)
    print(f"[OK] Token via JWT Bearer. Expires in: {token_data.get('expires_in')}s")
    return token_data["access_token"]


# ── Token cache helper ─────────────────────────────────────────────────────

def _store_token(token_data: dict):
    global _cached_token, _token_expires_at
    _cached_token     = token_data["access_token"]
    _token_expires_at = time.time() + int(token_data.get("expires_in", 1800))


# ── Public entry point ─────────────────────────────────────────────────────

def get_token(scope: str = SCOPE) -> str:
    if _is_token_valid():
        return _cached_token

    token = get_token_password(scope)
    if token:
        return token

    token = get_token_jwt_bearer(scope)
    if token:
        return token

    print("[ERROR] All auth methods failed. Check your .env credentials.")
    return None


if __name__ == "__main__":
    print("=== SWIFT OAuth Token Test ===\n")
    print(f"Consumer Key   : {CONSUMER_KEY}")
    print(f"License ID     : {LICENSE_ID or '❌ not set'}")
    print(f"Token URL      : {TOKEN_URL}")
    print(f"Scope          : {SCOPE or '(none)'}\n")

    token = get_token()
    if token:
        print(f"\n✅ Access Token:\n{token[:80]}...")
    else:
        print("\n❌ Failed. See .env.example for required variables.")
