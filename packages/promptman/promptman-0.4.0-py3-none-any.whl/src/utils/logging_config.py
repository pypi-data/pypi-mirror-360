"""
Centralized logging configuration for the AI Prompt Manager application.

This module provides consistent logging setup throughout the application,
replacing scattered print statements with proper structured logging.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.config.settings import LogLevel, get_config


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to log levels for console output."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )

        # Format the message
        formatted = super().format(record)

        # Reset levelname for other formatters
        record.levelname = levelname

        return formatted


def setup_logging(
    log_level: Optional[LogLevel] = None,
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_colors: bool = True,
) -> None:
    """
    Set up centralized logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses config or no file logging
        enable_console: Whether to enable console logging
        enable_colors: Whether to use colored console output
    """
    config = get_config()

    # Use provided log level or get from config
    level = log_level or config.log_level
    log_level_value = getattr(logging, level.value)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_value)

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level_value)

        console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        if enable_colors and sys.stdout.isatty():
            # Use colored formatter for terminals
            console_formatter: logging.Formatter = ColoredFormatter(console_format)
        else:
            # Use plain formatter for non-terminals (e.g., when redirected)
            console_formatter = logging.Formatter(console_format)

        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handler
    log_file_path = log_file or config.log_file
    if log_file_path:
        # Ensure log directory exists
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(log_level_value)

        # Use detailed format for file logging
        file_format = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)

        root_logger.addHandler(file_handler)

    # Set specific logger levels to reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("psycopg2").setLevel(logging.WARNING)
    logging.getLogger("gradio").setLevel(logging.WARNING)

    # Log the configuration
    logger = logging.getLogger("logging_config")
    logger.info(
        f"Logging configured - Level: {level.value}, Console: {enable_console}, File: {log_file_path}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (typically module name or class name)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class StructuredLogger:
    """
    Wrapper for structured logging with additional context.

    Provides methods for logging with structured data and context information.
    """

    def __init__(self, name: str):
        """Initialize structured logger."""
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}

    def set_context(self, **kwargs) -> None:
        """Set persistent context for all log messages."""
        self.context.update(kwargs)

    def clear_context(self) -> None:
        """Clear persistent context."""
        self.context.clear()

    def _log_with_context(self, level: int, message: str, **kwargs) -> None:
        """Log message with context and additional data."""
        # Combine persistent context with message-specific data
        log_data = {**self.context, **kwargs}

        # Create extra dict for structured logging
        extra = {"structured_data": log_data} if log_data else {}

        self.logger.log(level, message, extra=extra)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message with context."""
        self._log_with_context(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message with context."""
        self._log_with_context(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)


class AuditLogger:
    """
    Specialized logger for audit trails and security events.

    Provides methods for logging user actions, security events, and system changes.
    """

    def __init__(self):
        """Initialize audit logger."""
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)

    def log_user_action(
        self,
        action: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        success: bool = True,
    ) -> None:
        """
        Log user action for audit trail.

        Args:
            action: Action performed (e.g., 'create_prompt', 'login', 'delete_user')
            user_id: ID of user performing action
            tenant_id: Tenant ID (for multi-tenant applications)
            resource_type: Type of resource affected (e.g., 'prompt', 'user')
            resource_id: ID of affected resource
            details: Additional action details
            success: Whether the action was successful
        """
        audit_data = {
            "event_type": "user_action",
            "action": action,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
        }

        status = "SUCCESS" if success else "FAILURE"
        message = f"User action {action} - {status}"

        self.logger.info(message, extra={"audit_data": audit_data})

    def log_security_event(
        self,
        event_type: str,
        severity: str = "INFO",
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        """
        Log security-related event.

        Args:
            event_type: Type of security event (e.g., 'login_failure', 'token_expired')
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
            user_id: ID of user involved (if applicable)
            ip_address: Client IP address
            user_agent: Client user agent
            details: Additional event details
        """
        security_data = {
            "event_type": "security_event",
            "security_event_type": event_type,
            "severity": severity,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
        }

        message = f"Security event: {event_type}"

        # Log at appropriate level based on severity
        log_level = getattr(logging, severity.upper(), logging.INFO)
        self.logger.log(log_level, message, extra={"security_data": security_data})

    def log_system_event(
        self,
        event_type: str,
        component: str,
        details: Optional[dict] = None,
        success: bool = True,
    ) -> None:
        """
        Log system-level event.

        Args:
            event_type: Type of system event (e.g., 'startup', 'shutdown', 'migration')
            component: System component involved
            details: Additional event details
            success: Whether the event was successful
        """
        system_data = {
            "event_type": "system_event",
            "system_event_type": event_type,
            "component": component,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
        }

        status = "SUCCESS" if success else "FAILURE"
        message = f"System event {event_type} in {component} - {status}"

        log_level = logging.INFO if success else logging.ERROR
        self.logger.log(log_level, message, extra={"system_data": system_data})


# Global instances
_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def replace_print_statements():
    """
    Replace print statements with logging for better production practices.

    This function can be called to redirect print statements to logging,
    which is useful when migrating from print-based debugging.
    """
    import builtins

    original_print = builtins.print
    logger = get_logger("print_replacement")

    def logging_print(*args, **kwargs):
        # Convert print arguments to string
        message = " ".join(str(arg) for arg in args)

        # Log as info level
        logger.info(f"[PRINT] {message}")

        # Also call original print for backward compatibility
        original_print(*args, **kwargs)

    # Replace built-in print
    builtins.print = logging_print
