from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Model configurations
    MODEL_NAME: str
    MAX_LENGTH: int = 512
    POOLING_MODE: str = "mean"
    TRUST_REMOTE_CODE: bool = True
    
    # Hugging Face settings
    HF_TOKEN: str
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    
    # Model specific settings
    TORCH_DTYPE: str = "bfloat16"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
