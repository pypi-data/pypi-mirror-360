"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Release Announcement Management System

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

import json
import os
import re
import sqlite3
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

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
class ReleaseAnnouncement:
    """Release announcement data structure"""

    id: str
    version: str
    title: str
    description: str
    release_date: datetime
    is_major: bool
    is_featured: bool
    changelog_url: Optional[str] = None
    download_url: Optional[str] = None
    github_release_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class UserReleaseView:
    """User release view tracking"""

    user_id: str
    release_id: str
    viewed_at: datetime
    is_dismissed: bool = False


class ReleaseManager:
    """Comprehensive release announcement management system"""

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
        else:
            self.db_path = db_path or os.getenv("DB_PATH", "prompts.db")

        # GitHub configuration
        self.github_enabled = (
            os.getenv("GITHUB_RELEASES_ENABLED", "true").lower() == "true"
        )
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = os.getenv("GITHUB_REPO", "makercorn/ai-prompt-manager")
        self.github_api_base = "https://api.github.com"

        # Changelog configuration
        self.changelog_enabled = (
            os.getenv("CHANGELOG_ENABLED", "true").lower() == "true"
        )
        self.changelog_path = os.getenv("CHANGELOG_PATH", "CHANGELOG.md")

        # Cache configuration
        self.cache_duration = int(os.getenv("RELEASE_CACHE_DURATION", "3600"))  # 1 hour
        self.cache_file = os.path.join(tempfile.gettempdir(), "release_cache.json")

        self.init_database()

    def get_conn(self):
        """Get database connection"""
        if self.db_type == "postgres":
            return psycopg2.connect(self.dsn, cursor_factory=RealDictCursor)
        else:
            return sqlite3.connect(str(self.db_path))

    def init_database(self):
        """Initialize release management database tables"""
        conn = self.get_conn()
        cursor = conn.cursor()

        if self.db_type == "postgres":
            # PostgreSQL schema
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS release_announcements (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    version VARCHAR(50) UNIQUE NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    release_date TIMESTAMP NOT NULL,
                    is_major BOOLEAN DEFAULT FALSE,
                    is_featured BOOLEAN DEFAULT FALSE,
                    changelog_url VARCHAR(500),
                    download_url VARCHAR(500),
                    github_release_id VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_release_views (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL,
                    release_id UUID REFERENCES release_announcements(id)
                        ON DELETE CASCADE,
                    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_dismissed BOOLEAN DEFAULT FALSE,
                    UNIQUE(user_id, release_id)
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS release_cache (
                    cache_key VARCHAR(100) PRIMARY KEY,
                    cache_data JSONB NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
        else:
            # SQLite schema
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS release_announcements (
                    id TEXT PRIMARY KEY,
                    version TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    release_date TIMESTAMP NOT NULL,
                    is_major BOOLEAN DEFAULT 0,
                    is_featured BOOLEAN DEFAULT 0,
                    changelog_url TEXT,
                    download_url TEXT,
                    github_release_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_release_views (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    release_id TEXT REFERENCES release_announcements(id)
                        ON DELETE CASCADE,
                    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_dismissed BOOLEAN DEFAULT 0,
                    UNIQUE(user_id, release_id)
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS release_cache (
                    cache_key TEXT PRIMARY KEY,
                    cache_data TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

        conn.commit()
        conn.close()

    def create_release_announcement(
        self,
        version: str,
        title: str,
        description: str,
        release_date: Optional[datetime] = None,
        is_major: bool = False,
        is_featured: bool = False,
        changelog_url: Optional[str] = None,
        download_url: Optional[str] = None,
        github_release_id: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Create a new release announcement"""
        try:
            conn = self.get_conn()
            cursor = conn.cursor()

            release_id = str(uuid.uuid4())
            release_date = release_date or datetime.now()

            # Truncate description to prevent overly long entries
            description = description[:1000] if description else ""

            if self.db_type == "postgres":
                cursor.execute(
                    """
                    INSERT INTO release_announcements
                    (id, version, title, description, release_date, is_major,
                     is_featured, changelog_url, download_url, github_release_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        release_id,
                        version,
                        title,
                        description,
                        release_date,
                        is_major,
                        is_featured,
                        changelog_url,
                        download_url,
                        github_release_id,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO release_announcements
                    (id, version, title, description, release_date, is_major,
                     is_featured, changelog_url, download_url, github_release_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        release_id,
                        version,
                        title,
                        description,
                        release_date.isoformat(),
                        is_major,
                        is_featured,
                        changelog_url,
                        download_url,
                        github_release_id,
                    ),
                )

            conn.commit()
            conn.close()

            # Clear cache
            self._clear_cache()

            return (
                True,
                f"Release announcement for version {version} created successfully",
            )

        except Exception as e:
            return False, f"Error creating release announcement: {str(e)}"

    def get_releases(
        self,
        limit: int = 10,
        include_dismissed: bool = False,
        user_id: Optional[str] = None,
    ) -> List[ReleaseAnnouncement]:
        """Get release announcements with optional user context"""
        try:
            conn = self.get_conn()
            cursor = conn.cursor()

            if user_id and not include_dismissed:
                # Get releases not dismissed by user
                if self.db_type == "postgres":
                    cursor.execute(
                        """
                        SELECT r.*,
                               CASE WHEN urv.viewed_at IS NOT NULL
                                   THEN TRUE ELSE FALSE END as is_viewed
                        FROM release_announcements r
                        LEFT JOIN user_release_views urv ON r.id = urv.release_id
                            AND urv.user_id = %s AND urv.is_dismissed = FALSE
                        WHERE (urv.is_dismissed IS NULL OR urv.is_dismissed = FALSE)
                        ORDER BY r.release_date DESC, r.is_featured DESC
                        LIMIT %s
                    """,
                        (user_id, limit),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT r.*,
                               CASE WHEN urv.viewed_at IS NOT NULL
                                   THEN 1 ELSE 0 END as is_viewed
                        FROM release_announcements r
                        LEFT JOIN user_release_views urv ON r.id = urv.release_id
                            AND urv.user_id = ? AND urv.is_dismissed = 0
                        WHERE (urv.is_dismissed IS NULL OR urv.is_dismissed = 0)
                        ORDER BY r.release_date DESC, r.is_featured DESC
                        LIMIT ?
                    """,
                        (user_id, limit),
                    )
            else:
                # Get all releases
                if self.db_type == "postgres":
                    cursor.execute(
                        """
                        SELECT * FROM release_announcements
                        ORDER BY release_date DESC, is_featured DESC
                        LIMIT %s
                    """,
                        (limit,),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT * FROM release_announcements
                        ORDER BY release_date DESC, is_featured DESC
                        LIMIT ?
                    """,
                        (limit,),
                    )

            releases = []
            for row in cursor.fetchall():
                if self.db_type == "postgres":
                    release = ReleaseAnnouncement(
                        id=str(row["id"]),
                        version=row["version"],
                        title=row["title"],
                        description=row["description"],
                        release_date=row["release_date"],
                        is_major=bool(row["is_major"]),
                        is_featured=bool(row["is_featured"]),
                        changelog_url=row["changelog_url"],
                        download_url=row["download_url"],
                        github_release_id=row["github_release_id"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                else:
                    release = ReleaseAnnouncement(
                        id=row[0],
                        version=row[1],
                        title=row[2],
                        description=row[3],
                        release_date=(
                            datetime.fromisoformat(row[4])
                            if isinstance(row[4], str)
                            else row[4]
                        ),
                        is_major=bool(row[5]),
                        is_featured=bool(row[6]),
                        changelog_url=row[7],
                        download_url=row[8],
                        github_release_id=row[9],
                        created_at=(
                            datetime.fromisoformat(row[10])
                            if row[10] and isinstance(row[10], str)
                            else row[10]
                        ),
                        updated_at=(
                            datetime.fromisoformat(row[11])
                            if row[11] and isinstance(row[11], str)
                            else row[11]
                        ),
                    )
                releases.append(release)

            conn.close()
            return releases

        except Exception as e:
            print(f"Error getting releases: {e}")
            return []

    def mark_release_viewed(
        self, user_id: str, release_id: str, is_dismissed: bool = False
    ) -> Tuple[bool, str]:
        """Mark a release as viewed by a user"""
        try:
            conn = self.get_conn()
            cursor = conn.cursor()

            view_id = str(uuid.uuid4())

            if self.db_type == "postgres":
                cursor.execute(
                    """
                    INSERT INTO user_release_views
                    (id, user_id, release_id, is_dismissed)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id, release_id)
                    DO UPDATE SET viewed_at = CURRENT_TIMESTAMP, is_dismissed = %s
                """,
                    (view_id, user_id, release_id, is_dismissed, is_dismissed),
                )
            else:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO user_release_views
                    (id, user_id, release_id, is_dismissed, viewed_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                    (view_id, user_id, release_id, is_dismissed),
                )

            conn.commit()
            conn.close()

            return True, "Release view status updated"

        except Exception as e:
            return False, f"Error updating release view: {str(e)}"

    def sync_github_releases(self) -> Tuple[bool, str]:
        """Sync releases from GitHub API"""
        if not self.github_enabled:
            return False, "GitHub sync is disabled"

        try:
            # Check cache first
            cached_data = self._get_cached_data("github_releases")
            if cached_data:
                releases_data = cached_data
            else:
                # Fetch from GitHub API
                headers = {"Accept": "application/vnd.github.v3+json"}
                if self.github_token:
                    headers["Authorization"] = f"token {self.github_token}"

                url = f"{self.github_api_base}/repos/{self.github_repo}/releases"
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()

                releases_data = response.json()

                # Cache the data
                self._cache_data("github_releases", releases_data)

            synced_count = 0
            for release_data in releases_data[:20]:  # Limit to recent 20 releases
                version = release_data.get("tag_name", "").lstrip("v")
                if not version:
                    continue

                # Check if release already exists
                existing = self._get_release_by_version(version)
                if existing:
                    continue

                title = release_data.get("name", f"Release {version}")
                description = release_data.get("body", "")[
                    :1000
                ]  # Limit description length
                release_date = datetime.fromisoformat(
                    release_data.get("published_at", "").replace("Z", "+00:00")
                )
                is_major = self._is_major_release(version)
                changelog_url = release_data.get("html_url")
                download_url = release_data.get("tarball_url")
                github_release_id = str(release_data.get("id"))

                success, _ = self.create_release_announcement(
                    version=version,
                    title=title,
                    description=description,
                    release_date=release_date,
                    is_major=is_major,
                    is_featured=is_major,
                    changelog_url=changelog_url,
                    download_url=download_url,
                    github_release_id=github_release_id,
                )

                if success:
                    synced_count += 1

            return True, f"Synced {synced_count} new releases from GitHub"

        except Exception as e:
            return False, f"Error syncing GitHub releases: {str(e)}"

    def parse_changelog(self) -> Tuple[bool, str]:
        """Parse local CHANGELOG.md file"""
        if not self.changelog_enabled:
            return False, "Changelog parsing is disabled"

        try:
            if not os.path.exists(self.changelog_path):
                return False, f"Changelog file not found: {self.changelog_path}"

            with open(self.changelog_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse changelog sections
            releases = self._parse_changelog_content(content)

            synced_count = 0
            for release_data in releases:
                # Check if release already exists
                existing = self._get_release_by_version(release_data["version"])
                if existing:
                    continue

                success, _ = self.create_release_announcement(
                    version=release_data["version"],
                    title=release_data["title"],
                    description=release_data["description"],
                    release_date=release_data["date"],
                    is_major=release_data["is_major"],
                    is_featured=release_data["is_major"],
                )

                if success:
                    synced_count += 1

            return True, f"Parsed {synced_count} new releases from changelog"

        except Exception as e:
            return False, f"Error parsing changelog: {str(e)}"

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread releases for a user"""
        try:
            conn = self.get_conn()
            cursor = conn.cursor()

            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM release_announcements r
                    LEFT JOIN user_release_views urv ON r.id = urv.release_id
                        AND urv.user_id = %s
                    WHERE urv.viewed_at IS NULL
                """,
                    (user_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM release_announcements r
                    LEFT JOIN user_release_views urv ON r.id = urv.release_id
                        AND urv.user_id = ?
                    WHERE urv.viewed_at IS NULL
                """,
                    (user_id,),
                )

            count = (
                cursor.fetchone()[0]
                if self.db_type == "postgres"
                else cursor.fetchone()[0]
            )
            conn.close()

            return int(count)

        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0

    def _get_release_by_version(self, version: str) -> Optional[ReleaseAnnouncement]:
        """Get release by version"""
        try:
            conn = self.get_conn()
            cursor = conn.cursor()

            if self.db_type == "postgres":
                cursor.execute(
                    "SELECT * FROM release_announcements WHERE version = %s", (version,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM release_announcements WHERE version = ?", (version,)
                )

            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            if self.db_type == "postgres":
                return ReleaseAnnouncement(
                    id=str(row["id"]),
                    version=row["version"],
                    title=row["title"],
                    description=row["description"],
                    release_date=row["release_date"],
                    is_major=bool(row["is_major"]),
                    is_featured=bool(row["is_featured"]),
                    changelog_url=row["changelog_url"],
                    download_url=row["download_url"],
                    github_release_id=row["github_release_id"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            else:
                return ReleaseAnnouncement(
                    id=row[0],
                    version=row[1],
                    title=row[2],
                    description=row[3],
                    release_date=(
                        datetime.fromisoformat(row[4])
                        if isinstance(row[4], str)
                        else row[4]
                    ),
                    is_major=bool(row[5]),
                    is_featured=bool(row[6]),
                    changelog_url=row[7],
                    download_url=row[8],
                    github_release_id=row[9],
                    created_at=(
                        datetime.fromisoformat(row[10])
                        if row[10] and isinstance(row[10], str)
                        else row[10]
                    ),
                    updated_at=(
                        datetime.fromisoformat(row[11])
                        if row[11] and isinstance(row[11], str)
                        else row[11]
                    ),
                )
        except Exception as e:
            print(f"Error getting release by version: {e}")
            return None

    def _is_major_release(self, version: str) -> bool:
        """Determine if a version is a major release"""
        try:
            # Parse semantic version
            match = re.match(r"^(\d+)\.(\d+)\.(\d+)", version)
            if match:
                major, minor, patch = map(int, match.groups())
                # Consider major version changes or significant minor updates as major
                return (
                    major > 0
                    and (minor == 0 and patch == 0)
                    or (major == 0 and minor % 5 == 0)
                )
            return False
        except Exception:
            return False

    def _parse_changelog_content(self, content: str) -> List[Dict]:
        """Parse changelog markdown content"""
        releases = []
        current_version = None
        current_date = None
        current_description: List[str] = []

        lines = content.split("\n")
        for line in lines:
            # Look for version headers (e.g., ## [1.0.0] - 2023-01-01)
            version_match = re.match(
                r"^##\s*\[?([^\]]+)\]?\s*-?\s*(\d{4}-\d{2}-\d{2})?", line
            )
            if version_match:
                # Save previous release
                if current_version:
                    releases.append(
                        {
                            "version": current_version,
                            "title": f"Release {current_version}",
                            "description": "\n".join(current_description).strip()[
                                :1000
                            ],
                            "date": current_date or datetime.now(),
                            "is_major": self._is_major_release(current_version),
                        }
                    )

                # Start new release
                current_version = version_match.group(1)
                date_str = version_match.group(2)
                current_date = (
                    datetime.strptime(date_str, "%Y-%m-%d")
                    if date_str
                    else datetime.now()
                )
                current_description = []

            elif current_version and line.strip() and not line.startswith("#"):
                # Add to current description (skip empty lines and headers)
                current_description.append(line.strip())

        # Add final release
        if current_version:
            releases.append(
                {
                    "version": current_version,
                    "title": f"Release {current_version}",
                    "description": "\n".join(current_description).strip()[:1000],
                    "date": current_date or datetime.now(),
                    "is_major": self._is_major_release(current_version),
                }
            )

        return releases

    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Get cached data if not expired"""
        try:
            conn = self.get_conn()
            cursor = conn.cursor()

            if self.db_type == "postgres":
                cursor.execute(
                    """
                    SELECT cache_data FROM release_cache
                    WHERE cache_key = %s AND expires_at > %s
                """,
                    (cache_key, datetime.now()),
                )
            else:
                cursor.execute(
                    """
                    SELECT cache_data FROM release_cache
                    WHERE cache_key = ? AND expires_at > ?
                """,
                    (cache_key, datetime.now().isoformat()),
                )

            row = cursor.fetchone()
            conn.close()

            if row:
                cache_data = row[0] if self.db_type == "postgres" else row[0]
                if isinstance(cache_data, str):
                    parsed_data = json.loads(cache_data)
                    return dict(parsed_data) if isinstance(parsed_data, dict) else {}
                else:
                    return dict(cache_data) if cache_data else {}

            return None

        except Exception as e:
            print(f"Error getting cached data: {e}")
            return None

    def _cache_data(self, cache_key: str, data: Dict):
        """Cache data with expiration"""
        try:
            conn = self.get_conn()
            cursor = conn.cursor()

            expires_at = datetime.now() + timedelta(seconds=self.cache_duration)
            cache_data = json.dumps(data)

            if self.db_type == "postgres":
                cursor.execute(
                    """
                    INSERT INTO release_cache (cache_key, cache_data, expires_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (cache_key)
                    DO UPDATE SET cache_data = %s, expires_at = %s
                """,
                    (cache_key, cache_data, expires_at, cache_data, expires_at),
                )
            else:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO release_cache
                    (cache_key, cache_data, expires_at)
                    VALUES (?, ?, ?)
                """,
                    (cache_key, cache_data, expires_at.isoformat()),
                )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error caching data: {e}")

    def _clear_cache(self):
        """Clear all cached data"""
        try:
            conn = self.get_conn()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM release_cache")
            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error clearing cache: {e}")

    def cleanup_old_cache(self):
        """Clean up expired cache entries"""
        try:
            conn = self.get_conn()
            cursor = conn.cursor()

            if self.db_type == "postgres":
                cursor.execute(
                    "DELETE FROM release_cache WHERE expires_at < %s", (datetime.now(),)
                )
            else:
                cursor.execute(
                    "DELETE FROM release_cache WHERE expires_at < ?",
                    (datetime.now().isoformat(),),
                )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error cleaning cache: {e}")
