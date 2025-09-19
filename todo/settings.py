
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="todo/.env", 
        env_file_encoding="utf-8",
        env_prefix=""
    )
    jwt_secret: str = "your-super-secret-jwt-key-change-this-in-production"
    jwt_alg: str = "HS256"
    jwt_exp_minutes: int = 15
#cache the settings to avoid reloading them multiple times

@lru_cache
def get_settings() -> Settings:
    return Settings()
