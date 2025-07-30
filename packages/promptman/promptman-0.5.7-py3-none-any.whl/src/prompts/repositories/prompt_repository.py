"""
Prompt repository implementing data access for prompt entities.

This module provides the data access layer for prompts using the
repository pattern with proper tenant isolation and error handling.
"""

from typing import Any, Dict, List, Optional

from ...core.base.database_manager import BaseDatabaseManager
from ...core.base.repository_base import TenantAwareRepository
from ..models.prompt import Prompt


class PromptRepository(TenantAwareRepository[Prompt]):
    """
    Repository for prompt data access with tenant isolation.

    Provides CRUD operations for prompts with automatic tenant
    filtering and proper error handling.
    """

    def __init__(self, db_manager: BaseDatabaseManager):
        """Initialize prompt repository."""
        super().__init__(db_manager, "prompts")
        self._ensure_tables_exist()

    def _ensure_tables_exist(self) -> None:
        """Ensure prompt and config tables exist."""
        if self.db_manager.config.db_type.value == "postgres":
            # PostgreSQL table creation
            prompts_table_sql = """
                CREATE TABLE IF NOT EXISTS prompts (
                    id SERIAL PRIMARY KEY,
                    tenant_id UUID NOT NULL,
                    user_id UUID NOT NULL,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'Uncategorized',
                    tags TEXT DEFAULT '',
                    is_enhancement_prompt BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, name)
                )
            """

            config_table_sql = """
                CREATE TABLE IF NOT EXISTS config (
                    id SERIAL PRIMARY KEY,
                    tenant_id UUID NOT NULL,
                    user_id UUID NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, user_id, key)
                )
            """
        else:
            # SQLite table creation
            prompts_table_sql = """
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'Uncategorized',
                    tags TEXT DEFAULT '',
                    is_enhancement_prompt BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, name)
                )
            """

            config_table_sql = """
                CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, user_id, key)
                )
            """

        # Create tables
        self.db_manager.execute_query(prompts_table_sql)
        self.db_manager.execute_query(config_table_sql)

    def _row_to_entity(self, row: Dict[str, Any]) -> Prompt:
        """Convert database row to Prompt entity."""
        return Prompt.from_dict(row)

    def _entity_to_dict(self, entity: Prompt) -> Dict[str, Any]:
        """Convert Prompt entity to dictionary for database operations."""
        data = {
            "tenant_id": entity.tenant_id,
            "user_id": entity.user_id,
            "name": entity.name,
            "title": entity.title,
            "content": entity.content,
            "category": entity.category,
            "tags": entity.tags,
            "is_enhancement_prompt": entity.is_enhancement_prompt,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

        if entity.id is not None:
            data["id"] = entity.id

        return data

    def _dict_to_entity(self, entity_dict: Dict[str, Any]) -> Prompt:
        """Convert dictionary back to Prompt entity."""
        return Prompt.from_dict(entity_dict)

    def _get_id_field(self) -> str:
        """Get the primary key field name."""
        return "id"

    def find_by_name(self, name: str) -> Optional[Prompt]:
        """
        Find prompt by name within current tenant.

        Args:
            name: Prompt name to search for

        Returns:
            Prompt if found, None otherwise
        """
        self._ensure_tenant_context()

        query = "SELECT * FROM prompts WHERE tenant_id = ? AND name = ?"
        if self.db_manager.config.db_type.value == "postgres":
            query = query.replace("?", "%s")

        row = self.db_manager.execute_query(
            query, (self.current_tenant_id, name), fetch_one=True
        )

        return self._row_to_entity(row) if row else None

    def find_by_category(self, category: str) -> List[Prompt]:
        """
        Find all prompts in a category within current tenant.

        Args:
            category: Category to search for

        Returns:
            List of prompts in the category
        """
        return self.find_all(filters={"category": category})

    def find_by_user(self, user_id: str) -> List[Prompt]:
        """
        Find all prompts created by a specific user within current tenant.

        Args:
            user_id: User ID to search for

        Returns:
            List of prompts created by the user
        """
        return self.find_all(filters={"user_id": user_id})

    def find_enhancement_prompts(self) -> List[Prompt]:
        """
        Find all enhancement prompts within current tenant.

        Returns:
            List of enhancement prompts
        """
        return self.find_all(filters={"is_enhancement_prompt": True})

    def search_prompts(
        self,
        search_term: str,
        search_in: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[Prompt]:
        """
        Search prompts by content, name, or title within current tenant.

        Args:
            search_term: Term to search for
            search_in: Fields to search in ('name', 'title', 'content', 'tags')
            limit: Maximum number of results

        Returns:
            List of matching prompts
        """
        self._ensure_tenant_context()

        if not search_term.strip():
            return []

        search_fields = search_in or ["name", "title", "content", "tags"]

        # Build search conditions
        conditions = []
        params = [self.current_tenant_id]

        for field in search_fields:
            if self.db_manager.config.db_type.value == "postgres":
                conditions.append(f"{field} ILIKE %s")
            else:
                conditions.append(f"{field} LIKE ? COLLATE NOCASE")
            params.append(f"%{search_term}%")

        # Build query
        where_clause = f"tenant_id = {'%s' if self.db_manager.config.db_type.value == 'postgres' else '?'}"
        where_clause += f" AND ({' OR '.join(conditions)})"

        query = f"SELECT * FROM prompts WHERE {where_clause}"  # nosec B608: where_clause is built from controlled parameters
        if limit:
            query += f" LIMIT {limit}"

        rows = self.db_manager.execute_query(query, tuple(params), fetch_all=True)

        return [self._row_to_entity(row) for row in rows]

    def get_categories(self) -> List[str]:
        """
        Get all unique categories within current tenant.

        Returns:
            List of category names
        """
        self._ensure_tenant_context()

        query = "SELECT DISTINCT category FROM prompts WHERE tenant_id = ? ORDER BY category"
        if self.db_manager.config.db_type.value == "postgres":
            query = query.replace("?", "%s")

        rows = self.db_manager.execute_query(
            query, (self.current_tenant_id,), fetch_all=True
        )

        return [row["category"] for row in rows if row["category"]]

    def get_tags(self) -> List[str]:
        """
        Get all unique tags within current tenant.

        Returns:
            List of tag names
        """
        self._ensure_tenant_context()

        query = "SELECT DISTINCT tags FROM prompts WHERE tenant_id = ? AND tags IS NOT NULL AND tags != ''"
        if self.db_manager.config.db_type.value == "postgres":
            query = query.replace("?", "%s")

        rows = self.db_manager.execute_query(
            query, (self.current_tenant_id,), fetch_all=True
        )

        # Parse comma-separated tags
        all_tags = set()
        for row in rows:
            if row["tags"]:
                tags = [tag.strip() for tag in row["tags"].split(",") if tag.strip()]
                all_tags.update(tags)

        return sorted(list(all_tags))

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get prompt statistics for current tenant.

        Returns:
            Dictionary with statistics
        """
        self._ensure_tenant_context()

        # Total prompts
        total_query = "SELECT COUNT(*) as count FROM prompts WHERE tenant_id = ?"
        if self.db_manager.config.db_type.value == "postgres":
            total_query = total_query.replace("?", "%s")

        total_result = self.db_manager.execute_query(
            total_query, (self.current_tenant_id,), fetch_one=True
        )
        total_prompts = total_result["count"] if total_result else 0

        # Enhancement prompts
        enhancement_query = "SELECT COUNT(*) as count FROM prompts WHERE tenant_id = ? AND is_enhancement_prompt = ?"
        if self.db_manager.config.db_type.value == "postgres":
            enhancement_query = enhancement_query.replace("?", "%s")

        enhancement_result = self.db_manager.execute_query(
            enhancement_query, (self.current_tenant_id, True), fetch_one=True
        )
        enhancement_prompts = enhancement_result["count"] if enhancement_result else 0

        # Categories
        categories = self.get_categories()

        # Recent prompts (last 7 days)
        recent_query = """
            SELECT COUNT(*) as count FROM prompts
            WHERE tenant_id = ? AND created_at >= datetime('now', '-7 days')
        """
        if self.db_manager.config.db_type.value == "postgres":
            recent_query = """
                SELECT COUNT(*) as count FROM prompts
                WHERE tenant_id = %s AND created_at >= NOW() - INTERVAL '7 days'
            """

        recent_result = self.db_manager.execute_query(
            recent_query, (self.current_tenant_id,), fetch_one=True
        )
        recent_prompts = recent_result["count"] if recent_result else 0

        return {
            "total_prompts": total_prompts,
            "enhancement_prompts": enhancement_prompts,
            "regular_prompts": total_prompts - enhancement_prompts,
            "categories": len(categories),
            "recent_prompts": recent_prompts,
            "category_list": categories,
        }

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if a prompt name already exists within current tenant.

        Args:
            name: Prompt name to check
            exclude_id: ID to exclude from check (for updates)

        Returns:
            True if name exists, False otherwise
        """
        self._ensure_tenant_context()

        query = "SELECT id FROM prompts WHERE tenant_id = ? AND name = ?"
        params: List[Any] = [self.current_tenant_id, name]

        if exclude_id is not None:
            query += " AND id != ?"
            params.append(exclude_id)

        if self.db_manager.config.db_type.value == "postgres":
            query = query.replace("?", "%s")

        result = self.db_manager.execute_query(query, tuple(params), fetch_one=True)
        return result is not None

    def get_recent_prompts(self, limit: int = 10) -> List[Prompt]:
        """
        Get recently created prompts within current tenant.

        Args:
            limit: Maximum number of prompts to return

        Returns:
            List of recent prompts
        """
        return self.find_all(limit=limit, order_by="created_at", order_desc=True)

    def get_most_used_prompts(self, limit: int = 10) -> List[Prompt]:
        """
        Get most frequently used prompts within current tenant.

        Note: This would require usage tracking in the future.
        For now, returns most recently updated prompts.

        Args:
            limit: Maximum number of prompts to return

        Returns:
            List of frequently used prompts
        """
        return self.find_all(limit=limit, order_by="updated_at", order_desc=True)

    def delete_by_name(self, name: str) -> bool:
        """
        Delete prompt by name within current tenant.

        Args:
            name: Name of prompt to delete

        Returns:
            True if deleted, False if not found
        """
        prompt = self.find_by_name(name)
        if prompt and prompt.id:
            return self.delete(prompt.id)
        return False
