import pytest
from datetime import datetime, timezone, timedelta


@pytest.mark.asyncio
async def test_shorten_url(client):
    response = await client.post(
        "/shorten",
        json={"url": "https://example.com"},
    )
    assert response.status_code == 200
    assert "short_url" in response.json()


@pytest.mark.asyncio
async def test_redirect(client):
    res = await client.post(
        "/shorten",
        json={"url": "https://example.com"},
    )
    code = res.json()["short_url"].split("/")[-1]

    redirect = await client.get(f"/{code}", follow_redirects=False)
    assert redirect.status_code == 302
    assert redirect.headers["location"].rstrip("/") == "https://example.com"


@pytest.mark.asyncio
async def test_expired_url(client):
    expired_time = datetime.now(timezone.utc) - timedelta(days=1)

    res = await client.post(
        "/shorten",
        json={
            "url": "https://example.com",
            "expires_at": expired_time.isoformat(),
        },
    )
    code = res.json()["short_url"].split("/")[-1]

    redirect = await client.get(f"/{code}")
    assert redirect.status_code == 404
