# SWIFT API Integration — Sandbox

Zero-footprint sandbox integration for the SWIFT Messaging API.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your SWIFT_CONSUMER_SECRET
```

## Test OAuth Token

```bash
python auth.py
```

## Test Messaging API

```bash
python messaging_api.py
```

## Files

| File | Purpose |
|---|---|
| `auth.py` | OAuth 2.0 token retrieval |
| `messaging_api.py` | Messaging API calls (list, get, send, reports) |
| `.env` | Your credentials (gitignored) |
| `.env.example` | Template for credentials |
