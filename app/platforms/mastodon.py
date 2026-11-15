from app.config import Settings
from app.platforms.base import BasePlatform, PostOutcome


class Mastodon(BasePlatform):
    name = "mastodon"

    def __init__(self, client, settings: Settings):
        super().__init__(client)
        self.base = settings.mastodon_instance_url.rstrip("/")
        self.token = settings.mastodon_access_token

    def is_configured(self) -> bool:
        return bool(self.token)

    async def post(self, message: str) -> PostOutcome:
        r = await self.client.post(
            f"{self.base}/api/v1/statuses",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"status": message, "visibility": "public"},
        )
        self._raise_for_status(r)
        return PostOutcome(url=r.json()["url"])
