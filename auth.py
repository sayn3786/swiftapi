import os
import base64
import time
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY    = os.getenv("SWIFT_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("SWIFT_CONSUMER_SECRET")
TOKEN_URL       = os.getenv("SWIFT_TOKEN_URL", "https://sandbox.swift.com/oauth2/v1/token")
SCOPE           = os.getenv("SWIFT_SCOPE", "swift.messaging.api")

# ── Mode 1: Simple client_credentials (works for SwiftRef, KYC, Analytics) ──

def get_token_client_credentials(scope: str = SCOPE) -> str:
    credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    data = {"grant_type": "client_credentials"}
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
        print(f"[ERROR] client_credentials failed: {response.status_code}")
        print(response.text)
        return None

    token_data = response.json()
    print(f"[OK] Token obtained via client_credentials. Expires in: {token_data.get('expires_in')}s")
    return token_data["access_token"]


# ── Mode 2: JWT Bearer (required for Messaging API — needs PKI cert) ──
# Requires: SWIFT_CERT_PATH, SWIFT_KEY_PATH env vars pointing to your PKI files

def get_token_jwt_bearer(scope: str = SCOPE) -> str:
    cert_path = os.getenv("SWIFT_CERT_PATH")
    key_path  = os.getenv("SWIFT_KEY_PATH")

    if not cert_path or not key_path:
        print("[ERROR] JWT Bearer requires SWIFT_CERT_PATH and SWIFT_KEY_PATH in .env")
        print("        These are Swift-issued PKI certificates (not needed for sandbox of most APIs)")
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
        cert = load_pem_x509_certificate(cert_pem)
        cert_subject = cert.subject.rfc4514_string()

    now = int(time.time())
    payload = {
        "iat": now,
        "nbf": now,
        "exp": now + 300,           # 5 minutes
        "jti": uuid.uuid4().hex,
        "iss": CONSUMER_KEY,
        "sub": cert_subject,
        "aud": TOKEN_URL.replace("https://", ""),
    }
    headers = {
        "alg": "RS256",
        "x5c": [cert_b64],
        "typ": "JWT",
    }

    assertion = pyjwt.encode(payload=payload, headers=headers, key=private_key, algorithm="RS256")

    credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

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
        print(f"[ERROR] JWT Bearer failed: {response.status_code}")
        print(response.text)
        return None

    token_data = response.json()
    print(f"[OK] Token obtained via JWT Bearer. Expires in: {token_data.get('expires_in')}s")
    return token_data["access_token"]


# ── Auto-detect: try client_credentials first, fallback to JWT Bearer ──

def get_token(scope: str = SCOPE) -> str:
    token = get_token_client_credentials(scope)
    if token:
        return token
    print("[INFO] Falling back to JWT Bearer grant type...")
    return get_token_jwt_bearer(scope)


if __name__ == "__main__":
    print("=== SWIFT OAuth Token Test ===\n")
    print(f"Consumer Key : {CONSUMER_KEY}")
    print(f"Token URL    : {TOKEN_URL}")
    print(f"Scope        : {SCOPE}\n")

    # Try without scope first (some APIs don't need it)
    print("--- Attempt 1: client_credentials (no scope) ---")
    token = get_token_client_credentials(scope=None)

    if not token:
        print("\n--- Attempt 2: client_credentials (with scope) ---")
        token = get_token_client_credentials(scope=SCOPE)

    if not token:
        print("\n--- Attempt 3: JWT Bearer (requires PKI cert) ---")
        token = get_token_jwt_bearer(scope=SCOPE)

    if token:
        print(f"\n✅ Access Token (first 80 chars):\n{token[:80]}...")
    else:
        print("\n❌ All attempts failed. Check your Consumer Secret and SWIFT_SCOPE in .env")
