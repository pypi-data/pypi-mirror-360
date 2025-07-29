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
from langwatch_optimizer import langwatch_optimizer
from prompt_data_manager import PromptDataManager
from text_translator import text_translator

# Import enhanced AI services API
try:
    from api_endpoints_enhanced import get_ai_models_router

    AI_MODELS_API_AVAILABLE = True
except ImportError:
    AI_MODELS_API_AVAILABLE = False
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
                    {
                        "request": request,
                        "user": None,
                        "prompts": prompts,
                        "page_title": "Dashboard",
                        "single_user_mode": True,
                        "i18n": i18n,
                        "current_language": i18n.current_language,
                        "available_languages": i18n.get_available_languages(),
                    },
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
                    request, user, prompts=prompts, page_title="Dashboard"
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

            prompts = data_manager.get_all_prompts()
            categories = data_manager.get_categories()

            return self.templates.TemplateResponse(
                "prompts/list.html",
                self.get_template_context(
                    request,
                    user,
                    prompts=prompts,
                    categories=categories,
                    page_title=i18n.t("nav.prompts"),
                    single_user_mode=self.single_user_mode,
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
                    {
                        "request": request,
                        "user": None,
                        "categories": categories
                        or [],  # Ensure categories is never None
                        "page_title": i18n.t("prompt.create_new"),
                        "action": "create",
                        "name": "",
                        "content": "",
                        "category": "",
                        "description": "",
                        "tags": "",
                        "prompt_id": None,
                        "error": None,  # Explicitly set error to None
                        "single_user_mode": True,
                        "i18n": i18n,
                        "current_language": i18n.current_language,
                        "available_languages": i18n.get_available_languages(),
                    },
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
                {
                    "request": request,
                    "user": user,
                    "categories": categories or [],  # Ensure categories is never None
                    "page_title": i18n.t("prompt.create_new"),
                    "action": "create",
                    "name": "",
                    "content": "",
                    "category": "",
                    "description": "",
                    "tags": "",
                    "prompt_id": None,
                    "error": None,  # Explicitly set error to None
                    "i18n": i18n,
                    "available_languages": i18n.get_available_languages(),
                    "current_language": i18n.current_language,
                    "single_user_mode": self.single_user_mode,
                },
            )

        @self.app.post("/prompts/new")
        async def create_prompt(
            request: Request,
            name: str = Form(...),
            content: str = Form(...),
            category: str = Form(...),
            description: str = Form(default=""),
            tags: str = Form(default=""),
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

            result = data_manager.add_prompt(
                name=name,
                title=name,  # Using name as title
                content=content,
                category=category,
                tags=", ".join(tag_list),  # Convert list to string
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
                        page_title=i18n.t("prompt.create_new"),
                        action="create",
                        name=name,
                        content=content,
                        category=category,
                        description=description,
                        tags=tags,
                        single_user_mode=self.single_user_mode,
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
                {
                    "request": request,
                    "user": user,
                    "categories": categories,
                    "page_title": i18n.t("prompt.edit"),
                    "action": "edit",
                    "prompt_id": prompt_id,
                    "name": prompt.get("name", ""),
                    "content": prompt.get("content", ""),
                    "category": prompt.get("category", ""),
                    "description": prompt.get("description", ""),
                    "tags": prompt.get("tags", ""),
                    "i18n": i18n,
                    "available_languages": i18n.get_available_languages(),
                    "current_language": i18n.current_language,
                    "single_user_mode": self.single_user_mode,
                },
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

            result = data_manager.update_prompt(
                original_name=original_prompt["name"],
                new_name=name,
                title=name,  # Using name as title
                content=content,
                category=category,
                tags=tags,
            )

            if not result.startswith("Error:"):
                return RedirectResponse(url="/prompts", status_code=302)
            else:
                categories = data_manager.get_categories()
                return self.templates.TemplateResponse(
                    "prompts/form.html",
                    {
                        "request": request,
                        "user": user,
                        "categories": categories,
                        "error": result,
                        "page_title": i18n.t("prompt.edit"),
                        "action": "edit",
                        "prompt_id": prompt_id,
                        "name": name,
                        "content": content,
                        "category": category,
                        "description": description,
                        "tags": tags,
                        "i18n": i18n,
                        "available_languages": i18n.get_available_languages(),
                        "current_language": i18n.current_language,
                        "single_user_mode": self.single_user_mode,
                    },
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
                prompts = data_manager.get_all_prompts()
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
                    },
                )
            else:
                raise HTTPException(status_code=404, detail="Prompt not found")

        @self.app.get("/prompts/search")
        async def search_prompts(request: Request, q: str = ""):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            # Simple search implementation
            all_prompts = data_manager.get_all_prompts()
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
                ),
            )

        @self.app.get("/prompts/filter")
        async def filter_prompts(
            request: Request, category: str = "", sort: str = "created_desc"
        ):
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            data_manager = PromptDataManager(
                db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
            )

            # Get and filter prompts
            prompts = data_manager.get_all_prompts()

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
                ),
            )

        # Language switching route
        @self.app.post("/language")
        async def change_language(request: Request, language: str = Form(...)):
            """Change the interface language"""
            if i18n.set_language(language):
                request.session["language"] = language
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
            user = await self.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

            success, translated_text, error = text_translator.translate_to_english(text)

            return {
                "success": success,
                "translated_text": translated_text,
                "error": error,
                "original_text": text,
            }

        # Optimization route
        @self.app.post("/optimize")
        async def optimize_prompt(request: Request, prompt: str = Form(...)):
            """Optimize a prompt using available optimization services"""
            user = await self.get_current_user(request)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")

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
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            # Check if user is admin
            if user.role != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")

            # Get admin statistics
            stats = self.auth_manager.get_admin_stats()
            users = self.auth_manager.get_all_users_for_tenant(user.tenant_id)
            tenants = (
                self.auth_manager.get_all_tenants()
                if user.role == "admin"
                else [self.auth_manager.get_tenant_by_id(user.tenant_id)]
            )

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
                    {
                        "request": request,
                        "user": None,
                        "prompts": prompts,
                        "categories": categories,
                        "page_title": i18n.t("builder.title"),
                        "single_user_mode": True,
                        "i18n": i18n,
                        "current_language": i18n.current_language,
                        "available_languages": i18n.get_available_languages(),
                    },
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
                    page_title=i18n.t("builder.title"),
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
                    {
                        "request": request,
                        "user": None,
                        "templates": templates,
                        "categories": categories,
                        "page_title": "Templates",
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
                # In single-user mode, redirect to main page or show simplified settings
                return RedirectResponse(url="/", status_code=302)

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
                # In single-user mode, there's no user profile concept
                return RedirectResponse(url="/", status_code=302)

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
                # In single-user mode, API tokens are not user-specific
                return RedirectResponse(url="/", status_code=302)

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
                expiry_date = (
                    datetime.now() + timedelta(days=expires_days)
                    if expires_days > 0
                    else None
                )
                token_info = self.api_token_manager.create_token(
                    user_id=user.id,
                    tenant_id=user.tenant_id,
                    name=name,
                    expires_at=expiry_date,
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
            user = await self.get_current_user(request)
            if not user:
                return RedirectResponse(url="/login", status_code=302)

            return self.templates.TemplateResponse(
                "ai_services/config.html",
                self.get_template_context(request, user, page_title="AI Services"),
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
        i18n.set_language(language)

        if not all([user_id, tenant_id, login_time_str]):
            return None

        # Check session expiry (24 hours)
        try:
            login_time = datetime.fromisoformat(login_time_str)
            if datetime.now() - login_time > timedelta(hours=24):
                return None
        except ValueError:
            return None

        # Get user from database
        user = self.auth_manager.get_user_by_id(user_id)
        if user and user.tenant_id == tenant_id and user.is_active:
            return user

        return None

    def get_template_context(
        self, request: Request, user: Optional[User] = None, **kwargs
    ):
        """Get common template context with i18n support"""
        context = {
            "request": request,
            "user": user,
            "i18n": i18n,
            "current_language": i18n.current_language,
            "available_languages": i18n.get_available_languages(),
            **kwargs,
        }
        return context


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
