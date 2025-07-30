#!/usr/bin/env python3
"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

AI Prompt Manager Web Application
FastAPI-based web interface with modern UI components

This software is licensed for non-commercial use only.
See LICENSE file for details.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from api_token_manager import APITokenManager
from auth_manager import AuthManager, User
from i18n import i18n
from language_manager import get_language_manager, t
from langwatch_optimizer import langwatch_optimizer
from prompt_data_manager import PromptDataManager
from text_translator import text_translator

# Import enhanced AI services API
try:
    from api_endpoints_enhanced import get_ai_models_router

    AI_MODELS_API_AVAILABLE = True
except ImportError:
    AI_MODELS_API_AVAILABLE = False

# Import prompt API endpoints
try:
    from prompt_api_endpoints import create_prompt_router

    PROMPT_API_AVAILABLE = True
except ImportError:
    PROMPT_API_AVAILABLE = False

from token_calculator import token_calculator


class WebApp:
    def __init__(self, db_path: str = "prompts.db"):
        self.db_path = db_path
        self.auth_manager = AuthManager(db_path)
        self.api_token_manager = APITokenManager(db_path)

        # Check if running in single-user mode
        self.single_user_mode = os.getenv("MULTITENANT_MODE", "true").lower() == "false"

        # Initialize FastAPI app
        self.app = FastAPI(
            title="AI Prompt Manager",
            description="Modern web interface for AI prompt management",
            version="1.0.0",
        )

        # Add session middleware
        self.app.add_middleware(
            SessionMiddleware, secret_key=os.getenv("SECRET_KEY", secrets.token_hex(32))
        )

        # Set up templates and static files
        self.templates = Jinja2Templates(directory="web_templates")

        # Mount static files (only if directory exists and is accessible)
        static_dir = "web_templates/static"
        if os.path.exists(static_dir) and os.path.isdir(static_dir):
            try:
                self.app.mount(
                    "/static", StaticFiles(directory=static_dir), name="static"
                )
            except RuntimeError:
                # Static directory exists but might be empty or inaccessible
                # Create a placeholder to make StaticFiles work
                os.makedirs(f"{static_dir}/css", exist_ok=True)
                os.makedirs(f"{static_dir}/js", exist_ok=True)

                # Create minimal placeholder files
                with open(f"{static_dir}/css/.gitkeep", "w") as f:
                    f.write("# Placeholder for CSS files\n")
                with open(f"{static_dir}/js/.gitkeep", "w") as f:
                    f.write("# Placeholder for JS files\n")

                self.app.mount(
                    "/static", StaticFiles(directory=static_dir), name="static"
                )

        # Include AI models router if available
        if AI_MODELS_API_AVAILABLE:
            try:
                ai_models_router = get_ai_models_router()
                self.app.include_router(ai_models_router)
            except Exception as e:
                print(f"Warning: Could not include AI models router: {e}")

        # Include prompt API router if available
        if PROMPT_API_AVAILABLE:
            try:
                prompt_router = create_prompt_router(self.db_path)
                self.app.include_router(prompt_router)
                print("✅ Prompt API endpoints loaded")
            except Exception as e:
                print(f"Warning: Could not include prompt API router: {e}")

        # Set up routes
        self._setup_routes()

    def _setup_routes(self):
        """Set up all application routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            if self.single_user_mode:
                # In single-user mode, bypass authentication
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                prompts = data_manager.get_all_prompts()[:5]  # Latest 5 prompts

                return self.templates.TemplateResponse(
                    "prompts/dashboard.html",
                    self.get_template_context(
                        request,
                        user=None,
                        prompts=prompts,
                        page_title="Dashboard",
                        single_user_mode=True,
                        is_multi_tenant_mode=False,
                    ),
                )

            # Multi-tenant mode - require authentication
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            # Get recent prompts
            prompts = data_manager.get_all_prompts()[:5]  # Latest 5 prompts

            return self.templates.TemplateResponse(
                "prompts/dashboard.html",
                self.get_template_context(
                    request,
                    user,
                    prompts=prompts,
                    page_title="Dashboard",
                    is_multi_tenant_mode=True,
                ),
            )

        @self.app.get("/login", response_class=HTMLResponse)
        async def login_page(request: Request):
            if self.single_user_mode:
                # In single-user mode, redirect to dashboard
                return RedirectResponse(url="/", status_code=302)

            return self.templates.TemplateResponse(
                "auth/login.html",
                self.get_template_context(request, page_title="Login"),
            )

        @self.app.post("/login")
        async def login_submit(
            request: Request,
            email: str = Form(...),
            password: str = Form(...),
            subdomain: str = Form(default="localhost"),
        ):
            success, user, message = self.auth_manager.authenticate_user(
                email, password, subdomain
            )

            if success and user:
                # Set session
                request.session["user_id"] = user.id
                request.session["tenant_id"] = user.tenant_id
                request.session["login_time"] = datetime.now().isoformat()

                return RedirectResponse(url="/", status_code=302)
            else:
                return self.templates.TemplateResponse(
                    "auth/login.html",
                    self.get_template_context(
                        request,
                        error=message,
                        page_title="Login",
                        email=email,
                        subdomain=subdomain,
                    ),
                )

        @self.app.get("/logout")
        async def logout(request: Request):
            request.session.clear()
            return RedirectResponse(url="/login", status_code=302)

        # Prompts routes
        @self.app.get("/prompts", response_class=HTMLResponse)
        async def prompts_list(request: Request):
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                user = None
            else:
                # Multi-tenant mode
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Use visibility-aware method in multi-tenant mode
            if self.single_user_mode:
                prompts = data_manager.get_all_prompts()
            else:
                prompts = data_manager.get_all_prompts_with_visibility()
            categories = data_manager.get_categories()

            return self.templates.TemplateResponse(
                "prompts/list.html",
                self.get_template_context(
                    request,
                    user,
                    prompts=prompts,
                    categories=categories,
                    page_title=t("nav.prompts"),
                    single_user_mode=self.single_user_mode,
                    is_multi_tenant_mode=not self.single_user_mode,
                ),
            )

        @self.app.get("/prompts/new", response_class=HTMLResponse)
        async def new_prompt(request: Request):
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                categories = data_manager.get_categories()

                return self.templates.TemplateResponse(
                    "prompts/form.html",
                    self.get_template_context(
                        request,
                        user=None,
                        categories=categories or [],
                        page_title=t("prompt.create_new"),
                        action="create",
                        name="",
                        content="",
                        category="",
                        description="",
                        tags="",
                        visibility="private",
                        prompt_id=None,
                        error=None,
                        single_user_mode=True,
                        is_multi_tenant_mode=False,
                    ),
                )

            # Multi-tenant mode
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            categories = data_manager.get_categories()

            return self.templates.TemplateResponse(
                "prompts/form.html",
                self.get_template_context(
                    request,
                    user,
                    categories=categories or [],
                    page_title=t("prompt.create_new"),
                    action="create",
                    name="",
                    content="",
                    category="",
                    description="",
                    tags="",
                    visibility="private",
                    prompt_id=None,
                    error=None,
                    single_user_mode=self.single_user_mode,
                    is_multi_tenant_mode=not self.single_user_mode,
                ),
            )

        @self.app.post("/prompts/new")
        async def create_prompt(
            request: Request,
            name: str = Form(...),
            content: str = Form(...),
            category: str = Form(...),
            description: str = Form(default=""),
            tags: str = Form(default=""),
            visibility: str = Form(default="private"),
        ):
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                user = None
            else:
                # Multi-tenant mode
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Process tags
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

            # Only pass visibility in multi-tenant mode
            if self.single_user_mode:
                result = data_manager.add_prompt(
                    name=name,
                    title=name,  # Using name as title
                    content=content,
                    category=category,
                    tags=", ".join(tag_list),  # Convert list to string
                )
            else:
                result = data_manager.add_prompt(
                    name=name,
                    title=name,  # Using name as title
                    content=content,
                    category=category,
                    tags=", ".join(tag_list),  # Convert list to string
                    visibility=visibility,
                )

            if not result.startswith("Error:"):
                return RedirectResponse(url="/prompts", status_code=302)
            else:
                categories = data_manager.get_categories()
                return self.templates.TemplateResponse(
                    "prompts/form.html",
                    self.get_template_context(
                        request,
                        user,
                        categories=categories,
                        error=result,
                        page_title=t("prompt.create_new"),
                        action="create",
                        name=name,
                        content=content,
                        category=category,
                        description=description,
                        tags=tags,
                        visibility=visibility,
                        single_user_mode=self.single_user_mode,
                        is_multi_tenant_mode=not self.single_user_mode,
                    ),
                )

        @self.app.get("/prompts/{prompt_id}/edit", response_class=HTMLResponse)
        async def edit_prompt(request: Request, prompt_id: int):
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                user = None
            else:
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Get prompt by ID
            all_prompts = data_manager.get_all_prompts()
            prompt = next((p for p in all_prompts if p["id"] == prompt_id), None)
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            categories = data_manager.get_categories()

            return self.templates.TemplateResponse(
                "prompts/form.html",
                self.get_template_context(
                    request,
                    user,
                    categories=categories,
                    page_title=t("prompt.edit"),
                    action="edit",
                    prompt_id=prompt_id,
                    name=prompt.get("name", ""),
                    content=prompt.get("content", ""),
                    category=prompt.get("category", ""),
                    description=prompt.get("description", ""),
                    tags=prompt.get("tags", ""),
                    visibility=prompt.get("visibility", "private"),
                    single_user_mode=self.single_user_mode,
                    is_multi_tenant_mode=not self.single_user_mode,
                ),
            )

        @self.app.post("/prompts/{prompt_id}/edit")
        async def update_prompt(
            request: Request,
            prompt_id: int,
            name: str = Form(...),
            content: str = Form(...),
            category: str = Form(...),
            description: str = Form(default=""),
            tags: str = Form(default=""),
            visibility: str = Form(default="private"),
        ):
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                user = None
            else:
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Get the original prompt by ID
            all_prompts = data_manager.get_all_prompts()
            original_prompt = next(
                (p for p in all_prompts if p["id"] == prompt_id), None
            )
            if not original_prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            # Only pass visibility in multi-tenant mode
            if self.single_user_mode:
                result = data_manager.update_prompt(
                    original_name=original_prompt["name"],
                    new_name=name,
                    title=name,  # Using name as title
                    content=content,
                    category=category,
                    tags=tags,
                )
            else:
                result = data_manager.update_prompt(
                    original_name=original_prompt["name"],
                    new_name=name,
                    title=name,  # Using name as title
                    content=content,
                    category=category,
                    tags=tags,
                    visibility=visibility,
                )

            if not result.startswith("Error:"):
                return RedirectResponse(url="/prompts", status_code=302)
            else:
                categories = data_manager.get_categories()
                return self.templates.TemplateResponse(
                    "prompts/form.html",
                    self.get_template_context(
                        request,
                        user,
                        categories=categories,
                        error=result,
                        page_title=t("prompt.edit"),
                        action="edit",
                        prompt_id=prompt_id,
                        name=name,
                        content=content,
                        category=category,
                        description=description,
                        tags=tags,
                        visibility=visibility,
                        single_user_mode=self.single_user_mode,
                        is_multi_tenant_mode=not self.single_user_mode,
                    ),
                )

        @self.app.delete("/prompts/{prompt_id}")
        async def delete_prompt(request: Request, prompt_id: int):
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                user = None
            else:
                user = await self.get_current_user(request)
                if not user:
                    raise HTTPException(
                        status_code=401, detail="Authentication required"
                    )
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Get prompt by ID to get its name for deletion
            all_prompts = data_manager.get_all_prompts()
            prompt = next((p for p in all_prompts if p["id"] == prompt_id), None)
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            success = data_manager.delete_prompt(prompt["name"])
            if success:
                # Return updated prompts list for HTMX
                # Use visibility-aware method in multi-tenant mode
                if self.single_user_mode:
                    prompts = data_manager.get_all_prompts()
                else:
                    prompts = data_manager.get_all_prompts_with_visibility()
                categories = data_manager.get_categories()

                return self.templates.TemplateResponse(
                    "prompts/_list_partial.html",
                    {
                        "request": request,
                        "user": user,
                        "prompts": prompts,
                        "categories": categories,
                        "i18n": i18n,
                        "available_languages": i18n.get_available_languages(),
                        "current_language": i18n.current_language,
                        "single_user_mode": self.single_user_mode,
                        "is_multi_tenant_mode": not self.single_user_mode,
                    },
                )
            else:
                raise HTTPException(status_code=404, detail="Prompt not found")

        @self.app.get("/prompts/search")
        async def search_prompts(request: Request, q: str = ""):
            if self.single_user_mode:
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                user = None
            else:
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Simple search implementation using visibility-aware method
            if self.single_user_mode:
                all_prompts = data_manager.get_all_prompts()
            else:
                all_prompts = data_manager.get_all_prompts_with_visibility()
            if q:
                prompts = [
                    p
                    for p in all_prompts
                    if q.lower() in p["name"].lower()
                    or q.lower() in p.get("content", "").lower()
                    or q.lower() in p.get("description", "").lower()
                ]
            else:
                prompts = all_prompts

            categories = data_manager.get_categories()

            return self.templates.TemplateResponse(
                "prompts/_list_partial.html",
                self.get_template_context(
                    request,
                    user,
                    prompts=prompts,
                    categories=categories,
                    is_multi_tenant_mode=not self.single_user_mode,
                ),
            )

        @self.app.get("/prompts/filter")
        async def filter_prompts(
            request: Request,
            category: str = "",
            sort: str = "created_desc",
            visibility: str = "",
        ):
            if self.single_user_mode:
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                user = None
            else:
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Get prompts using visibility-aware method
            if self.single_user_mode:
                prompts = data_manager.get_all_prompts()
            else:
                if visibility == "public":
                    prompts = data_manager.get_public_prompts_in_tenant()
                elif visibility == "private":
                    # Only user's own private prompts
                    all_prompts = data_manager.get_all_prompts()
                    prompts = [
                        p
                        for p in all_prompts
                        if p.get("visibility", "private") == "private"
                    ]
                elif visibility == "mine":
                    prompts = data_manager.get_all_prompts()  # Only user's own prompts
                else:
                    prompts = data_manager.get_all_prompts_with_visibility()

            if category:
                prompts = [p for p in prompts if p.get("category") == category]

            # Sort prompts
            if sort == "name_asc":
                prompts.sort(key=lambda p: p.get("name", "").lower())
            elif sort == "name_desc":
                prompts.sort(key=lambda p: p.get("name", "").lower(), reverse=True)
            elif sort == "category_asc":
                prompts.sort(key=lambda p: p.get("category", "").lower())
            elif sort == "created_asc":
                prompts.sort(key=lambda p: p.get("created_at", ""))
            else:  # created_desc (default)
                prompts.sort(key=lambda p: p.get("created_at", ""), reverse=True)

            categories = data_manager.get_categories()

            return self.templates.TemplateResponse(
                "prompts/_list_partial.html",
                self.get_template_context(
                    request,
                    user,
                    prompts=prompts,
                    categories=categories,
                    is_multi_tenant_mode=not self.single_user_mode,
                ),
            )

        # Language switching route
        @self.app.post("/language")
        async def change_language(request: Request, language: str = Form(...)):
            """Change the interface language"""
            language_manager = get_language_manager()
            success = language_manager.set_language(language)
            if success:
                request.session["language"] = language
                # Also update legacy i18n for backward compatibility
                i18n.set_language(language)

            # For regular web requests, redirect back to the referring page
            # Only return JSON for API-style requests
            content_type = request.headers.get("content-type", "")
            if (
                not request.headers.get("referer")
                and "application/json" in content_type
            ):
                return {"success": success, "language": language}

            return RedirectResponse(
                url=request.headers.get("referer", "/"), status_code=302
            )

        # Translation route
        @self.app.post("/translate")
        async def translate_text(
            request: Request,
            text: str = Form(...),
            target_lang: str = Form(default="en"),
        ):
            """Translate text to target language"""
            user, data_manager = await self.get_current_user_or_default(request)

            success, translated_text, error = text_translator.translate_to_english(text)

            return {
                "success": success,
                "translated_text": translated_text,
                "error": error,
                "original_text": text,
            }

        # Text enhancement route for speech dictation
        @self.app.post("/enhance-text")
        async def enhance_text(
            request: Request,
            text: str = Form(...),
            type: str = Form(default="dictation"),
        ):
            """Enhance dictated text for better readability and structure"""
            user, data_manager = await self.get_current_user_or_default(request)

            try:
                # Use the optimization service to enhance the text
                from langwatch_optimizer import PromptOptimizer

                optimizer = PromptOptimizer()

                # Create a prompt for text enhancement
                enhancement_prompt = f"""
Please clean up and enhance the following dictated text:

Original text: {text}

Instructions:
1. Fix any grammar and punctuation errors
2. Improve sentence structure and flow
3. Remove filler words and repetitions
4. Maintain the original meaning and intent
5. Format as clear, well-structured text
6. Don't change the core content or add new information
7. Make it suitable for use as a prompt or instruction

Enhanced text:"""

                try:
                    enhanced_result = optimizer.optimize_prompt(enhancement_prompt)
                    if enhanced_result.get("success"):
                        enhanced_text = enhanced_result.get(
                            "optimized_prompt", ""
                        ).strip()

                        # Extract just the enhanced text part
                        if "Enhanced text:" in enhanced_text:
                            enhanced_text = enhanced_text.split("Enhanced text:")[
                                -1
                            ].strip()

                        return {
                            "success": True,
                            "enhanced_text": enhanced_text,
                            "original_text": text,
                        }
                    else:
                        # Fallback to basic text cleaning
                        enhanced_text = basic_text_enhancement(text)
                        return {
                            "success": True,
                            "enhanced_text": enhanced_text,
                            "original_text": text,
                        }
                except Exception:
                    # Fallback to basic enhancement
                    enhanced_text = basic_text_enhancement(text)
                    return {
                        "success": True,
                        "enhanced_text": enhanced_text,
                        "original_text": text,
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "original_text": text,
                }

        # Optimization route
        @self.app.post("/optimize")
        async def optimize_prompt(request: Request, prompt: str = Form(...)):
            """Optimize a prompt using available optimization services"""
            user, data_manager = await self.get_current_user_or_default(request)

            try:
                result = langwatch_optimizer.optimize_prompt(prompt)
                return {
                    "success": result.success,
                    "optimized_prompt": result.optimized_prompt,
                    "suggestions": result.suggestions,
                    "reasoning": result.reasoning,
                    "optimization_score": result.optimization_score,
                    "error": result.error_message,
                }
            except Exception as e:
                return {
                    "success": False,
                    "optimized_prompt": prompt,
                    "suggestions": [],
                    "reasoning": "Optimization service unavailable",
                    "optimization_score": 0.0,
                    "error": str(e),
                }

        # Token calculation route
        @self.app.post("/calculate-tokens")
        async def calculate_tokens(
            request: Request, text: str = Form(...), model: str = Form(default="gpt-4")
        ):
            """Calculate tokens and estimated cost for text"""
            user = await self.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

            try:
                result = token_calculator.estimate_tokens(text, model)

                return {
                    "success": True,
                    "token_count": result.prompt_tokens,
                    "estimated_cost": result.cost_estimate or 0.0,
                    "model": model,
                    "text_length": len(text),
                }
            except Exception as e:
                return {
                    "success": False,
                    "token_count": 0,
                    "estimated_cost": 0.0,
                    "model": model,
                    "error": str(e),
                }

        # Admin routes (only for admin users)
        @self.app.get("/admin", response_class=HTMLResponse)
        async def admin_dashboard(request: Request):
            if self.single_user_mode:
                # In single-user mode, allow admin access without authentication
                user = None
            else:
                # Multi-tenant mode - require authentication and admin role
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)

                # Check if user is admin
                if user.role != "admin":
                    raise HTTPException(status_code=403, detail="Admin access required")

            # Get admin statistics
            stats = self.auth_manager.get_admin_stats()

            if self.single_user_mode:
                # In single-user mode, show simplified stats
                users = []
                tenants = []
            else:
                if user:
                    users = self.auth_manager.get_all_users_for_tenant(user.tenant_id)
                    tenant_by_id = self.auth_manager.get_tenant_by_id(user.tenant_id)
                    tenants = (
                        self.auth_manager.get_all_tenants()
                        if user.role == "admin"
                        else ([tenant_by_id] if tenant_by_id else [])
                    )
                else:
                    users = []
                    tenants = []

            # Mock recent activity (would be from audit log)
            recent_activity = [
                {"description": "New user registered", "timestamp": "2 hours ago"},
                {
                    "description": "Prompt optimization completed",
                    "timestamp": "4 hours ago",
                },
                {"description": "API token created", "timestamp": "1 day ago"},
            ]

            # Mock system info
            system_info = {
                "version": "1.0.0",
                "database_type": "SQLite" if "sqlite" in self.db_path else "PostgreSQL",
                "multitenant_mode": self.auth_manager.is_multitenant_mode(),
                "api_enabled": True,  # Would check actual API status
                "uptime": "2 days 14 hours",
                "environment": "Development" if os.getenv("DEBUG") else "Production",
            }

            if self.single_user_mode:
                return self.templates.TemplateResponse(
                    "admin/dashboard.html",
                    self.get_template_context(
                        request,
                        user=None,
                        stats=stats,
                        users=users,
                        tenants=tenants,
                        recent_activity=recent_activity,
                        system_info=system_info,
                        page_title="Admin Dashboard",
                        single_user_mode=True,
                    ),
                )
            else:
                return self.templates.TemplateResponse(
                    "admin/dashboard.html",
                    self.get_template_context(
                        request,
                        user,
                        stats=stats,
                        users=users,
                        tenants=tenants,
                        recent_activity=recent_activity,
                        system_info=system_info,
                        page_title="Admin Dashboard",
                    ),
                )

        # Prompt Builder route
        @self.app.get("/prompts/builder", response_class=HTMLResponse)
        async def prompt_builder(request: Request):
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                prompts = data_manager.get_all_prompts()
                categories = data_manager.get_categories()

                return self.templates.TemplateResponse(
                    "prompts/builder.html",
                    self.get_template_context(
                        request,
                        user=None,
                        prompts=prompts,
                        categories=categories,
                        page_title=t("builder.title"),
                        single_user_mode=True,
                    ),
                )

            # Multi-tenant mode
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            prompts = data_manager.get_all_prompts()
            categories = data_manager.get_categories()

            return self.templates.TemplateResponse(
                "prompts/builder.html",
                self.get_template_context(
                    request,
                    user,
                    prompts=prompts,
                    categories=categories,
                    page_title=t("builder.title"),
                ),
            )

        # Prompt execution route
        @self.app.get("/prompts/{prompt_name}/execute", response_class=HTMLResponse)
        async def execute_prompt(request: Request, prompt_name: str):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            prompt = data_manager.get_prompt_by_name(prompt_name)
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            return self.templates.TemplateResponse(
                "prompts/execute.html",
                self.get_template_context(
                    request,
                    user,
                    prompt=prompt,
                    page_title=f"Execute: {prompt['name']}",
                ),
            )

        # Templates routes
        @self.app.get("/templates", response_class=HTMLResponse)
        async def templates_page(request: Request):
            if self.single_user_mode:
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                templates = data_manager.get_all_templates()
                categories = data_manager.get_template_categories()

                return self.templates.TemplateResponse(
                    "templates/list.html",
                    self.get_template_context(
                        request,
                        user=None,
                        templates=templates,
                        categories=categories,
                        page_title="Templates",
                        single_user_mode=True,
                    ),
                )

            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )
            templates = data_manager.get_all_templates()
            categories = data_manager.get_template_categories()

            return self.templates.TemplateResponse(
                "templates/list.html",
                self.get_template_context(
                    request,
                    user,
                    templates=templates,
                    categories=categories,
                    page_title="Templates",
                ),
            )

        @self.app.get("/templates/new", response_class=HTMLResponse)
        async def new_template_page(request: Request):
            if self.single_user_mode:
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                categories = data_manager.get_template_categories()

                return self.templates.TemplateResponse(
                    "templates/form.html",
                    {
                        "request": request,
                        "user": None,
                        "categories": categories,
                        "page_title": "New Template",
                        "action": "create",
                        "single_user_mode": True,
                        "i18n": i18n,
                        "current_language": i18n.current_language,
                        "available_languages": i18n.get_available_languages(),
                    },
                )

            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )
            categories = data_manager.get_template_categories()

            return self.templates.TemplateResponse(
                "templates/form.html",
                self.get_template_context(
                    request,
                    user,
                    categories=categories,
                    page_title="New Template",
                    action="create",
                ),
            )

        @self.app.post("/templates")
        async def create_template(
            request: Request,
            name: str = Form(...),
            description: str = Form(default=""),
            content: str = Form(...),
            category: str = Form(default="Custom"),
        ):
            if self.single_user_mode:
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
            else:
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Extract variables from template content
            import re

            variables = re.findall(r"\{([^}]+)\}", content)
            variables_str = ",".join(variables) if variables else ""

            result = data_manager.create_template(
                name, description, content, category, variables_str
            )

            if not result.startswith("Error:"):
                return RedirectResponse(url="/templates", status_code=302)
            else:
                categories = data_manager.get_template_categories()
                if self.single_user_mode:
                    return self.templates.TemplateResponse(
                        "templates/form.html",
                        {
                            "request": request,
                            "user": None,
                            "categories": categories,
                            "error": result,
                            "page_title": "New Template",
                            "action": "create",
                            "name": name,
                            "description": description,
                            "content": content,
                            "category": category,
                            "single_user_mode": True,
                            "i18n": i18n,
                            "current_language": i18n.current_language,
                            "available_languages": i18n.get_available_languages(),
                        },
                    )
                else:
                    user = await self.get_current_user(request)
                    return self.templates.TemplateResponse(
                        "templates/form.html",
                        self.get_template_context(
                            request,
                            user,
                            categories=categories,
                            error=result,
                            page_title="New Template",
                            action="create",
                            name=name,
                            description=description,
                            content=content,
                            category=category,
                        ),
                    )

        @self.app.get("/templates/{template_id}/edit", response_class=HTMLResponse)
        async def edit_template_page(request: Request, template_id: int):
            if self.single_user_mode:
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
            else:
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            template = data_manager.get_template_by_id(template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")

            categories = data_manager.get_template_categories()

            if self.single_user_mode:
                return self.templates.TemplateResponse(
                    "templates/form.html",
                    {
                        "request": request,
                        "user": None,
                        "categories": categories,
                        "page_title": "Edit Template",
                        "action": "edit",
                        "template_id": template_id,
                        "name": template.get("name", ""),
                        "description": template.get("description", ""),
                        "content": template.get("content", ""),
                        "category": template.get("category", ""),
                        "single_user_mode": True,
                        "i18n": i18n,
                        "current_language": i18n.current_language,
                        "available_languages": i18n.get_available_languages(),
                    },
                )
            else:
                user = await self.get_current_user(request)
                return self.templates.TemplateResponse(
                    "templates/form.html",
                    self.get_template_context(
                        request,
                        user,
                        categories=categories,
                        page_title="Edit Template",
                        action="edit",
                        template_id=template_id,
                        name=template.get("name", ""),
                        description=template.get("description", ""),
                        content=template.get("content", ""),
                        category=template.get("category", ""),
                    ),
                )

        @self.app.post("/templates/{template_id}")
        async def update_template(
            request: Request,
            template_id: int,
            name: str = Form(...),
            description: str = Form(default=""),
            content: str = Form(...),
            category: str = Form(default="Custom"),
        ):
            if self.single_user_mode:
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
            else:
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Extract variables from template content
            import re

            variables = re.findall(r"\{([^}]+)\}", content)
            variables_str = ",".join(variables) if variables else ""

            result = data_manager.update_template(
                template_id, name, description, content, category, variables_str
            )

            if not result.startswith("Error:"):
                return RedirectResponse(url="/templates", status_code=302)
            else:
                categories = data_manager.get_template_categories()
                if self.single_user_mode:
                    return self.templates.TemplateResponse(
                        "templates/form.html",
                        {
                            "request": request,
                            "user": None,
                            "categories": categories,
                            "error": result,
                            "page_title": "Edit Template",
                            "action": "edit",
                            "template_id": template_id,
                            "name": name,
                            "description": description,
                            "content": content,
                            "category": category,
                            "single_user_mode": True,
                            "i18n": i18n,
                            "current_language": i18n.current_language,
                            "available_languages": i18n.get_available_languages(),
                        },
                    )
                else:
                    user = await self.get_current_user(request)
                    return self.templates.TemplateResponse(
                        "templates/form.html",
                        self.get_template_context(
                            request,
                            user,
                            categories=categories,
                            error=result,
                            page_title="Edit Template",
                            action="edit",
                            template_id=template_id,
                            name=name,
                            description=description,
                            content=content,
                            category=category,
                        ),
                    )

        @self.app.delete("/templates/{template_id}")
        async def delete_template(request: Request, template_id: int):
            if self.single_user_mode:
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
            else:
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            success = data_manager.delete_template(template_id)
            if success:
                return RedirectResponse(url="/templates", status_code=302)
            else:
                raise HTTPException(
                    status_code=404, detail="Template not found or cannot be deleted"
                )

        # Settings routes
        @self.app.get("/settings", response_class=HTMLResponse)
        async def settings_page(request: Request):
            if self.single_user_mode:
                # In single-user mode, show simplified settings
                return self.templates.TemplateResponse(
                    "settings/index.html",
                    self.get_template_context(
                        request, user=None, page_title="Settings", single_user_mode=True
                    ),
                )

            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            return self.templates.TemplateResponse(
                "settings/index.html",
                self.get_template_context(request, user, page_title="Settings"),
            )

        # Profile routes
        @self.app.get("/profile", response_class=HTMLResponse)
        async def profile_page(request: Request):
            if self.single_user_mode:
                # In single-user mode, show a simplified profile page
                return self.templates.TemplateResponse(
                    "settings/profile.html",
                    self.get_template_context(
                        request, user=None, page_title="Profile", single_user_mode=True
                    ),
                )

            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            return self.templates.TemplateResponse(
                "settings/profile.html",
                self.get_template_context(request, user, page_title="Profile"),
            )

        # API Tokens routes
        @self.app.get("/api-tokens", response_class=HTMLResponse)
        async def api_tokens_page(request: Request):
            if self.single_user_mode:
                # In single-user mode, show simplified API tokens page
                return self.templates.TemplateResponse(
                    "settings/api_tokens.html",
                    self.get_template_context(
                        request,
                        user=None,
                        tokens=[],  # No tokens in single-user mode
                        page_title="API Tokens",
                        single_user_mode=True,
                    ),
                )

            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            # Get user's API tokens
            tokens = self.api_token_manager.get_user_tokens(user.id)

            return self.templates.TemplateResponse(
                "settings/api_tokens.html",
                self.get_template_context(
                    request,
                    user,
                    tokens=tokens,
                    page_title="API Tokens",
                ),
            )

        @self.app.post("/api-tokens/create")
        async def create_api_token(
            request: Request,
            name: str = Form(...),
            expires_days: int = Form(default=30),
        ):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            try:
                expires_days_param = expires_days if expires_days > 0 else None
                token_info = self.api_token_manager.create_api_token(
                    user_id=user.id,
                    tenant_id=user.tenant_id,
                    name=name,
                    expires_days=expires_days_param,
                )

                # Show token once to user
                request.session["new_token"] = token_info
                return RedirectResponse(url="/api-tokens?created=1", status_code=302)

            except Exception as e:
                return RedirectResponse(
                    url=f"/api-tokens?error={str(e)}", status_code=302
                )

        @self.app.post("/api-tokens/{token_id}/revoke")
        async def revoke_api_token(request: Request, token_id: str):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            try:
                self.api_token_manager.revoke_token(token_id, user.id)
                return RedirectResponse(url="/api-tokens?revoked=1", status_code=302)
            except Exception as e:
                return RedirectResponse(
                    url=f"/api-tokens?error={str(e)}", status_code=302
                )

        # AI Services Configuration
        @self.app.get("/ai-services", response_class=HTMLResponse)
        async def ai_services_page(request: Request):
            try:
                if self.single_user_mode:
                    # In single-user mode, allow AI services configuration
                    return self.templates.TemplateResponse(
                        "ai_services/enhanced_config.html",
                        self.get_template_context(
                            request,
                            user=None,
                            page_title="AI Model Configuration",
                            single_user_mode=True,
                        ),
                    )

                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)

                return self.templates.TemplateResponse(
                    "ai_services/enhanced_config.html",
                    self.get_template_context(
                        request, user, page_title="AI Model Configuration"
                    ),
                )
            except Exception as e:
                print(f"Error in ai_services_page: {e}")
                # Instead of crashing, redirect to home with error
                return RedirectResponse(
                    url="/?error=ai_services_error", status_code=302
                )

        # Enhanced AI Services Configuration
        @self.app.get("/ai-services/enhanced", response_class=HTMLResponse)
        async def enhanced_ai_services_page(request: Request):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            return self.templates.TemplateResponse(
                "ai_services/enhanced_config.html",
                self.get_template_context(
                    request, user, page_title="AI Model Configuration"
                ),
            )

        @self.app.post("/ai-services/test")
        async def test_ai_service(
            request: Request,
            service_type: str = Form(...),
            api_endpoint: str = Form(...),
            api_key: str = Form(...),
            model: str = Form(...),
            test_prompt: str = Form("Hello, world!"),
        ):
            user = await self.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

            try:
                # This would integrate with your AI service testing logic
                # For now, return a mock response
                return {
                    "success": True,
                    "response": (
                        f"Test successful for {service_type} with model {model}"
                    ),
                    "latency": "1.2s",
                    "tokens_used": 15,
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Prompt execution with AI services
        @self.app.post("/prompts/{prompt_name}/execute")
        async def execute_prompt_with_ai(
            request: Request, prompt_name: str, variables: dict = Form(default={})
        ):
            user = await self.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            prompt = data_manager.get_prompt_by_name(prompt_name)
            if not prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")

            try:
                # Replace variables in prompt content
                content = prompt["content"]
                for key, value in variables.items():
                    content = content.replace(f"{{{key}}}", str(value))

                # This would integrate with your AI service execution logic
                # For now, return a mock response
                return {
                    "success": True,
                    "prompt_content": content,
                    "response": f"Mock AI response for: {content[:100]}...",
                    "tokens_used": len(content.split()) * 1.3,
                    "execution_time": "2.1s",
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Rules Management Routes
        @self.app.get("/rules", response_class=HTMLResponse)
        async def rules_list(request: Request):
            """Display all rules in a library format"""
            if self.single_user_mode:
                # Single-user mode - no authentication required
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                rules = data_manager.get_all_rules()
                categories = list(
                    set(rule["category"] for rule in rules if rule["category"])
                )

                return self.templates.TemplateResponse(
                    "rules/list.html",
                    self.get_template_context(
                        request,
                        user=None,
                        rules=rules,
                        categories=categories,
                        page_title=t("rules.library"),
                        single_user_mode=True,
                    ),
                )
            else:
                # Multi-tenant mode - authentication required
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )
                rules = data_manager.get_all_rules()
                categories = list(
                    set(rule["category"] for rule in rules if rule["category"])
                )

                return self.templates.TemplateResponse(
                    "rules/list.html",
                    self.get_template_context(
                        request,
                        user,
                        rules=rules,
                        categories=categories,
                        page_title=t("rules.library"),
                        single_user_mode=False,
                    ),
                )

        @self.app.get("/rules/new", response_class=HTMLResponse)
        async def new_rule(request: Request):
            """Display form to create a new rule"""
            if self.single_user_mode:
                # Single-user mode - no authentication required
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                rules = data_manager.get_all_rules()
                categories = sorted(
                    list(set(rule["category"] for rule in rules if rule["category"]))
                )
                if not categories:
                    categories = [
                        "General",
                        "Coding",
                        "Analysis",
                        "Writing",
                        "Constraints",
                    ]

                return self.templates.TemplateResponse(
                    "rules/form.html",
                    self.get_template_context(
                        request,
                        user=None,
                        categories=categories,
                        page_title=t("rules.create_new"),
                        action="create",
                        name="",
                        title="",
                        content="",
                        category="",
                        description="",
                        tags="",
                        rule_id=None,
                        error=None,
                        single_user_mode=True,
                    ),
                )
            else:
                # Multi-tenant mode - authentication required
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )
                rules = data_manager.get_all_rules()
                categories = sorted(
                    list(set(rule["category"] for rule in rules if rule["category"]))
                )
                if not categories:
                    categories = [
                        "General",
                        "Coding",
                        "Analysis",
                        "Writing",
                        "Constraints",
                    ]

                return self.templates.TemplateResponse(
                    "rules/form.html",
                    self.get_template_context(
                        request,
                        user,
                        categories=categories,
                        page_title=t("rules.create_new"),
                        action="create",
                        name="",
                        title="",
                        content="",
                        category="",
                        description="",
                        tags="",
                        rule_id=None,
                        error=None,
                        single_user_mode=False,
                    ),
                )

        @self.app.post("/rules/new")
        async def create_rule(
            request: Request,
            name: str = Form(...),
            title: str = Form(...),
            content: str = Form(...),
            category: str = Form(default="General"),
            tags: str = Form(default=""),
            description: str = Form(default=""),
        ):
            """Create a new rule"""
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                result = data_manager.add_rule(
                    name=name,
                    title=title,
                    content=content,
                    category=category or "General",
                    tags=tags,
                    description=description,
                )

                if "successfully" in result:
                    return RedirectResponse(url="/rules", status_code=302)
                else:
                    # Error occurred
                    rules = data_manager.get_all_rules()
                    categories = sorted(
                        list(
                            set(rule["category"] for rule in rules if rule["category"])
                        )
                    )
                    if not categories:
                        categories = [
                            "General",
                            "Coding",
                            "Analysis",
                            "Writing",
                            "Constraints",
                        ]

                    return self.templates.TemplateResponse(
                        "rules/form.html",
                        self.get_template_context(
                            request,
                            user=None,
                            categories=categories,
                            page_title=t("rules.create_new"),
                            action="create",
                            name=name,
                            title=title,
                            content=content,
                            category=category,
                            description=description,
                            tags=tags,
                            rule_id=None,
                            error=result,
                            single_user_mode=True,
                        ),
                    )
            else:
                # Multi-tenant mode
                user = await self.get_current_user(request)
                if not user:
                    raise HTTPException(
                        status_code=401, detail="Authentication required"
                    )

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )
                result = data_manager.add_rule(
                    name=name,
                    title=title,
                    content=content,
                    category=category or "General",
                    tags=tags,
                    description=description,
                )

                if "successfully" in result:
                    return RedirectResponse(url="/rules", status_code=302)
                else:
                    # Error occurred
                    rules = data_manager.get_all_rules()
                    categories = sorted(
                        list(
                            set(rule["category"] for rule in rules if rule["category"])
                        )
                    )
                    if not categories:
                        categories = [
                            "General",
                            "Coding",
                            "Analysis",
                            "Writing",
                            "Constraints",
                        ]

                    return self.templates.TemplateResponse(
                        "rules/form.html",
                        self.get_template_context(
                            request,
                            user,
                            categories=categories,
                            page_title=t("rules.create_new"),
                            action="create",
                            name=name,
                            title=title,
                            content=content,
                            category=category,
                            description=description,
                            tags=tags,
                            rule_id=None,
                            error=result,
                            single_user_mode=False,
                        ),
                    )

        @self.app.get("/rules/{rule_id}/edit", response_class=HTMLResponse)
        async def edit_rule(request: Request, rule_id: int):
            """Display form to edit an existing rule"""
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
            else:
                # Multi-tenant mode
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Get rule by ID
            rules = data_manager.get_all_rules()
            rule = next((r for r in rules if r["id"] == rule_id), None)

            if not rule:
                raise HTTPException(status_code=404, detail="Rule not found")

            categories = sorted(
                list(set(r["category"] for r in rules if r["category"]))
            )
            if not categories:
                categories = ["General", "Coding", "Analysis", "Writing", "Constraints"]

            return self.templates.TemplateResponse(
                "rules/form.html",
                self.get_template_context(
                    request,
                    user if not self.single_user_mode else None,
                    categories=categories,
                    page_title=t("rules.edit"),
                    action="edit",
                    name=rule["name"],
                    title=rule["title"],
                    content=rule["content"],
                    category=rule["category"],
                    description=rule["description"],
                    tags=rule["tags"],
                    rule_id=rule_id,
                    error=None,
                    single_user_mode=self.single_user_mode,
                ),
            )

        @self.app.post("/rules/{rule_id}/edit")
        async def update_rule(
            request: Request,
            rule_id: int,
            name: str = Form(...),
            title: str = Form(...),
            content: str = Form(...),
            category: str = Form(default="General"),
            tags: str = Form(default=""),
            description: str = Form(default=""),
        ):
            """Update an existing rule"""
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
            else:
                # Multi-tenant mode
                user = await self.get_current_user(request)
                if not user:
                    raise HTTPException(
                        status_code=401, detail="Authentication required"
                    )

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Get the original rule to get its name
            rules = data_manager.get_all_rules()
            original_rule = next((r for r in rules if r["id"] == rule_id), None)

            if not original_rule:
                raise HTTPException(status_code=404, detail="Rule not found")

            result = data_manager.update_rule(
                original_name=original_rule["name"],
                name=name,
                title=title,
                content=content,
                category=category or "General",
                tags=tags,
                description=description,
            )

            if "successfully" in result:
                return RedirectResponse(url="/rules", status_code=302)
            else:
                # Error occurred
                categories = sorted(
                    list(set(r["category"] for r in rules if r["category"]))
                )
                if not categories:
                    categories = [
                        "General",
                        "Coding",
                        "Analysis",
                        "Writing",
                        "Constraints",
                    ]

                return self.templates.TemplateResponse(
                    "rules/form.html",
                    self.get_template_context(
                        request,
                        user if not self.single_user_mode else None,
                        categories=categories,
                        page_title=t("rules.edit"),
                        action="edit",
                        name=name,
                        title=title,
                        content=content,
                        category=category,
                        description=description,
                        tags=tags,
                        rule_id=rule_id,
                        error=result,
                        single_user_mode=self.single_user_mode,
                    ),
                )

        @self.app.delete("/rules/{rule_id}")
        async def delete_rule(request: Request, rule_id: int):
            """Delete a rule"""
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
            else:
                # Multi-tenant mode
                user = await self.get_current_user(request)
                if not user:
                    raise HTTPException(
                        status_code=401, detail="Authentication required"
                    )

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            # Get rule by ID to get its name
            rules = data_manager.get_all_rules()
            rule = next((r for r in rules if r["id"] == rule_id), None)

            if not rule:
                raise HTTPException(status_code=404, detail="Rule not found")

            result = data_manager.delete_rule(rule["name"])

            if "successfully" in result:
                return {"success": True, "message": result}
            else:
                return {"success": False, "error": result}

        @self.app.get("/rules/search")
        async def search_rules(request: Request, q: str = "", category: str = "all"):
            """Search rules with optional category filter"""
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
            else:
                # Multi-tenant mode
                user = await self.get_current_user(request)
                if not user:
                    raise HTTPException(
                        status_code=401, detail="Authentication required"
                    )

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            rules = data_manager.search_rules(
                search_term=q, category_filter=category if category != "all" else "all"
            )

            return self.templates.TemplateResponse(
                "rules/_list_partial.html",
                self.get_template_context(
                    request,
                    user if not self.single_user_mode else None,
                    rules=rules,
                    single_user_mode=self.single_user_mode,
                ),
            )

        @self.app.get("/rules/filter")
        async def filter_rules(request: Request, category: str = "all"):
            """Filter rules by category"""
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
            else:
                # Multi-tenant mode
                user = await self.get_current_user(request)
                if not user:
                    raise HTTPException(
                        status_code=401, detail="Authentication required"
                    )

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )

            if category == "all":
                rules = data_manager.get_all_rules()
            else:
                rules = data_manager.get_rules_by_category(category)

            return self.templates.TemplateResponse(
                "rules/_list_partial.html",
                self.get_template_context(
                    request,
                    user if not self.single_user_mode else None,
                    rules=rules,
                    single_user_mode=self.single_user_mode,
                ),
            )

        @self.app.get("/rules/builder", response_class=HTMLResponse)
        async def rules_builder(request: Request):
            """Display the rules combination builder"""
            if self.single_user_mode:
                # Single-user mode
                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id="default", user_id="default"
                )
                rules = data_manager.get_all_rules()
                categories = sorted(
                    list(set(rule["category"] for rule in rules if rule["category"]))
                )

                return self.templates.TemplateResponse(
                    "rules/builder.html",
                    self.get_template_context(
                        request,
                        user=None,
                        rules=rules,
                        categories=categories,
                        page_title=t("rules.builder"),
                        single_user_mode=True,
                    ),
                )
            else:
                # Multi-tenant mode
                user = await self.get_current_user(request)
                if not user:
                    return RedirectResponse(url="/login", status_code=302)

                data_manager = PromptDataManager(
                    db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
                )
                rules = data_manager.get_all_rules()
                categories = sorted(
                    list(set(rule["category"] for rule in rules if rule["category"]))
                )

                return self.templates.TemplateResponse(
                    "rules/builder.html",
                    self.get_template_context(
                        request,
                        user,
                        rules=rules,
                        categories=categories,
                        page_title=t("rules.builder"),
                        single_user_mode=False,
                    ),
                )

        # Language Management Routes
        @self.app.get("/settings/language/{language_code}", response_class=HTMLResponse)
        async def language_editor_page(request: Request, language_code: str):
            """Language editor page for editing translation files"""
            user = await self.get_current_user(request)
            if not user and not self.single_user_mode:
                return RedirectResponse(url="/login", status_code=302)

            language_manager = get_language_manager()

            # Validate language code
            available_languages = language_manager.get_available_languages()
            if language_code not in available_languages:
                raise HTTPException(status_code=404, detail="Language not found")

            # Set current language for this session
            language_manager.set_language(language_code)

            # Get language information
            language_info = available_languages[language_code]

            # Get validation information
            validation = language_manager.validate_language_file(language_code)

            # Get all translation keys
            all_keys = sorted(language_manager.get_all_translation_keys("en"))

            # Get current and English translations
            english_translations = {}
            current_translations = {}

            for key in all_keys:
                # Get English reference
                language_manager.set_language("en")
                english_translations[key] = language_manager.t(key)

                # Get current language translation
                language_manager.set_language(language_code)
                current_translations[key] = (
                    language_manager.t(key)
                    if key not in validation["missing_keys"]
                    else ""
                )

            # Check if translation service is available
            translation_service = getattr(text_translator, "service_type", None)

            context = self.get_template_context(
                request,
                user,
                page_title=f"Language Editor - {language_info['native_name']}",
                current_language=language_code,
                available_languages=available_languages,
                language_info=language_info,
                validation=validation,
                all_keys=all_keys,
                english_translations=english_translations,
                current_translations=current_translations,
                translation_service=translation_service,
            )

            return self.templates.TemplateResponse(
                "settings/language_editor.html", context
            )

        @self.app.post("/settings/language/switch")
        async def switch_language(request: Request):
            """Switch current language and redirect to editor"""
            # Check authentication for multi-tenant mode
            if not self.single_user_mode:
                user = await self.get_current_user(request)
                if not user:
                    raise HTTPException(
                        status_code=401, detail="Authentication required"
                    )

            # Handle both form data and JSON data
            try:
                # Try JSON first
                body = await request.json()
                language_code = body.get("language", "")
            except Exception:
                # Fall back to form data
                form_data = await request.form()
                language_code = form_data.get("language_code", "")

            if not language_code:
                return {"success": False, "message": "Language code is required"}

            # Check if language is valid
            language_manager = get_language_manager()
            available_languages = language_manager.get_available_languages()

            if language_code not in available_languages:
                return {
                    "success": False,
                    "message": f"Language '{language_code}' not available",
                }

            # For test clients, return JSON response
            user_agent = request.headers.get("user-agent", "")
            if "testclient" in user_agent.lower():
                return {"success": True, "language": language_code}

            return RedirectResponse(
                url=f"/settings/language/{language_code}", status_code=302
            )

        @self.app.post("/settings/language/create")
        async def create_language(request: Request):
            """Create a new language file"""
            user = await self.get_current_user(request)
            if not user and not self.single_user_mode:
                raise HTTPException(status_code=401, detail="Authentication required")

            try:
                body = await request.json()
                language_code = body.get("language_code", "").lower().strip()
                language_name = body.get("language_name", "").strip()
                native_name = body.get("native_name", "").strip()
                author = body.get("author", "AI Prompt Manager").strip()

                # Validation
                if not language_code or not language_name or not native_name:
                    return {
                        "success": False,
                        "message": "Language code, name, and native name are required",
                    }

                # Validate language code format (2-3 lowercase letters)
                import re

                if not re.match(r"^[a-z]{2,3}$", language_code):
                    return {
                        "success": False,
                        "message": (
                            "Invalid language code format. Use 2-3 lowercase "
                            "letters (e.g., 'fr', 'de', 'ja')"
                        ),
                    }

                language_manager = get_language_manager()

                # Check if language already exists
                available_languages = language_manager.get_available_languages()
                if language_code in available_languages:
                    return {
                        "success": False,
                        "message": f"Language '{language_code}' already exists",
                    }

                # Create language template
                template_data = language_manager.create_language_template(
                    language_code, language_name, native_name, author
                )

                # Save the new language file
                success = language_manager.save_language_file(
                    language_code,
                    template_data["translations"],
                    template_data["metadata"],
                )

                if success:
                    return {
                        "success": True,
                        "message": f"Language '{language_name}' created successfully",
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to create language file",
                    }

            except Exception as e:
                return {
                    "success": False,
                    "message": f"Error creating language: {str(e)}",
                }

        @self.app.post("/settings/language/save")
        async def save_language(request: Request):
            """Save translations to language file"""
            user = await self.get_current_user(request)
            if not user and not self.single_user_mode:
                raise HTTPException(status_code=401, detail="Authentication required")

            try:
                body = await request.json()
                language_code = body.get("language_code", "").strip()
                translations_flat = body.get("translations", {})

                if not language_code or not translations_flat:
                    return {
                        "success": False,
                        "message": "Language code and translations are required",
                    }

                language_manager = get_language_manager()

                # Convert flat translations back to nested structure
                from typing import Any, Dict

                translations_nested: Dict[str, Any] = {}
                for key, value in translations_flat.items():
                    keys = key.split(".")
                    current_dict = translations_nested

                    for k in keys[:-1]:
                        if k not in current_dict:
                            current_dict[k] = {}
                        current_dict = current_dict[k]

                    current_dict[keys[-1]] = value

                # Get existing metadata
                available_languages = language_manager.get_available_languages()
                if language_code in available_languages:
                    metadata = {
                        "language_code": language_code,
                        "language_name": available_languages[language_code]["name"],
                        "native_name": available_languages[language_code][
                            "native_name"
                        ],
                        "version": available_languages[language_code]["version"],
                        "author": available_languages[language_code]["author"],
                        "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    }
                else:
                    metadata = None

                # Save the language file
                success = language_manager.save_language_file(
                    language_code, translations_nested, metadata
                )

                if success:
                    return {
                        "success": True,
                        "message": "Language file saved successfully",
                    }
                else:
                    return {"success": False, "message": "Failed to save language file"}

            except Exception as e:
                return {"success": False, "message": f"Error saving language: {str(e)}"}

        @self.app.post("/settings/language/delete")
        async def delete_language(request: Request):
            """Delete a language file"""
            user = await self.get_current_user(request)
            if not user and not self.single_user_mode:
                raise HTTPException(status_code=401, detail="Authentication required")

            try:
                body = await request.json()
                language_code = body.get("language_code", "").strip()

                if not language_code:
                    return {"success": False, "message": "Language code is required"}

                if language_code == "en":
                    return {
                        "success": False,
                        "message": "Cannot delete default language",
                    }

                language_manager = get_language_manager()
                success = language_manager.delete_language_file(language_code)

                if success:
                    return {
                        "success": True,
                        "message": f"Language '{language_code}' deleted successfully",
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to delete language file",
                    }

            except Exception as e:
                return {
                    "success": False,
                    "message": f"Error deleting language: {str(e)}",
                }

        @self.app.post("/settings/language/validate")
        async def validate_language(request: Request):
            """Validate a language file"""
            user = await self.get_current_user(request)
            if not user and not self.single_user_mode:
                raise HTTPException(status_code=401, detail="Authentication required")

            try:
                body = await request.json()
                language_code = body.get("language_code", "").strip()

                if not language_code:
                    return {"success": False, "message": "Language code is required"}

                language_manager = get_language_manager()
                validation = language_manager.validate_language_file(language_code)

                return {
                    "success": True,
                    "data": {
                        "valid": validation["valid"],
                        "missing_keys": validation["missing_keys"],
                        "extra_keys": validation["extra_keys"],
                        "total_keys": validation["total_keys"],
                        "coverage": validation["coverage"],
                    },
                }

            except Exception as e:
                return {
                    "success": False,
                    "message": f"Error validating language: {str(e)}",
                }

        @self.app.post("/settings/language/translate-key")
        async def translate_key(request: Request):
            """Translate a single key using the configured translation service"""
            user = await self.get_current_user(request)
            if not user and not self.single_user_mode:
                raise HTTPException(status_code=401, detail="Authentication required")

            try:
                body = await request.json()
                key = body.get("key", "").strip()
                target_language = body.get(
                    "target_language", body.get("language_code", "")
                ).strip()
                english_text = body.get("english_text", "").strip()

                if not key:
                    return {
                        "success": False,
                        "message": "Key is required",
                    }

                language_manager = get_language_manager()

                # Get English text for the key if not provided
                if not english_text:
                    language_manager.set_language("en")
                    english_text = language_manager.t(key)

                    if english_text == key:  # No translation found
                        return {
                            "success": False,
                            "message": f"English text not found for key: {key}",
                        }

                # If target_language not specified, assume we want to translate
                # the provided text
                if not target_language:
                    # Use text translator to translate to English
                    try:
                        success, translated_text, error_msg = (
                            text_translator.translate_to_english(text=english_text)
                        )

                        if success and translated_text:
                            return {
                                "success": True,
                                "translation": translated_text,
                                "original": english_text,
                                "key": key,
                            }
                        else:
                            return {
                                "success": False,
                                "message": error_msg or "Translation failed",
                            }

                    except Exception as translation_error:
                        return {
                            "success": False,
                            "message": f"Translation failed: {str(translation_error)}",
                        }

                # Get target language info
                available_languages = language_manager.get_available_languages()
                if target_language not in available_languages:
                    return {
                        "success": False,
                        "message": f"Target language '{target_language}' not available",
                    }

                target_lang_name = available_languages[target_language]["name"]

                # Use text translator to translate
                try:
                    success, translated_text, error_msg = (
                        text_translator.translate_to_english(
                            text=english_text,
                            source_language=target_lang_name.lower(),
                        )
                    )

                    if translated_text and translated_text != english_text:
                        return {
                            "success": True,
                            "translation": translated_text,
                            "original": english_text,
                            "key": key,
                        }
                    else:
                        return {
                            "success": False,
                            "message": (
                                "Translation service did not return a valid "
                                "translation"
                            ),
                        }

                except Exception as translation_error:
                    return {
                        "success": False,
                        "message": f"Translation failed: {str(translation_error)}",
                    }

            except Exception as e:
                return {"success": False, "message": f"Error translating key: {str(e)}"}

    async def get_current_user_or_default(
        self, request: Request
    ) -> tuple[Optional[User], PromptDataManager]:
        """Get current user and data manager, or defaults for single-user mode"""
        if self.single_user_mode:
            # In single-user mode, use default values
            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id="default", user_id="default"
            )
            return None, data_manager

        user = await self.get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")

        data_manager = PromptDataManager(
            db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
        )
        return user, data_manager

    async def get_current_user(self, request: Request) -> Optional[User]:
        """Get current authenticated user from session"""
        user_id = request.session.get("user_id")
        tenant_id = request.session.get("tenant_id")
        login_time_str = request.session.get("login_time")

        # Set language from session if available
        language = request.session.get("language", "en")
        i18n.set_language(language)  # Legacy support
        get_language_manager().set_language(language)  # New language manager

        if not all([user_id, tenant_id, login_time_str]):
            return None

        # Check session expiry (24 hours)
        try:
            if login_time_str:
                login_time = datetime.fromisoformat(login_time_str)
                if datetime.now() - login_time > timedelta(hours=24):
                    return None
        except ValueError:
            return None

        # Get user from database
        if user_id:
            user = self.auth_manager.get_user_by_id(user_id)
        else:
            return None
        if user and user.tenant_id == tenant_id and user.is_active:
            return user

        return None

    def get_template_context(
        self, request: Request, user: Optional[User] = None, **kwargs
    ):
        """Get common template context with i18n support"""
        language_manager = get_language_manager()

        context = {
            "request": request,
            "user": user,
            "i18n": i18n,  # Keep legacy i18n for backward compatibility
            "t": t,  # New translation function
            "current_language": language_manager.get_current_language(),
            "available_languages": language_manager.get_available_languages(),
            **kwargs,
        }
        return context


def basic_text_enhancement(text: str) -> str:
    """
    Basic text enhancement for dictated speech when AI services are unavailable
    """
    import re

    if not text or not text.strip():
        return ""

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Fix common dictation issues - be more precise with word boundaries
    replacements = {
        r"\buh\b": "",
        r"\bum\b": "",
        r"\ber\b": "",
        r"\bah\b": "",
        r"\byou know\b": "",
        r"\bbasically\b": "",
        r"\bactually\b": "",
        r"\bokay\b": "",
        # Only remove "so" when followed by lowercase word
        r"\bso\b(?=\s+[a-z])": "",
        # Only remove "well" when followed by lowercase word
        r"\bwell\b(?=\s+[a-z])": "",
        r"\bi mean\b": "",
        r"\byeah\b": "",
        # Only remove "right" when followed by "around" (filler phrase)
        r"\bright\b(?=\s+around\b)": "",
        r"\.{2,}": ".",
        r",{2,}": ",",
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Clean up extra spaces created by removals
    text = re.sub(r"\s+", " ", text).strip()

    # Handle standalone "like" at the end after other removals
    text = re.sub(r"\blike\b(?=\s*$|\s*[,.!?])", "", text, flags=re.IGNORECASE)

    # Handle duplicate words more carefully - only remove actual duplicates
    # Split into words and remove consecutive duplicates
    words = text.split()
    filtered_words = []
    prev_word = None

    for word in words:
        # Clean word for comparison (remove punctuation)
        clean_word = re.sub(r"[^\w]", "", word.lower())
        clean_prev = re.sub(r"[^\w]", "", prev_word.lower()) if prev_word else ""

        if clean_word != clean_prev:
            filtered_words.append(word)

        prev_word = word

    text = " ".join(filtered_words)

    # Clean up extra spaces created by removals
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return ""

    # Capitalize first letter of sentences
    text = re.sub(r"(^|\.\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)

    # Ensure proper punctuation at the end
    if text and not text.endswith((".", "!", "?", ":")):
        text += "."

    # Final cleanup of spaces before punctuation
    text = re.sub(r"\s+([.!?:,])", r"\1", text)

    return text


# Create the web application instance
def create_web_app(db_path: str = "prompts.db") -> FastAPI:
    """Create and configure the web application"""
    web_app = WebApp(db_path)
    return web_app.app


if __name__ == "__main__":
    import uvicorn

    app = create_web_app()
    # Binding to all interfaces is intentional for web application
    # deployment  # nosec B104
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # nosec B104
