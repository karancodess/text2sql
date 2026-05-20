"""
Configuration management for the Text-to-SQL application.
Loads environment variables and provides centralized configuration.
"""
import os
from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/text2sql_db")
    postgres_user: str = os.getenv("POSTGRES_USER", "user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "password")
    postgres_db: str = os.getenv("POSTGRES_DB", "text2sql_db")
    
    # LLM Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    llm_provider: Literal["openai", "gemini"] = os.getenv("LLM_PROVIDER", "openai")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4")
    
    # Application Settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    model_config = {"env_file": ".env", "case_sensitive": False}


# Singleton instance
settings = Settings()
