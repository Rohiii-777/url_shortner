from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import URL, ClickEvent


async def create_url(
    db: AsyncSession,
    original_url: str,
    short_code: str,
    expires_at=None,
) -> URL:
    url = URL(
        original_url=original_url,
        short_code=short_code,
        expires_at=expires_at,
    )
    db.add(url)
    await db.commit()
    await db.refresh(url)
    return url


async def get_url_by_code(
    db: AsyncSession,
    short_code: str,
) -> URL | None:
    result = await db.execute(
        select(URL).where(URL.short_code == short_code)
    )
    return result.scalar_one_or_none()

async def create_click_event(
    db: AsyncSession,
    short_code: str,
    user_agent: str | None,
    referer: str | None,
    ip_address: str | None,
):
    event = ClickEvent(
        short_code=short_code,
        user_agent=user_agent,
        referer=referer,
        ip_address=ip_address,
    )
    db.add(event)
    await db.commit()
