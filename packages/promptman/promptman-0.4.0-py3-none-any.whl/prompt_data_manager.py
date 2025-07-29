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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, name)
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

            # Add columns to existing tables if they don't exist
            cursor.execute(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='prompts' AND column_name='tenant_id') THEN
                        ALTER TABLE prompts ADD COLUMN tenant_id UUID;
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='prompts' AND column_name='user_id') THEN
                        ALTER TABLE prompts ADD COLUMN user_id UUID;
                    END IF;
                END $$;
            """
            )
            cursor.execute(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='config' AND column_name='tenant_id') THEN
                        ALTER TABLE config ADD COLUMN tenant_id UUID;
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='config' AND column_name='user_id') THEN
                        ALTER TABLE config ADD COLUMN user_id UUID;
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='config' AND column_name='id') THEN
                        ALTER TABLE config ADD COLUMN id SERIAL PRIMARY KEY;
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tenant_id, name)
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
            cursor.execute("PRAGMA table_info(prompts)")
            columns = [column[1] for column in cursor.fetchall()]
            if "is_enhancement_prompt" not in columns:
                cursor.execute(
                    "ALTER TABLE prompts ADD COLUMN is_enhancement_prompt BOOLEAN DEFAULT 0"
                )
            if "tenant_id" not in columns:
                cursor.execute("ALTER TABLE prompts ADD COLUMN tenant_id TEXT")
            if "user_id" not in columns:
                cursor.execute("ALTER TABLE prompts ADD COLUMN user_id TEXT")
            if "name" not in columns:
                cursor.execute("ALTER TABLE prompts ADD COLUMN name TEXT")
                cursor.execute("UPDATE prompts SET name = title WHERE name IS NULL")

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
    ) -> str:
        if not name.strip():
            return "Error: Name is required!"
        if not title.strip() or not content.strip():
            return "Error: Title and content are required!"
        if not self.tenant_id:
            return "Error: No tenant context available!"

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
                INSERT INTO prompts (tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    datetime.now(),
                    datetime.now(),
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO prompts (tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    ) -> str:
        if not original_name.strip() or not new_name.strip():
            return "Error: Original name and new name are required!"
        if not title.strip() or not content.strip():
            return "Error: Title and content are required!"
        if not self.tenant_id:
            return "Error: No tenant context available!"

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
                return f"Error: A prompt with name '{new_name}' already exists in your workspace!"

        if self.db_type == "postgres":
            cursor.execute(
                """
                UPDATE prompts
                SET name=%s, title=%s, content=%s, category=%s, tags=%s, is_enhancement_prompt=%s, updated_at=%s
                WHERE name=%s AND tenant_id=%s
            """,
                (
                    new_name,
                    title.strip(),
                    content.strip(),
                    category,
                    tags.strip(),
                    is_enhancement_prompt,
                    datetime.now(),
                    original_name,
                    self.tenant_id,
                ),
            )
        else:
            cursor.execute(
                """
                UPDATE prompts
                SET name=?, title=?, content=?, category=?, tags=?, is_enhancement_prompt=?, updated_at=?
                WHERE name=? AND tenant_id=?
            """,
                (
                    new_name,
                    title.strip(),
                    content.strip(),
                    category,
                    tags.strip(),
                    is_enhancement_prompt,
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
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            if include_enhancement_prompts:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts WHERE tenant_id = %s ORDER BY category, name
                """,
                    (self.tenant_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts WHERE tenant_id = %s AND is_enhancement_prompt = FALSE ORDER BY category, name
                """,
                    (self.tenant_id,),
                )
        else:
            if include_enhancement_prompts:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts WHERE tenant_id = ? ORDER BY category, name
                """,
                    (self.tenant_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts WHERE tenant_id = ? AND is_enhancement_prompt = 0 ORDER BY category, name
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
                    "created_at": row[9],
                    "updated_at": row[10],
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
                SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                FROM prompts WHERE tenant_id = %s AND is_enhancement_prompt = TRUE ORDER BY name
            """,
                (self.tenant_id,),
            )
        else:
            cursor.execute(
                """
                SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                FROM prompts WHERE tenant_id = ? AND is_enhancement_prompt = 1 ORDER BY name
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
                "SELECT DISTINCT category FROM prompts WHERE tenant_id = %s ORDER BY category",
                (self.tenant_id,),
            )
        else:
            cursor.execute(
                "SELECT DISTINCT category FROM prompts WHERE tenant_id = ? ORDER BY category",
                (self.tenant_id,),
            )

        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories

    def search_prompts(
        self, search_term: str, include_enhancement_prompts: bool = True
    ) -> List[Dict]:
        if not search_term.strip():
            return self.get_all_prompts(include_enhancement_prompts)
        if not self.tenant_id:
            return []

        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            like = f"%{search_term}%"
            if include_enhancement_prompts:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts
                    WHERE tenant_id = %s AND (name ILIKE %s OR title ILIKE %s OR content ILIKE %s OR tags ILIKE %s)
                    ORDER BY category, name
                """,
                    (self.tenant_id, like, like, like, like),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts
                    WHERE tenant_id = %s AND (name ILIKE %s OR title ILIKE %s OR content ILIKE %s OR tags ILIKE %s) AND is_enhancement_prompt = FALSE
                    ORDER BY category, name
                """,
                    (self.tenant_id, like, like, like, like),
                )
        else:
            if include_enhancement_prompts:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts
                    WHERE tenant_id = ? AND (name LIKE ? OR title LIKE ? OR content LIKE ? OR tags LIKE ?)
                    ORDER BY category, name
                """,
                    (
                        self.tenant_id,
                        f"%{search_term}%",
                        f"%{search_term}%",
                        f"%{search_term}%",
                        f"%{search_term}%",
                    ),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts
                    WHERE tenant_id = ? AND (name LIKE ? OR title LIKE ? OR content LIKE ? OR tags LIKE ?) AND is_enhancement_prompt = 0
                    ORDER BY category, name
                """,
                    (
                        self.tenant_id,
                        f"%{search_term}%",
                        f"%{search_term}%",
                        f"%{search_term}%",
                        f"%{search_term}%",
                    ),
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
                    "created_at": row[9],
                    "updated_at": row[10],
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
                    SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts WHERE tenant_id = %s AND category = %s
                    ORDER BY name
                """,
                    (self.tenant_id, category),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts WHERE tenant_id = %s AND category = %s AND is_enhancement_prompt = FALSE
                    ORDER BY name
                """,
                    (self.tenant_id, category),
                )
        else:
            if include_enhancement_prompts:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts WHERE tenant_id = ? AND category = ?
                    ORDER BY name
                """,
                    (self.tenant_id, category),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
                    FROM prompts WHERE tenant_id = ? AND category = ? AND is_enhancement_prompt = 0
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
                    "created_at": row[9],
                    "updated_at": row[10],
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
                SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
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
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
        else:
            cursor.execute(
                """
                SELECT id, tenant_id, user_id, name, title, content, category, tags, is_enhancement_prompt, created_at, updated_at
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
                    "created_at": row[9],
                    "updated_at": row[10],
                }
        return None

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
                    "SELECT value FROM config WHERE tenant_id = %s AND user_id = %s AND key = %s",
                    (self.tenant_id, self.user_id, key),
                )
            else:
                cursor.execute(
                    "SELECT value FROM config WHERE tenant_id = ? AND user_id = ? AND key = ?",
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
