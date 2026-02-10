from urllib.parse import quote

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/funtech_orders"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    @computed_field
    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{quote(self.redis_password, safe='')}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_new_order_topic: str = "new_order"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    cors_origins: list[str] = ["http://localhost:8000"]
    rate_limit_default: str = "100/minute"

    log_level: str = "INFO"

settings = Settings()
