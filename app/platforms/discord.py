from app.config import Settings
from app.platforms.base import BasePlatform, PostOutcome


class Discord(BasePlatform):
    name = "discord"

    def __init__(self, client, settings: Settings):
        super().__init__(client)
        self.webhook = settings.discord_webhook_url

    def is_configured(self) -> bool:
        return bool(self.webhook)

    async def post(self, message: str) -> PostOutcome:
        r = await self.client.post(self.webhook, params={"wait": "true"}, json={"content": message})
        self._raise_for_status(r)
        # Discord messages have no anonymous public URL.
        return PostOutcome(url=None)
