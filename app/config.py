from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    api_key: str = "testkey"
    rate_limit: str = "1000/minute"
    cors_origins: list[str] = ["*"]
    database_url: str = "sqlite+aiosqlite:///./app.db"
    db_pool_size: int = 20
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 20
    redis_timeout: int = 5
    classification_ttl: int = 60 * 60 * 24  # 24 hours

    class Config:
        env_file = ".env"

settings = Settings()
