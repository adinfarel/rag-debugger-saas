"""
Configuration management for the Autonomous RAG Debugger SaaS.
Uses Pydantic BaseSettings to load environment variables safely.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str
    ENVIRONMENT: str = "environment"
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()