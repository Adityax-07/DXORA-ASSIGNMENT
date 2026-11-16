import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.platforms.base import BasePlatform, PlatformError, PostOutcome


class Ok(BasePlatform):
    name = "ok"

    def is_configured(self):
        return True

    async def post(self, m):
        return PostOutcome(url="https://example.com/p/1")

    async def check_public(self, url):
        return True


class Boom(Ok):
    name = "boom"

    async def post(self, m):
        raise PlatformError("HTTP 401: bad token")


class Crash(Ok):
    name = "crash"

    async def post(self, m):
        raise RuntimeError("kaput")


@pytest.fixture
def client():
    with TestClient(app) as c:
        app.state.platforms = [Ok(None), Boom(None), Crash(None)]
        yield c


GOOD = "Check this out https://example.com/cta"


def test_failures_are_isolated(client):
    r = client.post("/posting", json={"message": GOOD})
    assert r.status_code == 200
    by = {x["platform"]: x for x in r.json()["results"]}
    assert by["ok"]["status"] == "success" and by["ok"]["publicly_accessible"] is True
    assert by["boom"]["status"] == "failed" and "401" in by["boom"]["error"]
    assert by["crash"]["status"] == "failed"


@pytest.mark.parametrize("msg", [
    "no link here",
    "two https://a.com links https://b.com",
    "x" * 201 + " https://a.com",
    "   ",
    "bad https://",
])
def test_validation_rejects(client, msg):
    assert client.post("/posting", json={"message": msg}).status_code == 422


def test_missing_field(client):
    assert client.post("/posting", json={}).status_code == 422
