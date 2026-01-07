"""Application configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="GHDA-SaaS", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment: development/staging/production")
    debug: bool = Field(default=False, description="Debug mode")

    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    api_title: str = Field(default="Government Health Data Automation API", description="API title")
    api_description: str = Field(
        default="API for automating analysis of government health field survey reports",
        description="API description"
    )

    # Database
    database_url: str = Field(
        default="postgresql://ghda_user:ghda_password@localhost:5432/ghda_saas",
        description="Database connection URL"
    )
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow connections")
    database_pool_timeout: int = Field(default=30, description="Database pool timeout (seconds)")
    database_pool_recycle: int = Field(default=3600, description="Database pool recycle time (seconds)")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0", description="Celery broker URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", description="Celery result backend URL")
    celery_task_always_eager: bool = Field(default=False, description="Execute tasks synchronously for testing")
    celery_task_soft_time_limit: int = Field(default=300, description="Soft time limit for tasks (seconds)")
    celery_task_time_limit: int = Field(default=600, description="Hard time limit for tasks (seconds)")

    # Object Storage
    storage_type: str = Field(default="minio", description="Storage type: minio or s3")
    storage_endpoint: str = Field(default="localhost:9000", description="Storage endpoint")
    storage_access_key: str = Field(default="minioadmin", description="Storage access key")
    storage_secret_key: str = Field(default="minioadmin", description="Storage secret key")
    storage_bucket: str = Field(default="ghda-documents", description="Storage bucket name")
    storage_region: str = Field(default="us-east-1", description="Storage region")
    storage_secure: bool = Field(default=False, description="Use HTTPS for storage")

    # OCR
    tesseract_path: str = Field(default="/usr/bin/tesseract", description="Tesseract executable path")
    tesseract_lang: str = Field(default="eng+hin", description="Tesseract languages")
    ocr_timeout_seconds: int = Field(default=120, description="OCR timeout (seconds)")

    # Security
    secret_key: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT and encryption"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration (minutes)")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration (days)")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # File Upload
    max_upload_size_mb: int = Field(default=50, description="Maximum upload size (MB)")
    allowed_extensions: List[str] = Field(
        default=["docx", "pdf", "jpg", "jpeg", "png"],
        description="Allowed file extensions"
    )

    @field_validator("allowed_extensions", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v: str | List[str]) -> List[str]:
        """Parse allowed extensions from string or list."""
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",")]
        return [ext.lower() for ext in v]

    # Processing
    document_processing_timeout_seconds: int = Field(
        default=300,
        description="Document processing timeout (seconds)"
    )
    parser_confidence_threshold: float = Field(
        default=0.7,
        description="Minimum confidence threshold for parser",
        ge=0.0,
        le=1.0
    )
    phrase_match_confidence_threshold: float = Field(
        default=0.75,
        description="Minimum confidence threshold for phrase matching",
        ge=0.0,
        le=1.0
    )

    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format: json or text")
    log_file_path: str = Field(default="logs/app.log", description="Log file path")

    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, description="Metrics port")

    # Feature Flags
    enable_ocr: bool = Field(default=True, description="Enable OCR processing")
    enable_async_processing: bool = Field(default=True, description="Enable async document processing")
    enable_audit_logging: bool = Field(default=True, description="Enable audit logging")

    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
