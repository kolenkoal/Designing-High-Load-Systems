import asyncio

from fastapi import FastAPI

app = FastAPI()


@app.get("/auth")
async def auth():
    await asyncio.sleep(0.003)
    return {"ok": True}
