"""Конфигурация приложения"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./elia.db"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Upload
    upload_dir: str = "static/uploads"
    max_upload_size: int = 52428800  # 50MB
    
    # Application
    app_name: str = "Elia AI Platform"
    version: str = "1.0.1"
    
    # Logging
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_dir: str = "logs"
    log_retention_days: int = 30  # Сколько дней хранить логи
    
    # OpenAI API
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4"


settings = Settings()

