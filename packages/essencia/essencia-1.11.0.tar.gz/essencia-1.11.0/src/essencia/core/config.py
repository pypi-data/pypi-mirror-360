"""Configuration management for Essencia."""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration."""
    
    mongodb_url: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URL"
    )
    mongodb_database: str = Field(
        default="essencia",
        description="MongoDB database name"
    )
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    redis_db: int = Field(
        default=0,
        description="Redis database number"
    )


class AppConfig(BaseModel):
    """Application configuration."""
    
    app_name: str = Field(
        default="Essencia",
        description="Application name"
    )
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )
    host: str = Field(
        default="0.0.0.0",
        description="Application host"
    )
    port: int = Field(
        default=8550,
        description="Application port"
    )


class Config(BaseModel):
    """Main configuration class."""
    
    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        # Load .env file if it exists
        load_dotenv()
        
        return cls(
            app=AppConfig(
                app_name=os.getenv("APP_NAME", "Essencia"),
                debug=os.getenv("DEBUG", "false").lower() == "true",
                host=os.getenv("HOST", "0.0.0.0"),
                port=int(os.getenv("PORT", "8550"))
            ),
            database=DatabaseConfig(
                mongodb_url=os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
                mongodb_database=os.getenv("MONGODB_DATABASE", "essencia"),
                redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
                redis_db=int(os.getenv("REDIS_DB", "0"))
            )
        )