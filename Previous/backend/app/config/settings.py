from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
    app_name:str="SIH Financial Network Intelligence"
    api_prefix:str="/api/v1"
    frontend_url:str="http://localhost:5173"
    log_level:str="INFO"
    environment:str="development"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
@lru_cache
def get_settings(): return Settings()
