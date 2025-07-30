"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Release Management API Endpoints

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from api_token_manager import APITokenManager
from release_manager import ReleaseManager


class ReleaseCreateRequest(BaseModel):
    """Request model for creating release announcements"""

    version: str = Field(..., description="Release version (e.g., '1.2.3')")
    title: str = Field(..., description="Release title")
    description: str = Field("", description="Release description/changelog")
    is_major: bool = Field(False, description="Whether this is a major release")
    is_featured: bool = Field(False, description="Whether to feature this release")
    changelog_url: Optional[str] = Field(None, description="URL to detailed changelog")
    download_url: Optional[str] = Field(None, description="URL to download release")


class ReleaseUpdateRequest(BaseModel):
    """Request model for updating release announcements"""

    title: Optional[str] = Field(None, description="Release title")
    description: Optional[str] = Field(None, description="Release description")
    is_major: Optional[bool] = Field(
        None, description="Whether this is a major release"
    )
    is_featured: Optional[bool] = Field(
        None, description="Whether to feature this release"
    )
    changelog_url: Optional[str] = Field(None, description="URL to detailed changelog")
    download_url: Optional[str] = Field(None, description="URL to download release")


class ReleaseViewRequest(BaseModel):
    """Request model for marking releases as viewed"""

    release_id: str = Field(..., description="Release ID to mark as viewed")
    is_dismissed: bool = Field(False, description="Whether to dismiss the release")


class ReleaseResponse(BaseModel):
    """Response model for release data"""

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


class ReleaseSyncRequest(BaseModel):
    """Request model for syncing releases"""

    source: str = Field(..., description="Sync source: 'github' or 'changelog'")
    force: bool = Field(False, description="Force sync even if cached")


def get_current_user_context(
    authorization: str = Depends(lambda: None),
    token_manager: APITokenManager = Depends(lambda: None),
    db_path: str = Depends(lambda: os.getenv("DB_PATH", "prompts.db")),
) -> Dict[str, str]:
    """Extract user context from authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")

    token = authorization.replace("Bearer ", "")
    if not token_manager:
        token_manager = APITokenManager(db_path)

    is_valid, user_id, tenant_id = token_manager.validate_api_token(token)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"user_id": user_id or "", "tenant_id": tenant_id or ""}


def create_release_router(db_path: Optional[str] = None) -> APIRouter:
    """Create FastAPI router for release management endpoints"""
    router = APIRouter(prefix="/api/releases", tags=["Releases"])

    def get_release_manager():
        return ReleaseManager(db_path)

    def get_token_manager():
        return APITokenManager(db_path)

    @router.get("/", response_model=List[ReleaseResponse])
    async def list_releases(
        limit: int = Query(10, ge=1, le=50, description="Number of releases to return"),
        include_dismissed: bool = Query(
            False, description="Include dismissed releases"
        ),
        user_context: Dict[str, str] = Depends(get_current_user_context),
        release_manager: ReleaseManager = Depends(get_release_manager),
    ):
        """Get list of release announcements"""
        try:
            releases = release_manager.get_releases(
                limit=limit,
                include_dismissed=include_dismissed,
                user_id=user_context["user_id"],
            )

            return [
                ReleaseResponse(
                    id=release.id,
                    version=release.version,
                    title=release.title,
                    description=release.description,
                    release_date=release.release_date,
                    is_major=release.is_major,
                    is_featured=release.is_featured,
                    changelog_url=release.changelog_url,
                    download_url=release.download_url,
                    github_release_id=release.github_release_id,
                    created_at=release.created_at,
                    updated_at=release.updated_at,
                )
                for release in releases
            ]

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error retrieving releases: {str(e)}"
            )

    @router.post("/", response_model=Dict[str, str])
    async def create_release(
        request: ReleaseCreateRequest,
        user_context: Dict[str, str] = Depends(get_current_user_context),
        release_manager: ReleaseManager = Depends(get_release_manager),
    ):
        """Create a new release announcement (admin only)"""
        try:
            # TODO: Add admin role check here
            success, message = release_manager.create_release_announcement(
                version=request.version,
                title=request.title,
                description=request.description,
                is_major=request.is_major,
                is_featured=request.is_featured,
                changelog_url=request.changelog_url,
                download_url=request.download_url,
            )

            if not success:
                raise HTTPException(status_code=400, detail=message)

            return {"message": message}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error creating release: {str(e)}"
            )

    @router.get("/unread-count")
    async def get_unread_count(
        user_context: Dict[str, str] = Depends(get_current_user_context),
        release_manager: ReleaseManager = Depends(get_release_manager),
    ):
        """Get count of unread releases for current user"""
        try:
            count = release_manager.get_unread_count(user_context["user_id"])
            return {"unread_count": count}

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error getting unread count: {str(e)}"
            )

    @router.post("/mark-viewed")
    async def mark_release_viewed(
        request: ReleaseViewRequest,
        user_context: Dict[str, str] = Depends(get_current_user_context),
        release_manager: ReleaseManager = Depends(get_release_manager),
    ):
        """Mark a release as viewed by current user"""
        try:
            success, message = release_manager.mark_release_viewed(
                user_id=user_context["user_id"],
                release_id=request.release_id,
                is_dismissed=request.is_dismissed,
            )

            if not success:
                raise HTTPException(status_code=400, detail=message)

            return {"message": message}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error marking release as viewed: {str(e)}"
            )

    @router.post("/sync")
    async def sync_releases(
        request: ReleaseSyncRequest,
        user_context: Dict[str, str] = Depends(get_current_user_context),
        release_manager: ReleaseManager = Depends(get_release_manager),
    ):
        """Sync releases from external sources (admin only)"""
        try:
            # TODO: Add admin role check here
            if request.force:
                release_manager._clear_cache()

            if request.source == "github":
                success, message = release_manager.sync_github_releases()
            elif request.source == "changelog":
                success, message = release_manager.parse_changelog()
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid sync source. Use 'github' or 'changelog'",
                )

            if not success:
                raise HTTPException(status_code=400, detail=message)

            return {"message": message}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error syncing releases: {str(e)}"
            )

    @router.get("/health")
    async def release_system_health():
        """Check release system health"""
        try:
            release_manager = get_release_manager()

            # Test database connection
            releases = release_manager.get_releases(limit=1)

            # Check configuration
            config_status = {
                "github_enabled": release_manager.github_enabled,
                "changelog_enabled": release_manager.changelog_enabled,
                "cache_duration": release_manager.cache_duration,
            }

            return {
                "status": "healthy",
                "database": "connected",
                "releases_count": len(releases),
                "configuration": config_status,
            }

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Release system unhealthy: {str(e)}"
            )

    @router.get("/stats")
    async def get_release_stats(
        user_context: Dict[str, str] = Depends(get_current_user_context),
        release_manager: ReleaseManager = Depends(get_release_manager),
    ):
        """Get release statistics"""
        try:
            all_releases = release_manager.get_releases(limit=100)
            unread_count = release_manager.get_unread_count(user_context["user_id"])

            major_releases = len([r for r in all_releases if r.is_major])
            featured_releases = len([r for r in all_releases if r.is_featured])

            return {
                "total_releases": len(all_releases),
                "major_releases": major_releases,
                "featured_releases": featured_releases,
                "unread_releases": unread_count,
                "latest_version": all_releases[0].version if all_releases else None,
            }

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error getting release stats: {str(e)}"
            )

    return router


# Admin-specific endpoints (separate router for role-based access)
def create_admin_release_router(db_path: Optional[str] = None) -> APIRouter:
    """Create admin-only release management endpoints"""
    router = APIRouter(prefix="/api/admin/releases", tags=["Admin - Releases"])

    def get_release_manager():
        return ReleaseManager(db_path)

    def verify_admin_user(
        user_context: Dict[str, str] = Depends(get_current_user_context)
    ):
        """Verify user has admin privileges"""
        # TODO: Implement proper admin role checking
        # For now, allow all authenticated users
        return user_context

    @router.get("/all")
    async def list_all_releases(
        limit: int = Query(50, ge=1, le=200),
        admin_context: Dict[str, str] = Depends(verify_admin_user),
        release_manager: ReleaseManager = Depends(get_release_manager),
    ):
        """Get all releases without user filtering (admin only)"""
        try:
            releases = release_manager.get_releases(limit=limit, include_dismissed=True)

            return [
                {
                    "id": release.id,
                    "version": release.version,
                    "title": release.title,
                    "description": (
                        release.description[:200] + "..."
                        if len(release.description) > 200
                        else release.description
                    ),
                    "release_date": release.release_date,
                    "is_major": release.is_major,
                    "is_featured": release.is_featured,
                    "github_release_id": release.github_release_id,
                    "created_at": release.created_at,
                }
                for release in releases
            ]

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error retrieving all releases: {str(e)}"
            )

    @router.delete("/{release_id}")
    async def delete_release(
        release_id: str,
        admin_context: Dict[str, str] = Depends(verify_admin_user),
        release_manager: ReleaseManager = Depends(get_release_manager),
    ):
        """Delete a release announcement (admin only)"""
        try:
            # TODO: Implement delete functionality in ReleaseManager
            return {"message": f"Release {release_id} deleted (not yet implemented)"}

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error deleting release: {str(e)}"
            )

    @router.post("/bulk-sync")
    async def bulk_sync_releases(
        admin_context: Dict[str, str] = Depends(verify_admin_user),
        release_manager: ReleaseManager = Depends(get_release_manager),
    ):
        """Sync from all sources (admin only)"""
        try:
            results = []

            # Sync from GitHub
            if release_manager.github_enabled:
                success, message = release_manager.sync_github_releases()
                results.append(
                    {"source": "github", "success": success, "message": message}
                )

            # Sync from changelog
            if release_manager.changelog_enabled:
                success, message = release_manager.parse_changelog()
                results.append(
                    {"source": "changelog", "success": success, "message": message}
                )

            return {"sync_results": results}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in bulk sync: {str(e)}")

    @router.post("/cleanup-cache")
    async def cleanup_cache(
        admin_context: Dict[str, str] = Depends(verify_admin_user),
        release_manager: ReleaseManager = Depends(get_release_manager),
    ):
        """Clean up expired cache entries (admin only)"""
        try:
            release_manager.cleanup_old_cache()
            return {"message": "Cache cleanup completed"}

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error cleaning cache: {str(e)}"
            )

    return router
