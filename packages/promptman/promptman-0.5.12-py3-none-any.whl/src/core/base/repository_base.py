"""
Base repository class implementing the Repository pattern for data access.

This module provides a foundation for all data access layer components,
implementing common CRUD operations and database interaction patterns.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar

from ..exceptions.base import DatabaseException
from .database_manager import BaseDatabaseManager

T = TypeVar("T")  # Generic type for entity objects


class BaseRepository(ABC, Generic[T]):
    """
    Base repository implementing common CRUD operations.

    This class provides a foundation for all repository classes,
    implementing common database operations while allowing for
    entity-specific customization through abstract methods.

    Security Note: SQL queries in this class use f-strings for table and
    column names, which are controlled class attributes (not user input),
    combined with parameterized queries for all user data. This is a safe
    pattern used in ORMs and repository layers.
    """

    def __init__(self, db_manager: BaseDatabaseManager, table_name: str):
        """
        Initialize the repository.

        Args:
            db_manager: Database manager instance
            table_name: Name of the primary table for this repository
        """
        self.db_manager = db_manager
        self.table_name = table_name
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    @abstractmethod
    def _row_to_entity(self, row: Dict[str, Any]) -> T:
        """
        Convert database row to entity object.

        Args:
            row: Database row as dictionary

        Returns:
            Entity object of type T
        """
        pass

    @abstractmethod
    def _entity_to_dict(self, entity: T) -> Dict[str, Any]:
        """
        Convert entity object to dictionary for database operations.

        Args:
            entity: Entity object

        Returns:
            Dictionary representation suitable for database operations
        """
        pass

    @abstractmethod
    def _get_id_field(self) -> str:
        """
        Get the name of the primary key field.

        Returns:
            Name of the primary key field
        """
        pass

    def find_by_id(self, entity_id: Any) -> Optional[T]:
        """
        Find entity by primary key.

        Args:
            entity_id: Primary key value

        Returns:
            Entity object if found, None otherwise
        """
        try:
            id_field = self._get_id_field()
            # nosec B608: table_name and id_field are controlled, not user input
            query = f"SELECT * FROM {self.table_name} WHERE {id_field} = ?"

            if self.db_manager.config.db_type.value == "postgres":
                query = query.replace("?", "%s")

            row = self.db_manager.execute_query(query, (entity_id,), fetch_one=True)

            if row:
                return self._row_to_entity(row)
            return None

        except Exception as e:
            self.logger.error(
                f"Error finding {self.table_name} by ID {entity_id}: {str(e)}"
            )
            raise DatabaseException(f"Failed to find {self.table_name} by ID: {str(e)}")

    def find_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        """
        Find all entities with optional filtering and pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Field to order by
            order_desc: Whether to order in descending order
            filters: Optional field filters

        Returns:
            List of entity objects
        """
        try:
            # nosec B608: table_name is controlled, not user input
            query_parts = [f"SELECT * FROM {self.table_name}"]
            params = []

            # Add WHERE clause if filters provided
            if filters:
                where_conditions = []
                for field, value in filters.items():
                    if value is not None:
                        where_conditions.append(f"{field} = ?")
                        params.append(value)

                if where_conditions:
                    query_parts.append("WHERE " + " AND ".join(where_conditions))

            # Add ORDER BY clause
            if order_by:
                direction = "DESC" if order_desc else "ASC"
                query_parts.append(f"ORDER BY {order_by} {direction}")

            # Add pagination
            if limit:
                query_parts.append(f"LIMIT {limit}")
                if offset:
                    query_parts.append(f"OFFSET {offset}")

            query = " ".join(query_parts)

            # Convert to PostgreSQL syntax if needed
            if self.db_manager.config.db_type.value == "postgres":
                query = query.replace("?", "%s")

            rows = self.db_manager.execute_query(query, tuple(params), fetch_all=True)

            return [self._row_to_entity(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Error finding all {self.table_name}: {str(e)}")
            raise DatabaseException(
                f"Failed to find {self.table_name} records: {str(e)}"
            )

    def save(self, entity: T) -> T:
        """
        Save entity (insert or update).

        Args:
            entity: Entity to save

        Returns:
            Saved entity with updated fields (e.g., generated ID)
        """
        try:
            entity_dict = self._entity_to_dict(entity)
            id_field = self._get_id_field()

            # Check if this is an insert or update
            entity_id = entity_dict.get(id_field)

            if entity_id and self.find_by_id(entity_id):
                # Update existing entity
                return self._update_entity(entity_dict)
            else:
                # Insert new entity
                return self._insert_entity(entity_dict)

        except Exception as e:
            self.logger.error(f"Error saving {self.table_name}: {str(e)}")
            raise DatabaseException(f"Failed to save {self.table_name}: {str(e)}")

    def delete(self, entity_id: Any) -> bool:
        """
        Delete entity by primary key.

        Args:
            entity_id: Primary key value

        Returns:
            True if entity was deleted, False if not found
        """
        try:
            id_field = self._get_id_field()
            # nosec B608: table_name and id_field are controlled, not user input
            query = f"DELETE FROM {self.table_name} WHERE {id_field} = ?"

            if self.db_manager.config.db_type.value == "postgres":
                query = query.replace("?", "%s")

            affected_rows = self.db_manager.execute_query(query, (entity_id,))

            return bool(affected_rows) and affected_rows > 0

        except Exception as e:
            self.logger.error(
                f"Error deleting {self.table_name} ID {entity_id}: {str(e)}"
            )
            raise DatabaseException(f"Failed to delete {self.table_name}: {str(e)}")

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filtering.

        Args:
            filters: Optional field filters

        Returns:
            Number of matching entities
        """
        try:
            # nosec B608: table_name is controlled
            query_parts = [f"SELECT COUNT(*) as count FROM {self.table_name}"]
            params = []

            # Add WHERE clause if filters provided
            if filters:
                where_conditions = []
                for field, value in filters.items():
                    if value is not None:
                        where_conditions.append(f"{field} = ?")
                        params.append(value)

                if where_conditions:
                    query_parts.append("WHERE " + " AND ".join(where_conditions))

            query = " ".join(query_parts)

            # Convert to PostgreSQL syntax if needed
            if self.db_manager.config.db_type.value == "postgres":
                query = query.replace("?", "%s")

            result = self.db_manager.execute_query(query, tuple(params), fetch_one=True)

            return result["count"] if result else 0

        except Exception as e:
            self.logger.error(f"Error counting {self.table_name}: {str(e)}")
            raise DatabaseException(
                f"Failed to count {self.table_name} records: {str(e)}"
            )

    def exists(self, entity_id: Any) -> bool:
        """
        Check if entity exists by primary key.

        Args:
            entity_id: Primary key value

        Returns:
            True if entity exists, False otherwise
        """
        try:
            return self.find_by_id(entity_id) is not None
        except DatabaseException:
            return False

    def find_by_field(self, field: str, value: Any) -> List[T]:
        """
        Find entities by a specific field value.

        Args:
            field: Field name to search by
            value: Value to search for

        Returns:
            List of matching entities
        """
        return self.find_all(filters={field: value})

    def find_one_by_field(self, field: str, value: Any) -> Optional[T]:
        """
        Find single entity by a specific field value.

        Args:
            field: Field name to search by
            value: Value to search for

        Returns:
            First matching entity or None
        """
        results = self.find_by_field(field, value)
        return results[0] if results else None

    def _insert_entity(self, entity_dict: Dict[str, Any]) -> T:
        """
        Insert new entity into database.

        Args:
            entity_dict: Entity data as dictionary

        Returns:
            Inserted entity with generated fields
        """
        # Add timestamp fields if they exist
        current_time = datetime.now(timezone.utc)
        if "created_at" in entity_dict and entity_dict["created_at"] is None:
            entity_dict["created_at"] = current_time
        if "updated_at" in entity_dict:
            entity_dict["updated_at"] = current_time

        # Build INSERT query
        fields = [k for k, v in entity_dict.items() if v is not None]
        placeholders = ["?" for _ in fields]
        values = [entity_dict[field] for field in fields]

        if self.db_manager.config.db_type.value == "postgres":
            placeholders = ["%s" for _ in fields]
            # For PostgreSQL, use RETURNING to get the inserted record
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(fields)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """  # nosec B608: table_name and fields are controlled

            row = self.db_manager.execute_query(query, tuple(values), fetch_one=True)
            return self._row_to_entity(row)
        else:
            # For SQLite
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(fields)})
                VALUES ({', '.join(placeholders)})
            """  # nosec B608: table_name and fields are controlled

            self.db_manager.execute_query(query, tuple(values))

            # Get the inserted record by the last inserted row ID
            id_field = self._get_id_field()
            if id_field in entity_dict and entity_dict[id_field]:
                # Use provided ID
                result = self.find_by_id(entity_dict[id_field])
                if result is None:
                    raise DatabaseException(
                        f"Failed to retrieve saved {self.table_name}"
                    )
                return result
            else:
                # Use last insert rowid for auto-increment IDs
                with self.db_manager.get_connection_context() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT last_insert_rowid()")
                    last_id = cursor.fetchone()[0]
                    result = self.find_by_id(last_id)
                    if result is None:
                        raise DatabaseException(
                            f"Failed to retrieve saved {self.table_name}"
                        )
                    return result

    def _update_entity(self, entity_dict: Dict[str, Any]) -> T:
        """
        Update existing entity in database.

        Args:
            entity_dict: Entity data as dictionary

        Returns:
            Updated entity
        """
        id_field = self._get_id_field()
        entity_id = entity_dict[id_field]

        # Add updated timestamp if field exists
        if "updated_at" in entity_dict:
            entity_dict["updated_at"] = datetime.now(timezone.utc)

        # Build UPDATE query (exclude ID field from SET clause)
        update_fields = [
            k
            for k in entity_dict.keys()
            if k != id_field and entity_dict[k] is not None
        ]
        set_clauses = [f"{field} = ?" for field in update_fields]
        values = [entity_dict[field] for field in update_fields]
        values.append(entity_id)  # Add ID for WHERE clause

        query = f"""
            UPDATE {self.table_name}
            SET {', '.join(set_clauses)}
            WHERE {id_field} = ?
        """  # nosec B608: table_name and id_field are controlled

        if self.db_manager.config.db_type.value == "postgres":
            query = query.replace("?", "%s")

        affected_rows = self.db_manager.execute_query(query, tuple(values))

        if affected_rows == 0:
            raise DatabaseException(
                f"No {self.table_name} found with {id_field} = {entity_id}"
            )

        # Return updated entity
        result = self.find_by_id(entity_id)
        if result is None:
            raise DatabaseException(f"Failed to retrieve updated {self.table_name}")
        return result


class TenantAwareRepository(BaseRepository[T]):
    """
    Repository base class for multi-tenant aware entities.

    Automatically filters all operations by tenant_id to ensure
    complete data isolation between tenants.
    """

    def __init__(self, db_manager: BaseDatabaseManager, table_name: str):
        """Initialize tenant-aware repository."""
        super().__init__(db_manager, table_name)
        self.current_tenant_id: Optional[str] = None

    def set_tenant_context(self, tenant_id: str) -> None:
        """
        Set the current tenant context.

        Args:
            tenant_id: Current tenant ID
        """
        self.current_tenant_id = tenant_id

    def _ensure_tenant_context(self) -> None:
        """
        Ensure tenant context is set.

        Raises:
            DatabaseException: If tenant context is not set
        """
        if not self.current_tenant_id:
            raise DatabaseException(
                "Tenant context not set - call set_tenant_context() first"
            )

    def _add_tenant_filter(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add tenant filter to query filters.

        Args:
            filters: Existing filters

        Returns:
            Filters with tenant_id added
        """
        self._ensure_tenant_context()

        tenant_filters = filters.copy() if filters else {}
        tenant_filters["tenant_id"] = self.current_tenant_id

        return tenant_filters

    def find_by_id(self, entity_id: Any) -> Optional[T]:
        """Find entity by ID within current tenant."""
        try:
            self._ensure_tenant_context()

            id_field = self._get_id_field()
            # nosec B608: table_name and id_field are controlled
            query = (
                f"SELECT * FROM {self.table_name} "
                f"WHERE {id_field} = ? AND tenant_id = ?"
            )

            if self.db_manager.config.db_type.value == "postgres":
                query = query.replace("?", "%s")

            row = self.db_manager.execute_query(
                query, (entity_id, self.current_tenant_id), fetch_one=True
            )

            if row:
                return self._row_to_entity(row)
            return None

        except Exception as e:
            self.logger.error(
                f"Error finding tenant {self.table_name} by ID {entity_id}: {str(e)}"
            )
            raise DatabaseException(f"Failed to find {self.table_name} by ID: {str(e)}")

    def find_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        """Find all entities within current tenant."""
        tenant_filters = self._add_tenant_filter(filters)
        return super().find_all(limit, offset, order_by, order_desc, tenant_filters)

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities within current tenant."""
        tenant_filters = self._add_tenant_filter(filters)
        return super().count(tenant_filters)

    def delete(self, entity_id: Any) -> bool:
        """Delete entity within current tenant."""
        try:
            self._ensure_tenant_context()

            id_field = self._get_id_field()
            # nosec B608: table_name and id_field are controlled
            query = (
                f"DELETE FROM {self.table_name} "
                f"WHERE {id_field} = ? AND tenant_id = ?"
            )

            if self.db_manager.config.db_type.value == "postgres":
                query = query.replace("?", "%s")

            affected_rows = self.db_manager.execute_query(
                query, (entity_id, self.current_tenant_id)
            )

            return bool(affected_rows) and affected_rows > 0

        except Exception as e:
            self.logger.error(
                f"Error deleting tenant {self.table_name} ID {entity_id}: {str(e)}"
            )
            raise DatabaseException(f"Failed to delete {self.table_name}: {str(e)}")

    def save(self, entity: T) -> T:
        """Save entity with tenant context validation."""
        self._ensure_tenant_context()

        entity_dict = self._entity_to_dict(entity)

        # Ensure tenant_id is set correctly
        entity_dict["tenant_id"] = self.current_tenant_id

        # For updates, verify the entity belongs to current tenant
        id_field = self._get_id_field()
        entity_id = entity_dict.get(id_field)

        if entity_id:
            existing = self.find_by_id(entity_id)
            if existing is None:
                raise DatabaseException(
                    f"{self.table_name} with ID {entity_id} not found in current tenant"
                )

        return super().save(self._dict_to_entity(entity_dict))

    def _insert_entity(self, entity_dict: Dict[str, Any]) -> T:
        """
        Insert new entity into database with tenant context.

        Args:
            entity_dict: Entity data as dictionary

        Returns:
            Inserted entity with generated fields
        """
        # Add timestamp fields if they exist
        current_time = datetime.now(timezone.utc)
        if "created_at" in entity_dict and entity_dict["created_at"] is None:
            entity_dict["created_at"] = current_time
        if "updated_at" in entity_dict:
            entity_dict["updated_at"] = current_time

        # Ensure tenant_id is set
        entity_dict["tenant_id"] = self.current_tenant_id

        # Build INSERT query
        fields = [k for k, v in entity_dict.items() if v is not None]
        placeholders = ["?" for _ in fields]
        values = [entity_dict[field] for field in fields]

        if self.db_manager.config.db_type.value == "postgres":
            placeholders = ["%s" for _ in fields]
            # For PostgreSQL, use RETURNING to get the inserted record
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(fields)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """  # nosec B608: table_name and fields are controlled

            row = self.db_manager.execute_query(query, tuple(values), fetch_one=True)
            return self._row_to_entity(row)
        else:
            # For SQLite - do everything in the same connection context
            id_field = self._get_id_field()
            with self.db_manager.get_connection_context() as conn:
                cursor = conn.cursor()

                # Insert the record
                query = f"""
                    INSERT INTO {self.table_name} ({', '.join(fields)})
                    VALUES ({', '.join(placeholders)})
                """  # nosec B608: table_name and fields are controlled
                cursor.execute(query, tuple(values))

                # Commit the transaction
                conn.commit()

                # Get the last inserted row ID from the same connection
                cursor.execute("SELECT last_insert_rowid()")
                last_id = cursor.fetchone()[0]

                # Fetch record from same connection without tenant filtering
                # nosec B608: table_name and id_field are controlled
                fetch_query = (
                    f"SELECT * FROM {self.table_name} " f"WHERE {id_field} = ?"
                )
                cursor.execute(fetch_query, (last_id,))
                row = cursor.fetchone()

                if row:
                    # Convert to dict format that the db_manager.execute_query returns
                    columns = [desc[0] for desc in cursor.description]
                    row_dict = dict(zip(columns, row))
                    return self._row_to_entity(row_dict)
                else:
                    raise DatabaseException(
                        f"Failed to retrieve inserted {self.table_name} "
                        f"record with ID {last_id}"
                    )

    @abstractmethod
    def _dict_to_entity(self, entity_dict: Dict[str, Any]) -> T:
        """
        Convert dictionary back to entity object.

        Args:
            entity_dict: Dictionary representation

        Returns:
            Entity object
        """
        pass
