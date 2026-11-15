from app.config import Settings
from app.platforms.base import BasePlatform, PostOutcome


class DevTo(BasePlatform):
    name = "devto"

    def __init__(self, client, settings: Settings):
        super().__init__(client)
        self.key = settings.devto_api_key

    def is_configured(self) -> bool:
        return bool(self.key)

    async def post(self, message: str) -> PostOutcome:
        title = message if len(message) <= 60 else message[:57] + "..."
        r = await self.client.post(
            "https://dev.to/api/articles",
            headers={"api-key": self.key},
            json={"article": {"title": title, "body_markdown": message, "published": True}},
        )
        self._raise_for_status(r)
        return PostOutcome(url=r.json()["url"])
