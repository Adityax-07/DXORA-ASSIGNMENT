from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request

from app.config import get_settings
from app.platforms import build_platforms
from app.schemas import PostRequest, PostResponse
from app.services.posting import post_to_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        app.state.platforms = build_platforms(client, settings)
        yield


app = FastAPI(title="Multi-Platform Poster", lifespan=lifespan)


@app.post("/posting", response_model=PostResponse)
async def posting(body: PostRequest, request: Request) -> PostResponse:
    results = await post_to_all(request.app.state.platforms, body.message)
    return PostResponse(message=body.message, results=results)
