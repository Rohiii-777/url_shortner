from sqlalchemy import Column, Integer, String, DateTime, func, Index, Boolean
from .db import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String(10), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, nullable=False, server_default="true")
    __table_args__ = (
        Index("ix_urls_short_code", "short_code"),
    )

class ClickEvent(Base):
    __tablename__ = "click_events"

    id = Column(Integer, primary_key=True)
    short_code = Column(String(10), nullable=False)
    user_agent = Column(String)
    referer = Column(String)
    ip_address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_click_short_code_time", "short_code", "created_at"),
    )
