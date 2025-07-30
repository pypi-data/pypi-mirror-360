"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Multi-tenant prompt data manager with database abstraction for SQLite and PostgreSQL.

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
DB_PATH = os.getenv("DB_PATH", "prompts.db")
POSTGRES_DSN = os.getenv("POSTGRES_DSN")


class PromptDataManager:
    def __init__(
        self,
        db_path: Optional[str] = None,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        self.db_type = DB_TYPE
        self.tenant_id = tenant_id
        self.user_id = user_id
        if self.db_type == "postgres":
            if not POSTGRES_AVAILABLE:
                raise ImportError(
                    "psycopg2 is required for Postgres support. Please install it."
                )
            self.dsn = POSTGRES_DSN
            if not self.dsn:
                raise ValueError(
                    "POSTGRES_DSN environment variable must be set for Postgres."
                )
            self.db_path: Optional[str] = None
        else:
            self.db_path = db_path or DB_PATH
        self.init_database()

    def get_conn(self):
        if self.db_type == "postgres":
            return psycopg2.connect(self.dsn, cursor_factory=RealDictCursor)
        else:
            if self.db_path is None:
                raise ValueError("Database path not set for SQLite connection")
            return sqlite3.connect(self.db_path)

    def init_database(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        if self.db_type == "postgres":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS prompts (
                    id SERIAL PRIMARY KEY,
                    tenant_id UUID,
                    user_id UUID,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'Uncategorized',
                    tags TEXT,
                    is_enhancement_prompt BOOLEAN DEFAULT FALSE,
                    visibility TEXT DEFAULT 'private',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, name),
                    CHECK (visibility IN ('private', 'public'))
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS config (
                    id SERIAL PRIMARY KEY,
                    tenant_id UUID,
                    user_id UUID,
                    key TEXT NOT NULL,
                    value TEXT,
                    UNIQUE(tenant_id, user_id, key)
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS templates (
                    id SERIAL PRIMARY KEY,
                    tenant_id UUID,
                    user_id UUID,
                    name TEXT NOT NULL,
                    description TEXT,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'Custom',
                    tags TEXT DEFAULT '',
                    variables TEXT,
                    is_builtin BOOLEAN DEFAULT FALSE,
                    visibility TEXT DEFAULT 'private',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, name),
                    CHECK (visibility IN ('private', 'public'))
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS rules (
                    id SERIAL PRIMARY KEY,
                    tenant_id UUID,
                    user_id UUID,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'General',
                    tags TEXT DEFAULT '',
                    description TEXT,
                    is_builtin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, name)
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_models (
                    id SERIAL PRIMARY KEY,
                    tenant_id UUID,
                    user_id UUID,
                    name TEXT NOT NULL,
                    display_name TEXT,
                    provider TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    description TEXT,
                    api_key TEXT,
                    api_endpoint TEXT,
                    api_version TEXT,
                    deployment_name TEXT,
                    max_tokens INTEGER,
                    temperature DECIMAL(3,2) DEFAULT 0.7,
                    top_p DECIMAL(3,2) DEFAULT 1.0,
                    frequency_penalty DECIMAL(3,2) DEFAULT 0.0,
                    presence_penalty DECIMAL(3,2) DEFAULT 0.0,
                    cost_per_1k_input_tokens DECIMAL(10,6) DEFAULT 0.0,
                    cost_per_1k_output_tokens DECIMAL(10,6) DEFAULT 0.0,
                    max_context_length INTEGER,
                    supports_streaming BOOLEAN DEFAULT FALSE,
                    supports_function_calling BOOLEAN DEFAULT FALSE,
                    supports_vision BOOLEAN DEFAULT FALSE,
                    supports_json_mode BOOLEAN DEFAULT FALSE,
                    is_enabled BOOLEAN DEFAULT TRUE,
                    is_available BOOLEAN DEFAULT FALSE,
                    last_health_check TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, name)
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_operation_configs (
                    id SERIAL PRIMARY KEY,
                    tenant_id UUID,
                    user_id UUID,
                    operation_type TEXT NOT NULL,
                    primary_model TEXT,
                    fallback_models TEXT,
                    is_enabled BOOLEAN DEFAULT TRUE,
                    custom_parameters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, operation_type)
                )
            """
            )

            # Add columns to existing tables if they don't exist
            cursor.execute(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='prompts' AND column_name='tenant_id'
                    ) THEN
                        ALTER TABLE prompts ADD COLUMN tenant_id UUID;
                    END IF;
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='prompts' AND column_name='user_id'
                    ) THEN
                        ALTER TABLE prompts ADD COLUMN user_id UUID;
                    END IF;
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='prompts' AND column_name='visibility'
                    ) THEN
                        ALTER TABLE prompts ADD COLUMN visibility TEXT DEFAULT 'private';
                        ALTER TABLE prompts ADD CONSTRAINT prompts_visibility_check 
                            CHECK (visibility IN ('private', 'public'));
                    END IF;
                END $$;
            """
            )
            cursor.execute(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='config' AND column_name='tenant_id'
                    ) THEN
                        ALTER TABLE config ADD COLUMN tenant_id UUID;
                    END IF;
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='config' AND column_name='user_id'
                    ) THEN
                        ALTER TABLE config ADD COLUMN user_id UUID;
                    END IF;
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='config' AND column_name='id'
                    ) THEN
                        ALTER TABLE config ADD COLUMN id SERIAL PRIMARY KEY;
                    END IF;
                END $$;
            """
            )
            cursor.execute(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='templates' AND column_name='tags'
                    ) THEN
                        ALTER TABLE templates ADD COLUMN tags TEXT DEFAULT '';
                    END IF;
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='templates' AND column_name='visibility'
                    ) THEN
                        ALTER TABLE templates ADD COLUMN visibility TEXT DEFAULT 'private';
                        ALTER TABLE templates ADD CONSTRAINT templates_visibility_check 
                            CHECK (visibility IN ('private', 'public'));
                    END IF;
                END $$;
            """
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id TEXT,
                    user_id TEXT,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'Uncategorized',
                    tags TEXT,
                    is_enhancement_prompt BOOLEAN DEFAULT 0,
                    visibility TEXT DEFAULT 'private',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, name),
                    CHECK (visibility IN ('private', 'public'))
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id TEXT,
                    user_id TEXT,
                    key TEXT NOT NULL,
                    value TEXT,
                    UNIQUE(tenant_id, user_id, key)
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id TEXT,
                    user_id TEXT,
                    name TEXT NOT NULL,
                    description TEXT,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'Custom',
                    tags TEXT DEFAULT '',
                    variables TEXT,
                    is_builtin BOOLEAN DEFAULT 0,
                    visibility TEXT DEFAULT 'private',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, name),
                    CHECK (visibility IN ('private', 'public'))
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id TEXT,
                    user_id TEXT,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'General',
                    tags TEXT DEFAULT '',
                    description TEXT,
                    is_builtin BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, name)
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id TEXT,
                    user_id TEXT,
                    name TEXT NOT NULL,
                    display_name TEXT,
                    provider TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    description TEXT,
                    api_key TEXT,
                    api_endpoint TEXT,
                    api_version TEXT,
                    deployment_name TEXT,
                    max_tokens INTEGER,
                    temperature REAL DEFAULT 0.7,
                    top_p REAL DEFAULT 1.0,
                    frequency_penalty REAL DEFAULT 0.0,
                    presence_penalty REAL DEFAULT 0.0,
                    cost_per_1k_input_tokens REAL DEFAULT 0.0,
                    cost_per_1k_output_tokens REAL DEFAULT 0.0,
                    max_context_length INTEGER,
                    supports_streaming BOOLEAN DEFAULT 0,
                    supports_function_calling BOOLEAN DEFAULT 0,
                    supports_vision BOOLEAN DEFAULT 0,
                    supports_json_mode BOOLEAN DEFAULT 0,
                    is_enabled BOOLEAN DEFAULT 1,
                    is_available BOOLEAN DEFAULT 0,
                    last_health_check TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, name)
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_operation_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id TEXT,
                    user_id TEXT,
                    operation_type TEXT NOT NULL,
                    primary_model TEXT,
                    fallback_models TEXT,
                    is_enabled BOOLEAN DEFAULT 1,
                    custom_parameters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, operation_type)
                )
            """
            )
            cursor.execute("PRAGMA table_info(prompts)")
            columns = [column[1] for column in cursor.fetchall()]
            if "is_enhancement_prompt" not in columns:
                cursor.execute(
                    "ALTER TABLE prompts ADD COLUMN is_enhancement_prompt "
                    "BOOLEAN DEFAULT 0"
                )
            if "tenant_id" not in columns:
                cursor.execute("ALTER TABLE prompts ADD COLUMN tenant_id TEXT")
            if "user_id" not in columns:
                cursor.execute("ALTER TABLE prompts ADD COLUMN user_id TEXT")
            if "name" not in columns:
                cursor.execute("ALTER TABLE prompts ADD COLUMN name TEXT")
                cursor.execute("UPDATE prompts SET name = title WHERE name IS NULL")
            if "visibility" not in columns:
                cursor.execute(
                    "ALTER TABLE prompts ADD COLUMN visibility TEXT DEFAULT 'private'"
                )

            # Update templates table structure
            cursor.execute("PRAGMA table_info(templates)")
            template_columns = [column[1] for column in cursor.fetchall()]
            if "tags" not in template_columns:
                cursor.execute("ALTER TABLE templates ADD COLUMN tags TEXT DEFAULT ''")
            if "visibility" not in template_columns:
                cursor.execute(
                    "ALTER TABLE templates ADD COLUMN visibility TEXT DEFAULT 'private'"
                )

            # Update config table structure
            cursor.execute("PRAGMA table_info(config)")
            config_columns = [column[1] for column in cursor.fetchall()]
            if "tenant_id" not in config_columns:
                cursor.execute("ALTER TABLE config ADD COLUMN tenant_id TEXT")
            if "user_id" not in config_columns:
                cursor.execute("ALTER TABLE config ADD COLUMN user_id TEXT")
            if "id" not in config_columns:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS config_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tenant_id TEXT,
                        user_id TEXT,
                        key TEXT NOT NULL,
                        value TEXT,
                        UNIQUE(tenant_id, user_id, key)
                    )
                """
                )
                cursor.execute(
                    "INSERT INTO config_new (key, value) SELECT key, value FROM config"
                )
                cursor.execute("DROP TABLE config")
                cursor.execute("ALTER TABLE config_new RENAME TO config")
        conn.commit()
        conn.close()

    def add_prompt(
        self,
        name: str,
        title: str,
        content: str,
        category: str,
        tags: str,
        is_enhancement_prompt: bool = False,
        visibility: str = "private",
    ) -> str:
        if not name.strip():
            return "Error: Name is required!"
        if not title.strip() or not content.strip():
            return "Error: Title and content are required!"
        if not self.tenant_id:
            return "Error: No tenant context available!"
        if visibility not in ["private", "public"]:
            return "Error: Visibility must be 'private' or 'public'!"

        name = name.strip()
        category = category.strip() or "Uncategorized"
        conn = self.get_conn()
        cursor = conn.cursor()

        # Check for existing prompt within tenant
        if self.db_type == "postgres":
            cursor.execute(
                "SELECT id FROM prompts WHERE name = %s AND tenant_id = %s",
                (name, self.tenant_id),
            )
        else:
            cursor.execute(
                "SELECT id FROM prompts WHERE name = ? AND tenant_id = ?",
                (name, self.tenant_id),
            )

        if cursor.fetchone():
            conn.close()
            return (
                f"Error: A prompt with name '{name}' already exists in your workspace!"
            )

        if self.db_type == "postgres":
            cursor.execute(
                """
                INSERT INTO prompts (tenant_id, user_id, name, title, content,
                category, tags, is_enhancement_prompt, visibility, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    self.tenant_id,
                    self.user_id,
                    name,
                    title.strip(),
                    content.strip(),
                    category,
                    tags.strip(),
                    is_enhancement_prompt,
                    visibility,
                    datetime.now(),
                    datetime.now(),
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO prompts (tenant_id, user_id, name, title, content,
                category, tags, is_enhancement_prompt, visibility, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.tenant_id,
                    self.user_id,
                    name,
                    title.strip(),
                    content.strip(),
                    category,
                    tags.strip(),
                    is_enhancement_prompt,
                    visibility,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )

        conn.commit()
        conn.close()
        prompt_type = "Enhancement prompt" if is_enhancement_prompt else "Prompt"
        return f"{prompt_type} '{name}' added successfully!"

    def update_prompt(
        self,
        original_name: str,
        new_name: str,
        title: str,
        content: str,
        category: str,
        tags: str,
        is_enhancement_prompt: bool = False,
        visibility: str = "private",
    ) -> str:
        if not original_name.strip() or not new_name.strip():
            return "Error: Original name and new name are required!"
        if not title.strip() or not content.strip():
            return "Error: Title and content are required!"
        if not self.tenant_id:
            return "Error: No tenant context available!"
        if visibility not in ["private", "public"]:
            return "Error: Visibility must be 'private' or 'public'!"

        original_name = original_name.strip()
        new_name = new_name.strip()
        category = category.strip() or "Uncategorized"
        conn = self.get_conn()
        cursor = conn.cursor()

        # Check if original prompt exists in tenant
        if self.db_type == "postgres":
            cursor.execute(
                "SELECT id FROM prompts WHERE name = %s AND tenant_id = %s",
                (original_name, self.tenant_id),
            )
        else:
            cursor.execute(
                "SELECT id FROM prompts WHERE name = ? AND tenant_id = ?",
                (original_name, self.tenant_id),
            )

        if not cursor.fetchone():
            conn.close()
            return f"Error: Prompt '{original_name}' not found in your workspace!"

        # Check if new name conflicts within tenant
        if original_name != new_name:
            if self.db_type == "postgres":
                cursor.execute(
                    "SELECT id FROM prompts WHERE name = %s AND tenant_id = %s",
                    (new_name, self.tenant_id),
                )
            else:
                cursor.execute(
                    "SELECT id FROM prompts WHERE name = ? AND tenant_id = ?",
                    (new_name, self.tenant_id),
                )

            if cursor.fetchone():
                conn.close()
                return (
                    f"Error: A prompt with name '{new_name}' already exists "
                    "in your workspace!"
                )

        if self.db_type == "postgres":
            cursor.execute(
                """
                UPDATE prompts
                SET name=%s, title=%s, content=%s, category=%s, tags=%s,
                is_enhancement_prompt=%s, visibility=%s, updated_at=%s
                WHERE name=%s AND tenant_id=%s
            """,
                (
                    new_name,
                    title.strip(),
                    content.strip(),
                    category,
                    tags.strip(),
                    is_enhancement_prompt,
                    visibility,
                    datetime.now(),
                    original_name,
                    self.tenant_id,
                ),
            )
        else:
            cursor.execute(
                """
                UPDATE prompts
                SET name=?, title=?, content=?, category=?, tags=?,
                is_enhancement_prompt=?, visibility=?, updated_at=?
                WHERE name=? AND tenant_id=?
            """,
                (
                    new_name,
                    title.strip(),
                    content.strip(),
                    category,
                    tags.strip(),
                    is_enhancement_prompt,
                    visibility,
                    datetime.now().isoformat(),
                    original_name,
                    self.tenant_id,
                ),
            )

        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return "Prompt updated successfully!"
        else:
            conn.close()
            return "Error: Prompt not found in your workspace!"

    def delete_prompt(self, name: str) -> str:
        if not name.strip():
            return "Error: Name is required!"
        if not self.tenant_id:
            return "Error: No tenant context available!"

        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            cursor.execute(
                "DELETE FROM prompts WHERE name = %s AND tenant_id = %s",
                (name.strip(), self.tenant_id),
            )
        else:
            cursor.execute(
                "DELETE FROM prompts WHERE name = ? AND tenant_id = ?",
                (name.strip(), self.tenant_id),
            )

        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return f"Prompt '{name}' deleted successfully!"
        else:
            conn.close()
            return f"Error: Prompt '{name}' not found in your workspace!"

    def get_all_prompts(self, include_enhancement_prompts: bool = True) -> List[Dict]:
        """
        Get all prompts with visibility filtering.
        In multi-tenant mode: user's own prompts + public prompts from tenant
        In single-user mode: all prompts (visibility ignored)
        """
        if not self.tenant_id:
            return []

        # Check if single-user mode by environment variable
        import os

        is_single_user = os.getenv("MULTITENANT_MODE", "true").lower() == "false"

        if is_single_user or not self.user_id:
            # Single-user mode or no user context - show all prompts
            return self._get_all_prompts_no_visibility(include_enhancement_prompts)
        else:
            # Multi-tenant mode - use visibility filtering
            return self.get_all_prompts_with_visibility(
                include_enhancement_prompts, include_public_from_tenant=True
            )

    def _get_all_prompts_no_visibility(
        self, include_enhancement_prompts: bool = True
    ) -> List[Dict]:
        """Internal method for single-user mode - shows all prompts regardless of visibility"""
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            if include_enhancement_prompts:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts WHERE tenant_id = %s ORDER BY category, name
                """,
                    (self.tenant_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts WHERE tenant_id = %s
                    AND is_enhancement_prompt = FALSE ORDER BY category, name
                """,
                    (self.tenant_id,),
                )
        else:
            if include_enhancement_prompts:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts WHERE tenant_id = ? ORDER BY category, name
                """,
                    (self.tenant_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts WHERE tenant_id = ?
                    AND is_enhancement_prompt = 0 ORDER BY category, name
                """,
                    (self.tenant_id,),
                )

        prompts = []
        for row in cursor.fetchall():
            prompts.append(
                {
                    "id": row[0],
                    "tenant_id": row[1],
                    "user_id": row[2],
                    "name": row[3],
                    "title": row[4],
                    "content": row[5],
                    "category": row[6],
                    "tags": row[7],
                    "is_enhancement_prompt": (
                        bool(row[8]) if row[8] is not None else False
                    ),
                    "visibility": row[9] if row[9] is not None else "private",
                    "created_at": row[10],
                    "updated_at": row[11],
                }
            )
        conn.close()
        return prompts

    def get_enhancement_prompts(self) -> List[Dict]:
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            cursor.execute(
                """
                SELECT id, tenant_id, user_id, name, title, content, category,
                tags, is_enhancement_prompt, visibility, created_at, updated_at
                FROM prompts WHERE tenant_id = %s AND is_enhancement_prompt = TRUE
                ORDER BY name
            """,
                (self.tenant_id,),
            )
        else:
            cursor.execute(
                """
                SELECT id, tenant_id, user_id, name, title, content, category,
                tags, is_enhancement_prompt, visibility, created_at, updated_at
                FROM prompts WHERE tenant_id = ? AND is_enhancement_prompt = 1
                ORDER BY name
            """,
                (self.tenant_id,),
            )

        prompts = []
        for row in cursor.fetchall():
            prompts.append(
                {
                    "id": row[0],
                    "tenant_id": row[1],
                    "user_id": row[2],
                    "name": row[3],
                    "title": row[4],
                    "content": row[5],
                    "category": row[6],
                    "tags": row[7],
                    "is_enhancement_prompt": bool(row[8]),
                    "created_at": row[9],
                    "updated_at": row[10],
                }
            )
        conn.close()
        return prompts

    def get_categories(self) -> List[str]:
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            cursor.execute(
                "SELECT DISTINCT category FROM prompts WHERE tenant_id = %s "
                "ORDER BY category",
                (self.tenant_id,),
            )
        else:
            cursor.execute(
                "SELECT DISTINCT category FROM prompts WHERE tenant_id = ? "
                "ORDER BY category",
                (self.tenant_id,),
            )

        categories = [row[0] for row in cursor.fetchall()]
        conn.close()

        # If no categories exist yet (empty database), provide default categories
        if not categories:
            categories = ["Business", "Technical", "Creative", "Analytical", "General"]

        return sorted(categories)

    def search_prompts(
        self, search_term: str, include_enhancement_prompts: bool = True
    ) -> List[Dict]:
        if not search_term.strip():
            return self.get_all_prompts(include_enhancement_prompts)
        if not self.tenant_id:
            return []

        # Check if single-user mode by environment variable
        import os

        is_single_user = os.getenv("MULTITENANT_MODE", "true").lower() == "false"

        conn = self.get_conn()
        cursor = conn.cursor()

        # Build visibility conditions
        if is_single_user or not self.user_id:
            # Single-user mode or no user context - no visibility filtering
            visibility_condition = ""
            visibility_params = []
        else:
            # Multi-tenant mode - include user's own prompts + public prompts
            if self.db_type == "postgres":
                visibility_condition = " AND (user_id = %s OR visibility = 'public')"
            else:
                visibility_condition = " AND (user_id = ? OR visibility = 'public')"
            visibility_params = [self.user_id]

        if self.db_type == "postgres":
            like = f"%{search_term}%"
            base_params = [self.tenant_id, like, like, like, like]

            if include_enhancement_prompts:
                query = f"""
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts
                    WHERE tenant_id = %s
                    AND (name ILIKE %s OR title ILIKE %s OR content ILIKE %s
                    OR tags ILIKE %s){visibility_condition}
                    ORDER BY category, name
                """
                cursor.execute(query, base_params + visibility_params)
            else:
                query = f"""
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts
                    WHERE tenant_id = %s
                    AND (name ILIKE %s OR title ILIKE %s OR content ILIKE %s
                    OR tags ILIKE %s) AND is_enhancement_prompt = FALSE{visibility_condition}
                    ORDER BY category, name
                """
                cursor.execute(query, base_params + visibility_params)
        else:
            base_params = [
                self.tenant_id,
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
            ]

            if include_enhancement_prompts:
                query = f"""
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts
                    WHERE tenant_id = ?
                    AND (name LIKE ? OR title LIKE ? OR content LIKE ?
                    OR tags LIKE ?){visibility_condition}
                    ORDER BY category, name
                """
                cursor.execute(query, base_params + visibility_params)
            else:
                query = f"""
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts
                    WHERE tenant_id = ?
                    AND (name LIKE ? OR title LIKE ? OR content LIKE ?
                    OR tags LIKE ?) AND is_enhancement_prompt = 0{visibility_condition}
                    ORDER BY category, name
                """
                cursor.execute(query, base_params + visibility_params)

        prompts = []
        for row in cursor.fetchall():
            prompts.append(
                {
                    "id": row[0],
                    "tenant_id": row[1],
                    "user_id": row[2],
                    "name": row[3],
                    "title": row[4],
                    "content": row[5],
                    "category": row[6],
                    "tags": row[7],
                    "is_enhancement_prompt": (
                        bool(row[8]) if row[8] is not None else False
                    ),
                    "visibility": row[9] if row[9] is not None else "private",
                    "created_at": row[10],
                    "updated_at": row[11],
                }
            )
        conn.close()
        return prompts

    def get_prompts_by_category(
        self, category: Optional[str] = None, include_enhancement_prompts: bool = True
    ) -> List[Dict]:
        if not category or category == "All":
            return self.get_all_prompts(include_enhancement_prompts)
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            if include_enhancement_prompts:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts WHERE tenant_id = %s AND category = %s
                    ORDER BY name
                """,
                    (self.tenant_id, category),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts WHERE tenant_id = %s AND category = %s
                    AND is_enhancement_prompt = FALSE
                    ORDER BY name
                """,
                    (self.tenant_id, category),
                )
        else:
            if include_enhancement_prompts:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts WHERE tenant_id = ? AND category = ?
                    ORDER BY name
                """,
                    (self.tenant_id, category),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts WHERE tenant_id = ? AND category = ?
                    AND is_enhancement_prompt = 0
                    ORDER BY name
                """,
                    (self.tenant_id, category),
                )

        prompts = []
        for row in cursor.fetchall():
            prompts.append(
                {
                    "id": row[0],
                    "tenant_id": row[1],
                    "user_id": row[2],
                    "name": row[3],
                    "title": row[4],
                    "content": row[5],
                    "category": row[6],
                    "tags": row[7],
                    "is_enhancement_prompt": (
                        bool(row[8]) if row[8] is not None else False
                    ),
                    "visibility": row[9] if row[9] is not None else "private",
                    "created_at": row[10],
                    "updated_at": row[11],
                }
            )
        conn.close()
        return prompts

    def get_prompt_by_name(self, name: str) -> Optional[Dict]:
        if not name.strip() or not self.tenant_id:
            return None

        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            cursor.execute(
                """
                SELECT id, tenant_id, user_id, name, title, content, category,
                       tags, is_enhancement_prompt, visibility, created_at, updated_at
                FROM prompts WHERE name = %s AND tenant_id = %s
            """,
                (name.strip(), self.tenant_id),
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "id": row["id"],
                    "tenant_id": row["tenant_id"],
                    "user_id": row["user_id"],
                    "name": row["name"],
                    "title": row["title"],
                    "content": row["content"],
                    "category": row["category"],
                    "tags": row["tags"],
                    "is_enhancement_prompt": (
                        bool(row["is_enhancement_prompt"])
                        if row["is_enhancement_prompt"] is not None
                        else False
                    ),
                    "visibility": (
                        row["visibility"]
                        if row["visibility"] is not None
                        else "private"
                    ),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
        else:
            cursor.execute(
                """
                SELECT id, tenant_id, user_id, name, title, content, category,
                       tags, is_enhancement_prompt, visibility, created_at, updated_at
                FROM prompts WHERE name = ? AND tenant_id = ?
            """,
                (name.strip(), self.tenant_id),
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "id": row[0],
                    "tenant_id": row[1],
                    "user_id": row[2],
                    "name": row[3],
                    "title": row[4],
                    "content": row[5],
                    "category": row[6],
                    "tags": row[7],
                    "is_enhancement_prompt": (
                        bool(row[8]) if row[8] is not None else False
                    ),
                    "visibility": row[9] if row[9] is not None else "private",
                    "created_at": row[10],
                    "updated_at": row[11],
                }
        return None

    # Rules Management Methods

    def add_rule(
        self,
        name: str,
        title: str,
        content: str,
        category: str = "General",
        tags: str = "",
        description: str = "",
        is_builtin: bool = False,
    ) -> str:
        """Add a new rule to the database."""
        if not name.strip() or not title.strip() or not content.strip():
            return "Name, title, and content are required."

        if not self.tenant_id or not self.user_id:
            return "Tenant ID and User ID are required."

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    INSERT INTO rules (tenant_id, user_id, name, title, content, category, tags, description, is_builtin)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        self.tenant_id,
                        self.user_id,
                        name.strip(),
                        title.strip(),
                        content.strip(),
                        category.strip() or "General",
                        tags.strip(),
                        description.strip(),
                        is_builtin,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO rules (tenant_id, user_id, name, title, content, category, tags, description, is_builtin)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        self.tenant_id,
                        self.user_id,
                        name.strip(),
                        title.strip(),
                        content.strip(),
                        category.strip() or "General",
                        tags.strip(),
                        description.strip(),
                        is_builtin,
                    ),
                )
            conn.commit()
            conn.close()
            return "Rule added successfully."
        except Exception as e:
            conn.rollback()
            conn.close()
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                return f"Error: A rule with the name '{name}' already exists."
            return f"Error adding rule: {str(e)}"

    def update_rule(
        self,
        original_name: str,
        name: str,
        title: str,
        content: str,
        category: str = "General",
        tags: str = "",
        description: str = "",
    ) -> str:
        """Update an existing rule."""
        if not name.strip() or not title.strip() or not content.strip():
            return "Name, title, and content are required."

        if not self.tenant_id:
            return "Tenant ID is required."

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    UPDATE rules
                    SET name = %s, title = %s, content = %s, category = %s, tags = %s, description = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE name = %s AND tenant_id = %s
                """,
                    (
                        name.strip(),
                        title.strip(),
                        content.strip(),
                        category.strip() or "General",
                        tags.strip(),
                        description.strip(),
                        original_name.strip(),
                        self.tenant_id,
                    ),
                )
            else:
                cursor.execute(
                    """
                    UPDATE rules
                    SET name = ?, title = ?, content = ?, category = ?, tags = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ? AND tenant_id = ?
                """,
                    (
                        name.strip(),
                        title.strip(),
                        content.strip(),
                        category.strip() or "General",
                        tags.strip(),
                        description.strip(),
                        original_name.strip(),
                        self.tenant_id,
                    ),
                )

            if cursor.rowcount == 0:
                conn.close()
                return f"Error: Rule '{original_name}' not found."

            conn.commit()
            conn.close()
            return "Rule updated successfully."
        except Exception as e:
            conn.rollback()
            conn.close()
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                return f"Error: A rule with the name '{name}' already exists."
            return f"Error updating rule: {str(e)}"

    def delete_rule(self, name: str) -> str:
        """Delete a rule from the database."""
        if not name.strip() or not self.tenant_id:
            return "Rule name and tenant ID are required."

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    "DELETE FROM rules WHERE name = %s AND tenant_id = %s",
                    (name.strip(), self.tenant_id),
                )
            else:
                cursor.execute(
                    "DELETE FROM rules WHERE name = ? AND tenant_id = ?",
                    (name.strip(), self.tenant_id),
                )

            if cursor.rowcount == 0:
                conn.close()
                return f"Error: Rule '{name}' not found."

            conn.commit()
            conn.close()
            return "Rule deleted successfully."
        except Exception as e:
            conn.rollback()
            conn.close()
            return f"Error deleting rule: {str(e)}"

    def get_all_rules(self) -> List[Dict]:
        """Retrieve all rules for the current tenant."""
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            cursor.execute(
                """
                SELECT id, tenant_id, user_id, name, title, content, category,
                       tags, description, is_builtin, created_at, updated_at
                FROM rules WHERE tenant_id = %s
                ORDER BY created_at DESC
            """,
                (self.tenant_id,),
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "id": row["id"],
                    "tenant_id": row["tenant_id"],
                    "user_id": row["user_id"],
                    "name": row["name"],
                    "title": row["title"],
                    "content": row["content"],
                    "category": row["category"],
                    "tags": row["tags"],
                    "description": row["description"],
                    "is_builtin": (
                        bool(row["is_builtin"])
                        if row["is_builtin"] is not None
                        else False
                    ),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
                for row in rows
            ]
        else:
            cursor.execute(
                """
                SELECT id, tenant_id, user_id, name, title, content, category,
                       tags, description, is_builtin, created_at, updated_at
                FROM rules WHERE tenant_id = ?
                ORDER BY created_at DESC
            """,
                (self.tenant_id,),
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "id": row[0],
                    "tenant_id": row[1],
                    "user_id": row[2],
                    "name": row[3],
                    "title": row[4],
                    "content": row[5],
                    "category": row[6],
                    "tags": row[7],
                    "description": row[8],
                    "is_builtin": bool(row[9]) if row[9] is not None else False,
                    "created_at": row[10],
                    "updated_at": row[11],
                }
                for row in rows
            ]

    def search_rules(
        self,
        search_term: str,
        category_filter: str = "all",
        tags_filter: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Search rules by name, title, content, or tags."""
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        # Build search conditions
        conditions = []
        params = []

        # Add tenant filter
        if self.db_type == "postgres":
            conditions.append("tenant_id = %s")
            placeholder = "%s"
        else:
            conditions.append("tenant_id = ?")
            placeholder = "?"
        params.append(self.tenant_id)

        # Add search term filter
        if search_term.strip():
            search_condition = (
                f"(name ILIKE {placeholder} OR title ILIKE {placeholder} OR content ILIKE {placeholder} OR tags ILIKE {placeholder})"
                if self.db_type == "postgres"
                else f"(name LIKE {placeholder} OR title LIKE {placeholder} OR content LIKE {placeholder} OR tags LIKE {placeholder})"
            )
            conditions.append(search_condition)
            search_pattern = f"%{search_term.strip()}%"
            params.extend([search_pattern] * 4)

        # Add category filter
        if category_filter and category_filter.lower() != "all":
            conditions.append(f"category = {placeholder}")
            params.append(category_filter)

        # Add tags filter
        if tags_filter:
            for tag in tags_filter:
                conditions.append(
                    f"tags ILIKE {placeholder}"
                    if self.db_type == "postgres"
                    else f"tags LIKE {placeholder}"
                )
                params.append(f"%{tag.strip()}%")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT id, tenant_id, user_id, name, title, content, category,
                   tags, description, is_builtin, created_at, updated_at
            FROM rules WHERE {where_clause}
            ORDER BY created_at DESC
        """

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        if self.db_type == "postgres":
            return [
                {
                    "id": row["id"],
                    "tenant_id": row["tenant_id"],
                    "user_id": row["user_id"],
                    "name": row["name"],
                    "title": row["title"],
                    "content": row["content"],
                    "category": row["category"],
                    "tags": row["tags"],
                    "description": row["description"],
                    "is_builtin": (
                        bool(row["is_builtin"])
                        if row["is_builtin"] is not None
                        else False
                    ),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
                for row in rows
            ]
        else:
            return [
                {
                    "id": row[0],
                    "tenant_id": row[1],
                    "user_id": row[2],
                    "name": row[3],
                    "title": row[4],
                    "content": row[5],
                    "category": row[6],
                    "tags": row[7],
                    "description": row[8],
                    "is_builtin": bool(row[9]) if row[9] is not None else False,
                    "created_at": row[10],
                    "updated_at": row[11],
                }
                for row in rows
            ]

    def get_rules_by_category(self, category: str) -> List[Dict]:
        """Get all rules in a specific category."""
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            cursor.execute(
                """
                SELECT id, tenant_id, user_id, name, title, content, category,
                       tags, description, is_builtin, created_at, updated_at
                FROM rules WHERE tenant_id = %s AND category = %s
                ORDER BY created_at DESC
            """,
                (self.tenant_id, category),
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "id": row["id"],
                    "tenant_id": row["tenant_id"],
                    "user_id": row["user_id"],
                    "name": row["name"],
                    "title": row["title"],
                    "content": row["content"],
                    "category": row["category"],
                    "tags": row["tags"],
                    "description": row["description"],
                    "is_builtin": (
                        bool(row["is_builtin"])
                        if row["is_builtin"] is not None
                        else False
                    ),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
                for row in rows
            ]
        else:
            cursor.execute(
                """
                SELECT id, tenant_id, user_id, name, title, content, category,
                       tags, description, is_builtin, created_at, updated_at
                FROM rules WHERE tenant_id = ? AND category = ?
                ORDER BY created_at DESC
            """,
                (self.tenant_id, category),
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "id": row[0],
                    "tenant_id": row[1],
                    "user_id": row[2],
                    "name": row[3],
                    "title": row[4],
                    "content": row[5],
                    "category": row[6],
                    "tags": row[7],
                    "description": row[8],
                    "is_builtin": bool(row[9]) if row[9] is not None else False,
                    "created_at": row[10],
                    "updated_at": row[11],
                }
                for row in rows
            ]

    def get_rule_by_name(self, name: str) -> Optional[Dict]:
        """Get a specific rule by name."""
        if not name.strip() or not self.tenant_id:
            return None

        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            cursor.execute(
                """
                SELECT id, tenant_id, user_id, name, title, content, category,
                       tags, description, is_builtin, created_at, updated_at
                FROM rules WHERE name = %s AND tenant_id = %s
            """,
                (name.strip(), self.tenant_id),
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "id": row["id"],
                    "tenant_id": row["tenant_id"],
                    "user_id": row["user_id"],
                    "name": row["name"],
                    "title": row["title"],
                    "content": row["content"],
                    "category": row["category"],
                    "tags": row["tags"],
                    "description": row["description"],
                    "is_builtin": (
                        bool(row["is_builtin"])
                        if row["is_builtin"] is not None
                        else False
                    ),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
        else:
            cursor.execute(
                """
                SELECT id, tenant_id, user_id, name, title, content, category,
                       tags, description, is_builtin, created_at, updated_at
                FROM rules WHERE name = ? AND tenant_id = ?
            """,
                (name.strip(), self.tenant_id),
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "id": row[0],
                    "tenant_id": row[1],
                    "user_id": row[2],
                    "name": row[3],
                    "title": row[4],
                    "content": row[5],
                    "category": row[6],
                    "tags": row[7],
                    "description": row[8],
                    "is_builtin": bool(row[9]) if row[9] is not None else False,
                    "created_at": row[10],
                    "updated_at": row[11],
                }
        return None

    # Tag Management Methods

    def get_all_tags(self, entity_type: str = "all") -> List[str]:
        """Get all unique tags across prompts, templates, and/or rules."""
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()
        all_tags = set()

        try:
            # Get tags from prompts
            if entity_type in ["all", "prompts"]:
                if self.db_type == "postgres":
                    cursor.execute(
                        "SELECT tags FROM prompts WHERE tenant_id = %s AND tags IS NOT NULL",
                        (self.tenant_id,),
                    )
                else:
                    cursor.execute(
                        "SELECT tags FROM prompts WHERE tenant_id = ? AND tags IS NOT NULL",
                        (self.tenant_id,),
                    )

                for row in cursor.fetchall():
                    if row[0]:
                        tags = [tag.strip() for tag in row[0].split(",") if tag.strip()]
                        all_tags.update(tags)

            # Get tags from templates
            if entity_type in ["all", "templates"]:
                if self.db_type == "postgres":
                    cursor.execute(
                        "SELECT tags FROM templates WHERE tenant_id = %s AND tags IS NOT NULL",
                        (self.tenant_id,),
                    )
                else:
                    cursor.execute(
                        "SELECT tags FROM templates WHERE tenant_id = ? AND tags IS NOT NULL",
                        (self.tenant_id,),
                    )

                for row in cursor.fetchall():
                    if row[0]:
                        tags = [tag.strip() for tag in row[0].split(",") if tag.strip()]
                        all_tags.update(tags)

            # Get tags from rules
            if entity_type in ["all", "rules"]:
                if self.db_type == "postgres":
                    cursor.execute(
                        "SELECT tags FROM rules WHERE tenant_id = %s AND tags IS NOT NULL",
                        (self.tenant_id,),
                    )
                else:
                    cursor.execute(
                        "SELECT tags FROM rules WHERE tenant_id = ? AND tags IS NOT NULL",
                        (self.tenant_id,),
                    )

                for row in cursor.fetchall():
                    if row[0]:
                        tags = [tag.strip() for tag in row[0].split(",") if tag.strip()]
                        all_tags.update(tags)

            conn.close()
            return sorted(list(all_tags))

        except Exception:
            conn.close()
            return []

    def search_by_tags(
        self,
        tags: List[str],
        entity_type: str = "prompts",
        match_all: bool = False,
        include_enhancement_prompts: bool = True,
    ) -> List[Dict]:
        """Search entities by tags with AND/OR logic."""
        if not tags or not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        # Prepare tag conditions
        tag_conditions = []
        params = [self.tenant_id]

        for tag in tags:
            if self.db_type == "postgres":
                tag_conditions.append("tags ILIKE %s")
                params.append(f"%{tag}%")
            else:
                tag_conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")

        # Join conditions with AND or OR
        condition_join = " AND " if match_all else " OR "
        tag_where = f"({condition_join.join(tag_conditions)})"

        try:
            if entity_type == "prompts":
                enhancement_filter = (
                    ""
                    if include_enhancement_prompts
                    else " AND is_enhancement_prompt = FALSE"
                )

                if self.db_type == "postgres":
                    query = f"""
                        SELECT id, tenant_id, user_id, name, title, content, category,
                               tags, is_enhancement_prompt, created_at, updated_at
                        FROM prompts
                        WHERE tenant_id = %s AND {tag_where}{enhancement_filter}
                        ORDER BY category, name
                    """
                else:
                    query = f"""
                        SELECT id, tenant_id, user_id, name, title, content, category,
                               tags, is_enhancement_prompt, created_at, updated_at
                        FROM prompts
                        WHERE tenant_id = ? AND {tag_where}{enhancement_filter}
                        ORDER BY category, name
                    """

                cursor.execute(query, params)
                results = []
                for row in cursor.fetchall():
                    results.append(
                        {
                            "id": row[0],
                            "tenant_id": row[1],
                            "user_id": row[2],
                            "name": row[3],
                            "title": row[4],
                            "content": row[5],
                            "category": row[6],
                            "tags": row[7],
                            "is_enhancement_prompt": (
                                bool(row[8]) if row[8] is not None else False
                            ),
                            "created_at": row[9],
                            "updated_at": row[10],
                        }
                    )

            elif entity_type == "templates":
                if self.db_type == "postgres":
                    query = f"""
                        SELECT id, tenant_id, user_id, name, description, content,
                               category, tags, variables, is_builtin, created_at, updated_at
                        FROM templates
                        WHERE tenant_id = %s AND {tag_where}
                        ORDER BY category, name
                    """
                else:
                    query = f"""
                        SELECT id, tenant_id, user_id, name, description, content,
                               category, tags, variables, is_builtin, created_at, updated_at
                        FROM templates
                        WHERE tenant_id = ? AND {tag_where}
                        ORDER BY category, name
                    """

                cursor.execute(query, params)
                results = []
                for row in cursor.fetchall():
                    results.append(
                        {
                            "id": row[0],
                            "tenant_id": row[1],
                            "user_id": row[2],
                            "name": row[3],
                            "description": row[4],
                            "content": row[5],
                            "category": row[6],
                            "tags": row[7],
                            "variables": row[8],
                            "is_builtin": bool(row[9]) if row[9] is not None else False,
                            "created_at": row[10],
                            "updated_at": row[11],
                        }
                    )
            else:
                results = []

            conn.close()
            return results

        except Exception:
            conn.close()
            return []

    def get_tag_statistics(self) -> Dict[str, Dict]:
        """Get statistics about tag usage across prompts, templates, and rules."""
        if not self.tenant_id:
            return {}

        conn = self.get_conn()
        cursor = conn.cursor()
        tag_stats = {}

        try:
            # Count tags in prompts
            if self.db_type == "postgres":
                cursor.execute(
                    "SELECT tags FROM prompts WHERE tenant_id = %s AND tags IS NOT NULL",
                    (self.tenant_id,),
                )
            else:
                cursor.execute(
                    "SELECT tags FROM prompts WHERE tenant_id = ? AND tags IS NOT NULL",
                    (self.tenant_id,),
                )

            for row in cursor.fetchall():
                if row[0]:
                    tags = [tag.strip() for tag in row[0].split(",") if tag.strip()]
                    for tag in tags:
                        if tag not in tag_stats:
                            tag_stats[tag] = {
                                "prompts": 0,
                                "templates": 0,
                                "rules": 0,
                                "total": 0,
                            }
                        tag_stats[tag]["prompts"] += 1
                        tag_stats[tag]["total"] += 1

            # Count tags in templates
            if self.db_type == "postgres":
                cursor.execute(
                    "SELECT tags FROM templates WHERE tenant_id = %s AND tags IS NOT NULL",
                    (self.tenant_id,),
                )
            else:
                cursor.execute(
                    "SELECT tags FROM templates WHERE tenant_id = ? AND tags IS NOT NULL",
                    (self.tenant_id,),
                )

            for row in cursor.fetchall():
                if row[0]:
                    tags = [tag.strip() for tag in row[0].split(",") if tag.strip()]
                    for tag in tags:
                        if tag not in tag_stats:
                            tag_stats[tag] = {
                                "prompts": 0,
                                "templates": 0,
                                "rules": 0,
                                "total": 0,
                            }
                        tag_stats[tag]["templates"] += 1
                        tag_stats[tag]["total"] += 1

            # Count tags in rules
            if self.db_type == "postgres":
                cursor.execute(
                    "SELECT tags FROM rules WHERE tenant_id = %s AND tags IS NOT NULL",
                    (self.tenant_id,),
                )
            else:
                cursor.execute(
                    "SELECT tags FROM rules WHERE tenant_id = ? AND tags IS NOT NULL",
                    (self.tenant_id,),
                )

            for row in cursor.fetchall():
                if row[0]:
                    tags = [tag.strip() for tag in row[0].split(",") if tag.strip()]
                    for tag in tags:
                        if tag not in tag_stats:
                            tag_stats[tag] = {
                                "prompts": 0,
                                "templates": 0,
                                "rules": 0,
                                "total": 0,
                            }
                        tag_stats[tag]["rules"] += 1
                        tag_stats[tag]["total"] += 1

            conn.close()
            return tag_stats

        except Exception:
            conn.close()
            return {}

    def get_popular_tags(self, entity_type: str = "all", limit: int = 10) -> List[Dict]:
        """Get most popular tags with usage counts."""
        tag_stats = self.get_tag_statistics()

        # Filter by entity type if specified
        if entity_type == "prompts":
            filtered_stats = {
                tag: stats for tag, stats in tag_stats.items() if stats["prompts"] > 0
            }
            sort_key = "prompts"
        elif entity_type == "templates":
            filtered_stats = {
                tag: stats for tag, stats in tag_stats.items() if stats["templates"] > 0
            }
            sort_key = "templates"
        else:
            filtered_stats = tag_stats
            sort_key = "total"

        # Sort by usage count and limit results
        popular_tags = [
            {"tag": tag, "count": stats[sort_key], "details": stats}
            for tag, stats in filtered_stats.items()
        ]
        popular_tags.sort(key=lambda x: x["count"], reverse=True)

        return popular_tags[:limit]

    def suggest_tags(self, partial_tag: str, limit: int = 5) -> List[str]:
        """Suggest tags based on partial input."""
        if not partial_tag.strip():
            return []

        all_tags = self.get_all_tags()
        partial_lower = partial_tag.lower()

        # Find exact matches first, then prefix matches, then substring matches
        exact_matches = [tag for tag in all_tags if tag.lower() == partial_lower]
        prefix_matches = [
            tag
            for tag in all_tags
            if tag.lower().startswith(partial_lower) and tag.lower() != partial_lower
        ]
        substring_matches = [
            tag
            for tag in all_tags
            if partial_lower in tag.lower()
            and not tag.lower().startswith(partial_lower)
        ]

        # Combine and limit results
        suggestions = exact_matches + prefix_matches + substring_matches
        return suggestions[:limit]

    def save_config(self, key: str, value: str) -> bool:
        """Save configuration for tenant/user"""
        if not self.tenant_id:
            return False

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    INSERT INTO config (tenant_id, user_id, key, value)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (tenant_id, user_id, key)
                    DO UPDATE SET value = EXCLUDED.value
                """,
                    (self.tenant_id, self.user_id, key, value),
                )
            else:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO config (tenant_id, user_id, key, value)
                    VALUES (?, ?, ?, ?)
                """,
                    (self.tenant_id, self.user_id, key, value),
                )

            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False

    def get_config(self, key: str) -> Optional[str]:
        """Get configuration for tenant/user"""
        if not self.tenant_id:
            return None

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT value FROM config
                    WHERE tenant_id = %s AND user_id = %s AND key = %s
                    """,
                    (self.tenant_id, self.user_id, key),
                )
            else:
                cursor.execute(
                    """
                    SELECT value FROM config
                    WHERE tenant_id = ? AND user_id = ? AND key = ?
                    """,
                    (self.tenant_id, self.user_id, key),
                )

            result = cursor.fetchone()
            conn.close()

            if result:
                value = result[0] if not self.db_type == "postgres" else result["value"]
                return str(value) if value is not None else None
            return None
        except Exception:
            conn.close()
            return None

    # Template management methods
    def get_all_templates(self) -> List[Dict]:
        """Get all templates for the current tenant"""
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, description, content,
                           category, tags, variables, is_builtin, created_at, updated_at
                    FROM templates
                    WHERE tenant_id = %s
                    ORDER BY created_at DESC
                    """,
                    (self.tenant_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, description, content,
                           category, tags, variables, is_builtin, created_at, updated_at
                    FROM templates
                    WHERE tenant_id = ?
                    ORDER BY created_at DESC
                    """,
                    (self.tenant_id,),
                )

            rows = cursor.fetchall()
            conn.close()

            templates = []
            for row in rows:
                if self.db_type == "postgres":
                    template = dict(row)
                else:
                    template = {
                        "id": row[0],
                        "tenant_id": row[1],
                        "user_id": row[2],
                        "name": row[3],
                        "description": row[4],
                        "content": row[5],
                        "category": row[6],
                        "tags": row[7],
                        "variables": row[8],
                        "is_builtin": bool(row[9]) if row[9] is not None else False,
                        "created_at": row[10],
                        "updated_at": row[11],
                    }
                templates.append(template)

            return templates
        except Exception:
            conn.close()
            return []

    def get_template_by_id(self, template_id: int) -> Optional[Dict]:
        """Get a specific template by ID"""
        if not self.tenant_id:
            return None

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, description, content,
                           category, tags, variables, is_builtin, created_at, updated_at
                    FROM templates
                    WHERE id = %s AND tenant_id = %s
                    """,
                    (template_id, self.tenant_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, description, content,
                           category, tags, variables, is_builtin, created_at, updated_at
                    FROM templates
                    WHERE id = ? AND tenant_id = ?
                    """,
                    (template_id, self.tenant_id),
                )

            row = cursor.fetchone()
            conn.close()

            if row:
                if self.db_type == "postgres":
                    return dict(row)
                else:
                    return {
                        "id": row[0],
                        "tenant_id": row[1],
                        "user_id": row[2],
                        "name": row[3],
                        "description": row[4],
                        "content": row[5],
                        "category": row[6],
                        "tags": row[7],
                        "variables": row[8],
                        "is_builtin": bool(row[9]) if row[9] is not None else False,
                        "created_at": row[10],
                        "updated_at": row[11],
                    }
            return None
        except Exception:
            conn.close()
            return None

    def get_template_by_name(self, name: str) -> Optional[Dict]:
        """Get a specific template by name"""
        if not self.tenant_id:
            return None

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, description, content,
                           category, tags, variables, is_builtin, created_at, updated_at
                    FROM templates
                    WHERE name = %s AND tenant_id = %s
                    """,
                    (name, self.tenant_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, description, content,
                           category, tags, variables, is_builtin, created_at, updated_at
                    FROM templates
                    WHERE name = ? AND tenant_id = ?
                    """,
                    (name, self.tenant_id),
                )

            row = cursor.fetchone()
            conn.close()

            if row:
                if self.db_type == "postgres":
                    return dict(row)
                else:
                    return {
                        "id": row[0],
                        "tenant_id": row[1],
                        "user_id": row[2],
                        "name": row[3],
                        "description": row[4],
                        "content": row[5],
                        "category": row[6],
                        "tags": row[7],
                        "variables": row[8],
                        "is_builtin": bool(row[9]) if row[9] is not None else False,
                        "created_at": row[10],
                        "updated_at": row[11],
                    }
            return None
        except Exception:
            conn.close()
            return None

    def create_template(
        self,
        name: str,
        description: str,
        content: str,
        category: str = "Custom",
        variables: str = "",
        tags: str = "",
    ) -> str:
        """Create a new template"""
        if not self.tenant_id or not self.user_id:
            return "Error: Missing tenant or user information"

        if not name or not content:
            return "Error: Template name and content are required"

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            current_time = datetime.now().isoformat()

            if self.db_type == "postgres":
                cursor.execute(
                    """
                    INSERT INTO templates (tenant_id, user_id, name, description,
                                          content, category, tags, variables, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        self.tenant_id,
                        self.user_id,
                        name,
                        description,
                        content,
                        category,
                        tags,
                        variables,
                        current_time,
                        current_time,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO templates (tenant_id, user_id, name, description,
                                          content, category, tags, variables, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.tenant_id,
                        self.user_id,
                        name,
                        description,
                        content,
                        category,
                        tags,
                        variables,
                        current_time,
                        current_time,
                    ),
                )

            conn.commit()
            conn.close()
            return "Template created successfully"

        except Exception as e:
            conn.close()
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                return "Error: A template with this name already exists"
            return f"Error: Failed to create template - {str(e)}"

    def update_template(
        self,
        template_id: int,
        name: str,
        description: str,
        content: str,
        category: str = "Custom",
        variables: str = "",
        tags: str = "",
    ) -> str:
        """Update an existing template"""
        if not self.tenant_id or not self.user_id:
            return "Error: Missing tenant or user information"

        if not name or not content:
            return "Error: Template name and content are required"

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            current_time = datetime.now().isoformat()

            if self.db_type == "postgres":
                cursor.execute(
                    """
                    UPDATE templates
                    SET name = %s, description = %s, content = %s,
                        category = %s, tags = %s, variables = %s, updated_at = %s
                    WHERE id = %s AND tenant_id = %s AND user_id = %s
                    """,
                    (
                        name,
                        description,
                        content,
                        category,
                        tags,
                        variables,
                        current_time,
                        template_id,
                        self.tenant_id,
                        self.user_id,
                    ),
                )
            else:
                cursor.execute(
                    """
                    UPDATE templates
                    SET name = ?, description = ?, content = ?,
                        category = ?, tags = ?, variables = ?, updated_at = ?
                    WHERE id = ? AND tenant_id = ? AND user_id = ?
                    """,
                    (
                        name,
                        description,
                        content,
                        category,
                        tags,
                        variables,
                        current_time,
                        template_id,
                        self.tenant_id,
                        self.user_id,
                    ),
                )

            if cursor.rowcount == 0:
                conn.close()
                return (
                    "Error: Template not found or you don't have permission to edit it"
                )

            conn.commit()
            conn.close()
            return "Template updated successfully"

        except Exception as e:
            conn.close()
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                return "Error: A template with this name already exists"
            return f"Error: Failed to update template - {str(e)}"

    def delete_template(self, template_id: int) -> bool:
        """Delete a template"""
        if not self.tenant_id or not self.user_id:
            return False

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    DELETE FROM templates
                    WHERE id = %s AND tenant_id = %s AND user_id = %s
                    AND is_builtin = FALSE
                    """,
                    (template_id, self.tenant_id, self.user_id),
                )
            else:
                cursor.execute(
                    """
                    DELETE FROM templates
                    WHERE id = ? AND tenant_id = ? AND user_id = ?
                    AND is_builtin = 0
                    """,
                    (template_id, self.tenant_id, self.user_id),
                )

            success = bool(cursor.rowcount > 0)
            conn.commit()
            conn.close()
            return success

        except Exception:
            conn.close()
            return False

    def get_template_categories(self) -> List[str]:
        """Get all unique template categories for the current tenant"""
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT DISTINCT category FROM templates
                    WHERE tenant_id = %s ORDER BY category
                    """,
                    (self.tenant_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT DISTINCT category FROM templates
                    WHERE tenant_id = ? ORDER BY category
                    """,
                    (self.tenant_id,),
                )

            rows = cursor.fetchall()
            conn.close()

            categories = []
            for row in rows:
                category = row[0] if not self.db_type == "postgres" else row["category"]
                if category:
                    categories.append(category)

            # Add default categories if not present
            default_categories = [
                "Business",
                "Technical",
                "Creative",
                "Analytical",
                "Custom",
                "General",
            ]
            for cat in default_categories:
                if cat not in categories:
                    categories.append(cat)

            return sorted(categories)
        except Exception:
            conn.close()
            return [
                "Business",
                "Technical",
                "Creative",
                "Analytical",
                "Custom",
                "General",
            ]

    # AI Model Management Methods

    def add_ai_model(self, model_data: Dict) -> bool:
        """Add a new AI model configuration"""
        if not self.tenant_id:
            return False

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    INSERT INTO ai_models (
                        tenant_id, user_id, name, display_name, provider, model_id, description,
                        api_key, api_endpoint, api_version, deployment_name, max_tokens,
                        temperature, top_p, frequency_penalty, presence_penalty,
                        cost_per_1k_input_tokens, cost_per_1k_output_tokens, max_context_length,
                        supports_streaming, supports_function_calling,
                        supports_vision, supports_json_mode,
                        is_enabled, is_available
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    """,
                    (
                        self.tenant_id,
                        self.user_id,
                        model_data.get("name"),
                        model_data.get("display_name"),
                        model_data.get("provider"),
                        model_data.get("model_id"),
                        model_data.get("description"),
                        model_data.get("api_key"),
                        model_data.get("api_endpoint"),
                        model_data.get("api_version"),
                        model_data.get("deployment_name"),
                        model_data.get("max_tokens"),
                        model_data.get("temperature", 0.7),
                        model_data.get("top_p", 1.0),
                        model_data.get("frequency_penalty", 0.0),
                        model_data.get("presence_penalty", 0.0),
                        model_data.get("cost_per_1k_input_tokens", 0.0),
                        model_data.get("cost_per_1k_output_tokens", 0.0),
                        model_data.get("max_context_length"),
                        model_data.get("supports_streaming", False),
                        model_data.get("supports_function_calling", False),
                        model_data.get("supports_vision", False),
                        model_data.get("supports_json_mode", False),
                        model_data.get("is_enabled", True),
                        model_data.get("is_available", False),
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO ai_models (
                        tenant_id, user_id, name, display_name, provider, model_id, description,
                        api_key, api_endpoint, api_version, deployment_name, max_tokens,
                        temperature, top_p, frequency_penalty, presence_penalty,
                        cost_per_1k_input_tokens, cost_per_1k_output_tokens, max_context_length,
                        supports_streaming, supports_function_calling,
                        supports_vision, supports_json_mode,
                        is_enabled, is_available
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        self.tenant_id,
                        self.user_id,
                        model_data.get("name"),
                        model_data.get("display_name"),
                        model_data.get("provider"),
                        model_data.get("model_id"),
                        model_data.get("description"),
                        model_data.get("api_key"),
                        model_data.get("api_endpoint"),
                        model_data.get("api_version"),
                        model_data.get("deployment_name"),
                        model_data.get("max_tokens"),
                        model_data.get("temperature", 0.7),
                        model_data.get("top_p", 1.0),
                        model_data.get("frequency_penalty", 0.0),
                        model_data.get("presence_penalty", 0.0),
                        model_data.get("cost_per_1k_input_tokens", 0.0),
                        model_data.get("cost_per_1k_output_tokens", 0.0),
                        model_data.get("max_context_length"),
                        int(model_data.get("supports_streaming", False)),
                        int(model_data.get("supports_function_calling", False)),
                        int(model_data.get("supports_vision", False)),
                        int(model_data.get("supports_json_mode", False)),
                        int(model_data.get("is_enabled", True)),
                        int(model_data.get("is_available", False)),
                    ),
                )

            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False

    def get_ai_models(self) -> List[Dict]:
        """Get all AI models for the current tenant"""
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, display_name, provider,
                           model_id, description, api_key, api_endpoint, api_version,
                           deployment_name, max_tokens, temperature, top_p,
                           frequency_penalty, presence_penalty,
                           cost_per_1k_input_tokens, cost_per_1k_output_tokens,
                           max_context_length, supports_streaming,
                           supports_function_calling, supports_vision,
                           supports_json_mode, is_enabled, is_available,
                           last_health_check, created_at, updated_at
                    FROM ai_models WHERE tenant_id = %s ORDER BY name
                    """,
                    (self.tenant_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, display_name, provider,
                           model_id, description, api_key, api_endpoint, api_version,
                           deployment_name, max_tokens, temperature, top_p,
                           frequency_penalty, presence_penalty,
                           cost_per_1k_input_tokens, cost_per_1k_output_tokens,
                           max_context_length, supports_streaming,
                           supports_function_calling, supports_vision,
                           supports_json_mode, is_enabled, is_available,
                           last_health_check, created_at, updated_at
                    FROM ai_models WHERE tenant_id = ? ORDER BY name
                    """,
                    (self.tenant_id,),
                )

            models = []
            for row in cursor.fetchall():
                if self.db_type == "postgres":
                    model = dict(row)
                else:
                    model = {
                        "id": row[0],
                        "tenant_id": row[1],
                        "user_id": row[2],
                        "name": row[3],
                        "display_name": row[4],
                        "provider": row[5],
                        "model_id": row[6],
                        "description": row[7],
                        "api_key": row[8],
                        "api_endpoint": row[9],
                        "api_version": row[10],
                        "deployment_name": row[11],
                        "max_tokens": row[12],
                        "temperature": row[13],
                        "top_p": row[14],
                        "frequency_penalty": row[15],
                        "presence_penalty": row[16],
                        "cost_per_1k_input_tokens": row[17],
                        "cost_per_1k_output_tokens": row[18],
                        "max_context_length": row[19],
                        "supports_streaming": bool(row[20]),
                        "supports_function_calling": bool(row[21]),
                        "supports_vision": bool(row[22]),
                        "supports_json_mode": bool(row[23]),
                        "is_enabled": bool(row[24]),
                        "is_available": bool(row[25]),
                        "last_health_check": row[26],
                        "created_at": row[27],
                        "updated_at": row[28],
                    }
                models.append(model)

            conn.close()
            return models
        except Exception:
            conn.close()
            return []

    def update_ai_model(self, model_name: str, updates: Dict) -> bool:
        """Update an AI model configuration"""
        if not self.tenant_id:
            return False

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            # Build dynamic update query
            set_clauses = []
            values = []

            for key, value in updates.items():
                if key in [
                    "display_name",
                    "description",
                    "api_key",
                    "api_endpoint",
                    "api_version",
                    "deployment_name",
                    "max_tokens",
                    "temperature",
                    "top_p",
                    "frequency_penalty",
                    "presence_penalty",
                    "cost_per_1k_input_tokens",
                    "cost_per_1k_output_tokens",
                    "max_context_length",
                    "supports_streaming",
                    "supports_function_calling",
                    "supports_vision",
                    "supports_json_mode",
                    "is_enabled",
                    "is_available",
                    "last_health_check",
                ]:
                    set_clauses.append(
                        f"{key} = {'%s' if self.db_type == 'postgres' else '?'}"
                    )
                    if key.startswith("supports_") or key in [
                        "is_enabled",
                        "is_available",
                    ]:
                        values.append(
                            value if self.db_type == "postgres" else int(value)
                        )
                    else:
                        values.append(value)

            if not set_clauses:
                # No valid fields to update, but this is not an error
                conn.close()
                return True

            # Add updated_at
            set_clauses.append(
                "updated_at = "
                + (
                    "CURRENT_TIMESTAMP"
                    if self.db_type == "postgres"
                    else "CURRENT_TIMESTAMP"
                )
            )

            # Add WHERE clause values
            values.extend([self.tenant_id, model_name])

            # set_clauses and WHERE params are controlled, not user input  # nosec B608
            query = f"""
                UPDATE ai_models
                SET {', '.join(set_clauses)}
                WHERE tenant_id = {'%s' if self.db_type == 'postgres' else '?'}
                AND name = {'%s' if self.db_type == 'postgres' else '?'}
            """

            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return bool(cursor.rowcount > 0)
        except Exception:
            conn.close()
            return False

    def delete_ai_model(self, model_name: str) -> bool:
        """Delete an AI model configuration"""
        if not self.tenant_id:
            return False

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    "DELETE FROM ai_models WHERE tenant_id = %s AND name = %s",
                    (self.tenant_id, model_name),
                )
            else:
                cursor.execute(
                    "DELETE FROM ai_models WHERE tenant_id = ? AND name = ?",
                    (self.tenant_id, model_name),
                )

            conn.commit()
            conn.close()
            return bool(cursor.rowcount > 0)
        except Exception:
            conn.close()
            return False

    def get_ai_operation_configs(self) -> List[Dict]:
        """Get all AI operation configurations for the current tenant"""
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, operation_type, primary_model,
                           fallback_models, is_enabled, custom_parameters,
                           created_at, updated_at
                    FROM ai_operation_configs WHERE tenant_id = %s
                    ORDER BY operation_type
                    """,
                    (self.tenant_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, operation_type, primary_model,
                           fallback_models, is_enabled, custom_parameters,
                           created_at, updated_at
                    FROM ai_operation_configs WHERE tenant_id = ?
                    ORDER BY operation_type
                    """,
                    (self.tenant_id,),
                )

            configs = []
            for row in cursor.fetchall():
                if self.db_type == "postgres":
                    config = dict(row)
                else:
                    config = {
                        "id": row[0],
                        "tenant_id": row[1],
                        "user_id": row[2],
                        "operation_type": row[3],
                        "primary_model": row[4],
                        "fallback_models": row[5],
                        "is_enabled": bool(row[6]),
                        "custom_parameters": row[7],
                        "created_at": row[8],
                        "updated_at": row[9],
                    }
                configs.append(config)

            conn.close()
            return configs
        except Exception:
            conn.close()
            return []

    def update_ai_operation_config(
        self, operation_type: str, config_data: Dict
    ) -> bool:
        """Update or create an AI operation configuration"""
        if not self.tenant_id:
            return False

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            # Check if config exists
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT id FROM ai_operation_configs
                    WHERE tenant_id = %s AND operation_type = %s
                    """,
                    (self.tenant_id, operation_type),
                )
            else:
                cursor.execute(
                    """
                    SELECT id FROM ai_operation_configs
                    WHERE tenant_id = ? AND operation_type = ?
                    """,
                    (self.tenant_id, operation_type),
                )

            exists = cursor.fetchone() is not None

            if exists:
                # Update existing config
                if self.db_type == "postgres":
                    cursor.execute(
                        """
                        UPDATE ai_operation_configs
                        SET primary_model = %s, fallback_models = %s, is_enabled = %s,
                            custom_parameters = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE tenant_id = %s AND operation_type = %s
                        """,
                        (
                            config_data.get("primary_model"),
                            config_data.get("fallback_models"),
                            config_data.get("is_enabled", True),
                            config_data.get("custom_parameters"),
                            self.tenant_id,
                            operation_type,
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE ai_operation_configs
                        SET primary_model = ?, fallback_models = ?, is_enabled = ?,
                            custom_parameters = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE tenant_id = ? AND operation_type = ?
                        """,
                        (
                            config_data.get("primary_model"),
                            config_data.get("fallback_models"),
                            int(config_data.get("is_enabled", True)),
                            config_data.get("custom_parameters"),
                            self.tenant_id,
                            operation_type,
                        ),
                    )
            else:
                # Create new config
                if self.db_type == "postgres":
                    cursor.execute(
                        """
                        INSERT INTO ai_operation_configs (
                            tenant_id, user_id, operation_type, primary_model, fallback_models,
                            is_enabled, custom_parameters
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            self.tenant_id,
                            self.user_id,
                            operation_type,
                            config_data.get("primary_model"),
                            config_data.get("fallback_models"),
                            config_data.get("is_enabled", True),
                            config_data.get("custom_parameters"),
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO ai_operation_configs (
                            tenant_id, user_id, operation_type, primary_model, fallback_models,
                            is_enabled, custom_parameters
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            self.tenant_id,
                            self.user_id,
                            operation_type,
                            config_data.get("primary_model"),
                            config_data.get("fallback_models"),
                            int(config_data.get("is_enabled", True)),
                            config_data.get("custom_parameters"),
                        ),
                    )

            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False

    def get_all_prompts_with_visibility(
        self,
        include_enhancement_prompts: bool = True,
        include_public_from_tenant: bool = True,
    ) -> List[Dict]:
        """
        Get prompts with visibility filtering.
        - Always includes user's own prompts (private + public)
        - Optionally includes public prompts from other users in the same tenant
        """
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        # Base query conditions
        conditions = [
            "tenant_id = %s" if self.db_type == "postgres" else "tenant_id = ?"
        ]
        params = [self.tenant_id]

        # Visibility filtering
        if include_public_from_tenant:
            # Include user's own prompts AND public prompts from others
            visibility_condition = (
                "(user_id = %s OR visibility = 'public')"
                if self.db_type == "postgres"
                else "(user_id = ? OR visibility = 'public')"
            )
            conditions.append(visibility_condition)
            params.append(self.user_id)
        else:
            # Only user's own prompts
            user_condition = (
                "user_id = %s" if self.db_type == "postgres" else "user_id = ?"
            )
            conditions.append(user_condition)
            params.append(self.user_id)

        # Enhancement prompt filtering
        if not include_enhancement_prompts:
            enhancement_condition = (
                "is_enhancement_prompt = FALSE"
                if self.db_type == "postgres"
                else "is_enhancement_prompt = 0"
            )
            conditions.append(enhancement_condition)

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT id, tenant_id, user_id, name, title, content, category,
            tags, is_enhancement_prompt, visibility, created_at, updated_at
            FROM prompts WHERE {where_clause} ORDER BY category, name
        """

        cursor.execute(query, tuple(params))

        prompts = []
        for row in cursor.fetchall():
            prompts.append(
                {
                    "id": row[0],
                    "tenant_id": row[1],
                    "user_id": row[2],
                    "name": row[3],
                    "title": row[4],
                    "content": row[5],
                    "category": row[6],
                    "tags": row[7],
                    "is_enhancement_prompt": (
                        bool(row[8]) if row[8] is not None else False
                    ),
                    "visibility": row[9] if row[9] is not None else "private",
                    "created_at": row[10],
                    "updated_at": row[11],
                }
            )
        conn.close()
        return prompts

    def get_public_prompts_in_tenant(
        self, include_enhancement_prompts: bool = True
    ) -> List[Dict]:
        """Get all public prompts within the tenant (excluding user's own prompts)"""
        if not self.tenant_id or not self.user_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            if include_enhancement_prompts:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts 
                    WHERE tenant_id = %s AND visibility = 'public' AND user_id != %s
                    ORDER BY category, name
                """,
                    (self.tenant_id, self.user_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts 
                    WHERE tenant_id = %s AND visibility = 'public' AND user_id != %s
                    AND is_enhancement_prompt = FALSE
                    ORDER BY category, name
                """,
                    (self.tenant_id, self.user_id),
                )
        else:
            if include_enhancement_prompts:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts 
                    WHERE tenant_id = ? AND visibility = 'public' AND user_id != ?
                    ORDER BY category, name
                """,
                    (self.tenant_id, self.user_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category,
                    tags, is_enhancement_prompt, visibility, created_at, updated_at
                    FROM prompts 
                    WHERE tenant_id = ? AND visibility = 'public' AND user_id != ?
                    AND is_enhancement_prompt = 0
                    ORDER BY category, name
                """,
                    (self.tenant_id, self.user_id),
                )

        prompts = []
        for row in cursor.fetchall():
            prompts.append(
                {
                    "id": row[0],
                    "tenant_id": row[1],
                    "user_id": row[2],
                    "name": row[3],
                    "title": row[4],
                    "content": row[5],
                    "category": row[6],
                    "tags": row[7],
                    "is_enhancement_prompt": (
                        bool(row[8]) if row[8] is not None else False
                    ),
                    "visibility": row[9] if row[9] is not None else "private",
                    "created_at": row[10],
                    "updated_at": row[11],
                }
            )
        conn.close()
        return prompts
