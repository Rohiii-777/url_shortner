# URL Shortener (FastAPI)

A production-oriented URL shortener focused on read scalability, correctness,
and operational reliability.

## Features
- FastAPI (async)
- Postgres + Alembic migrations
- Redis cache for redirect hot path
- Expiring links
- Rate limiting
- SSRF / unsafe URL protection
- Event-driven analytics (non-blocking)
- Graceful failure handling
- Load-tested redirect path

## Architecture
- Cache-first redirects (Redis → DB fallback)
- DB-enforced uniqueness
- Best-effort analytics
- Explicit failure degradation

## Why not Snowflake IDs?
Writes are rare and URLs must stay short.
Random Base62 with DB uniqueness provides the best tradeoff.

## Running locally
(brief steps)

## Future work
- Auth & quotas
- Read replicas
- Analytics dashboards
