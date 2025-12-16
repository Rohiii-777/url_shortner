from sqlalchemy.ext.asyncio import AsyncSession
from .crud import create_click_event


async def record_click(
    db: AsyncSession,
    short_code: str,
    user_agent: str | None,
    referer: str | None,
    ip_address: str | None,
):
    await create_click_event(
        db=db,
        short_code=short_code,
        user_agent=user_agent,
        referer=referer,
        ip_address=ip_address,
    )
