from datetime import datetime
from fastapi import HTTPException, Request
from .cache import redis

RATE_LIMIT = 60  # requests
WINDOW_SECONDS = 60


def _window_key(ip: str) -> str:
    window = datetime.utcnow().strftime("%Y%m%d%H%M")
    return f"rl:shorten:{ip}:{window}"


async def rate_limit_shorten(request: Request):
    ip = request.client.host if request.client else "unknown"
    key = _window_key(ip)

    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, WINDOW_SECONDS)

    if count > RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Try again later.",
        )
