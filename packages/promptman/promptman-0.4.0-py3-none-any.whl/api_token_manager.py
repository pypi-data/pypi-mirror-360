"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

API Token Management System
Handles creation, validation, and management of API tokens for user
authentication

This software is licensed for non-commercial use only.
See LICENSE file for details.
"""

import hashlib
import os
import secrets
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

load_dotenv()


@dataclass
class APIToken:
    id: str
    user_id: str
    tenant_id: str
    name: str
    token_prefix: str  # First 8 chars for display
    token_hash: str
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    created_at: datetime
    is_active: bool


class APITokenManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_type = os.getenv("DB_TYPE", "sqlite").lower()
        if self.db_type == "postgres":
            if not POSTGRES_AVAILABLE:
                raise ImportError("psycopg2 is required for Postgres support.")
            self.dsn = os.getenv("POSTGRES_DSN")
            if not self.dsn:
                raise ValueError(
                    "POSTGRES_DSN environment variable must be set for Postgres."
                )
            self.db_path: Optional[str] = None
        else:
            self.db_path = db_path or os.getenv("DB_PATH", "prompts.db")

        self.init_api_token_database()

    def get_conn(self):
        if self.db_type == "postgres":
            return psycopg2.connect(self.dsn, cursor_factory=RealDictCursor)
        else:
            if self.db_path is None:
                raise ValueError("Database path not set for SQLite connection")
            return sqlite3.connect(self.db_path)

    def init_api_token_database(self):
        """Initialize API token tables"""
        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS api_tokens (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL,
                    tenant_id UUID NOT NULL,
                    name TEXT NOT NULL,
                    token_prefix TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    expires_at TIMESTAMP,
                    last_used TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    UNIQUE(user_id, name)
                )
            """
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS api_tokens (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    token_prefix TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    expires_at TIMESTAMP,
                    last_used TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    UNIQUE(user_id, name)
                )
            """
            )

        conn.commit()
        conn.close()

    def generate_secure_token(self) -> Tuple[str, str, str]:
        """
        Generate a secure API token following industry standards
        Returns: (full_token, token_prefix, token_hash)
        """
        # Generate a cryptographically secure random token
        # Format: apm_<random_32_chars> (AI Prompt Manager prefix)
        random_part = secrets.token_urlsafe(24)  # 32 chars base64url
        full_token = f"apm_{random_part}"

        # Store only first 8 chars for display (after prefix)
        token_prefix = full_token[:12]  # "apm_" + first 8 chars

        # Hash the full token for secure storage
        token_hash = hashlib.sha256(full_token.encode()).hexdigest()

        return full_token, token_prefix, token_hash

    def create_api_token(
        self,
        user_id: str,
        tenant_id: str,
        name: str,
        expires_days: Optional[int] = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new API token for a user
        Returns: (success, message, full_token_if_success)
        """
        if not name.strip():
            return False, "Token name is required", None

        # Check if token name already exists for this user
        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT id FROM api_tokens
                    WHERE user_id = %s AND name = %s AND is_active = TRUE
                """,
                    (user_id, name.strip()),
                )
            else:
                cursor.execute(
                    """
                    SELECT id FROM api_tokens
                    WHERE user_id = ? AND name = ? AND is_active = 1
                """,
                    (user_id, name.strip()),
                )

            if cursor.fetchone():
                conn.close()
                return False, f"Token with name '{name}' already exists", None

            # Generate secure token
            full_token, token_prefix, token_hash = self.generate_secure_token()

            # Calculate expiration
            expires_at = None
            if expires_days and expires_days > 0:
                expires_at = datetime.now() + timedelta(days=expires_days)

            # Store token
            token_id = str(uuid.uuid4())
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    INSERT INTO api_tokens (id, user_id, tenant_id, name, token_prefix, token_hash, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        token_id,
                        user_id,
                        tenant_id,
                        name.strip(),
                        token_prefix,
                        token_hash,
                        expires_at,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO api_tokens (id, user_id, tenant_id, name, token_prefix, token_hash, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        token_id,
                        user_id,
                        tenant_id,
                        name.strip(),
                        token_prefix,
                        token_hash,
                        expires_at.isoformat() if expires_at else None,
                    ),
                )

            conn.commit()
            conn.close()

            expiry_msg = (
                f" (expires in {expires_days} days)"
                if expires_days
                else " (never expires)"
            )
            return (
                True,
                f"API token '{name}' created successfully{expiry_msg}",
                full_token,
            )

        except Exception as e:
            conn.close()
            return False, f"Error creating token: {str(e)}", None

    def validate_api_token(
        self, token: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate an API token and return user/tenant info
        Returns: (is_valid, user_id, tenant_id)
        """
        if not token or not token.startswith("apm_"):
            return False, None, None

        # Hash the provided token
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            current_time = datetime.now()

            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT user_id, tenant_id, id FROM api_tokens
                    WHERE token_hash = %s AND is_active = TRUE
                    AND (expires_at IS NULL OR expires_at > %s)
                """,
                    (token_hash, current_time),
                )
            else:
                cursor.execute(
                    """
                    SELECT user_id, tenant_id, id FROM api_tokens
                    WHERE token_hash = ? AND is_active = 1
                    AND (expires_at IS NULL OR expires_at > ?)
                """,
                    (token_hash, current_time.isoformat()),
                )

            result = cursor.fetchone()

            if result:
                if self.db_type == "postgres":
                    user_id, tenant_id, token_id = (
                        result["user_id"],
                        result["tenant_id"],
                        result["id"],
                    )
                else:
                    user_id, tenant_id, token_id = result[0], result[1], result[2]

                # Update last_used timestamp
                if self.db_type == "postgres":
                    cursor.execute(
                        """
                        UPDATE api_tokens SET last_used = %s WHERE id = %s
                    """,
                        (current_time, token_id),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE api_tokens SET last_used = ? WHERE id = ?
                    """,
                        (current_time.isoformat(), token_id),
                    )

                conn.commit()
                conn.close()
                return True, user_id, tenant_id
            else:
                conn.close()
                return False, None, None

        except Exception:
            conn.close()
            return False, None, None

    def get_user_tokens(self, user_id: str) -> List[APIToken]:
        """Get all active API tokens for a user"""
        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT id, user_id, tenant_id, name, token_prefix, token_hash,
                           expires_at, last_used, created_at, is_active
                    FROM api_tokens
                    WHERE user_id = %s AND is_active = TRUE
                    ORDER BY created_at DESC
                """,
                    (user_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, user_id, tenant_id, name, token_prefix, token_hash,
                           expires_at, last_used, created_at, is_active
                    FROM api_tokens
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY created_at DESC
                """,
                    (user_id,),
                )

            tokens = []
            for row in cursor.fetchall():
                if self.db_type == "postgres":
                    token = APIToken(
                        id=row["id"],
                        user_id=row["user_id"],
                        tenant_id=row["tenant_id"],
                        name=row["name"],
                        token_prefix=row["token_prefix"],
                        token_hash=row["token_hash"],
                        expires_at=row["expires_at"],
                        last_used=row["last_used"],
                        created_at=row["created_at"],
                        is_active=bool(row["is_active"]),
                    )
                else:
                    expires_at = datetime.fromisoformat(row[6]) if row[6] else None
                    last_used = datetime.fromisoformat(row[7]) if row[7] else None
                    created_at = (
                        datetime.fromisoformat(row[8]) if row[8] else datetime.now()
                    )

                    token = APIToken(
                        id=row[0],
                        user_id=row[1],
                        tenant_id=row[2],
                        name=row[3],
                        token_prefix=row[4],
                        token_hash=row[5],
                        expires_at=expires_at,
                        last_used=last_used,
                        created_at=created_at,
                        is_active=bool(row[9]),
                    )
                tokens.append(token)

            conn.close()
            return tokens

        except Exception:
            conn.close()
            return []

    def revoke_token(self, user_id: str, token_id: str) -> Tuple[bool, str]:
        """Revoke (deactivate) an API token"""
        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    UPDATE api_tokens
                    SET is_active = FALSE
                    WHERE id = %s AND user_id = %s
                """,
                    (token_id, user_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE api_tokens
                    SET is_active = 0
                    WHERE id = ? AND user_id = ?
                """,
                    (token_id, user_id),
                )

            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, "Token revoked successfully"
            else:
                conn.close()
                return False, "Token not found or already revoked"

        except Exception as e:
            conn.close()
            return False, f"Error revoking token: {str(e)}"

    def revoke_all_tokens(self, user_id: str) -> Tuple[bool, str]:
        """Revoke all API tokens for a user"""
        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    UPDATE api_tokens
                    SET is_active = FALSE
                    WHERE user_id = %s AND is_active = TRUE
                """,
                    (user_id,),
                )
            else:
                cursor.execute(
                    """
                    UPDATE api_tokens
                    SET is_active = 0
                    WHERE user_id = ? AND is_active = 1
                """,
                    (user_id,),
                )

            revoked_count = cursor.rowcount
            conn.commit()
            conn.close()

            if revoked_count > 0:
                return True, f"Revoked {revoked_count} token(s) successfully"
            else:
                return True, "No active tokens to revoke"

        except Exception as e:
            conn.close()
            return False, f"Error revoking tokens: {str(e)}"

    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from database (maintenance function)"""
        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            current_time = datetime.now()

            if self.db_type == "postgres":
                cursor.execute(
                    """
                    DELETE FROM api_tokens
                    WHERE expires_at IS NOT NULL AND expires_at < %s
                """,
                    (current_time,),
                )
            else:
                cursor.execute(
                    """
                    DELETE FROM api_tokens
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """,
                    (current_time.isoformat(),),
                )

            deleted_count = int(cursor.rowcount) if cursor.rowcount is not None else 0
            conn.commit()
            conn.close()

            return deleted_count

        except Exception:
            conn.close()
            return 0

    def get_token_stats(self, user_id: str) -> Dict:
        """Get token statistics for a user"""
        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            # Count active tokens
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_active,
                        COUNT(CASE WHEN expires_at IS NULL THEN 1 END) as never_expire,
                        COUNT(CASE WHEN expires_at IS NOT NULL AND expires_at > %s THEN 1 END) as will_expire,
                        COUNT(CASE WHEN last_used IS NOT NULL THEN 1 END) as used_tokens
                    FROM api_tokens
                    WHERE user_id = %s AND is_active = TRUE
                """,
                    (datetime.now(), user_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_active,
                        COUNT(CASE WHEN expires_at IS NULL THEN 1 END) as never_expire,
                        COUNT(CASE WHEN expires_at IS NOT NULL AND expires_at > ? THEN 1 END) as will_expire,
                        COUNT(CASE WHEN last_used IS NOT NULL THEN 1 END) as used_tokens
                    FROM api_tokens
                    WHERE user_id = ? AND is_active = 1
                """,
                    (datetime.now().isoformat(), user_id),
                )

            result = cursor.fetchone()
            conn.close()

            if self.db_type == "postgres":
                return {
                    "total_active": result["total_active"],
                    "never_expire": result["never_expire"],
                    "will_expire": result["will_expire"],
                    "used_tokens": result["used_tokens"],
                }
            else:
                return {
                    "total_active": result[0],
                    "never_expire": result[1],
                    "will_expire": result[2],
                    "used_tokens": result[3],
                }

        except Exception:
            conn.close()
            return {
                "total_active": 0,
                "never_expire": 0,
                "will_expire": 0,
                "used_tokens": 0,
            }
