from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    discord_webhook_url: str = ""
    mastodon_instance_url: str = "https://mastodon.social"
    mastodon_access_token: str = ""
    bluesky_handle: str = ""
    bluesky_app_password: str = ""
    devto_api_key: str = ""
    http_timeout: float = 15.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
