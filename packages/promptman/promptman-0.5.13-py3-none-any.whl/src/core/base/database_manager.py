"""
Base database manager providing common database operations and connection management.

This module provides a foundation for all database managers in the application,
handling connection management, query execution, and error handling consistently.
"""

import logging
import sqlite3
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

from ..config.settings import DatabaseConfig, DatabaseType
from ..exceptions.base import ConfigurationException, DatabaseException


class BaseDatabaseManager(ABC):
    """
    Base class for all database managers.

    Provides common functionality for database operations including:
    - Connection management
    - Query execution with error handling
    - Transaction management
    - Schema initialization
    """

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize the database manager.

        Args:
            config: Database configuration. If None, loads from environment.
        """
        self.config = config or DatabaseConfig.from_env()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Validate configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate database configuration."""
        if self.config.db_type == DatabaseType.POSTGRES and not POSTGRES_AVAILABLE:
            raise ConfigurationException(
                "PostgreSQL support requires psycopg2 package. "
                "Install with: pip install psycopg2-binary"
            )

        self.config.validate()

    def get_connection(self):
        """
        Get a database connection.

        Returns:
            Database connection object (sqlite3.Connection or psycopg2.Connection)

        Raises:
            DatabaseException: If connection cannot be established
        """
        try:
            if self.config.db_type == DatabaseType.POSTGRES:
                if not self.config.dsn:
                    raise DatabaseException("PostgreSQL DSN not configured")

                conn = psycopg2.connect(self.config.dsn, cursor_factory=RealDictCursor)
                # Set isolation level for better performance
                conn.set_isolation_level(
                    psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
                )
                return conn
            else:
                conn = sqlite3.connect(self.config.db_path, timeout=30.0)
                conn.row_factory = sqlite3.Row
                # Enable foreign key support
                conn.execute("PRAGMA foreign_keys = ON")
                return conn

        except Exception as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            raise DatabaseException(f"Database connection failed: {str(e)}")

    @contextmanager
    def get_connection_context(self):
        """
        Get a database connection as a context manager.

        Automatically handles connection cleanup and error handling.

        Yields:
            Database connection object
        """
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        except Exception as e:  # noqa: F841
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    # nosec B110: Silent rollback failure is acceptable here
                    pass
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    self.logger.warning(f"Error closing connection: {str(e)}")

    def execute_query(
        self,
        query: str,
        params: Union[Tuple, Dict, None] = None,
        fetch_one: bool = False,
        fetch_all: bool = False,
    ) -> Any:
        """
        Execute a query with proper error handling.

        Args:
            query: SQL query to execute
            params: Query parameters (tuple for positional, dict for named)
            fetch_one: Whether to fetch only one result
            fetch_all: Whether to fetch all results

        Returns:
            Query results or None for non-SELECT queries

        Raises:
            DatabaseException: If query execution fails
        """
        with self.get_connection_context() as conn:
            try:
                cursor = conn.cursor()

                # Execute query with parameters
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Handle different result types
                if fetch_one:
                    result = cursor.fetchone()
                    return dict(result) if result else None
                elif fetch_all:
                    results = cursor.fetchall()
                    return [dict(row) for row in results] if results else []
                else:
                    # For INSERT/UPDATE/DELETE, commit and return success
                    conn.commit()
                    return cursor.rowcount

            except Exception as e:
                self.logger.error(
                    f"Query execution failed: {query[:100]}... Error: {str(e)}"
                )
                raise DatabaseException(f"Query execution failed: {str(e)}")

    def execute_many(self, query: str, params_list: List[Union[Tuple, Dict]]) -> int:
        """
        Execute a query multiple times with different parameters.

        Args:
            query: SQL query to execute
            params_list: List of parameter sets

        Returns:
            Number of affected rows

        Raises:
            DatabaseException: If query execution fails
        """
        with self.get_connection_context() as conn:
            try:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return int(cursor.rowcount) if cursor.rowcount is not None else 0

            except Exception as e:
                self.logger.error(f"Batch query execution failed: {str(e)}")
                raise DatabaseException(f"Batch query execution failed: {str(e)}")

    @contextmanager
    def transaction(self) -> Generator[Any, None, None]:
        """
        Execute operations within a database transaction.

        Automatically commits on success or rolls back on error.

        Yields:
            Database connection for transaction operations
        """
        with self.get_connection_context() as conn:
            try:
                # Start transaction
                if self.config.db_type == DatabaseType.POSTGRES:
                    conn.autocommit = False

                yield conn

                # Commit transaction
                conn.commit()

            except Exception as e:
                # Rollback on error
                try:
                    conn.rollback()
                except Exception:
                    # nosec B110: Silent rollback failure is acceptable here
                    pass
                self.logger.error(f"Transaction failed, rolled back: {str(e)}")
                raise DatabaseException(f"Transaction failed: {str(e)}")
            finally:
                if self.config.db_type == DatabaseType.POSTGRES:
                    conn.autocommit = True

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name: Name of the table to check

        Returns:
            True if table exists, False otherwise
        """
        try:
            if self.config.db_type == DatabaseType.POSTGRES:
                query = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = %s
                    )
                """
                result = self.execute_query(query, (table_name,), fetch_one=True)
                return result["exists"] if result else False
            else:
                query = """
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name=?
                """
                result = self.execute_query(query, (table_name,), fetch_one=True)
                return result is not None

        except Exception as e:
            self.logger.error(f"Error checking if table {table_name} exists: {str(e)}")
            return False

    def column_exists(self, table_name: str, column_name: str) -> bool:
        """
        Check if a column exists in a table.

        Args:
            table_name: Name of the table
            column_name: Name of the column to check

        Returns:
            True if column exists, False otherwise
        """
        try:
            if self.config.db_type == DatabaseType.POSTGRES:
                query = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns
                        WHERE table_name = %s AND column_name = %s
                    )
                """
                result = self.execute_query(
                    query, (table_name, column_name), fetch_one=True
                )
                return result["exists"] if result else False
            else:
                # For SQLite, get table info
                query = f"PRAGMA table_info({table_name})"
                columns = self.execute_query(query, fetch_all=True)
                return any(col["name"] == column_name for col in columns)

        except Exception as e:
            self.logger.error(
                f"Error checking if column {column_name} exists in "
                f"{table_name}: {str(e)}"
            )
            return False

    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the database.

        Returns:
            Dictionary containing database information
        """
        info = {
            "type": self.config.db_type.value,
            "path": (
                self.config.db_path
                if self.config.db_type == DatabaseType.SQLITE
                else None
            ),
            "dsn": (
                self.config.dsn
                if self.config.db_type == DatabaseType.POSTGRES
                else None
            ),
        }

        try:
            with self.get_connection_context() as conn:
                if self.config.db_type == DatabaseType.POSTGRES:
                    cursor = conn.cursor()
                    cursor.execute("SELECT version()")
                    info["version"] = cursor.fetchone()[0]
                else:
                    cursor = conn.cursor()
                    cursor.execute("SELECT sqlite_version()")
                    info["version"] = cursor.fetchone()[0]

        except Exception as e:
            self.logger.warning(f"Could not get database version: {str(e)}")
            info["version"] = "unknown"

        return info

    @abstractmethod
    def init_tables(self) -> None:
        """
        Initialize required tables for this manager.

        Must be implemented by subclasses to create their specific tables.
        """
        pass

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the database connection.

        Returns:
            Dictionary containing health status information
        """
        try:
            start_time = __import__("time").time()

            # Test basic connectivity
            with self.get_connection_context() as conn:
                cursor = conn.cursor()
                if self.config.db_type == DatabaseType.POSTGRES:
                    cursor.execute("SELECT 1")
                else:
                    cursor.execute("SELECT 1")

                result = cursor.fetchone()

            end_time = __import__("time").time()

            return {
                "status": "healthy" if result else "unhealthy",
                "response_time_ms": round((end_time - start_time) * 1000, 2),
                "database_type": self.config.db_type.value,
                "timestamp": __import__("datetime")
                .datetime.now(__import__("datetime").timezone.utc)
                .isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_type": self.config.db_type.value,
                "timestamp": __import__("datetime")
                .datetime.now(__import__("datetime").timezone.utc)
                .isoformat(),
            }


class DatabaseManager(BaseDatabaseManager):
    """
    Concrete implementation of BaseDatabaseManager.

    This is a general-purpose database manager that can be used
    directly when no specialized functionality is needed.
    """

    def init_tables(self) -> None:
        """
        Initialize basic tables.

        This implementation doesn't create any tables by default.
        Subclasses or external code should handle table creation.
        """
        pass
