"""
Base classes and shared functionality for the AI Prompt Manager application.
"""

from .database_manager import BaseDatabaseManager, DatabaseManager
from .repository_base import BaseRepository
from .service_base import BaseService, ServiceResult

__all__ = [
    "BaseDatabaseManager",
    "DatabaseManager",
    "BaseService",
    "ServiceResult",
    "BaseRepository",
]
