from fastapi import FastAPI, Depends, HTTPException,BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy.exc import IntegrityError

from .db import engine, Base, get_db
from . import crud
from .utils import generate_short_code, is_safe_url
from .schemas import ShortenRequest, ShortenResponse
from .config import settings
from datetime import datetime, timezone
from .cache import redis
from .tasks import record_click
from .ratelimit import rate_limit_shorten
from fastapi.responses import RedirectResponse
import logging
from .logging import setup_logging
import uuid
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    setup_logging()
    yield


app = FastAPI(lifespan=lifespan)
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.post("/shorten", response_model=ShortenResponse)
async def shorten_url(
    request: Request,
    payload: ShortenRequest,
    db: AsyncSession = Depends(get_db),
):
    if not is_safe_url(str(payload.url)):
        raise HTTPException(
            status_code=400,
            detail="Unsafe or invalid URL",
        )

    try:
        await rate_limit_shorten(request)
    except Exception:
        pass

    MAX_RETRIES = 5

    for _ in range(MAX_RETRIES):
        short_code = generate_short_code()
        try:
            url = await crud.create_url(
                db=db,
                original_url=str(payload.url),
                short_code=short_code,
                expires_at=payload.expires_at,
            )

            return {
                "short_url": f"{settings.base_url}/{url.short_code}"
            }
        except IntegrityError:
            await db.rollback()
            continue

    raise HTTPException(
        status_code=500,
        detail="Failed to generate unique short URL"
    )

import time



@app.get("/{short_code}")
async def redirect(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    start = time.perf_counter()
    cache_key = f"url:{short_code}"

    cached_url = None
    try:
        cached_url = await redis.get(cache_key)
    except Exception:
        pass  # Redis is optional

    if cached_url:
        logger.info(
            "redirect_lookup",
            extra={
                "short_code": short_code,
                "cache_hit": bool(cached_url),
            },
        )
        elapsed = time.perf_counter() - start

        logger.info(
            "redirect_complete",
            extra={
                "short_code": short_code,
                "latency_ms": round(elapsed * 1000, 2),
            },
        )


        return RedirectResponse(url=cached_url, status_code=302)

    # 2️⃣ Cache miss → DB
    url = await crud.get_url_by_code(db, short_code)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    if not url.is_active:
        raise HTTPException(status_code=404, detail="URL disabled")

    # 3️⃣ Expiry check
    if url.expires_at and url.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=404, detail="URL expired")

    # 4️⃣ Cache it
    ttl = None

    if url.expires_at:
        expires_at = url.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=404, detail="URL expired")
        
    background_tasks.add_task(
        record_click,
        db,
        short_code,
        request.headers.get("user-agent"),
        request.headers.get("referer"),
        request.client.host if request.client else None,
    )

    try:
        await redis.set(cache_key, url.original_url, ex=ttl)
    except Exception:
        pass

    logger.info(
        "redirect",
        extra={
            "short_code": short_code,
            "cache_hit": bool(cached_url),
        },
    )

    response = RedirectResponse(
        url=url.original_url,
        status_code=302,
    )

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"

    return response


@app.get("/health")
async def health():
    return {"status": "ok"}
