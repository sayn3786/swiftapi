"""
SwiftRef API client — BIC lookup, IBAN validation, LEI lookup, national ID lookup.
Sandbox base URL: https://sandbox.swift.com/swiftref-api-phase1/v1
"""
import os
import json
import requests
from dotenv import load_dotenv
from auth import get_token

load_dotenv()

BASE_URL = os.getenv("SWIFT_BASE_URL", "https://sandbox.swift.com")
API_PATH = "/swiftref-api-phase1/v1"


def _headers() -> dict:
    token = get_token()
    if not token:
        raise RuntimeError("Could not obtain access token. Check your .env credentials.")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def _get(path: str) -> dict:
    url = f"{BASE_URL}{API_PATH}{path}"
    response = requests.get(url, headers=_headers())
    print(f"[{response.status_code}] GET {path}")
    try:
        data = response.json()
    except Exception:
        data = {"raw": response.text}
    print(json.dumps(data, indent=2))
    return data


# ── BIC Operations ─────────────────────────────────────────────────────────

def get_bic_details(bic: str) -> dict:
    """Get full details for a BIC (e.g. DEUTDEDB or DEUTDEBB500)."""
    return _get(f"/bics/{bic}")


def get_bic_for_iban(iban: str) -> dict:
    """Get the BIC associated with an IBAN."""
    return _get(f"/ibans/{iban}/bic")


def get_bic_for_national_id(country: str, national_id: str, id_type: str = "SORT") -> dict:
    """
    Get BIC for a national bank identifier.
    id_type examples: SORT (UK sort code), BLKC (ABA routing), IFSC (India)
    """
    return _get(f"/national-ids/{country}/{id_type}/{national_id}/bic")


# ── IBAN Operations ────────────────────────────────────────────────────────

def validate_iban(iban: str) -> dict:
    """Validate an IBAN and get its components (country, check digits, BBAN)."""
    return _get(f"/ibans/{iban}")


def get_iban_details(iban: str) -> dict:
    """Get full details for an IBAN including bank name and address."""
    return _get(f"/ibans/{iban}/details")


# ── LEI Operations ─────────────────────────────────────────────────────────

def get_lei_details(lei: str) -> dict:
    """Get Legal Entity Identifier (LEI) details."""
    return _get(f"/leis/{lei}")


# ── National ID Operations ─────────────────────────────────────────────────

def get_national_id_details(country: str, id_type: str, national_id: str) -> dict:
    """Get details for a national bank identifier."""
    return _get(f"/national-ids/{country}/{id_type}/{national_id}")


# ── SSI Operations ─────────────────────────────────────────────────────────

def get_ssi(bic: str, currency: str = None) -> dict:
    """Get Standard Settlement Instructions for a BIC."""
    path = f"/ssis/{bic}"
    if currency:
        path += f"?currency={currency}"
    return _get(path)


# ── Demo runner ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== SwiftRef API — Sandbox Demo ===\n")

    print("1. BIC details — Deutsche Bank Frankfurt")
    get_bic_details("DEUTDEDB")

    print("\n2. BIC for IBAN — German IBAN")
    get_bic_for_iban("DE89370400440532013000")

    print("\n3. Validate IBAN")
    validate_iban("GB29NWBK60161331926819")

    print("\n4. BIC from UK Sort Code")
    get_bic_for_national_id("GB", "205964", id_type="SORT")

    print("\n5. LEI details")
    get_lei_details("7H6GLXDRUGQFU57RNE97")
