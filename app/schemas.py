from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class ShortenRequest(BaseModel):
    url: HttpUrl
    expires_at: Optional[datetime] = None


class ShortenResponse(BaseModel):
    short_url: str
