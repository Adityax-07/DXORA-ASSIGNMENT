# Multi-Platform Poster (FastAPI)

`POST /posting` takes one short message (max 200 chars, exactly one link) and publishes it to
five platforms in parallel: **Telegram, Discord, Mastodon, Bluesky, DEV.to**. Each platform is
independent; one failing never blocks the others.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # fill in credentials (never commit .env)
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Docs: http://localhost:4000/docs

## Credentials

| Platform | Env vars | How to get them |
|---|---|---|
| Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Bot via @BotFather; add bot as admin of a **public** channel; chat id is `@channelname` |
| Discord | `DISCORD_WEBHOOK_URL` | Channel settings > Integrations > Webhooks |
| Mastodon | `MASTODON_INSTANCE_URL`, `MASTODON_ACCESS_TOKEN` | Preferences > Development > New application (`write:statuses`) |
| Bluesky | `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` | Settings > App Passwords |
| DEV.to | `DEVTO_API_KEY` | Settings > Extensions > Generate API key |

A platform with missing credentials is reported as `failed` ("missing credentials").

## Sample request

```bash
curl -X POST http://localhost:4000/posting -H "Content-Type: application/json" \
  -d '{"message": "Try our new product today https://example.com/signup"}'
```

## Sample response

```json
{
  "message": "Try our new product today https://example.com/signup",
  "results": [
    {"platform": "mastodon", "status": "success", "posted_url": "https://mastodon.social/@me/1234",
     "publicly_accessible": true, "date": "2026-11-15", "time": "21:04:11 +0530", "error": null},
    {"platform": "discord", "status": "success", "posted_url": null,
     "publicly_accessible": null, "date": "2026-11-15", "time": "21:04:11 +0530", "error": null},
    {"platform": "devto", "status": "failed", "posted_url": null, "publicly_accessible": null,
     "date": "2026-11-15", "time": "21:04:11 +0530", "error": "missing credentials in environment"}
  ]
}
```

Invalid input returns HTTP 422 with a message such as `message must contain exactly one link (found 0)`.

> Replace the sample above with real output / screenshots from your own run before submitting.

## Design

- `app/schemas.py` – request validation (length, exactly one valid http(s) URL) and response models
- `app/platforms/` – `BasePlatform` + one module per platform
- `app/services/posting.py` – concurrent fan-out with per-platform error isolation
- `publicly_accessible` is determined by an anonymous GET of the posted URL (`null` when the platform exposes no public URL, e.g. Discord webhooks)

## Tests

```bash
pytest
```
