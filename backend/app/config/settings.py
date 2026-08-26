from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
    app_name:str="SIH Financial Network Intelligence"
    api_prefix:str="/api/v1"
    frontend_url:str="http://localhost:5173"
    log_level:str="INFO"
    environment:str="development"
    # --- machine learning ---
    # Share of the final risk score contributed by the trained XGBoost model.
    # The remainder comes from the calibrated domain rules. 1.0 = model only.
    ml_model_weight:float=0.70
    # Train a model on first use if backend/model/ is empty. Keeps a fresh clone
    # working without a setup step; pre-train in CI/Docker to avoid the delay.
    ml_auto_train:bool=True
    ml_auto_train_samples:int=6000
    ml_seed:int=42
    model_config=SettingsConfigDict(env_file=".env",extra="ignore",protected_namespaces=())
@lru_cache
def get_settings(): return Settings()
