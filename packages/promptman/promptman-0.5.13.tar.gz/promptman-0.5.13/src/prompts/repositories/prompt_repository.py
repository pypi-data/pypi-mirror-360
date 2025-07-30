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
                    visibility TEXT DEFAULT 'private' CHECK (visibility IN ('private', 'public')),
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
                    visibility TEXT DEFAULT 'private' CHECK (visibility IN ('private', 'public')),
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
            "visibility": entity.visibility,
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
        user_id: Optional[str] = None,
        include_public_from_tenant: bool = True,
    ) -> List[Prompt]:
        """
        Search prompts by content, name, or title within current tenant with visibility filtering.

        Args:
            search_term: Term to search for
            search_in: Fields to search in ('name', 'title', 'content', 'tags')
            limit: Maximum number of results
            user_id: User ID for visibility filtering (optional)
            include_public_from_tenant: Whether to include public prompts from other users

        Returns:
            List of matching prompts with visibility filtering applied
        """
        self._ensure_tenant_context()

        if not search_term.strip():
            return []

        search_fields = search_in or ["name", "title", "content", "tags"]

        # Build search conditions
        search_conditions = []
        params = [self.current_tenant_id]

        for field in search_fields:
            if self.db_manager.config.db_type.value == "postgres":
                search_conditions.append(f"{field} ILIKE %s")
            else:
                search_conditions.append(f"{field} LIKE ? COLLATE NOCASE")
            params.append(f"%{search_term}%")

        # Build base conditions
        base_conditions = [
            f"tenant_id = {'%s' if self.db_manager.config.db_type.value == 'postgres' else '?'}"
        ]

        # Add search conditions
        base_conditions.append(f"({' OR '.join(search_conditions)})")

        # Add visibility filtering
        if user_id and include_public_from_tenant:
            # User's own prompts OR public prompts from tenant
            visibility_condition = f"(user_id = {'%s' if self.db_manager.config.db_type.value == 'postgres' else '?'} OR visibility = 'public')"
            base_conditions.append(visibility_condition)
            params.append(user_id)
        elif user_id:
            # Only user's own prompts
            base_conditions.append(
                f"user_id = {'%s' if self.db_manager.config.db_type.value == 'postgres' else '?'}"
            )
            params.append(user_id)
        elif include_public_from_tenant:
            # Only public prompts
            base_conditions.append("visibility = 'public'")

        # Build final query
        where_clause = " AND ".join(base_conditions)

        # nosec B608: where_clause is built from controlled parameters
        query = f"SELECT * FROM prompts WHERE {where_clause}"
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

        query = (
            "SELECT DISTINCT category FROM prompts WHERE tenant_id = ? "
            "ORDER BY category"
        )
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

        query = (
            "SELECT DISTINCT tags FROM prompts WHERE tenant_id = ? "
            "AND tags IS NOT NULL AND tags != ''"
        )
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
        enhancement_query = (
            "SELECT COUNT(*) as count FROM prompts WHERE tenant_id = ? "
            "AND is_enhancement_prompt = ?"
        )
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

    def find_all_with_visibility(
        self,
        include_enhancement_prompts: bool = True,
        include_public_from_tenant: bool = True,
        user_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ) -> List[Prompt]:
        """
        Find all prompts with visibility filtering.

        - Always includes user's own prompts (private + public)
        - Optionally includes public prompts from other users in the tenant

        Args:
            include_enhancement_prompts: Whether to include enhancement prompts
            include_public_from_tenant: Whether to include public prompts from other users
            user_id: User ID for filtering (if not provided, uses current tenant filtering)
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Field to order by
            order_desc: Whether to order in descending order

        Returns:
            List of prompts with visibility filtering applied
        """
        self._ensure_tenant_context()

        # Build query with visibility conditions
        query_parts = ["SELECT * FROM prompts"]
        params = []

        # Base tenant filtering
        conditions = ["tenant_id = ?"]
        params.append(self.current_tenant_id)

        # Visibility filtering
        if user_id and include_public_from_tenant:
            # User's own prompts OR public prompts from tenant
            visibility_condition = "(user_id = ? OR visibility = 'public')"
            conditions.append(visibility_condition)
            params.append(user_id)
        elif user_id:
            # Only user's own prompts
            conditions.append("user_id = ?")
            params.append(user_id)
        elif include_public_from_tenant:
            # Only public prompts
            conditions.append("visibility = 'public'")

        # Enhancement prompts filter
        if not include_enhancement_prompts:
            conditions.append("is_enhancement_prompt = ?")
            params.append(False)

        # Add WHERE clause
        if conditions:
            query_parts.append("WHERE " + " AND ".join(conditions))

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

    def find_public_prompts_in_tenant(
        self,
        include_enhancement_prompts: bool = True,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ) -> List[Prompt]:
        """
        Find all public prompts within current tenant.

        Args:
            include_enhancement_prompts: Whether to include enhancement prompts
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Field to order by
            order_desc: Whether to order in descending order

        Returns:
            List of public prompts in the tenant
        """
        filters = {"visibility": "public"}
        if not include_enhancement_prompts:
            filters["is_enhancement_prompt"] = False

        return self.find_all(
            filters=filters,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_desc=order_desc,
        )

    def find_by_visibility(
        self,
        visibility: str,
        user_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Prompt]:
        """
        Find prompts by visibility level.

        Args:
            visibility: 'private' or 'public'
            user_id: Optional user ID for filtering
            limit: Maximum number of results

        Returns:
            List of prompts with specified visibility
        """
        filters = {"visibility": visibility}
        if user_id:
            filters["user_id"] = user_id

        return self.find_all(filters=filters, limit=limit)

    def get_visibility_statistics(self) -> Dict[str, Any]:
        """
        Get visibility statistics for current tenant.

        Returns:
            Dictionary with visibility statistics
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

        # Private prompts
        private_query = (
            "SELECT COUNT(*) as count FROM prompts WHERE tenant_id = ? "
            "AND visibility = ?"
        )
        if self.db_manager.config.db_type.value == "postgres":
            private_query = private_query.replace("?", "%s")

        private_result = self.db_manager.execute_query(
            private_query, (self.current_tenant_id, "private"), fetch_one=True
        )
        private_prompts = private_result["count"] if private_result else 0

        # Public prompts
        public_query = (
            "SELECT COUNT(*) as count FROM prompts WHERE tenant_id = ? "
            "AND visibility = ?"
        )
        if self.db_manager.config.db_type.value == "postgres":
            public_query = public_query.replace("?", "%s")

        public_result = self.db_manager.execute_query(
            public_query, (self.current_tenant_id, "public"), fetch_one=True
        )
        public_prompts = public_result["count"] if public_result else 0

        return {
            "total_prompts": total_prompts,
            "private_prompts": private_prompts,
            "public_prompts": public_prompts,
            "private_percentage": (
                (private_prompts / total_prompts * 100) if total_prompts > 0 else 0
            ),
            "public_percentage": (
                (public_prompts / total_prompts * 100) if total_prompts > 0 else 0
            ),
        }
