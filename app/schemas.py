import re
from typing import Literal, Optional

from pydantic import AnyHttpUrl, BaseModel, Field, TypeAdapter, field_validator

URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
_url_adapter = TypeAdapter(AnyHttpUrl)


class PostRequest(BaseModel):
    message: str = Field(..., description="Max 200 chars, exactly one call-to-action link")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("message must not be empty")
        if len(v) > 200:
            raise ValueError(f"message must be at most 200 characters (got {len(v)})")
        links = URL_RE.findall(v)
        if len(links) != 1:
            raise ValueError(f"message must contain exactly one link (found {len(links)})")
        try:
            _url_adapter.validate_python(links[0])
        except Exception:
            raise ValueError(f"{links[0]} is not a valid URL")
        return v


class PlatformResult(BaseModel):
    platform: str
    status: Literal["success", "failed"]
    posted_url: Optional[str] = None
    publicly_accessible: Optional[bool] = None
    date: str
    time: str
    error: Optional[str] = None


class PostResponse(BaseModel):
    message: str
    results: list[PlatformResult]
