from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    api_key: str = "testkey"
    rate_limit: str = "1000/minute"
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
