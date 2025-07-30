from pydantic import BaseModel, Field
from typing import Optional, List
import os

class BaseServiceConfig(BaseModel):
    """Base configuration class for all microservices."""
    
    # Service Identity
    SERVICE_NAME: str
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = Field(default=["http://localhost:3000"], env="ALLOWED_ORIGINS")
    
    # Database Configuration
    TIMESCALEDB_HOST: str = Field(env="TIMESCALEDB_HOST")
    TIMESCALEDB_PORT: int = Field(default=5432, env="TIMESCALEDB_PORT")
    TIMESCALEDB_DB: str = Field(env="TIMESCALEDB_DB")
    TIMESCALEDB_USER: str = Field(env="TIMESCALEDB_USER")
    TIMESCALEDB_PASSWORD: str = Field(env="TIMESCALEDB_PASSWORD")
    
    # Redis Configuration
    REDIS_HOST: str = Field(env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_CLUSTER_NODES: Optional[str] = Field(default=None, env="REDIS_CLUSTER_NODES")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Service Discovery
    SERVICE_PORT: int = Field(env="SERVICE_PORT")
    SERVICE_HOST: str = Field(default="0.0.0.0", env="SERVICE_HOST")
    
    @classmethod
    def create_for_service(cls, service_name: str, **overrides):
        """Create configuration instance for a specific service."""
        # Set SERVICE_NAME
        overrides["SERVICE_NAME"] = service_name
        
        # Load from environment with service-specific prefixes
        env_vars = {}
        
        # Check if we're using Pydantic v1 or v2
        if hasattr(cls, '__fields__'):
            # Pydantic v1
            fields = cls.__fields__
            for field_name, field_info in fields.items():
                env_key = getattr(field_info.field_info, 'extra', {}).get("env", field_name.upper()) if hasattr(field_info, 'field_info') else field_name.upper()
                
                # Try service-specific env var first, then general
                service_env_key = f"{service_name.upper()}_{env_key}"
                value = os.getenv(service_env_key) or os.getenv(env_key)
                
                if value is not None:
                    env_vars[field_name] = value
        else:
            # Pydantic v2
            fields = cls.model_fields
            for field_name, field_info in fields.items():
                # For Pydantic v2, check json_schema_extra or other metadata
                env_key = field_name.upper()
                if hasattr(field_info, 'json_schema_extra') and field_info.json_schema_extra:
                    env_key = field_info.json_schema_extra.get("env", field_name.upper())
                
                # Try service-specific env var first, then general
                service_env_key = f"{service_name.upper()}_{env_key}"
                value = os.getenv(service_env_key) or os.getenv(env_key)
                
                if value is not None:
                    env_vars[field_name] = value
        
        # Merge with overrides
        env_vars.update(overrides)
        
        return cls(**env_vars)
    
    @property
    def database_url(self) -> str:
        """Generate database URL for SQLAlchemy."""
        return f"postgresql://{self.TIMESCALEDB_USER}:{self.TIMESCALEDB_PASSWORD}@{self.TIMESCALEDB_HOST}:{self.TIMESCALEDB_PORT}/{self.TIMESCALEDB_DB}"
    
    @property
    def redis_url(self) -> str:
        """Generate Redis URL."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/"
    
    class Config:
        env_file = ".env"
        case_sensitive = True