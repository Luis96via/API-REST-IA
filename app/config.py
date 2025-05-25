from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Configuración de la base de datos
    DATABASE_URL: str
    SUPABASE_DB_URL: Optional[str] = None
    
    # Configuración de OpenAI/OpenRouter
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
    MODEL_NAME: str = "anthropic/claude-3-opus:beta"
    
    # Claves de Supabase
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # Configuración de la API
    SITE_URL: str = "http://localhost:3000"
    SITE_NAME: str = "API REST Python MCP"
    
    # Configuración de CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Configuración de la API
    API_TITLE: str = "API REST Python MCP"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API REST para interactuar con la base de datos PostgreSQL usando MCP"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Permitir variables extra en el archivo .env

# Instancia global de la configuración
settings = Settings() 