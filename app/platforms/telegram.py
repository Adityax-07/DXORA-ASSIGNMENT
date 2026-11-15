from app.config import Settings
from app.platforms.base import BasePlatform, PlatformError, PostOutcome


class Telegram(BasePlatform):
    name = "telegram"

    def __init__(self, client, settings: Settings):
        super().__init__(client)
        self.token, self.chat_id = settings.telegram_bot_token, settings.telegram_chat_id

    def is_configured(self) -> bool:
        return bool(self.token and self.chat_id)

    async def post(self, message: str) -> PostOutcome:
        r = await self.client.post(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            json={"chat_id": self.chat_id, "text": message},
        )
        self._raise_for_status(r)
        msg = r.json()["result"]
        username = msg["chat"].get("username")
        if not username:
            raise PlatformError("posted, but chat has no public @username (not a public channel)")
        return PostOutcome(url=f"https://t.me/{username}/{msg['message_id']}")
