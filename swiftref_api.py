"""
SwiftRef API client — v4.0.0 spec (Dec 2024)
Base URL: https://sandbox.swift.com/swiftrefdata/v5

Covers all sections:
  7  Account Numbers
  8  BICs
  9  BBANs
 10  IBANs
 11  National IDs
 12  Countries
 13  Currencies
 14  LEIs
 15  IBAN National IDs
 16  PMIs (Payment Market Infrastructures)
"""
import os
import json
import requests
from dotenv import load_dotenv
from auth import get_token

load_dotenv()

BASE_URL = os.getenv("SWIFT_BASE_URL", "https://sandbox.swift.com")
API_PATH = "/swiftrefdata/v5"   # per SwiftRef API spec v4.0.0 (Dec 2024)


def _headers() -> dict:
    token = get_token()
    if not token:
        raise RuntimeError("Could not obtain access token. Check your .env credentials.")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _get(path: str, params: dict = None) -> dict:
    url = f"{BASE_URL}{API_PATH}{path}"
    r = requests.get(url, headers=_headers(), params=params)
    print(f"[{r.status_code}] GET {path}")
    _print(r)
    return r.json() if r.ok else r.text


def _post(path: str, body: dict) -> dict:
    url = f"{BASE_URL}{API_PATH}{path}"
    r = requests.post(url, headers=_headers(), json=body)
    print(f"[{r.status_code}] POST {path}")
    _print(r)
    return r.json() if r.ok else r.text


def _print(r):
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text[:500])


# ── Section 7: Account Numbers ─────────────────────────────────────────────

def validate_account_number(account_number: str, bic: str = None,
                             country_code: str = None, national_id: str = None) -> dict:
    """7.3 Validate account number format against SwiftRef data."""
    body = {"account_number": account_number}
    if bic:          body["bic"]          = bic
    if country_code: body["country_code"] = country_code
    if national_id:  body["national_id"]  = national_id
    return _post("/account_numbers/validity", body)


# ── Section 8: BICs ────────────────────────────────────────────────────────

def get_bic_details(bic: str, effective_date: str = None) -> dict:
    """8.2 Get full details of a BIC (name, address, connectivity, services)."""
    params = {"effective_date": effective_date} if effective_date else None
    return _get(f"/bics/{bic}", params)


def check_bic_validity(bic: str, effective_date: str = None) -> dict:
    """8.3 Check if a BIC is valid. Returns validity code VBIC or IBIC."""
    params = {"effective_date": effective_date} if effective_date else None
    return _get(f"/bics/{bic}/validity", params)


def get_lei_for_bic(bic: str) -> dict:
    """8.4 Get the Legal Entity Identifier (LEI) for a BIC."""
    return _get(f"/bics/{bic}/lei")


def get_national_ids_for_bic(bic: str) -> dict:
    """8.5 Get all national bank IDs (sort codes, routing numbers) for a BIC."""
    return _get(f"/bics/{bic}/national_ids")


def validate_sepa_reachability(bic: str, payment_channel: str = None) -> dict:
    """8.6 Check if a BIC is reachable via SEPA."""
    params = {"payment_channel": payment_channel} if payment_channel else None
    return _post(f"/bics/{bic}/sepa/reachability", params or {})


def get_ssis_for_bic(bic: str, service_category_code: str = None, category: str = None) -> dict:
    """8.7 Get Standard Settlement Instructions (SSIs) for a BIC."""
    params = {}
    if service_category_code: params["service_category_code"] = service_category_code
    if category:              params["category"]               = category
    return _get(f"/bics/{bic}/ssis", params or None)


def get_connected_bic(bic: str) -> dict:
    """8.8 Get the connected BIC for a branch BIC."""
    return _get(f"/bics/{bic}/connected_bic")


# ── Section 9: BBANs ───────────────────────────────────────────────────────

def get_iban_from_bban(country_code: str, bban: str) -> dict:
    """9.1 Construct IBAN from a Basic Bank Account Number (BBAN)."""
    return _post("/ibans", {"country_code": country_code, "bban": bban})


def get_bban_elements(country_code: str) -> dict:
    """9.2 Get BBAN structure/elements for an IBAN country."""
    return _get(f"/ibans/{country_code}/elements")


# ── Section 10: IBANs ──────────────────────────────────────────────────────

def get_iban_details(iban: str) -> dict:
    """10.2 Get full details for an IBAN (constituent parts, country, bank)."""
    return _get(f"/ibans/{iban}")


def check_iban_validity(iban: str) -> dict:
    """10.3 Check validity of an IBAN. Returns IVAL or error code."""
    return _get(f"/ibans/{iban}/validity")


def get_bic_for_iban(iban: str) -> dict:
    """10.4 Get the BIC associated with an IBAN."""
    return _get(f"/ibans/{iban}/bic")


def construct_iban(country_code: str, code_identifier: str = None) -> dict:
    """10.5 Construct IBAN for a country from BBAN elements."""
    params = {}
    if code_identifier: params["code_identifier"] = code_identifier
    return _get(f"/ibans/{country_code}/construct", params or None)


# ── Section 11: National IDs ───────────────────────────────────────────────

def check_national_id_validity(national_id: str, id_type: str, country_code: str) -> dict:
    """11.2 Check validity of a national bank ID (sort code, routing number, etc.)."""
    return _get(f"/national_ids/{country_code}/{id_type}/{national_id}/validity")


def get_bics_for_national_id(national_id: str, id_type: str, country_code: str) -> dict:
    """11.3 Get BICs associated with a national bank identifier."""
    return _get(f"/national_ids/{country_code}/{id_type}/{national_id}/bics")


def get_national_id_details(national_id: str, id_type: str, country_code: str) -> dict:
    """11.4 Get full details for a national bank identifier."""
    return _get(f"/national_ids/{country_code}/{id_type}/{national_id}")


# ── Section 12: Countries ──────────────────────────────────────────────────

def validate_country_code(country_code: str) -> dict:
    """12.1 Validate an ISO country code."""
    return _get(f"/countries/{country_code}/validity")


def get_country_details(country_code: str) -> dict:
    """12.2 Get details for a country code."""
    return _get(f"/countries/{country_code}")


# ── Section 13: Currencies ─────────────────────────────────────────────────

def validate_currency_code(currency_code: str) -> dict:
    """13.1 Validate an ISO 4217 currency code."""
    return _get(f"/currencies/{currency_code}/validity")


def get_currency_details(currency_code: str) -> dict:
    """13.2 Get details for a currency code."""
    return _get(f"/currencies/{currency_code}")


def validate_currency_amount(currency_code: str, amount: str) -> dict:
    """13.3 Validate a currency amount (decimal places, format)."""
    return _get(f"/currencies/{currency_code}/amounts/{amount}/validity")


# ── Section 14: LEIs ───────────────────────────────────────────────────────

def get_bic_for_lei(lei: str) -> dict:
    """14.2 Get BIC for a Legal Entity Identifier."""
    return _get(f"/leis/{lei}/bic")


def validate_lei(lei: str) -> dict:
    """14.3 Validate an LEI."""
    return _get(f"/leis/{lei}/validity")


def get_lei_details(lei: str) -> dict:
    """14.4 Get full details for an LEI."""
    return _get(f"/leis/{lei}")


# ── Section 15: IBAN National IDs ─────────────────────────────────────────

def get_bic_for_iban_national_id(country_code: str, national_id: str) -> dict:
    """15.1 Get BIC from an IBAN national ID."""
    return _get(f"/iban_national_ids/{country_code}/{national_id}/bic")


# ── Section 16: PMIs (Payment Market Infrastructures) ─────────────────────

def search_pmis(country_code: str = None, currency: str = None,
                pmi_type: str = None, page: int = None) -> dict:
    """16.1 Search for Payment Market Infrastructures."""
    params = {}
    if country_code: params["country_code"] = country_code
    if currency:     params["currency"]      = currency
    if pmi_type:     params["pmi_type"]      = pmi_type
    if page:         params["page"]          = page
    return _get("/pmis", params or None)


def get_pmi_details(pmi_id: str) -> dict:
    """16.2 Get full details for a PMI."""
    return _get(f"/pmis/{pmi_id}")


def search_pmi_participants(pmi_id: str, national_id: str = None,
                             bic: str = None, page: int = None) -> dict:
    """16.3 Search participants in a PMI."""
    params = {}
    if national_id: params["national_id"] = national_id
    if bic:         params["bic"]         = bic
    if page:        params["page"]        = page
    return _get(f"/pmis/{pmi_id}/participants", params or None)


def get_pmi_participant_details(pmi_id: str, participant_id: str) -> dict:
    """16.4 Get details for a specific PMI participant."""
    return _get(f"/pmis/{pmi_id}/participants/{participant_id}")


def get_pmi_structure(pmi_id: str) -> dict:
    """16.5 Get the structural hierarchy of a PMI."""
    return _get(f"/pmis/{pmi_id}/structure")


# ── Demo runner ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== SwiftRef API v5 — Sandbox Demo ===\n")

    print("── 8.2 BIC details ──")
    get_bic_details("DEUTDEFF")

    print("\n── 8.3 Check BIC validity ──")
    check_bic_validity("DEUTDEFF")

    print("\n── 8.4 LEI for BIC ──")
    get_lei_for_bic("DEUTDEFF")

    print("\n── 8.5 National IDs for BIC ──")
    get_national_ids_for_bic("DEUTDEFF")

    print("\n── 10.3 Validate IBAN ──")
    check_iban_validity("DE89370400440532013000")

    print("\n── 10.4 BIC for IBAN ──")
    get_bic_for_iban("DE89370400440532013000")

    print("\n── 11.3 BICs for UK Sort Code ──")
    get_bics_for_national_id("205964", "SORT", "GB")

    print("\n── 12.2 Country details ──")
    get_country_details("DE")

    print("\n── 13.2 Currency details ──")
    get_currency_details("EUR")

    print("\n── 14.4 LEI details ──")
    get_lei_details("7LTWFZYICNSX8D621K86")

    print("\n── 16.1 Search PMIs (Germany, EUR) ──")
    search_pmis(country_code="DE", currency="EUR")
