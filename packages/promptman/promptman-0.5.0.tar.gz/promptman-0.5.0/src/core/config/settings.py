"""
Centralized configuration management for the AI Prompt Manager application.

This module provides a type-safe, environment-aware configuration system
that validates settings and provides defaults for all application components.
"""

import os
import secrets
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from ..exceptions.base import ConfigurationException


class DatabaseType(Enum):
    """Supported database types."""

    SQLITE = "sqlite"
    POSTGRES = "postgres"


class LogLevel(Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OptimizationService(Enum):
    """Supported optimization services."""

    BUILTIN = "builtin"
    LANGWATCH = "langwatch"
    PROMPTPERFECT = "promptperfect"
    LANGSMITH = "langsmith"
    HELICONE = "helicone"


class TranslationService(Enum):
    """Supported translation services."""

    MOCK = "mock"
    OPENAI = "openai"
    GOOGLE = "google"
    LIBRE = "libre"


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    db_type: DatabaseType = DatabaseType.SQLITE
    db_path: str = "prompts.db"
    dsn: Optional[str] = None
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create database config from environment variables."""
        db_type_str = os.getenv("DB_TYPE", "sqlite").lower()
        try:
            db_type = DatabaseType(db_type_str)
        except ValueError:
            raise ConfigurationException(f"Invalid DB_TYPE: {db_type_str}")

        return cls(
            db_type=db_type,
            db_path=os.getenv("DB_PATH", "prompts.db"),
            dsn=os.getenv("POSTGRES_DSN"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        )

    def validate(self) -> None:
        """Validate database configuration."""
        if self.db_type == DatabaseType.POSTGRES and not self.dsn:
            raise ConfigurationException(
                "POSTGRES_DSN is required when using PostgreSQL"
            )

        if self.db_type == DatabaseType.SQLITE:
            # Ensure directory exists for SQLite database
            db_path = Path(self.db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class AuthConfig:
    """Authentication configuration settings."""

    secret_key: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    jwt_expiry_hours: int = 24
    password_min_length: int = 8
    multitenant_mode: bool = True
    local_dev_mode: bool = False

    # SSO Configuration
    sso_enabled: bool = False
    sso_client_id: Optional[str] = None
    sso_client_secret: Optional[str] = None
    sso_authority: Optional[str] = None
    sso_redirect_uri: Optional[str] = None

    # Entra ID Configuration
    entra_id_enabled: bool = False
    entra_client_id: Optional[str] = None
    entra_client_secret: Optional[str] = None
    entra_tenant_id: Optional[str] = None
    entra_redirect_uri: Optional[str] = None
    entra_scopes: str = "openid email profile User.Read"

    @classmethod
    def from_env(cls) -> "AuthConfig":
        """Create auth config from environment variables."""
        return cls(
            secret_key=os.getenv("SECRET_KEY", secrets.token_urlsafe(32)),
            jwt_expiry_hours=int(os.getenv("JWT_EXPIRY_HOURS", "24")),
            password_min_length=int(os.getenv("PASSWORD_MIN_LENGTH", "8")),
            multitenant_mode=os.getenv("MULTITENANT_MODE", "true").lower() == "true",
            local_dev_mode=os.getenv("LOCAL_DEV_MODE", "false").lower() == "true",
            # SSO
            sso_enabled=os.getenv("SSO_ENABLED", "false").lower() == "true",
            sso_client_id=os.getenv("SSO_CLIENT_ID"),
            sso_client_secret=os.getenv("SSO_CLIENT_SECRET"),
            sso_authority=os.getenv("SSO_AUTHORITY"),
            sso_redirect_uri=os.getenv("SSO_REDIRECT_URI"),
            # Entra ID
            entra_id_enabled=os.getenv("ENTRA_ID_ENABLED", "false").lower() == "true",
            entra_client_id=os.getenv("ENTRA_CLIENT_ID"),
            entra_client_secret=os.getenv("ENTRA_CLIENT_SECRET"),
            entra_tenant_id=os.getenv("ENTRA_TENANT_ID"),
            entra_redirect_uri=os.getenv("ENTRA_REDIRECT_URI"),
            entra_scopes=os.getenv("ENTRA_SCOPES", "openid email profile User.Read"),
        )

    def validate(self) -> None:
        """Validate authentication configuration."""
        if self.sso_enabled:
            missing_fields = []
            if not self.sso_client_id:
                missing_fields.append("SSO_CLIENT_ID")
            if not self.sso_client_secret:
                missing_fields.append("SSO_CLIENT_SECRET")
            if not self.sso_authority:
                missing_fields.append("SSO_AUTHORITY")

            if missing_fields:
                raise ConfigurationException(
                    f"SSO enabled but missing: {', '.join(missing_fields)}"
                )

        if self.entra_id_enabled:
            missing_fields = []
            if not self.entra_client_id:
                missing_fields.append("ENTRA_CLIENT_ID")
            if not self.entra_client_secret:
                missing_fields.append("ENTRA_CLIENT_SECRET")
            if not self.entra_tenant_id:
                missing_fields.append("ENTRA_TENANT_ID")

            if missing_fields:
                raise ConfigurationException(
                    f"Entra ID enabled but missing: {', '.join(missing_fields)}"
                )


@dataclass
class ExternalServicesConfig:
    """External services configuration."""

    # Optimization Services
    prompt_optimizer: OptimizationService = OptimizationService.BUILTIN
    langwatch_api_key: Optional[str] = None
    langwatch_project_id: str = "ai-prompt-manager"
    promptperfect_api_key: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    langsmith_project: Optional[str] = None
    helicone_api_key: Optional[str] = None

    # Translation Services
    translation_service: TranslationService = TranslationService.MOCK
    openai_api_key: Optional[str] = None
    google_translate_api_key: Optional[str] = None
    libretranslate_url: Optional[str] = None
    libretranslate_api_key: Optional[str] = None

    # Azure Services
    azure_ai_enabled: bool = False
    azure_ai_endpoint: Optional[str] = None
    azure_ai_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_key: Optional[str] = None
    azure_openai_version: str = "2024-02-15-preview"

    # Template Configuration
    prompt_template: Optional[str] = None
    enhancement_template: Optional[str] = None
    custom_template_variables: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "ExternalServicesConfig":
        """Create external services config from environment variables."""
        optimizer_str = os.getenv("PROMPT_OPTIMIZER", "builtin").lower()
        try:
            prompt_optimizer = OptimizationService(optimizer_str)
        except ValueError:
            prompt_optimizer = OptimizationService.BUILTIN

        translation_str = os.getenv("TRANSLATION_SERVICE", "mock").lower()
        try:
            translation_service = TranslationService(translation_str)
        except ValueError:
            translation_service = TranslationService.MOCK

        return cls(
            # Optimization
            prompt_optimizer=prompt_optimizer,
            langwatch_api_key=os.getenv("LANGWATCH_API_KEY"),
            langwatch_project_id=os.getenv("LANGWATCH_PROJECT_ID", "ai-prompt-manager"),
            promptperfect_api_key=os.getenv("PROMPTPERFECT_API_KEY"),
            langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
            langsmith_project=os.getenv("LANGSMITH_PROJECT"),
            helicone_api_key=os.getenv("HELICONE_API_KEY"),
            # Translation
            translation_service=translation_service,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            google_translate_api_key=os.getenv("GOOGLE_TRANSLATE_API_KEY"),
            libretranslate_url=os.getenv("LIBRETRANSLATE_URL"),
            libretranslate_api_key=os.getenv("LIBRETRANSLATE_API_KEY"),
            # Azure
            azure_ai_enabled=os.getenv("AZURE_AI_ENABLED", "false").lower() == "true",
            azure_ai_endpoint=os.getenv("AZURE_AI_ENDPOINT"),
            azure_ai_key=os.getenv("AZURE_AI_KEY"),
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_openai_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_openai_version=os.getenv(
                "AZURE_OPENAI_VERSION", "2024-02-15-preview"
            ),
            # Templates
            prompt_template=os.getenv("PROMPT_TEMPLATE"),
            enhancement_template=os.getenv("ENHANCEMENT_TEMPLATE"),
            custom_template_variables={},
        )


@dataclass
class AppConfig:
    """Main application configuration."""

    # Server settings
    host: str = "0.0.0.0"  # nosec B104: Binding to all interfaces is intentional
    port: int = 7860
    debug: bool = False

    # Application settings
    enable_api: bool = False
    default_language: str = "en"

    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[str] = None

    # Feature flags

    # Component configs
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    external_services: ExternalServicesConfig = field(
        default_factory=ExternalServicesConfig
    )

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create app config from environment variables."""
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        try:
            log_level = LogLevel(log_level_str)
        except ValueError:
            log_level = LogLevel.INFO

        return cls(
            host=os.getenv(
                "SERVER_HOST", "0.0.0.0"
            ),  # nosec B104: Binding to all interfaces is intentional for deployment
            port=int(os.getenv("SERVER_PORT", "7860")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            enable_api=os.getenv("ENABLE_API", "false").lower() == "true",
            default_language=os.getenv("DEFAULT_LANGUAGE", "en"),
            log_level=log_level,
            log_file=os.getenv("LOG_FILE"),
            # Component configs
            database=DatabaseConfig.from_env(),
            auth=AuthConfig.from_env(),
            external_services=ExternalServicesConfig.from_env(),
        )

    def validate(self) -> None:
        """Validate all configuration settings."""
        if not (1024 <= self.port <= 65535):
            raise ConfigurationException(f"Invalid port number: {self.port}")

        self.database.validate()
        self.auth.validate()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for logging/debugging."""
        config_dict = {
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "enable_api": self.enable_api,
            "multitenant_mode": self.auth.multitenant_mode,
            "database_type": self.database.db_type.value,
            "log_level": self.log_level.value,
        }

        # Don't include sensitive information
        return config_dict


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    Get the global application configuration.

    Creates and validates configuration on first call.
    """
    global _config
    if _config is None:
        _config = AppConfig.from_env()
        _config.validate()
    return _config


def reset_config() -> None:
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None
