import httpx

from app.config import Settings
from app.platforms.base import BasePlatform
from app.platforms.bluesky import Bluesky
from app.platforms.devto import DevTo
from app.platforms.discord import Discord
from app.platforms.mastodon import Mastodon
from app.platforms.telegram import Telegram


def build_platforms(client: httpx.AsyncClient, settings: Settings) -> list[BasePlatform]:
    return [cls(client, settings) for cls in (Telegram, Discord, Mastodon, Bluesky, DevTo)]
