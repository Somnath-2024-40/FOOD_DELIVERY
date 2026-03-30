from pydantic_settings import BaseSettings,SettingsConfigDict
from typing import List
from functools import lru_cache

class Settings(BaseSettings):

    PROJECT_NAME: str
    # DATABASE
    DATABASE_URL: str
    # SECURITY
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_EMAIL: str

    BACKEND_CORS_ORIGINS: list[str]= ["http://localhost:3000", "http://localhost:8080"]


    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = True
    )


@lru_cache
def get_settings() ->Settings:
    return Settings()

settings = get_settings()

