"""
Configuration Management

This file handles all application configuration using Pydantic Settings.
It automatically loads environment variables from .env file and validates them.

Why we use this approach:
- Type safety: Pydantic validates types automatically
- Environment-aware: Different configs for dev/staging/prod
- Centralized: All config in one place
- Auto-completion: IDEs can suggest config options
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Pydantic will automatically:
    1. Load values from environment variables
    2. Load from .env file if present
    3. Validate types and required fields
    4. Provide default values where specified
    """

    # Application Configuration
    APP_NAME: str = Field(default_factory=lambda: os.getenv("APP_NAME", "AppNamePlaceholder"), description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # Database Configuration
    DATABASE_URL: str = Field(
        description="PostgreSQL database URL",
        json_schema_extra={"example": "postgresql://user:password@localhost:5432/app_db"}
    )

    # JWT Authentication
    JWT_SECRET_KEY: str = Field(
        description="Secret key for JWT token signing - MUST be secure in production"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT token expiration time in minutes"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=30,
        description="JWT refresh token expiration time in days"
    )

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = Field(
        description="Google OAuth client ID"
    )
    GOOGLE_CLIENT_SECRET: str = Field(
        description="Google OAuth client secret"
    )
    GOOGLE_REDIRECT_URI: str = Field(
        default="http://localhost:8000/auth/google/callback",
        description="Google OAuth redirect URI"
    )

    # Frontend Configuration
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend application URL"
    )

    # CORS Configuration
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins"
    )

    # Rate Limiting (for future use)
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        default=60,
        description="Default rate limit per minute"
    )

    # AI Configuration - Gemini 2.5 Flash Optimized
    GOOGLE_GEMINI_API_KEY: str = Field(
        default="",
        description="Google Gemini API key for AI features - Get from https://aistudio.google.com/app/apikey"
    )
    AI_MODEL_NAME: str = Field(
        default="gemini-2.5-flash-latest",
        description="Gemini model to use for AI responses (gemini-2.5-flash-latest for best performance)"
    )
    AI_TEMPERATURE: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="AI response creativity (0.0 = deterministic, 1.0 = very creative)"
    )
    AI_MAX_TOKENS: int = Field(
        default=2048,
        ge=1,
        le=8192,
        description="Maximum tokens for AI responses (Gemini 2.5 Flash supports up to 8192)"
    )
    AI_TOP_P: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="AI nucleus sampling parameter"
    )
    AI_TOP_K: int = Field(
        default=40,
        ge=1,
        le=100,
        description="AI top-k sampling parameter"
    )
    
    # AI Service Configuration
    AI_ENABLE_SAFETY_FILTERS: bool = Field(
        default=True,
        description="Enable Google's safety filters for content moderation"
    )
    AI_REQUEST_TIMEOUT: int = Field(
        default=30,
        description="Timeout for AI API requests in seconds"
    )
    
    # Rate Limiting for AI
    AI_RATE_LIMIT_RPM: int = Field(
        default=15,
        description="AI requests per minute limit (Gemini free tier: 15 RPM)"
    )
    AI_RATE_LIMIT_TPM: int = Field(
        default=1000000,
        description="AI tokens per minute limit (Gemini free tier: 1M TPM)"
    )

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )


# Create a single instance of settings
# This is imported throughout the application
settings = Settings()


def get_database_url() -> str:
    """
    Get the database URL.

    In the future, this function could handle different database URLs
    for different environments (dev/staging/prod).
    """
    return settings.DATABASE_URL


def get_cors_origins() -> List[str]:
    """
    Get CORS origins as a list.

    Converts the comma-separated string into a list of URLs.
    """
    return [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]


# Development helper function
def print_settings():
    """
    Print current settings (for debugging).

    NEVER prints sensitive information like secrets or passwords.
    """
    print("🔧 Current Settings:")
    print(f"  App Name: {settings.APP_NAME}")
    print(f"  Version: {settings.APP_VERSION}")
    print(f"  Debug: {settings.DEBUG}")
    print(f"  Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'Not configured'}")
    print(f"  CORS Origins: {get_cors_origins()}")
    print(f"  JWT Algorithm: {settings.JWT_ALGORITHM}")
    print(f"  JWT Expiry: {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes")


# Usage example:
# from app.core.config import settings
# print(settings.DATABASE_URL)