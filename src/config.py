from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Cloudflare Config
    CLOUDFLARE_ACCOUNT_ID: str = Field(..., env="CLOUDFLARE_ACCOUNT_ID")
    CLOUDFLARE_API_TOKEN: str = Field(..., env="CLOUDFLARE_API_TOKEN")
    CLOUDFLARE_D1_DATABASE_ID: str = Field(..., env="CLOUDFLARE_D1_DATABASE_ID")
    CLOUDFLARE_VECTORIZE_INDEX_NAME: str = Field("sgd-hbd-policy", env="CLOUDFLARE_VECTORIZE_INDEX_NAME")
    
    # App Config
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
