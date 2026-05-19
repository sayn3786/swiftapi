# SWIFT API — Sandbox Integration

Zero-footprint Python client for SWIFT APIs. Targets the sandbox environment
at `https://sandbox.swift.com`.

---

## Project Structure

```
swiftapi/
├── auth.py            # OAuth token management (password grant + JWT Bearer)
├── swiftref_api.py    # SwiftRef: BIC, IBAN, LEI, national ID lookups
├── messaging_api.py   # Messaging API: FIN/MT, InterAct/MX, FileAct (needs Alliance Cloud)
├── debug_auth.py      # OAuth diagnostic — run when auth fails
├── .env               # Your credentials (gitignored)
├── .env.example       # Credential template
└── requirements.txt   # Python dependencies
```

---

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials (see below)
```

---

## Credentials — What You Need

SWIFT uses **two separate credential sets**:

| Credential | Purpose | Where to get |
|---|---|---|
| Consumer Key + Secret | `Authorization: Basic` header | developer.swift.com → Apps → Your App |
| License ID + Secret | `username` + `password` in OAuth body | swift.com → My Profile → Admin Functions → License ID Creation |

The OAuth token request (password grant) combines both:
```
POST https://sandbox.swift.com/oauth2/v1/token
Authorization: Basic base64(ConsumerKey:ConsumerSecret)
Content-Type: application/x-www-form-urlencoded

grant_type=password&username=<LicenseID>&password=<LicenseSecret>
```

> **No swift.com contract?** Email `developer-support@swift.com` for sandbox credentials.

---

## Usage

### Test authentication
```bash
python auth.py
```

### SwiftRef API (free sandbox, no Alliance Cloud needed)
```bash
python swiftref_api.py
```

### OAuth diagnostic (run when auth fails)
```bash
python debug_auth.py
```

### Messaging API (requires Alliance Cloud subscription)
```bash
python messaging_api.py
```

---

## API Coverage

### SwiftRef (`swiftref_api.py`)
| Function | Description |
|---|---|
| `get_bic_details(bic)` | Full BIC info — bank name, address, connectivity |
| `get_bic_for_iban(iban)` | Get BIC from any IBAN |
| `validate_iban(iban)` | Validate IBAN format and get components |
| `get_iban_details(iban)` | Full IBAN details including bank info |
| `get_bic_for_national_id(country, id, type)` | BIC from sort code / routing number / IFSC |
| `get_national_id_details(country, type, id)` | National bank ID details |
| `get_lei_details(lei)` | Legal Entity Identifier lookup |
| `get_ssi(bic, currency)` | Standard Settlement Instructions |

### Messaging API (`messaging_api.py`) — needs Alliance Cloud
| Function | Description |
|---|---|
| `list_messages(service)` | List downloadable FIN/InterAct/FileAct messages |
| `download_message(id)` | Download a specific message |
| `send_fin_message(from, to, mt)` | Send FIN (MT103, MT202, etc.) |
| `send_mx_message(from, to, xml)` | Send InterAct ISO 20022 MX message |
| `get_reports(type)` | Transmission/delivery reports |

---

## Sandbox vs Live Environments

| Environment | URL | Auth | Cost |
|---|---|---|---|
| **Sandbox** | `sandbox.swift.com` | Password grant (no PKI) | Free |
| **Pilot/T&T** | `api-test.swiftnet.sipn.swift.com` | Password grant or JWT | Free (needs SWIFT membership) |
| **Live** | `api.swiftnet.sipn.swift.com` | JWT Bearer + PKI cert | Paid subscription |

---

## Known Limitations

- Messaging API sandbox returns **static/mocked responses** (no real message exchange without Alliance Cloud)
- SwiftRef sandbox returns **dynamic responses** — suitable for integration testing
- This cloud environment (GitHub Codespaces / remote) is blocked by SWIFT's IP allowlist — run locally
