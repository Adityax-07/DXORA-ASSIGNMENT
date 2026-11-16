import asyncio
from datetime import datetime

import httpx

from app.platforms.base import BasePlatform, PlatformError
from app.schemas import PlatformResult


async def _post_one(p: BasePlatform, message: str) -> PlatformResult:
    now = datetime.now().astimezone()
    stamp = {"platform": p.name, "date": now.date().isoformat(), "time": now.strftime("%H:%M:%S %z")}
    if not p.is_configured():
        return PlatformResult(**stamp, status="failed", error="missing credentials in environment")
    try:
        outcome = await p.post(message)
        public = await p.check_public(outcome.url)
        return PlatformResult(**stamp, status="success", posted_url=outcome.url, publicly_accessible=public)
    except PlatformError as e:
        return PlatformResult(**stamp, status="failed", error=str(e))
    except httpx.HTTPError as e:
        return PlatformResult(**stamp, status="failed", error=f"network error: {e!r}")
    except Exception as e:  # one platform must never break the others
        return PlatformResult(**stamp, status="failed", error=f"unexpected error: {e!r}")


async def post_to_all(platforms: list[BasePlatform], message: str) -> list[PlatformResult]:
    return list(await asyncio.gather(*(_post_one(p, message) for p in platforms)))
