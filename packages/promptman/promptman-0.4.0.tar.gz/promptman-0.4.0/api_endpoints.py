"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

REST API endpoints for AI Prompt Manager
Provides programmatic access to prompts via secure API tokens

This software is licensed for non-commercial use only.
See LICENSE file for details.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from api_token_manager import APITokenManager
from auth_manager import AuthManager
from prompt_data_manager import PromptDataManager


# Pydantic models for API
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class PromptResponse(BaseModel):
    id: int
    name: str
    title: str
    content: str
    category: str
    tags: Optional[str] = None
    is_enhancement_prompt: bool
    user_id: str
    created_at: str
    updated_at: str


class PromptListResponse(BaseModel):
    prompts: List[PromptResponse]
    total: int
    page: int
    page_size: int


class UserInfo(BaseModel):
    user_id: str
    tenant_id: str
    email: str
    first_name: str
    last_name: str
    role: str


# API Security
security = HTTPBearer()


class APIManager:
    def __init__(self, db_path: str = "prompts.db"):
        self.db_path = db_path
        self.token_manager = APITokenManager(db_path)
        self.auth_manager = AuthManager(db_path)

        # Create FastAPI app
        self.app = FastAPI(
            title="AI Prompt Manager API",
            description="Secure API for managing AI prompts with multi-tenant support",
            version="1.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc",
        )

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )

        self.setup_routes()

    def get_router(self):
        """Get a router with all API routes for integration with other FastAPI apps"""
        from fastapi import APIRouter

        router = APIRouter()

        # Since routes are defined with /api/ prefix in setup_routes,
        # we need to create new routes without the prefix for the router
        # The prefix will be added when including the router

        # Health endpoint
        @router.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}

        # User info endpoint
        @router.get("/user/info", response_model=APIResponse)
        async def get_user_info(
            current_user: UserInfo = Depends(self.get_current_user),
        ):
            return APIResponse(
                success=True,
                message="User info retrieved successfully",
                data={
                    "user_id": current_user.user_id,
                    "tenant_id": current_user.tenant_id,
                    "role": current_user.role,
                },
            )

        return router

    async def get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> UserInfo:
        """Validate API token and return user info"""
        token = credentials.credentials

        # Validate token
        is_valid, user_id, tenant_id = self.token_manager.validate_api_token(token)

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid or expired API token")

        # Get user details
        users = self.auth_manager.get_tenant_users(str(tenant_id))
        user = next((u for u in users if u.id == user_id), None)

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return UserInfo(
            user_id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        )

    def get_data_manager(self, user_info: UserInfo) -> PromptDataManager:
        """Get tenant-aware data manager for the user"""
        return PromptDataManager(
            db_path=self.db_path,
            tenant_id=user_info.tenant_id,
            user_id=user_info.user_id,
        )

    def setup_routes(self):
        """Setup all API routes"""

        @self.app.get("/api/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}

        @self.app.get("/api/user/info", response_model=APIResponse)
        async def get_user_info(user_info: UserInfo = Depends(self.get_current_user)):
            """Get current user information"""
            return APIResponse(
                success=True,
                message="User information retrieved successfully",
                data={
                    "user": user_info.dict(),
                    "token_stats": self.token_manager.get_token_stats(
                        user_info.user_id
                    ),
                },
            )

        @self.app.get("/api/prompts", response_model=PromptListResponse)
        async def list_prompts(
            user_info: UserInfo = Depends(self.get_current_user),
            page: int = Query(1, ge=1, description="Page number"),
            page_size: int = Query(50, ge=1, le=100, description="Items per page"),
            category: Optional[str] = Query(None, description="Filter by category"),
            search: Optional[str] = Query(
                None, description="Search in name, title, content"
            ),
            include_enhancement: bool = Query(
                True, description="Include enhancement prompts"
            ),
        ):
            """List prompts with pagination and filtering"""
            data_manager = self.get_data_manager(user_info)

            # Get prompts based on filters
            if search:
                prompts = data_manager.search_prompts(search, include_enhancement)
            elif category:
                prompts = data_manager.get_prompts_by_category(
                    category, include_enhancement
                )
            else:
                prompts = data_manager.get_all_prompts(include_enhancement)

            # Apply pagination
            total = len(prompts)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_prompts = prompts[start_idx:end_idx]

            # Convert to response format
            prompt_responses = []
            for prompt in paginated_prompts:
                prompt_responses.append(
                    PromptResponse(
                        id=prompt["id"],
                        name=prompt["name"],
                        title=prompt["title"],
                        content=prompt["content"],
                        category=prompt["category"],
                        tags=prompt["tags"],
                        is_enhancement_prompt=prompt["is_enhancement_prompt"],
                        user_id=prompt["user_id"],
                        created_at=str(prompt["created_at"]),
                        updated_at=str(prompt["updated_at"]),
                    )
                )

            return PromptListResponse(
                prompts=prompt_responses, total=total, page=page, page_size=page_size
            )

        @self.app.get("/api/prompts/{prompt_id}", response_model=APIResponse)
        async def get_prompt_by_id(
            prompt_id: int, user_info: UserInfo = Depends(self.get_current_user)
        ):
            """Get a specific prompt by ID"""
            data_manager = self.get_data_manager(user_info)
            prompts = data_manager.get_all_prompts()

            prompt = next((p for p in prompts if p["id"] == prompt_id), None)

            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            return APIResponse(
                success=True,
                message="Prompt retrieved successfully",
                data={"prompt": prompt},
            )

        @self.app.get("/api/prompts/name/{prompt_name}", response_model=APIResponse)
        async def get_prompt_by_name(
            prompt_name: str, user_info: UserInfo = Depends(self.get_current_user)
        ):
            """Get a specific prompt by name"""
            data_manager = self.get_data_manager(user_info)
            prompt = data_manager.get_prompt_by_name(prompt_name)

            if not prompt:
                raise HTTPException(
                    status_code=404, detail=f"Prompt '{prompt_name}' not found"
                )

            return APIResponse(
                success=True,
                message="Prompt retrieved successfully",
                data={"prompt": prompt},
            )

        @self.app.get("/api/categories", response_model=APIResponse)
        async def list_categories(user_info: UserInfo = Depends(self.get_current_user)):
            """List all categories for the user's tenant"""
            data_manager = self.get_data_manager(user_info)
            categories = data_manager.get_categories()

            return APIResponse(
                success=True,
                message="Categories retrieved successfully",
                data={"categories": categories},
            )

        @self.app.get(
            "/api/prompts/category/{category_name}", response_model=PromptListResponse
        )
        async def get_prompts_by_category(
            category_name: str,
            user_info: UserInfo = Depends(self.get_current_user),
            page: int = Query(1, ge=1),
            page_size: int = Query(50, ge=1, le=100),
            include_enhancement: bool = Query(True),
        ):
            """Get prompts by category with pagination"""
            data_manager = self.get_data_manager(user_info)
            prompts = data_manager.get_prompts_by_category(
                category_name, include_enhancement
            )

            # Apply pagination
            total = len(prompts)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_prompts = prompts[start_idx:end_idx]

            # Convert to response format
            prompt_responses = []
            for prompt in paginated_prompts:
                prompt_responses.append(
                    PromptResponse(
                        id=prompt["id"],
                        name=prompt["name"],
                        title=prompt["title"],
                        content=prompt["content"],
                        category=prompt["category"],
                        tags=prompt["tags"],
                        is_enhancement_prompt=prompt["is_enhancement_prompt"],
                        user_id=prompt["user_id"],
                        created_at=str(prompt["created_at"]),
                        updated_at=str(prompt["updated_at"]),
                    )
                )

            return PromptListResponse(
                prompts=prompt_responses, total=total, page=page, page_size=page_size
            )

        @self.app.get("/api/search", response_model=PromptListResponse)
        async def search_prompts(
            q: str = Query(..., description="Search query"),
            user_info: UserInfo = Depends(self.get_current_user),
            page: int = Query(1, ge=1),
            page_size: int = Query(50, ge=1, le=100),
            include_enhancement: bool = Query(True),
        ):
            """Search prompts with pagination"""
            data_manager = self.get_data_manager(user_info)
            prompts = data_manager.search_prompts(q, include_enhancement)

            # Apply pagination
            total = len(prompts)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_prompts = prompts[start_idx:end_idx]

            # Convert to response format
            prompt_responses = []
            for prompt in paginated_prompts:
                prompt_responses.append(
                    PromptResponse(
                        id=prompt["id"],
                        name=prompt["name"],
                        title=prompt["title"],
                        content=prompt["content"],
                        category=prompt["category"],
                        tags=prompt["tags"],
                        is_enhancement_prompt=prompt["is_enhancement_prompt"],
                        user_id=prompt["user_id"],
                        created_at=str(prompt["created_at"]),
                        updated_at=str(prompt["updated_at"]),
                    )
                )

            return PromptListResponse(
                prompts=prompt_responses, total=total, page=page, page_size=page_size
            )

        @self.app.get("/api/stats", response_model=APIResponse)
        async def get_stats(user_info: UserInfo = Depends(self.get_current_user)):
            """Get user statistics"""
            data_manager = self.get_data_manager(user_info)

            prompts = data_manager.get_all_prompts()
            enhancement_prompts = data_manager.get_enhancement_prompts()
            categories = data_manager.get_categories()

            # Calculate statistics
            regular_prompts = [p for p in prompts if not p["is_enhancement_prompt"]]

            stats = {
                "total_prompts": len(prompts),
                "regular_prompts": len(regular_prompts),
                "enhancement_prompts": len(enhancement_prompts),
                "categories": len(categories),
                "category_breakdown": {},
            }

            # Category breakdown
            category_breakdown: Dict[str, int] = {}
            for category in categories:
                category_prompts = [
                    p for p in regular_prompts if p["category"] == category
                ]
                category_breakdown[str(category)] = len(category_prompts)
            stats["category_breakdown"] = category_breakdown

            return APIResponse(
                success=True,
                message="Statistics retrieved successfully",
                data={"stats": stats},
            )


# Global API manager instance
api_manager = None


def get_api_app(db_path: str = "prompts.db") -> FastAPI:
    """Get or create the FastAPI application"""
    global api_manager
    if api_manager is None:
        api_manager = APIManager(db_path)
    return api_manager.app
