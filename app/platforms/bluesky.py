from datetime import datetime, timezone

from app.config import Settings
from app.platforms.base import BasePlatform, PostOutcome
from app.schemas import URL_RE

PDS = "https://bsky.social/xrpc"


class Bluesky(BasePlatform):
    name = "bluesky"

    def __init__(self, client, settings: Settings):
        super().__init__(client)
        self.handle, self.password = settings.bluesky_handle, settings.bluesky_app_password

    def is_configured(self) -> bool:
        return bool(self.handle and self.password)

    async def post(self, message: str) -> PostOutcome:
        s = await self.client.post(
            f"{PDS}/com.atproto.server.createSession",
            json={"identifier": self.handle, "password": self.password},
        )
        self._raise_for_status(s)
        session = s.json()

        record = {
            "$type": "app.bsky.feed.post",
            "text": message,
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        m = URL_RE.search(message)
        if m:  # make the link clickable; facet offsets are UTF-8 byte positions
            start = len(message[: m.start()].encode())
            record["facets"] = [{
                "index": {"byteStart": start, "byteEnd": start + len(m.group().encode())},
                "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group()}],
            }]
        r = await self.client.post(
            f"{PDS}/com.atproto.repo.createRecord",
            headers={"Authorization": f"Bearer {session['accessJwt']}"},
            json={"repo": session["did"], "collection": "app.bsky.feed.post", "record": record},
        )
        self._raise_for_status(r)
        rkey = r.json()["uri"].rsplit("/", 1)[-1]
        return PostOutcome(url=f"https://bsky.app/profile/{session['handle']}/post/{rkey}")
