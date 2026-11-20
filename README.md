# Multi-Platform Poster (FastAPI)

`POST /posting` takes one short message (max 200 chars, exactly one link) and publishes it to
five platforms at once: **Telegram, Discord, Mastodon, Bluesky, DEV.to**. Each platform is
independent, so one failing never blocks the others.

## How it works

```
POST /posting ─► validate message ─► post to all 5 in parallel ─► check each post is public ─► JSON report
                 (schemas.py)         (services/posting.py)        (anonymous GET of the URL)
```

1. **Validate:** the message must be 1–200 chars with exactly one valid http(s) link, else HTTP 422.
2. **Fan out:** every platform runs concurrently (`asyncio.gather`). A platform without credentials,
   or one that errors or times out, is reported as `failed` with the reason. The rest still post.
3. **Verify:** for each successful post, an anonymous GET of the posted URL sets `publicly_accessible`.
   It is `null` when there is no public URL (Discord webhooks) or the URL can't be reached from the
   server's network.
4. **Report:** one result per platform: status, posted URL, public flag, date, time and error.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # fill in credentials (never commit .env)
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Docs: http://localhost:4000/docs  |  Tests: `pytest`

## Credentials

| Platform | Env vars | How to get them |
|---|---|---|
| Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Bot via @BotFather; add bot as admin of a **public** channel; chat id is `@channelname` |
| Discord | `DISCORD_WEBHOOK_URL` | Channel settings > Integrations > Webhooks |
| Mastodon | `MASTODON_INSTANCE_URL`, `MASTODON_ACCESS_TOKEN` | Preferences > Development > New application (`write:statuses`) |
| Bluesky | `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` | Settings > App Passwords |
| DEV.to | `DEVTO_API_KEY` | Settings > Extensions > Generate API key |

## Example

```bash
curl -X POST http://localhost:4000/posting -H "Content-Type: application/json" \
  -d '{"message": "Try our new product today https://example.com/signup"}'
```

```json
{
  "message": "Try our new product today https://example.com/signup",
  "results": [
    {"platform": "mastodon", "status": "success", "posted_url": "https://mastodon.social/@me/1234",
     "publicly_accessible": true, "date": "2026-11-20", "time": "00:39:14 +0530", "error": null},
    {"platform": "discord", "status": "success", "posted_url": null,
     "publicly_accessible": null, "date": "2026-11-20", "time": "00:39:14 +0530", "error": null},
    {"platform": "devto", "status": "failed", "posted_url": null, "publicly_accessible": null,
     "date": "2026-11-20", "time": "00:39:14 +0530", "error": "missing credentials in environment"}
  ]
}
```

(Trimmed to three platforms; the real response has all five.)

## Project layout

- `app/main.py`, `app/schemas.py`: FastAPI app, request validation and response models
- `app/platforms/`: `BasePlatform` (shared HTTP error handling and public check) plus one small module per platform
- `app/services/posting.py`: concurrent fan-out with per-platform error isolation

To add a platform, subclass `BasePlatform` (`is_configured()` and `post()`), then register it in `app/platforms/__init__.py`.
