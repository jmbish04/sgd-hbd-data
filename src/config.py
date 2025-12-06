from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # Cloudflare Config
    CLOUDFLARE_ACCOUNT_ID: Optional[str] = Field(None, env="CLOUDFLARE_ACCOUNT_ID")
    CLOUDFLARE_API_TOKEN: Optional[str] = Field(None, env="CLOUDFLARE_API_TOKEN")
    CLOUDFLARE_D1_DATABASE_ID: Optional[str] = Field(None, env="CLOUDFLARE_D1_DATABASE_ID")
    CLOUDFLARE_VECTORIZE_INDEX_NAME: str = Field("sgd-hbd-policy", env="CLOUDFLARE_VECTORIZE_INDEX_NAME")
    
    # App Config
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
