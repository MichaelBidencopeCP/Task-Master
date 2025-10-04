
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache
import os

class Settings(BaseSettings):
    if os.getenv("ENV") == "production":
        jwt_secret: str = Field(..., env="JWT_SECRET")
        jwt_alg: str = Field("HS256", env="JWT_ALG")
        jwt_exp_minutes: int = Field(15, env="JWT_EXP_MINUTES")
    else:
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
