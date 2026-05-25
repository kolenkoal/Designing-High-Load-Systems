import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

AUTH_URL = os.environ.get("AUTH_URL", "http://mock-auth:8001/auth")
DOWNSTREAM_URL = os.environ.get("DOWNSTREAM_URL", "http://mock-downstream:8002/api/ping")


@asynccontextmanager
async def lifespan(app: FastAPI):
    limits = httpx.Limits(max_connections=1000, max_keepalive_connections=200)
    timeout = httpx.Timeout(5.0, connect=2.0)
    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        app.state.http = client
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/ping")
async def ping():
    client: httpx.AsyncClient = app.state.http
    await client.get(AUTH_URL)
    await client.get(DOWNSTREAM_URL)
    return {"ok": True}
