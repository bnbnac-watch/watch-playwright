import asyncio
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright, Playwright
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "1"))

_semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
_playwright: Playwright | None = None


class RenderRequest(BaseModel):
    url: str
    wait_until: str = "networkidle"
    wait_for: str | None = None
    sleep: float = 0
    goto_timeout_ms: int = 30000
    wait_for_timeout_ms: int = 10000


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _playwright
    async with async_playwright() as p:
        _playwright = p
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/render")
async def render(req: RenderRequest):
    async with _semaphore:
        logger.info("render 시작: %s", req.url)
        browser = await _playwright.chromium.launch()
        try:
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(req.url, wait_until=req.wait_until, timeout=req.goto_timeout_ms)
            if req.wait_for:
                await page.wait_for_selector(req.wait_for, timeout=req.wait_for_timeout_ms)
            if req.sleep:
                await asyncio.sleep(req.sleep)
            html = await page.content()
            logger.info("render 완료: %s (%d bytes)", req.url, len(html))
            return {"html": html}
        except Exception as e:
            logger.error("render 실패: %s: %s", req.url, e)
            raise HTTPException(status_code=500, detail=str(e).splitlines()[0])
        finally:
            await browser.close()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, loop="asyncio")
