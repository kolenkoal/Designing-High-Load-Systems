import asyncio

from fastapi import FastAPI

app = FastAPI()


@app.get("/api/ping")
async def ping():
    await asyncio.sleep(0.003)
    return {"ok": True}
