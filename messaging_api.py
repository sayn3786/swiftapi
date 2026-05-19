"""
SWIFT Messaging API client — FIN (MT), InterAct (MX/ISO 20022), FileAct.

⚠️  REQUIRES: Active Alliance Cloud subscription (not needed for sandbox auth only).
    For sandbox testing without Alliance Cloud, use swiftref_api.py instead.
"""
import os
import json
import requests
from dotenv import load_dotenv
from auth import get_token

load_dotenv()

BASE_URL = os.getenv("SWIFT_BASE_URL", "https://sandbox.swift.com")
API_PATH = "/swift-messaging-api/v1"


def _headers() -> dict:
    token = get_token(scope="swift.messaging.api")
    if not token:
        raise RuntimeError("Could not obtain access token.")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def list_messages(service: str = None) -> dict:
    """
    List messages available to download.
    service: 'fin' | 'interact' | 'fileact' | None (all)
    """
    url = f"{BASE_URL}{API_PATH}/messages"
    params = {"service": service} if service else {}
    r = requests.get(url, headers=_headers(), params=params)
    print(f"\n[LIST MESSAGES] {r.status_code}")
    print(json.dumps(r.json(), indent=2))
    return r.json()


def download_message(message_id: str) -> dict:
    """Download a specific message by ID."""
    url = f"{BASE_URL}{API_PATH}/messages/{message_id}"
    r = requests.get(url, headers=_headers())
    print(f"\n[DOWNLOAD {message_id}] {r.status_code}")
    print(json.dumps(r.json(), indent=2))
    return r.json()


def send_fin_message(sender_bic: str, receiver_bic: str, mt_content: str) -> dict:
    """Send a FIN (MT) message."""
    url = f"{BASE_URL}{API_PATH}/messages"
    payload = {
        "service": "fin",
        "from": sender_bic,
        "to": receiver_bic,
        "content": mt_content,
    }
    r = requests.post(url, headers=_headers(), json=payload)
    print(f"\n[SEND FIN] {r.status_code}")
    print(json.dumps(r.json(), indent=2))
    return r.json()


def send_mx_message(sender_bic: str, receiver_bic: str, mx_xml: str) -> dict:
    """Send an InterAct (ISO 20022 MX) message."""
    url = f"{BASE_URL}{API_PATH}/messages"
    payload = {
        "service": "interact",
        "from": sender_bic,
        "to": receiver_bic,
        "content": mx_xml,
    }
    r = requests.post(url, headers=_headers(), json=payload)
    print(f"\n[SEND MX] {r.status_code}")
    print(json.dumps(r.json(), indent=2))
    return r.json()


def get_reports(report_type: str = "transmission") -> dict:
    """
    Get delivery/transmission reports.
    report_type: 'transmission' | 'delivery'
    """
    url = f"{BASE_URL}{API_PATH}/reports"
    r = requests.get(url, headers=_headers(), params={"type": report_type})
    print(f"\n[REPORTS:{report_type}] {r.status_code}")
    print(json.dumps(r.json(), indent=2))
    return r.json()


# ── Sample payloads ─────────────────────────────────────────────────────────

SAMPLE_MT103 = (
    "{1:F01BANKBEBBAXXX0000000000}"
    "{2:I103BANKDEBBXXXXN}"
    "{4:\n"
    ":20:REF20240101001\n"
    ":23B:CRED\n"
    ":32A:240101EUR5000,00\n"
    ":50K:/BE71096123456769\nACME CORP BRUSSELS\n"
    ":59:/DE89370400440532013000\nBENEFICIARY GMBH BERLIN\n"
    ":70:INVOICE 2024-001\n"
    ":71A:SHA\n"
    "-}"
)

SAMPLE_PACS008_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.12">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>MSG20240101001</MsgId>
      <CreDtTm>2024-01-01T10:00:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="EUR">5000.00</TtlIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-01-01</IntrBkSttlmDt>
    </GrpHdr>
  </FIToFICstmrCdtTrf>
</Document>"""


if __name__ == "__main__":
    print("=== SWIFT Messaging API — Sandbox Test ===")
    print("⚠️  Requires Alliance Cloud subscription for live use.\n")

    print("1. Listing available messages...")
    list_messages()

    print("\n2. Transmission reports...")
    get_reports("transmission")

    print("\n3. Sending MT103 FIN message...")
    send_fin_message("BANKBEBBAXXX", "DEUTDEDBXXX", SAMPLE_MT103)
