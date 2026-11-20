from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import httpx


class PlatformError(Exception):
    """Raised by a platform for any expected failure (config, API error)."""


@dataclass
class PostOutcome:
    url: Optional[str] = None


class BasePlatform(ABC):
    name: str

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @abstractmethod
    def is_configured(self) -> bool: ...

    @abstractmethod
    async def post(self, message: str) -> PostOutcome: ...

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.status_code >= 400:
            raise PlatformError(f"HTTP {resp.status_code}: {resp.text[:300]}")

    async def check_public(self, url: Optional[str]) -> Optional[bool]:
        """Anonymous GET of the posted URL; None if there is no URL or it could not be reached.

        A network/TLS failure says nothing about the post itself (e.g. t.me is blocked on some
        networks), so it is reported as unknown rather than as not public.
        """
        if not url:
            return None
        try:
            r = await self.client.get(url, follow_redirects=True)
            return r.status_code == 200
        except httpx.HTTPError:
            return None
