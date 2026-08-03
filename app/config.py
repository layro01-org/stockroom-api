from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://stockroom:stockroom@localhost:5432/stockroom"
    api_key: str = "demo-api-key"

    class Config:
        env_file = ".env"


settings = Settings()
