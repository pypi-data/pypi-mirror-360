"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Authentication and user management system with SSO/ADFS support

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
from urllib.parse import urlencode

import jwt
import requests
from dotenv import load_dotenv

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

load_dotenv()


@dataclass
class User:
    id: str
    tenant_id: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    tenant_name: Optional[str] = None  # For admin views


@dataclass
class Tenant:
    id: str
    name: str
    subdomain: str
    is_active: bool
    created_at: datetime
    max_users: int = 100
    user_count: Optional[int] = None  # For admin views


class AuthManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_type = os.getenv("DB_TYPE", "sqlite").lower()
        if self.db_type == "postgres":
            if not POSTGRES_AVAILABLE:
                raise ImportError("psycopg2 is required for Postgres support.")
            self.dsn = os.getenv("POSTGRES_DSN")
            if not self.dsn:
                raise ValueError(
                    "POSTGRES_DSN environment variable must be set for " "Postgres."
                )
        else:
            self.db_path = db_path or os.getenv("DB_PATH", "prompts.db")

        # Authentication configuration
        self.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))
        self.local_dev_mode = os.getenv("LOCAL_DEV_MODE", "false").lower() == "true"

        # SSO Configuration
        self.sso_enabled = os.getenv("SSO_ENABLED", "false").lower() == "true"
        self.adfs_enabled = os.getenv("ADFS_ENABLED", "false").lower() == "true"
        self.sso_client_id = os.getenv("SSO_CLIENT_ID")
        self.sso_client_secret = os.getenv("SSO_CLIENT_SECRET")
        self.sso_authority = os.getenv("SSO_AUTHORITY")
        self.sso_redirect_uri = os.getenv(
            "SSO_REDIRECT_URI", "http://localhost:7860/auth/callback"
        )

        # Entra ID (Azure AD) Configuration
        self.entra_id_enabled = os.getenv("ENTRA_ID_ENABLED", "false").lower() == "true"
        self.entra_client_id = os.getenv("ENTRA_CLIENT_ID") or self.sso_client_id
        self.entra_client_secret = (
            os.getenv("ENTRA_CLIENT_SECRET") or self.sso_client_secret
        )
        self.entra_tenant_id = os.getenv("ENTRA_TENANT_ID")
        self.entra_redirect_uri = os.getenv(
            "ENTRA_REDIRECT_URI", "http://localhost:7860/auth/entra-callback"
        )
        self.entra_scopes = os.getenv(
            "ENTRA_SCOPES", "openid email profile User.Read"
        ).split()

        # Azure AI Configuration
        self.azure_ai_enabled = os.getenv("AZURE_AI_ENABLED", "false").lower() == "true"
        self.azure_ai_endpoint = os.getenv("AZURE_AI_ENDPOINT")
        self.azure_ai_key = os.getenv("AZURE_AI_KEY")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
        self.azure_openai_version = os.getenv(
            "AZURE_OPENAI_VERSION", "2024-02-15-preview"
        )

        self.init_auth_database()
        self._ensure_default_tenant()

    def is_multitenant_mode(self) -> bool:
        """Check if the application is running in multi-tenant mode."""
        return os.getenv("MULTITENANT_MODE", "true").lower() == "true"

    def get_conn(self):
        if self.db_type == "postgres":
            return psycopg2.connect(self.dsn, cursor_factory=RealDictCursor)
        else:
            return sqlite3.connect(str(self.db_path))

    def init_auth_database(self):
        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            # Create tenants table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tenants (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name TEXT NOT NULL,
                    subdomain TEXT UNIQUE NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    max_users INTEGER DEFAULT 100,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create users table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    role TEXT DEFAULT 'user'
                        CHECK (role IN ('admin', 'user', 'readonly')),
                    is_active BOOLEAN DEFAULT TRUE,
                    sso_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    UNIQUE(tenant_id, email)
                )
            """
            )

            # Create sessions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    token_hash TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address INET,
                    user_agent TEXT
                )
            """
            )
        else:
            # SQLite version
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tenants (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    subdomain TEXT UNIQUE NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    max_users INTEGER DEFAULT 100,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT REFERENCES tenants(id) ON DELETE CASCADE,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    role TEXT DEFAULT 'user'
                        CHECK (role IN ('admin', 'user', 'readonly')),
                    is_active BOOLEAN DEFAULT 1,
                    sso_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    UNIQUE(tenant_id, email)
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                    token_hash TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT
                )
            """
            )

        conn.commit()
        conn.close()

    def _ensure_default_tenant(self):
        """Ensure a default tenant exists for local development"""
        if self.local_dev_mode:
            conn = self.get_conn()
            cursor = conn.cursor()

            if self.db_type == "postgres":
                cursor.execute(
                    "SELECT id FROM tenants WHERE subdomain = %s", ("localhost",)
                )
            else:
                cursor.execute(
                    "SELECT id FROM tenants WHERE subdomain = ?", ("localhost",)
                )

            if not cursor.fetchone():
                tenant_id = str(uuid.uuid4())
                if self.db_type == "postgres":
                    cursor.execute(
                        """
                        INSERT INTO tenants (id, name, subdomain, is_active, max_users)
                        VALUES (%s, %s, %s, %s, %s)
                    """,
                        (tenant_id, "Local Development", "localhost", True, 1000),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO tenants (id, name, subdomain, is_active, max_users)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (tenant_id, "Local Development", "localhost", True, 1000),
                    )

                # Create default admin user for local development
                admin_id = str(uuid.uuid4())
                admin_password = self._hash_password("admin123")

                if self.db_type == "postgres":
                    cursor.execute(
                        """
                        INSERT INTO users (id, tenant_id, email, password_hash,
                                         first_name, last_name, role, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                        (
                            admin_id,
                            tenant_id,
                            "admin@localhost",
                            admin_password,
                            "Admin",
                            "User",
                            "admin",
                            True,
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO users (id, tenant_id, email, password_hash,
                                         first_name, last_name, role, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            admin_id,
                            tenant_id,
                            "admin@localhost",
                            admin_password,
                            "Admin",
                            "User",
                            "admin",
                            True,
                        ),
                    )

                conn.commit()

            conn.close()

    def _hash_password(self, password: str) -> str:
        """Hash password using PBKDF2"""
        salt = secrets.token_hex(32)
        pwdhash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return f"{salt}:{pwdhash.hex()}"

    def _verify_password(self, password: str, hash_str: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = hash_str.split(":")
            pwdhash = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
            )
            return pwdhash.hex() == stored_hash
        except ValueError:
            return False

    def create_tenant(
        self, name: str, subdomain: str, max_users: int = 100
    ) -> Tuple[bool, str]:
        """Create a new tenant"""
        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            # Check if subdomain already exists
            if self.db_type == "postgres":
                cursor.execute(
                    "SELECT id FROM tenants WHERE subdomain = %s", (subdomain,)
                )
            else:
                cursor.execute(
                    "SELECT id FROM tenants WHERE subdomain = ?", (subdomain,)
                )

            if cursor.fetchone():
                conn.close()
                return False, f"Subdomain '{subdomain}' already exists"

            tenant_id = str(uuid.uuid4())
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    INSERT INTO tenants (id, name, subdomain, is_active, max_users)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    (tenant_id, name, subdomain, True, max_users),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO tenants (id, name, subdomain, is_active, max_users)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (tenant_id, name, subdomain, True, max_users),
                )

            conn.commit()
            conn.close()
            return True, f"Tenant '{name}' created successfully"

        except Exception as e:
            conn.close()
            return False, f"Error creating tenant: {str(e)}"

    def create_user(
        self,
        tenant_id: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str = "user",
        sso_id: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Create a new user

        Returns:
            Tuple[bool, str]: (success, success_message) if successful,
                             (False, error_message) if failed
        """
        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            # Check if user already exists
            if self.db_type == "postgres":
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            else:
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))

            if cursor.fetchone():
                conn.close()
                return False, f"User with email '{email}' already exists"

            # Check tenant user limit
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT COUNT(*) as user_count, max_users
                    FROM users u JOIN tenants t ON u.tenant_id = t.id
                    WHERE u.tenant_id = %s AND u.is_active = TRUE
                    GROUP BY t.max_users
                """,
                    (tenant_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT COUNT(*) as user_count, max_users
                    FROM users u JOIN tenants t ON u.tenant_id = t.id
                    WHERE u.tenant_id = ? AND u.is_active = 1
                    GROUP BY t.max_users
                """,
                    (tenant_id,),
                )

            result = cursor.fetchone()
            if result:
                if self.db_type == "postgres":
                    user_count, max_users = result["user_count"], result["max_users"]
                else:
                    user_count, max_users = result[0], result[1]

                if user_count >= max_users:
                    conn.close()
                    return (
                        False,
                        f"Tenant has reached maximum user limit of {max_users}",
                    )

            user_id = str(uuid.uuid4())
            password_hash = self._hash_password(password) if password else None

            if self.db_type == "postgres":
                cursor.execute(
                    """
                    INSERT INTO users (id, tenant_id, email, password_hash,
                                     first_name, last_name, role, is_active, sso_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        user_id,
                        tenant_id,
                        email,
                        password_hash,
                        first_name,
                        last_name,
                        role,
                        True,
                        sso_id,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO users (id, tenant_id, email, password_hash,
                                     first_name, last_name, role, is_active, sso_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        user_id,
                        tenant_id,
                        email,
                        password_hash,
                        first_name,
                        last_name,
                        role,
                        True,
                        sso_id,
                    ),
                )

            conn.commit()
            conn.close()
            return True, f"User '{email}' created successfully"

        except Exception as e:
            conn.close()
            return False, f"Error creating user: {str(e)}"

    def authenticate_user(
        self, email: str, password: str, subdomain: Optional[str] = None
    ) -> Tuple[bool, Optional[User], str]:
        """Authenticate user with email/password"""
        try:
            conn = self.get_conn()
            cursor = conn.cursor()
            # Find user with optional tenant filtering
            if subdomain and subdomain != "localhost":
                if self.db_type == "postgres":
                    cursor.execute(
                        """
                        SELECT u.*, t.name as tenant_name, t.subdomain
                        FROM users u
                        JOIN tenants t ON u.tenant_id = t.id
                        WHERE u.email = %s AND t.subdomain = %s
                          AND u.is_active = TRUE AND t.is_active = TRUE
                    """,
                        (email, subdomain),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT u.*, t.name as tenant_name, t.subdomain
                        FROM users u
                        JOIN tenants t ON u.tenant_id = t.id
                        WHERE u.email = ? AND t.subdomain = ?
                          AND u.is_active = 1 AND t.is_active = 1
                    """,
                        (email, subdomain),
                    )
            else:
                if self.db_type == "postgres":
                    cursor.execute(
                        """
                        SELECT u.*, t.name as tenant_name, t.subdomain
                        FROM users u
                        JOIN tenants t ON u.tenant_id = t.id
                        WHERE u.email = %s AND u.is_active = TRUE AND t.is_active = TRUE
                    """,
                        (email,),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT u.*, t.name as tenant_name, t.subdomain
                        FROM users u
                        JOIN tenants t ON u.tenant_id = t.id
                        WHERE u.email = ? AND u.is_active = 1 AND t.is_active = 1
                    """,
                        (email,),
                    )

            row = cursor.fetchone()
            if not row:
                conn.close()
                return False, None, "Invalid email or password"

            # Extract user data
            if self.db_type == "postgres":
                user_data = dict(row)
                password_hash = user_data["password_hash"]
            else:
                user_data = {
                    "id": row[0],
                    "tenant_id": row[1],
                    "email": row[2],
                    "password_hash": row[3],
                    "first_name": row[4],
                    "last_name": row[5],
                    "role": row[6],
                    "is_active": row[7],
                    "sso_id": row[8],
                    "created_at": row[9],
                    "last_login": row[10],
                }
                password_hash = user_data["password_hash"]

            # Verify password
            if not password_hash or not self._verify_password(password, password_hash):
                conn.close()
                return False, None, "Invalid email or password"

            # Update last login
            if self.db_type == "postgres":
                cursor.execute(
                    "UPDATE users SET last_login = %s WHERE id = %s",
                    (datetime.now(), user_data["id"]),
                )
            else:
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now().isoformat(), user_data["id"]),
                )
            conn.commit()

            user = User(
                id=user_data["id"],
                tenant_id=user_data["tenant_id"],
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                is_active=bool(user_data["is_active"]),
                created_at=user_data["created_at"],
                last_login=datetime.now(),
            )

            conn.close()
            return True, user, "Authentication successful"

        except Exception as e:
            try:
                conn.close()
            except Exception:
                # Silent rollback failure is acceptable here  # nosec B110
                pass
            return False, None, f"Authentication error: {str(e)}"

    def create_session(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> str:
        """Create a new user session and return JWT token"""
        conn = self.get_conn()
        cursor = conn.cursor()

        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=24)

        # Create JWT token
        payload = {
            "session_id": session_id,
            "user_id": user_id,
            "exp": expires_at.timestamp(),
            "iat": datetime.now().timestamp(),
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Store session in database
        if self.db_type == "postgres":
            cursor.execute(
                """
                INSERT INTO user_sessions (id, user_id, token_hash, expires_at,
                                          ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (session_id, user_id, token_hash, expires_at, ip_address, user_agent),
            )
        else:
            cursor.execute(
                """
                INSERT INTO user_sessions (id, user_id, token_hash, expires_at,
                                          ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    session_id,
                    user_id,
                    token_hash,
                    expires_at.isoformat(),
                    ip_address,
                    user_agent,
                ),
            )

        conn.commit()
        conn.close()

        return token

    def validate_session(self, token: str) -> Tuple[bool, Optional[User]]:
        """Validate session token and return user if valid"""
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            session_id = payload["session_id"]

            conn = self.get_conn()
            cursor = conn.cursor()

            # Verify session exists and is not expired
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT s.*, u.*, t.name as tenant_name, t.subdomain
                    FROM user_sessions s
                    JOIN users u ON s.user_id = u.id
                    JOIN tenants t ON u.tenant_id = t.id
                    WHERE s.id = %s AND s.token_hash = %s AND s.expires_at > %s
                    AND u.is_active = TRUE AND t.is_active = TRUE
                """,
                    (session_id, token_hash, datetime.now()),
                )
            else:
                cursor.execute(
                    """
                    SELECT s.*, u.*, t.name as tenant_name, t.subdomain
                    FROM user_sessions s
                    JOIN users u ON s.user_id = u.id
                    JOIN tenants t ON u.tenant_id = t.id
                    WHERE s.id = ? AND s.token_hash = ? AND s.expires_at > ?
                    AND u.is_active = 1 AND t.is_active = 1
                """,
                    (session_id, token_hash, datetime.now().isoformat()),
                )

            row = cursor.fetchone()
            if not row:
                conn.close()
                return False, None

            # Create user object
            if self.db_type == "postgres":
                user = User(
                    id=row["id"],
                    tenant_id=row["tenant_id"],
                    email=row["email"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    role=row["role"],
                    is_active=bool(row["is_active"]),
                    created_at=row["created_at"],
                    last_login=row["last_login"],
                )
            else:
                user = User(
                    id=row[7],  # u.id
                    tenant_id=row[8],  # u.tenant_id
                    email=row[9],  # u.email
                    first_name=row[11],  # u.first_name
                    last_name=row[12],  # u.last_name
                    role=row[13],  # u.role
                    is_active=bool(row[14]),  # u.is_active
                    created_at=row[16],  # u.created_at
                    last_login=row[17],  # u.last_login
                )

            conn.close()
            return True, user

        except jwt.ExpiredSignatureError:
            return False, None
        except jwt.InvalidTokenError:
            return False, None
        except Exception:
            return False, None

    def logout_user(self, token: str) -> bool:
        """Logout user by invalidating session"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            session_id = payload["session_id"]

            conn = self.get_conn()
            cursor = conn.cursor()

            if self.db_type == "postgres":
                cursor.execute("DELETE FROM user_sessions WHERE id = %s", (session_id,))
            else:
                cursor.execute("DELETE FROM user_sessions WHERE id = ?", (session_id,))

            conn.commit()
            conn.close()
            return True

        except Exception:
            return False

    def get_sso_login_url(self, subdomain: Optional[str] = None) -> str:
        """Generate SSO login URL"""
        if not self.sso_enabled or not self.sso_client_id:
            return ""

        state = secrets.token_urlsafe(32)
        params = {
            "client_id": self.sso_client_id,
            "response_type": "code",
            "redirect_uri": self.sso_redirect_uri,
            "scope": "openid email profile",
            "state": f"{state}:{subdomain}" if subdomain else state,
        }

        return f"{self.sso_authority}/oauth2/v2.0/authorize?{urlencode(params)}"

    def get_entra_id_login_url(self, subdomain: Optional[str] = None) -> str:
        """Generate Entra ID (Azure AD) login URL"""
        if (
            not self.entra_id_enabled
            or not self.entra_client_id
            or not self.entra_tenant_id
        ):
            return ""

        state = secrets.token_urlsafe(32)
        params = {
            "client_id": self.entra_client_id,
            "response_type": "code",
            "redirect_uri": self.entra_redirect_uri,
            "scope": " ".join(self.entra_scopes),
            "state": f"{state}:{subdomain}" if subdomain else state,
            "response_mode": "query",
        }

        base_url = (
            f"https://login.microsoftonline.com/{self.entra_tenant_id}"
            "/oauth2/v2.0/authorize"
        )
        return f"{base_url}?{urlencode(params)}"

    def handle_sso_callback(
        self, code: str, state: str
    ) -> Tuple[bool, Optional[User], str]:
        """Handle SSO callback and create/authenticate user"""
        if not self.sso_enabled:
            return False, None, "SSO not enabled"

        try:
            # Extract subdomain from state if present
            subdomain = None
            if ":" in state:
                _, subdomain = state.split(":", 1)

            # Exchange code for token
            token_data = {
                "client_id": self.sso_client_id,
                "client_secret": self.sso_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.sso_redirect_uri,
            }

            token_response = requests.post(
                f"{self.sso_authority}/oauth2/v2.0/token", data=token_data, timeout=30
            )
            token_response.raise_for_status()
            tokens = token_response.json()

            # Get user info from token
            user_info_response = requests.get(
                f"{self.sso_authority}/oidc/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"},
                timeout=30,
            )
            user_info_response.raise_for_status()
            user_info = user_info_response.json()

            # Find or create user
            email = user_info.get("email")
            if not email:
                return False, None, "Email not provided by SSO provider"

            # Find tenant
            tenant_id = None
            if subdomain:
                conn = self.get_conn()
                cursor = conn.cursor()
                if self.db_type == "postgres":
                    cursor.execute(
                        "SELECT id FROM tenants WHERE subdomain = %s "
                        "AND is_active = TRUE",
                        (subdomain,),
                    )
                else:
                    cursor.execute(
                        "SELECT id FROM tenants WHERE subdomain = ? AND is_active = 1",
                        (subdomain,),
                    )
                result = cursor.fetchone()
                if result:
                    tenant_id = (
                        str(result[0])
                        if not self.db_type == "postgres"
                        else str(result["id"])
                    )
                conn.close()

            if not tenant_id:
                return False, None, "Invalid tenant"

            # Try to find existing user
            conn = self.get_conn()
            cursor = conn.cursor()

            sso_id = user_info.get("sub") or user_info.get("oid")
            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT * FROM users
                    WHERE (email = %s OR sso_id = %s) AND tenant_id = %s
                    AND is_active = TRUE
                """,
                    (email, sso_id, tenant_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM users
                    WHERE (email = ? OR sso_id = ?) AND tenant_id = ? AND is_active = 1
                """,
                    (email, sso_id, tenant_id),
                )

            existing_user = cursor.fetchone()

            if existing_user:
                # Update existing user
                user_id = (
                    str(existing_user[0])
                    if not self.db_type == "postgres"
                    else str(existing_user["id"])
                )
                if self.db_type == "postgres":
                    cursor.execute(
                        """
                        UPDATE users SET sso_id = %s, last_login = %s WHERE id = %s
                    """,
                        (sso_id, datetime.now(), user_id),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE users SET sso_id = ?, last_login = ? WHERE id = ?
                    """,
                        (sso_id, datetime.now().isoformat(), user_id),
                    )

                conn.commit()
                conn.close()

                # Return user object
                if self.db_type == "postgres":
                    user_data = dict(existing_user)
                else:
                    user_data = {
                        "id": existing_user[0],
                        "tenant_id": existing_user[1],
                        "email": existing_user[2],
                        "first_name": existing_user[4],
                        "last_name": existing_user[5],
                        "role": existing_user[6],
                        "is_active": existing_user[7],
                        "created_at": existing_user[9],
                    }

                user = User(
                    id=user_data["id"],
                    tenant_id=user_data["tenant_id"],
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=user_data["role"],
                    is_active=bool(user_data["is_active"]),
                    created_at=user_data["created_at"],
                    last_login=datetime.now(),
                )

                return True, user, "SSO authentication successful"
            else:
                # Create new user
                first_name = user_info.get("given_name", email.split("@")[0])
                last_name = user_info.get("family_name", "")

                success, message = self.create_user(
                    tenant_id=tenant_id,
                    email=email,
                    password="",  # nosec B106: No password for SSO users is intentional
                    first_name=first_name,
                    last_name=last_name,
                    role="user",
                    sso_id=sso_id,
                )

                if success:
                    # Get the created user
                    if self.db_type == "postgres":
                        cursor.execute(
                            "SELECT * FROM users WHERE email = %s AND tenant_id = %s",
                            (email, tenant_id),
                        )
                    else:
                        cursor.execute(
                            "SELECT * FROM users WHERE email = ? AND tenant_id = ?",
                            (email, tenant_id),
                        )

                    new_user_row = cursor.fetchone()
                    conn.close()

                    if self.db_type == "postgres":
                        user_data = dict(new_user_row)
                    else:
                        user_data = {
                            "id": new_user_row[0],
                            "tenant_id": new_user_row[1],
                            "email": new_user_row[2],
                            "first_name": new_user_row[4],
                            "last_name": new_user_row[5],
                            "role": new_user_row[6],
                            "is_active": new_user_row[7],
                            "created_at": new_user_row[9],
                        }

                    user = User(
                        id=user_data["id"],
                        tenant_id=user_data["tenant_id"],
                        email=user_data["email"],
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"],
                        role=user_data["role"],
                        is_active=bool(user_data["is_active"]),
                        created_at=user_data["created_at"],
                        last_login=datetime.now(),
                    )

                    return True, user, "SSO user created and authenticated"
                else:
                    conn.close()
                    return False, None, f"Failed to create SSO user: {message}"

        except Exception as e:
            return False, None, f"SSO authentication failed: {str(e)}"

    def get_all_tenants(self) -> List[Tenant]:
        """Get all tenants (admin only)"""
        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tenants ORDER BY name")
        tenants = []

        for row in cursor.fetchall():
            if self.db_type == "postgres":
                tenant = Tenant(
                    id=row["id"],
                    name=row["name"],
                    subdomain=row["subdomain"],
                    is_active=bool(row["is_active"]),
                    created_at=row["created_at"],
                    max_users=row["max_users"],
                )
            else:
                # Parse datetime string for SQLite
                created_at_str = row[5]
                try:
                    if isinstance(created_at_str, str):
                        created_at = datetime.fromisoformat(
                            created_at_str.replace("Z", "+00:00")
                        )
                    else:
                        created_at = created_at_str
                except (ValueError, TypeError):
                    created_at = datetime.now()

                tenant = Tenant(
                    id=row[0],
                    name=row[1],
                    subdomain=row[2],
                    is_active=bool(row[3]),
                    created_at=created_at,
                    max_users=row[4],
                )
            tenants.append(tenant)

        conn.close()
        return tenants

    def get_tenant_users(self, tenant_id: str) -> List[User]:
        """Get all users for a tenant"""
        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            cursor.execute(
                "SELECT * FROM users WHERE tenant_id = %s ORDER BY email", (tenant_id,)
            )
        else:
            cursor.execute(
                "SELECT * FROM users WHERE tenant_id = ? ORDER BY email", (tenant_id,)
            )

        users = []
        for row in cursor.fetchall():
            if self.db_type == "postgres":
                user = User(
                    id=row["id"],
                    tenant_id=row["tenant_id"],
                    email=row["email"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    role=row["role"],
                    is_active=bool(row["is_active"]),
                    created_at=row["created_at"],
                    last_login=row["last_login"],
                )
            else:
                user = User(
                    id=row[0],
                    tenant_id=row[1],
                    email=row[2],
                    first_name=row[4],
                    last_name=row[5],
                    role=row[6],
                    is_active=bool(row[7]),
                    created_at=row[9],
                    last_login=row[10],
                )
            users.append(user)

        conn.close()
        return users

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        if self.db_type == "postgres":
            user = User(
                id=row["id"],
                tenant_id=row["tenant_id"],
                email=row["email"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                role=row["role"],
                is_active=bool(row["is_active"]),
                created_at=row["created_at"],
                last_login=row["last_login"],
            )
        else:
            user = User(
                id=row[0],
                tenant_id=row[1],
                email=row[2],
                first_name=row[4],
                last_name=row[5],
                role=row[6],
                is_active=bool(row[7]),
                created_at=row[9],
                last_login=row[10],
            )

        conn.close()
        return user

    def get_user_by_email(
        self, email: str, tenant_id: Optional[str] = None
    ) -> Optional[User]:
        """Get user by email with optional tenant filtering"""
        conn = self.get_conn()
        cursor = conn.cursor()

        if tenant_id:
            if self.db_type == "postgres":
                cursor.execute(
                    "SELECT * FROM users WHERE email = %s AND tenant_id = %s",
                    (email, tenant_id),
                )
            else:
                cursor.execute(
                    "SELECT * FROM users WHERE email = ? AND tenant_id = ?",
                    (email, tenant_id),
                )
        else:
            if self.db_type == "postgres":
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            else:
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        if self.db_type == "postgres":
            user = User(
                id=row["id"],
                tenant_id=row["tenant_id"],
                email=row["email"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                role=row["role"],
                is_active=bool(row["is_active"]),
                created_at=row["created_at"],
                last_login=row["last_login"],
            )
        else:
            user = User(
                id=row[0],
                tenant_id=row[1],
                email=row[2],
                first_name=row[4],
                last_name=row[5],
                role=row[6],
                is_active=bool(row[7]),
                created_at=row[9],
                last_login=row[10],
            )

        conn.close()
        return user

    def handle_entra_id_callback(
        self, code: str, state: str
    ) -> Tuple[bool, Optional[User], str]:
        """Handle Entra ID callback and create/authenticate user"""
        if not self.entra_id_enabled:
            return False, None, "Entra ID not enabled"

        try:
            # Extract subdomain from state if present
            subdomain = None
            if ":" in state:
                _, subdomain = state.split(":", 1)

            # Exchange code for token
            token_data = {
                "client_id": self.entra_client_id,
                "client_secret": self.entra_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.entra_redirect_uri,
                "scope": " ".join(self.entra_scopes),
            }

            token_url = (
                f"https://login.microsoftonline.com/{self.entra_tenant_id}"
                "/oauth2/v2.0/token"
            )
            token_response = requests.post(token_url, data=token_data, timeout=30)
            token_response.raise_for_status()
            tokens = token_response.json()

            # Get user info from Microsoft Graph API
            graph_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            user_info_response = requests.get(
                "https://graph.microsoft.com/v1.0/me", headers=graph_headers, timeout=30
            )
            user_info_response.raise_for_status()
            user_info = user_info_response.json()

            # Extract user details
            email = user_info.get("mail") or user_info.get("userPrincipalName")
            if not email:
                return False, None, "Email not provided by Entra ID"

            first_name = user_info.get("givenName", "")
            last_name = user_info.get("surname", "")
            object_id = user_info.get("id")  # Entra ID object ID

            # Find tenant
            tenant_id = None
            if subdomain:
                conn = self.get_conn()
                cursor = conn.cursor()
                if self.db_type == "postgres":
                    cursor.execute(
                        "SELECT id FROM tenants WHERE subdomain = %s "
                        "AND is_active = TRUE",
                        (subdomain,),
                    )
                else:
                    cursor.execute(
                        "SELECT id FROM tenants WHERE subdomain = ? AND is_active = 1",
                        (subdomain,),
                    )
                result = cursor.fetchone()
                if result:
                    tenant_id = (
                        str(result[0])
                        if not self.db_type == "postgres"
                        else str(result["id"])
                    )
                conn.close()

            if not tenant_id:
                return False, None, "Invalid tenant"

            # Try to find existing user
            conn = self.get_conn()
            cursor = conn.cursor()

            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT * FROM users
                    WHERE (email = %s OR sso_id = %s) AND tenant_id = %s
                    AND is_active = TRUE
                """,
                    (email, object_id, tenant_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM users
                    WHERE (email = ? OR sso_id = ?) AND tenant_id = ? AND is_active = 1
                """,
                    (email, object_id, tenant_id),
                )

            existing_user = cursor.fetchone()

            if existing_user:
                # Update existing user
                user_id = (
                    str(existing_user[0])
                    if not self.db_type == "postgres"
                    else str(existing_user["id"])
                )
                if self.db_type == "postgres":
                    cursor.execute(
                        """
                        UPDATE users SET sso_id = %s, last_login = %s WHERE id = %s
                    """,
                        (object_id, datetime.now(), user_id),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE users SET sso_id = ?, last_login = ? WHERE id = ?
                    """,
                        (object_id, datetime.now().isoformat(), user_id),
                    )

                conn.commit()
                conn.close()

                # Return user object
                if self.db_type == "postgres":
                    user_data = dict(existing_user)
                else:
                    user_data = {
                        "id": existing_user[0],
                        "tenant_id": existing_user[1],
                        "email": existing_user[2],
                        "first_name": existing_user[4],
                        "last_name": existing_user[5],
                        "role": existing_user[6],
                        "is_active": existing_user[7],
                        "created_at": existing_user[9],
                    }

                user = User(
                    id=user_data["id"],
                    tenant_id=user_data["tenant_id"],
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=user_data["role"],
                    is_active=bool(user_data["is_active"]),
                    created_at=user_data["created_at"],
                    last_login=datetime.now(),
                )

                return True, user, "Entra ID authentication successful"
            else:
                # Create new user
                if not first_name and not last_name:
                    # Use email username as fallback
                    first_name = email.split("@")[0]
                    last_name = ""

                success, message = self.create_user(
                    tenant_id=tenant_id,
                    email=email,
                    password="",  # nosec B106: No password for Entra ID users
                    first_name=first_name,
                    last_name=last_name,
                    role="user",
                    sso_id=object_id,
                )

                if success:
                    # Get the created user
                    if self.db_type == "postgres":
                        cursor.execute(
                            "SELECT * FROM users WHERE email = %s AND tenant_id = %s",
                            (email, tenant_id),
                        )
                    else:
                        cursor.execute(
                            "SELECT * FROM users WHERE email = ? AND tenant_id = ?",
                            (email, tenant_id),
                        )

                    new_user_row = cursor.fetchone()
                    conn.close()

                    if self.db_type == "postgres":
                        user_data = dict(new_user_row)
                    else:
                        user_data = {
                            "id": new_user_row[0],
                            "tenant_id": new_user_row[1],
                            "email": new_user_row[2],
                            "first_name": new_user_row[4],
                            "last_name": new_user_row[5],
                            "role": new_user_row[6],
                            "is_active": new_user_row[7],
                            "created_at": new_user_row[9],
                        }

                    user = User(
                        id=user_data["id"],
                        tenant_id=user_data["tenant_id"],
                        email=user_data["email"],
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"],
                        role=user_data["role"],
                        is_active=bool(user_data["is_active"]),
                        created_at=user_data["created_at"],
                        last_login=datetime.now(),
                    )

                    return True, user, "Entra ID user created and authenticated"
                else:
                    conn.close()
                    return False, None, f"Failed to create Entra ID user: {message}"

        except Exception as e:
            return False, None, f"Entra ID authentication failed: {str(e)}"

    def get_azure_ai_config(self) -> Dict[str, Dict[str, object]]:
        """Get Azure AI configuration for models"""
        config = {}

        if self.azure_ai_enabled and self.azure_ai_endpoint and self.azure_ai_key:
            config["azure_ai"] = {
                "endpoint": self.azure_ai_endpoint,
                "api_key": self.azure_ai_key,
                "enabled": True,
            }

        if self.azure_openai_endpoint and self.azure_openai_key:
            config["azure_openai"] = {
                "endpoint": self.azure_openai_endpoint,
                "api_key": self.azure_openai_key,
                "api_version": self.azure_openai_version,
                "enabled": True,
            }

        return config

    def validate_azure_credentials(self) -> Tuple[bool, str]:
        """Validate Azure credentials by testing API access"""
        try:
            azure_config = self.get_azure_ai_config()

            if not azure_config:
                return False, "No Azure credentials configured"

            # Test Azure OpenAI if configured
            if "azure_openai" in azure_config:
                config = azure_config["azure_openai"]
                test_url = (
                    f"{config['endpoint']}/openai/models"
                    f"?api-version={config['api_version']}"
                )
                headers = {
                    "api-key": str(config["api_key"]),
                    "Content-Type": "application/json",
                }

                response = requests.get(test_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    return True, "Azure OpenAI credentials validated successfully"
                else:
                    return (
                        False,
                        f"Azure OpenAI validation failed: {response.status_code}",
                    )

            # Test Azure AI if configured
            if "azure_ai" in azure_config:
                config = azure_config["azure_ai"]
                # Basic endpoint validation
                test_url = f"{config['endpoint']}/models"
                headers = {
                    "Authorization": f"Bearer {str(config['api_key'])}",
                    "Content-Type": "application/json",
                }

                response = requests.get(test_url, headers=headers, timeout=10)
                if response.status_code in [
                    200,
                    401,
                    403,
                ]:  # 401/403 means endpoint is reachable
                    return True, "Azure AI credentials validated successfully"
                else:
                    return False, f"Azure AI validation failed: {response.status_code}"

            return False, "No testable Azure services configured"

        except Exception as e:
            return False, f"Azure credential validation error: {str(e)}"

    def is_entra_id_enabled(self) -> bool:
        """Check if Entra ID authentication is enabled and configured"""
        return bool(
            self.entra_id_enabled
            and self.entra_client_id
            and self.entra_client_secret
            and self.entra_tenant_id
        )

    def is_azure_ai_enabled(self) -> bool:
        """Check if Azure AI services are enabled and configured"""
        return bool(
            self.azure_ai_enabled
            and (
                (self.azure_ai_endpoint and self.azure_ai_key)
                or (self.azure_openai_endpoint and self.azure_openai_key)
            )
        )

    def get_authentication_methods(self) -> Dict[str, bool]:
        """Get available authentication methods"""
        return {
            "local": True,  # Always available
            "sso": self.sso_enabled and bool(self.sso_client_id),
            "entra_id": self.is_entra_id_enabled(),
            "adfs": self.adfs_enabled,
        }

    def get_admin_stats(self) -> Dict[str, int]:
        """Get admin dashboard statistics"""
        with self.get_conn() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total users
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = ?", (True,))
            stats["total_users"] = cursor.fetchone()[0]

            # Active tenants
            cursor.execute("SELECT COUNT(*) FROM tenants WHERE is_active = ?", (True,))
            stats["active_tenants"] = cursor.fetchone()[0]

            # Total prompts (approximate, would need access to prompts table)
            try:
                cursor.execute("SELECT COUNT(*) FROM prompts")
                stats["total_prompts"] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                stats["total_prompts"] = 0

            # API tokens
            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM api_tokens WHERE expires_at > ? "
                    "OR expires_at IS NULL",
                    (datetime.now(),),
                )
                stats["api_tokens"] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                stats["api_tokens"] = 0

            return stats

    def get_all_users_for_tenant(self, tenant_id: str) -> List["User"]:
        """Get all users for a specific tenant (for admin view)"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT u.id, u.tenant_id, u.email, u.first_name, u.last_name,
                       u.role, u.is_active, u.created_at, u.last_login,
                       t.name as tenant_name
                FROM users u
                LEFT JOIN tenants t ON u.tenant_id = t.id
                WHERE u.tenant_id = ?
                ORDER BY u.created_at DESC
            """,
                (tenant_id,),
            )

            users = []
            for row in cursor.fetchall():
                user = User(
                    id=row[0],
                    tenant_id=row[1],
                    email=row[2],
                    first_name=row[3] or "",
                    last_name=row[4] or "",
                    role=row[5],
                    is_active=bool(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    last_login=datetime.fromisoformat(row[8]) if row[8] else None,
                )
                # Add tenant name as extra attribute
                user.tenant_name = row[9]
                users.append(user)

            return users

    def get_tenant_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, subdomain, max_users, is_active, created_at,
                       (SELECT COUNT(*) FROM users WHERE tenant_id = t.id
                        AND is_active = 1) as user_count
                FROM tenants t
                WHERE id = ?
            """,
                (tenant_id,),
            )

            row = cursor.fetchone()
            if row:
                tenant = Tenant(
                    id=row[0],
                    name=row[1],
                    subdomain=row[2],
                    max_users=row[3],
                    is_active=bool(row[4]),
                    created_at=(
                        datetime.fromisoformat(row[5]) if row[5] else datetime.now()
                    ),
                    user_count=row[6],
                )
                return tenant

            return None

    def get_tenant_by_subdomain(self, subdomain: str) -> Optional[Tenant]:
        """Get tenant by subdomain"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, subdomain, max_users, is_active, created_at,
                       (SELECT COUNT(*) FROM users WHERE tenant_id = t.id
                        AND is_active = 1) as user_count
                FROM tenants t
                WHERE subdomain = ?
            """,
                (subdomain,),
            )

            row = cursor.fetchone()
            if row:
                tenant = Tenant(
                    id=row[0],
                    name=row[1],
                    subdomain=row[2],
                    max_users=row[3],
                    is_active=bool(row[4]),
                    created_at=(
                        datetime.fromisoformat(row[5]) if row[5] else datetime.now()
                    ),
                    user_count=row[6],
                )
                return tenant

            return None
