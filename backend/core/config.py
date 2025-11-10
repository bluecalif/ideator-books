"""Application configuration using Pydantic Settings"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Supabase
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_anon_key: str = Field(..., alias="SUPABASE_ANON_KEY")
    supabase_service_key: str = Field(..., alias="SUPABASE_SERVICE_KEY")
    
    # OpenAI
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    
    # LLM Models (노드별 독립 설정 가능)
    anchor_mapper_model: str = Field(default="gpt-4o-mini", alias="ANCHOR_MAPPER_MODEL")
    reviewer_model: str = Field(default="gpt-4o-mini", alias="REVIEWER_MODEL")
    integrator_model: str = Field(default="gpt-4o-mini", alias="INTEGRATOR_MODEL")
    producer_model: str = Field(default="gpt-4o-mini", alias="PRODUCER_MODEL")
    
    # Application
    pythonpath: str = Field(default="", alias="PYTHONPATH")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # FastAPI
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    
    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="CORS_ORIGINS"
    )
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated string to list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        # 프로젝트 루트의 .env 파일을 찾기
        import os
        from pathlib import Path
        
        # backend/core/config.py 기준으로 프로젝트 루트 찾기
        project_root = Path(__file__).parent.parent.parent
        env_file = project_root / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

