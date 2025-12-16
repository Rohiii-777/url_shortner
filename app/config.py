from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "URL Shortener"
    base_url: str = "http://localhost:8000"
    redis_url: str = "redis://localhost:6379/0"
    database_url_sync: str
    # URL_SHORTENER_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/url_shortener

    database_url: str = "sqlite+aiosqlite:///./shortener.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="URL_SHORTENER_",
    )


settings = Settings()
