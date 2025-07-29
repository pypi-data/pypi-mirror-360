"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

AI Prompt Manager - Unified version supporting both single-user and multi-tenant modes.
Features: Authentication, SSO/ADFS support, admin interface, API endpoints, and standalone mode.

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import gradio as gr
import requests

from api_token_manager import APITokenManager
from auth_manager import AuthManager, Tenant, User
from i18n import i18n, t
from langwatch_optimizer import langwatch_optimizer
from prompt_builder import prompt_builder
from prompt_data_manager import PromptDataManager
from text_translator import text_translator
from token_calculator import token_calculator
from ui_components import ModernTheme, ResponsiveCSS, UIComponents


class AIPromptManager:
    def __init__(self, db_path: str = "prompts.db"):
        self.db_path = db_path
        self.auth_manager = AuthManager(db_path)
        self.api_token_manager = APITokenManager(db_path)
        self.current_user: Optional[User] = None
        self.current_tenant: Optional[Tenant] = None

        # Initialize data manager without tenant context initially
        self.data: Optional[PromptDataManager] = None

    def get_data_manager(self) -> Optional[PromptDataManager]:
        """Get tenant-aware data manager"""
        if self.current_user:
            if not self.data or self.data.tenant_id != self.current_user.tenant_id:
                self.data = PromptDataManager(
                    db_path=self.db_path,
                    tenant_id=self.current_user.tenant_id,
                    user_id=self.current_user.id,
                )
            return self.data
        return None

    def set_current_user(self, user: User):
        """Set current user and initialize tenant-aware data manager"""
        self.current_user = user
        self.data = PromptDataManager(
            db_path=self.db_path, tenant_id=user.tenant_id, user_id=user.id
        )

        # Load configurations
        self.config = self.load_config()
        self.enhancement_config = self.load_enhancement_config()
        self.test_config = self.load_test_config()

    def clear_current_user(self):
        """Clear current user session"""
        self.current_user = None
        self.data = None
        self.config = {}
        self.enhancement_config = {}
        self.test_config = {}

    def login(
        self, email: str, password: str, subdomain: str = "localhost"
    ) -> Tuple[bool, str, Optional[str]]:
        """Authenticate user and return success, message, and session token"""
        success, user, message = self.auth_manager.authenticate_user(
            email, password, subdomain
        )

        if success and user:
            self.set_current_user(user)
            token = self.auth_manager.create_session(user.id)
            return True, f"Welcome, {user.first_name}!", token
        else:
            return False, message, None

    def validate_session(self, token: str) -> bool:
        """Validate session token and set current user"""
        if not token:
            return False

        success, user = self.auth_manager.validate_session(token)
        if success and user:
            self.set_current_user(user)
            return True
        else:
            self.clear_current_user()
            return False

    def logout(self, token: str) -> bool:
        """Logout user"""
        if token:
            self.auth_manager.logout_user(token)
        self.clear_current_user()
        return True

    def save_config(
        self, service_type: str, api_endpoint: str, api_key: str, model_name: str
    ) -> str:
        """Save AI service configuration"""
        if not self.current_user:
            return "Error: User not authenticated!"

        config: Dict[str, object] = {
            "service_type": service_type,
            "api_endpoint": api_endpoint,
            "api_key": api_key,
            "model_name": model_name,
        }

        data_manager = self.get_data_manager()
        if data_manager and data_manager.save_config("ai_service", json.dumps(config)):
            self.config = config
            return "Configuration saved successfully!"
        return "Error saving configuration!"

    def save_enhancement_config(
        self,
        service_type: str,
        api_endpoint: str,
        api_key: str,
        model_name: str,
        enhancement_prompt_name: Optional[str] = None,
    ) -> str:
        """Save enhancement service configuration"""
        if not self.current_user:
            return "Error: User not authenticated!"

        config: Dict[str, object] = {
            "service_type": service_type,
            "api_endpoint": api_endpoint,
            "api_key": api_key,
            "model_name": model_name,
            "enhancement_prompt_name": enhancement_prompt_name,
        }

        data_manager = self.get_data_manager()
        if data_manager and data_manager.save_config(
            "enhancement_service", json.dumps(config)
        ):
            self.enhancement_config = config
            return "Enhancement configuration saved successfully!"
        return "Error saving enhancement configuration!"

    def load_config(self) -> Dict[str, object]:
        """Load AI service configuration"""
        if not self.current_user:
            return self._get_default_config()

        data_manager = self.get_data_manager()
        if data_manager:
            config_str = data_manager.get_config("ai_service")
            if config_str:
                try:
                    loaded_config = json.loads(config_str)
                    return (
                        dict(loaded_config)
                        if isinstance(loaded_config, dict)
                        else self._get_default_config()
                    )
                except json.JSONDecodeError:
                    pass

        return self._get_default_config()

    def load_enhancement_config(self) -> Dict[str, object]:
        """Load enhancement service configuration"""
        if not self.current_user:
            return self._get_default_enhancement_config()

        data_manager = self.get_data_manager()
        if data_manager:
            config_str = data_manager.get_config("enhancement_service")
            if config_str:
                try:
                    loaded_config = json.loads(config_str)
                    return (
                        dict(loaded_config)
                        if isinstance(loaded_config, dict)
                        else self._get_default_enhancement_config()
                    )
                except json.JSONDecodeError:
                    pass

        return self._get_default_enhancement_config()

    def _get_default_config(self) -> Dict[str, object]:
        return {
            "service_type": "openai",
            "api_endpoint": "http://localhost:1234/v1",
            "api_key": "",
            "model_name": "gpt-3.5-turbo",
        }

    def _get_default_enhancement_config(self) -> Dict[str, object]:
        return {
            "service_type": "openai",
            "api_endpoint": "http://localhost:1234/v1",
            "api_key": "",
            "model_name": "gpt-4",
            "enhancement_prompt_name": None,
        }

    def save_test_config(
        self, service_type: str, api_endpoint: str, api_key: str, model_name: str
    ) -> str:
        """Save test service configuration"""
        if not self.current_user:
            return "Error: User not authenticated!"

        config: Dict[str, object] = {
            "service_type": service_type,
            "api_endpoint": api_endpoint,
            "api_key": api_key,
            "model_name": model_name,
        }

        data_manager = self.get_data_manager()
        if data_manager and data_manager.save_config(
            "test_service", json.dumps(config)
        ):
            self.test_config = config
            return "Test configuration saved successfully!"
        return "Error saving test configuration!"

    def load_test_config(self) -> Dict[str, object]:
        """Load test service configuration"""
        if not self.current_user:
            return self._get_default_test_config()

        data_manager = self.get_data_manager()
        if data_manager:
            config_str = data_manager.get_config("test_service")
            if config_str:
                try:
                    loaded_config = json.loads(config_str)
                    return (
                        dict(loaded_config)
                        if isinstance(loaded_config, dict)
                        else self._get_default_test_config()
                    )
                except json.JSONDecodeError:
                    pass

        return self._get_default_test_config()

    def _get_default_test_config(self) -> Dict[str, object]:
        return {
            "service_type": "openai",
            "api_endpoint": "http://localhost:1234/v1",
            "api_key": "",
            "model_name": "gpt-3.5-turbo",
        }

    def format_prompts_for_display(self, prompts: List[Dict]) -> str:
        """Format prompts for tree view display"""
        if not prompts:
            return "No prompts found."

        # Separate enhancement prompts from regular prompts
        regular_prompts = [
            p for p in prompts if not p.get("is_enhancement_prompt", False)
        ]
        enhancement_prompts = [
            p for p in prompts if p.get("is_enhancement_prompt", False)
        ]

        output: List[str] = []

        # Display enhancement prompts first if any
        if enhancement_prompts:
            output.append("🔧 **Enhancement Prompts**")
            for prompt in sorted(enhancement_prompts, key=lambda x: str(x["name"])):
                content = str(prompt["content"])
                preview = content[:100] + "..." if len(content) > 100 else content
                tags_str = f" 🏷️ {prompt['tags']}" if prompt.get("tags") else ""
                user_id = prompt.get("user_id")
                created_by = f" 👤 {str(user_id)[:8]}..." if user_id else ""
                output.append(
                    f"  └── ⚡ **{str(prompt['name'])}** - {str(prompt['title'])}{tags_str}{created_by}"
                )
                output.append(f"      {preview}")
                output.append("")

        # Group regular prompts by category
        categories: Dict[str, List[Dict]] = {}
        for prompt in regular_prompts:
            category = str(prompt["category"])
            if category not in categories:
                categories[category] = []
            categories[category].append(prompt)

        # Format regular prompts as tree view
        for category, category_prompts in sorted(categories.items()):
            output.append(f"📁 **{category}** ({len(category_prompts)} prompts)")
            for prompt in sorted(category_prompts, key=lambda x: str(x["name"])):
                content = str(prompt["content"])
                preview = content[:100] + "..." if len(content) > 100 else content
                tags_str = f" 🏷️ {prompt['tags']}" if prompt.get("tags") else ""
                user_id = prompt.get("user_id")
                created_by = f" 👤 {str(user_id)[:8]}..." if user_id else ""
                output.append(
                    f"  └── 📄 **{str(prompt['name'])}** - {str(prompt['title'])}{tags_str}{created_by}"
                )
                output.append(f"      {preview}")
                output.append("")

        return "\n".join(output)

    def call_ai_service(self, prompt_text: str, config: Dict[str, object]) -> str:
        """Call AI service with given configuration"""
        try:
            service_type = config["service_type"]
            api_endpoint = config["api_endpoint"]
            api_key = config["api_key"]
            model_name = config["model_name"]

            headers = {"Content-Type": "application/json"}

            if service_type == "ollama":
                # Ollama API format
                endpoint = f"{str(api_endpoint).rstrip('/')}/generate"
                payload = {"model": model_name, "prompt": prompt_text, "stream": False}
            elif service_type == "llamacpp":
                # Llama.cpp server format
                endpoint = f"{str(api_endpoint).rstrip('/')}/completion"
                payload = {
                    "prompt": prompt_text,
                    "n_predict": 1024,
                    "temperature": 0.7,
                    "stop": ["</s>", "Human:", "Assistant:"],
                }
            else:
                # OpenAI compatible format (including LMStudio)
                endpoint = f"{str(api_endpoint).rstrip('/')}/chat/completions"
                payload = {
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt_text}],
                    "temperature": 0.7,
                    "max_tokens": 1500,
                }
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"

            response = requests.post(
                endpoint, json=payload, headers=headers, timeout=120
            )
            response.raise_for_status()

            result = response.json()

            # Extract response based on service type
            if service_type == "ollama":
                return str(result.get("response", "No response received"))
            elif service_type == "llamacpp":
                return str(result.get("content", "No response received"))
            else:
                # OpenAI compatible
                if "choices" in result and len(result["choices"]) > 0:
                    return str(result["choices"][0]["message"]["content"])
                else:
                    return "No response received"

        except requests.exceptions.RequestException as e:
            return f"Error connecting to AI service: {str(e)}"
        except json.JSONDecodeError as e:
            return f"Error decoding response from AI service: {str(e)}"
        except KeyError as e:
            return f"Error parsing AI service response: missing key {str(e)}"

    def execute_prompt(self, prompt_text: str) -> str:
        """Execute a prompt against the configured AI service"""
        if not self.current_user:
            return "Error: User not authenticated!"

        if not prompt_text.strip():
            return "Error: No prompt provided!"

        if not self.config.get("api_endpoint") or not self.config.get("model_name"):
            return (
                "Error: AI service not configured! Please configure the service first."
            )

        return self.call_ai_service(prompt_text, self.config)

    def enhance_prompt(
        self, original_prompt: str, enhancement_prompt_name: Optional[str] = None
    ) -> str:
        """Enhance a prompt using the enhancement service and prompt"""
        if not self.current_user:
            return "Error: User not authenticated!"

        if not original_prompt.strip():
            return "Error: No original prompt provided!"

        if not self.enhancement_config.get(
            "api_endpoint"
        ) or not self.enhancement_config.get("model_name"):
            return "Error: Enhancement service not configured! Please configure the enhancement service first."

        data_manager = self.get_data_manager()
        if not data_manager:
            return "Error: Data manager not available!"

        # Get enhancement prompt
        if enhancement_prompt_name:
            enhancement_prompt_data = data_manager.get_prompt_by_name(
                enhancement_prompt_name
            )
            if not enhancement_prompt_data:
                return (
                    f"Error: Enhancement prompt '{enhancement_prompt_name}' not found!"
                )
            enhancement_template = enhancement_prompt_data["content"]
        else:
            # Default enhancement prompt
            enhancement_template = """You are an expert prompt engineer. Your task is to enhance and improve the given prompt to make it more effective, clear, and likely to produce better results from AI models.

Please improve the following prompt by:
1. Making it more specific and clear
2. Adding context where helpful
3. Improving the structure and flow
4. Adding relevant constraints or guidelines
5. Making it more engaging and effective

Original prompt:
{original_prompt}

Please provide only the enhanced prompt as your response, without any explanations or additional text.
"""

        # Replace placeholder with original prompt
        full_enhancement_prompt = enhancement_template.replace(
            "{original_prompt}", original_prompt
        )

        return self.call_ai_service(full_enhancement_prompt, self.enhancement_config)

    # Admin functions
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return bool(self.current_user and self.current_user.role == "admin")

    def create_tenant(
        self, name: str, subdomain: str, max_users: int
    ) -> Tuple[bool, str]:
        """Create new tenant (admin only)"""
        if not self.is_admin():
            return False, "Access denied: Admin privileges required"

        return self.auth_manager.create_tenant(name, subdomain, max_users)

    def create_user(
        self,
        tenant_id: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str,
    ) -> Tuple[bool, str]:
        """Create new user (admin only)"""
        if not self.is_admin():
            return False, "Access denied: Admin privileges required"

        return self.auth_manager.create_user(
            tenant_id, email, password, first_name, last_name, role
        )

    def get_all_tenants(self) -> List[Tenant]:
        """Get all tenants (admin only)"""
        if not self.is_admin():
            return []

        return self.auth_manager.get_all_tenants()

    def get_tenant_users(self, tenant_id: str) -> List[User]:
        """Get users for a tenant (admin only)"""
        if not self.is_admin():
            return []

        return self.auth_manager.get_tenant_users(tenant_id)

    # API Token management functions
    def create_api_token(
        self, name: str, expires_days: Optional[int] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """Create API token for current user"""
        if not self.current_user:
            return False, "User not authenticated", None

        return self.api_token_manager.create_api_token(
            self.current_user.id, self.current_user.tenant_id, name, expires_days
        )

    def get_user_api_tokens(self) -> List:
        """Get all API tokens for current user"""
        if not self.current_user:
            return []

        return self.api_token_manager.get_user_tokens(self.current_user.id)

    def revoke_api_token(self, token_id: str) -> Tuple[bool, str]:
        """Revoke API token"""
        if not self.current_user:
            return False, "User not authenticated"

        return self.api_token_manager.revoke_token(self.current_user.id, token_id)

    def revoke_all_api_tokens(self) -> Tuple[bool, str]:
        """Revoke all API tokens for current user"""
        if not self.current_user:
            return False, "User not authenticated"

        return self.api_token_manager.revoke_all_tokens(self.current_user.id)

    def get_api_token_stats(self) -> Dict[str, object]:
        """Get API token statistics for current user"""
        if not self.current_user:
            return {}

        return self.api_token_manager.get_token_stats(self.current_user.id)

    # LangWatch optimization functions
    def optimize_prompt_with_langwatch(
        self,
        prompt_text: str,
        context: Optional[str] = None,
        target_model: str = "gpt-4",
    ) -> Tuple[bool, str, Dict[str, object]]:
        """Optimize prompt using LangWatch"""
        if not self.current_user:
            return False, "Error: User not authenticated!", {}

        if not prompt_text.strip():
            return False, "Error: No prompt provided for optimization!", {}

        try:
            result = langwatch_optimizer.optimize_prompt(
                original_prompt=prompt_text, context=context, target_model=target_model
            )

            if result.success:
                optimization_data = {
                    "optimized_prompt": result.optimized_prompt,
                    "original_prompt": result.original_prompt,
                    "score": result.optimization_score,
                    "suggestions": result.suggestions,
                    "reasoning": result.reasoning,
                    "timestamp": result.timestamp.isoformat(),
                }
                return True, "Prompt optimized successfully!", optimization_data
            else:
                return False, f"Optimization failed: {result.error_message}", {}

        except Exception as e:
            return False, f"Error during optimization: {str(e)}", {}

    def get_langwatch_status(self) -> Dict[str, object]:
        """Get LangWatch optimization service status"""
        return langwatch_optimizer.get_status()


# Initialize the prompt manager
prompt_manager = AIPromptManager()

# Handle single-user mode
if os.getenv("MULTITENANT_MODE", "true").lower() == "false":
    # Create a default user for single-user mode
    default_user = User(
        id="single-user-1",
        tenant_id="single-tenant",
        email="user@local",
        first_name="User",
        last_name="Local",
        role="admin",
        is_active=True,
        created_at=datetime.now(),
    )
    prompt_manager.set_current_user(default_user)

# Session state management
session_store: Dict[str, object] = {}


def get_session_token(request: gr.Request) -> Optional[str]:
    """Extract session token from request"""
    if hasattr(request, "headers") and "authorization" in request.headers:
        auth_header = request.headers["authorization"]
        if auth_header.startswith("Bearer "):
            return str(auth_header[7:])

    # Fallback to cookies or query params
    if hasattr(request, "query_params") and "token" in request.query_params:
        return str(request.query_params["token"])

    return None


def check_authentication(request: gr.Request) -> Tuple[bool, str]:
    """Check if user is authenticated and handle language parameter"""
    # Check for language parameter in URL
    if hasattr(request, "query_params") and "lang" in request.query_params:
        lang_param = request.query_params["lang"].lower()
        if lang_param in ["en", "es", "fr", "de", "zh", "ja", "pt", "ru", "ar", "hi"]:
            i18n.set_language(lang_param)

    token = get_session_token(request)
    if token and prompt_manager.validate_session(token):
        if prompt_manager.current_user:
            user_info = f"{prompt_manager.current_user.first_name} {prompt_manager.current_user.last_name} ({prompt_manager.current_user.email})"
            role_badge = "🛡️ Admin" if prompt_manager.is_admin() else "👤 User"
            return True, f"✅ {role_badge} | {user_info}"
        else:
            return False, "❌ Not authenticated"
    else:
        prompt_manager.clear_current_user()
        return False, "❌ Not authenticated"


# Authentication functions
def login_user(email, password, subdomain):
    """Login user"""
    success, message, token = prompt_manager.login(email, password, subdomain)
    if success:
        return (
            gr.update(visible=False),  # Hide login
            gr.update(visible=True),  # Show main app
            gr.update(visible=prompt_manager.is_admin()),  # Show admin if admin
            message,
            f"✅ {'🛡️ Admin' if prompt_manager.is_admin() else '👤 User'} | {prompt_manager.current_user.first_name if prompt_manager.current_user else ''} {prompt_manager.current_user.last_name if prompt_manager.current_user else ''}",
            token,
        )
    else:
        return (
            gr.update(visible=True),  # Keep login visible
            gr.update(visible=False),  # Hide main app
            gr.update(visible=False),  # Hide admin
            message,
            "❌ Not authenticated",
            "",
        )


def logout_user(token):
    """Logout user"""
    prompt_manager.logout(token)
    return (
        gr.update(visible=True),  # Show login
        gr.update(visible=False),  # Hide main app
        gr.update(visible=False),  # Hide admin
        "Logged out successfully",
        "❌ Not authenticated",
        "",
    )


def handle_sso_login(subdomain):
    """Handle SSO login"""
    login_url = prompt_manager.auth_manager.get_sso_login_url(subdomain)
    if login_url:
        return f"Please visit: {login_url}"
    else:
        return "SSO not configured"


# Prompt management functions
def add_new_prompt(name, title, content, category, tags, is_enhancement_prompt):
    """Add new prompt"""
    if not prompt_manager.current_user:
        return "Error: User not authenticated!", "", "", "", "", "", False

    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return "Error: Data manager not available!", "", "", "", "", "", False

    result = data_manager.add_prompt(
        name, title, content, category, tags, is_enhancement_prompt
    )

    # Refresh the prompts display
    prompts = data_manager.get_all_prompts()
    tree_view = prompt_manager.format_prompts_for_display(prompts)
    categories = ["All"] + data_manager.get_categories()

    # Update enhancement prompts dropdown
    enhancement_prompts = data_manager.get_enhancement_prompts()
    enhancement_choices = [
        (f"{p['name']} - {p['title']}", p["name"]) for p in enhancement_prompts
    ]

    return (
        result,
        tree_view,
        gr.update(choices=categories),
        gr.update(choices=enhancement_choices),
        "",
        "",
        "",
        "",
        "",
        False,
    )


def refresh_prompts_display(search_term="", category_filter="All"):
    """Refresh prompts display"""
    if not prompt_manager.current_user:
        return "No prompts found - not authenticated."

    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return "Data manager not available."

    if search_term:
        prompts = data_manager.search_prompts(search_term)
    else:
        prompts = data_manager.get_prompts_by_category(
            category_filter if category_filter != "All" else None
        )

    return prompt_manager.format_prompts_for_display(prompts)


def load_prompt_for_editing(prompt_name):
    """Load prompt for editing"""
    if not prompt_manager.current_user:
        return "", "", "", "", "", False, "Error: User not authenticated!"

    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return "", "", "", "", "", False, "Error: Data manager not available!"

    if not prompt_name.strip():
        return "", "", "", "", "", False, "Please enter a prompt name!"

    prompt = data_manager.get_prompt_by_name(prompt_name.strip())
    if prompt:
        return (
            prompt["name"],
            prompt["title"],
            prompt["content"],
            prompt["category"],
            prompt["tags"] or "",
            prompt.get("is_enhancement_prompt", False),
            f"Loaded prompt '{prompt['name']}' for editing",
        )
    else:
        return "", "", "", "", "", False, f"Prompt '{prompt_name}' not found!"


def update_existing_prompt(
    original_name, new_name, title, content, category, tags, is_enhancement_prompt
):
    """Update existing prompt"""
    if not prompt_manager.current_user:
        return (
            "Error: User not authenticated!",
            "",
            gr.update(),
            gr.update(),
            "",
            "",
            "",
            "",
            "",
            False,
            "",
        )

    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return (
            "Error: Data manager not available!",
            "",
            gr.update(),
            gr.update(),
            "",
            "",
            "",
            "",
            "",
            False,
            "",
        )

    if not original_name.strip():
        return (
            "Please enter the original prompt name!",
            "",
            gr.update(),
            gr.update(),
            "",
            "",
            "",
            "",
            "",
            False,
            "",
        )

    result = data_manager.update_prompt(
        original_name, new_name, title, content, category, tags, is_enhancement_prompt
    )

    # Refresh the prompts display
    prompts = data_manager.get_all_prompts()
    tree_view = prompt_manager.format_prompts_for_display(prompts)
    categories = ["All"] + data_manager.get_categories()

    # Update enhancement prompts dropdown
    enhancement_prompts = data_manager.get_enhancement_prompts()
    enhancement_choices = [
        (f"{p['name']} - {p['title']}", p["name"]) for p in enhancement_prompts
    ]

    return (
        result,
        tree_view,
        gr.update(choices=categories),
        gr.update(choices=enhancement_choices),
        "",
        "",
        "",
        "",
        "",
        False,
        "",
    )


def delete_existing_prompt(prompt_name):
    """Delete existing prompt"""
    if not prompt_manager.current_user:
        return "Error: User not authenticated!", "", gr.update(), gr.update()

    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return "Error: Data manager not available!", "", gr.update(), gr.update()

    if not prompt_name.strip():
        return "Please enter a prompt name!", "", gr.update(), gr.update()

    result = data_manager.delete_prompt(prompt_name.strip())

    # Refresh the prompts display
    prompts = data_manager.get_all_prompts()
    tree_view = prompt_manager.format_prompts_for_display(prompts)
    categories = ["All"] + data_manager.get_categories()

    # Update enhancement prompts dropdown
    enhancement_prompts = data_manager.get_enhancement_prompts()
    enhancement_choices = [
        (f"{p['name']} - {p['title']}", p["name"]) for p in enhancement_prompts
    ]

    return (
        result,
        tree_view,
        gr.update(choices=categories),
        gr.update(choices=enhancement_choices),
    )


def select_prompt_for_execution(prompt_name):
    """Select prompt for execution"""
    if not prompt_manager.current_user:
        return "Error: User not authenticated!"

    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return "Error: Data manager not available!"

    if not prompt_name.strip():
        return "Please enter a prompt name!"

    prompt = data_manager.get_prompt_by_name(prompt_name.strip())
    if prompt:
        return prompt["content"]
    else:
        return f"Prompt '{prompt_name}' not found!"


def execute_ai_prompt(prompt_text):
    """Execute AI prompt"""
    if not prompt_text.strip():
        return "Please enter a prompt to execute!"

    return prompt_manager.execute_prompt(prompt_text)


def enhance_ai_prompt(original_prompt, enhancement_prompt_name):
    """Enhance AI prompt"""
    if not original_prompt.strip():
        return "Please enter a prompt to enhance!"

    return prompt_manager.enhance_prompt(original_prompt, enhancement_prompt_name)


def test_prompt_with_llm(prompt_content, test_input):
    """Test prompt with configured LLM model"""
    if not prompt_content.strip():
        return "Please enter a prompt to test!", "❌ No prompt provided"

    try:
        # Combine prompt with test input if provided
        if test_input and test_input.strip():
            combined_prompt = f"{prompt_content.strip()}\n\n{test_input.strip()}"
        else:
            combined_prompt = prompt_content.strip()

        # Check authentication
        if not prompt_manager.current_user:
            return "Please log in to test prompts.", "❌ Authentication required"

        # Use test configuration if available, fallback to main config
        test_config = getattr(prompt_manager, "test_config", None)
        if not test_config or not test_config.get("model_name"):
            config = prompt_manager.config
            if not config or not config.get("model_name"):
                return (
                    "Please configure your AI service or Test service in the Configuration tab first.",
                    "❌ No configuration found",
                )
        else:
            config = test_config

        # Test the prompt using the configured LLM
        result = prompt_manager.call_ai_service(combined_prompt, config)

        if result.startswith("Error:"):
            return result, "❌ Test failed"
        else:
            return result, "✅ Test completed successfully"

    except Exception as e:
        return f"Error testing prompt: {str(e)}", "❌ Test error"


def save_configuration(service_type, api_endpoint, api_key, model_name):
    """Save the AI service configuration"""
    return prompt_manager.save_config(service_type, api_endpoint, api_key, model_name)


def save_enhancement_configuration(
    service_type, api_endpoint, api_key, model_name, enhancement_prompt_name
):
    """Save enhancement configuration"""
    return prompt_manager.save_enhancement_config(
        service_type, api_endpoint, api_key, model_name, enhancement_prompt_name
    )


def save_test_configuration(service_type, api_endpoint, api_key, model_name):
    """Save test configuration"""
    return prompt_manager.save_test_config(
        service_type, api_endpoint, api_key, model_name
    )


# LangWatch optimization functions
def optimize_prompt_langwatch(prompt_text, context, target_model):
    """Optimize prompt using LangWatch"""
    if not prompt_text.strip():
        return (
            gr.update(visible=False),  # Hide results
            "Error: Please enter a prompt to optimize",
            "",
            0,
            "",
            "",
            "",
        )

    success, message, optimization_data = prompt_manager.optimize_prompt_with_langwatch(
        prompt_text, context, target_model
    )

    if success:
        return (
            gr.update(visible=True),  # Show results
            message,
            optimization_data["optimized_prompt"],
            optimization_data["score"],
            "\n".join(
                str(s)
                for s in (
                    optimization_data["suggestions"]
                    if isinstance(optimization_data["suggestions"], list)
                    else []
                )
            ),
            optimization_data["reasoning"],
            "",  # Clear optimization status
        )
    else:
        return (gr.update(visible=False), message, "", 0, "", "", "")  # Hide results


def accept_optimization(optimized_prompt):
    """Accept the optimized prompt"""
    if not optimized_prompt:
        return "", "No optimization to accept"

    return (
        optimized_prompt,
        "✅ Optimization accepted! The prompt content has been updated.",
    )


def retry_optimization(prompt_text, context, target_model):
    """Retry the optimization"""
    return optimize_prompt_langwatch(prompt_text, context, target_model)


def reject_optimization():
    """Reject the optimization"""
    return (
        gr.update(visible=False),  # Hide results
        "❌ Optimization rejected. Original prompt unchanged.",
    )


def get_langwatch_status_display():
    """Get LangWatch status for display"""
    status = prompt_manager.get_langwatch_status()

    if status["available"]:
        return "✅ LangWatch Ready"
    elif not status["library_installed"]:
        return "⚠️ LangWatch library not installed"
    elif not status["api_key_set"]:
        return "⚠️ LangWatch API key not configured"
    else:
        return "❌ LangWatch not available"


# Token Calculator function
def calculate_token_estimate(prompt_text, model, max_completion_tokens):
    """Calculate token estimate for prompt"""
    if not prompt_text or not prompt_text.strip():
        return "Enter some prompt content to calculate tokens..."

    try:
        # Get token estimate
        estimate = token_calculator.estimate_tokens(
            text=prompt_text,
            model=model,
            max_completion_tokens=(
                int(max_completion_tokens) if max_completion_tokens else 1000
            ),
        )

        # Format the results
        result_lines = [
            f"🧮 **Token Estimate for {estimate.model_name}**",
            "",
            f"📝 **Prompt Tokens:** {estimate.prompt_tokens:,}",
            f"💬 **Max Completion Tokens:** {estimate.max_completion_tokens:,}",
            f"📊 **Total Tokens:** {estimate.total_tokens:,}",
            f"⚙️ **Tokenizer:** {estimate.tokenizer_used}",
        ]

        # Add cost estimate if available
        if estimate.cost_estimate is not None:
            result_lines.extend(
                [
                    "",
                    f"💰 **Estimated Cost:** ${estimate.cost_estimate:.4f} {estimate.currency}",
                    f"   • Input: ${(estimate.prompt_tokens / 1000) * token_calculator.MODEL_PRICING.get(estimate.model_name.lower(), {}).get('input', 0):.4f}",
                    f"   • Output: ${(estimate.max_completion_tokens / 1000) * token_calculator.MODEL_PRICING.get(estimate.model_name.lower(), {}).get('output', 0):.4f}",
                ]
            )

        # Add complexity analysis
        analysis = token_calculator.analyze_prompt_complexity(prompt_text)
        if analysis.get("suggestions"):
            result_lines.extend(["", "⚠️ **Suggestions:**"])
            for suggestion in analysis["suggestions"]:
                result_lines.append(f"   • {suggestion}")

        return "\n".join(result_lines)

    except Exception as e:
        return f"❌ Error calculating tokens: {str(e)}"


# API Token management functions
def create_new_api_token(token_name, expires_days_str):
    """Create new API token"""
    if not token_name.strip():
        return "Error: Token name is required", "", gr.update()

    expires_days = None
    if expires_days_str and expires_days_str.strip():
        try:
            expires_days = int(expires_days_str)
            if expires_days <= 0:
                return "Error: Expiration days must be positive", "", gr.update()
        except ValueError:
            return "Error: Invalid expiration days", "", gr.update()

    success, message, token = prompt_manager.create_api_token(
        token_name.strip(), expires_days
    )

    if success:
        # Refresh token list
        tokens = prompt_manager.get_user_api_tokens()
        token_display = format_tokens_display(tokens)

        return message, token if token else "", gr.update(value=token_display)
    else:
        return message, "", gr.update()


def revoke_api_token_by_id(token_id):
    """Revoke specific API token"""
    if not token_id:
        return "Error: No token selected", gr.update()

    success, message = prompt_manager.revoke_api_token(token_id)

    # Refresh token list
    tokens = prompt_manager.get_user_api_tokens()
    token_display = format_tokens_display(tokens)

    return message, gr.update(value=token_display)


def revoke_all_api_tokens():
    """Revoke all API tokens"""
    success, message = prompt_manager.revoke_all_api_tokens()

    # Refresh token list
    tokens = prompt_manager.get_user_api_tokens()
    token_display = format_tokens_display(tokens)

    return message, gr.update(value=token_display)


# Prompt Builder functions
def load_available_prompts():
    """Load available prompts for the builder"""
    if not prompt_manager.current_user:
        return "<div class='available-prompts'><p>Please login to view available prompts</p></div>"

    data_manager = prompt_manager.get_data_manager()
    if not data_manager:
        return "<div class='available-prompts'><p>No data manager available</p></div>"

    try:
        available_prompts = prompt_builder.get_available_prompts(data_manager)

        if not available_prompts:
            return "<div class='available-prompts'><p>No prompts available. Create some prompts first!</p></div>"

        # Generate HTML for available prompts
        html_cards = []
        for prompt in available_prompts:
            card_html = f"""
            <div class="prompt-card" data-prompt-id="{prompt['id']}" draggable="true">
                <div class="prompt-card-header">
                    <span class="prompt-icon">{'⚡' if prompt['is_enhancement'] else '📄'}</span>
                    <h4 class="prompt-name">{prompt['name']}</h4>
                    <span class="prompt-category">{prompt['category']}</span>
                </div>
                <div class="prompt-card-body">
                    <p class="prompt-title">{prompt.get('title', '')}</p>
                    <p class="prompt-preview">{prompt['preview']}</p>
                    <div class="prompt-meta">
                        <span class="prompt-length">{prompt['length']} chars</span>
                        {'<span class="enhancement-badge">Enhancement</span>' if prompt['is_enhancement'] else ''}
                    </div>
                </div>
            </div>
            """
            html_cards.append(card_html)

        return f"<div class='available-prompts'>{''.join(html_cards)}</div>"

    except Exception as e:
        return f"<div class='available-prompts'><p>Error loading prompts: {str(e)}</p></div>"


def update_builder_preview(selected_prompts, template, custom_separator, add_numbers):
    """Update the preview of combined prompts"""
    if not selected_prompts:
        return t("builder.preview.empty")

    try:
        # Convert template value if needed
        template_key = template if isinstance(template, str) else "sequential"

        # Note: custom options would be used for advanced template processing
        preview = prompt_builder.get_combination_preview(selected_prompts, template_key)
        return preview

    except Exception as e:
        return f"{t('builder.preview.error')}: {str(e)}"


def combine_selected_prompts(selected_prompts, template, custom_separator, add_numbers):
    """Combine selected prompts and return result"""
    if not selected_prompts:
        return f"{t('builder.error.no_prompts')}", {}, []

    try:
        # Convert template value if needed
        template_key = template if isinstance(template, str) else "sequential"

        # Prepare custom options for prompt builder
        separator = (
            custom_separator.replace("\\n", "\n") if custom_separator else "\n\n"
        )
        use_numbers = add_numbers

        success, error_message, combined_data = prompt_builder.combine_prompts(
            selected_prompts,
            template_key,
            {"separator": separator, "add_numbers": use_numbers},
        )

        if success:
            return (
                f"✅ {t('status.success')}: Combined {len(selected_prompts)} prompts successfully!",
                combined_data,
                [],
            )
        else:
            return f"❌ {error_message}", {}, selected_prompts

    except Exception as e:
        return f"❌ {t('builder.error.combination')}: {str(e)}", {}, selected_prompts


def clear_selected_prompts():
    """Clear the selected prompts"""
    drop_zone_html = f"""
    <div class="drop-zone drop-zone-selected" data-zone-type="selected">
        <div class="drop-zone-content">
            <div class="drop-zone-icon">📥</div>
            <p class="drop-zone-message">{t("builder.drag.add")}</p>
        </div>
    </div>
    """
    return drop_zone_html, [], t("builder.preview.empty")


def open_combined_in_editor(combined_data):
    """Open combined prompt in the main editor"""
    if not combined_data or "content" not in combined_data:
        return (
            "",  # prompt_name
            "",  # prompt_title
            "",  # prompt_content
            "",  # prompt_category
            "",  # prompt_tags
            False,  # is_enhancement_prompt
            "❌ No combined prompt to open in editor",  # status
        )

    try:
        return (
            combined_data.get("suggested_name", ""),
            combined_data.get("suggested_title", ""),
            combined_data.get("content", ""),
            combined_data.get("suggested_category", "Combined"),
            combined_data.get("suggested_tags", ""),
            False,  # Enhancement prompt checkbox
            f"✅ Combined prompt loaded into editor. Contains {combined_data.get('source_count', 0)} source prompts.",
        )
    except Exception as e:
        return "", "", "", "", "", False, f"❌ Error opening in editor: {str(e)}"


def refresh_api_tokens():
    """Refresh API token display"""
    tokens = prompt_manager.get_user_api_tokens()
    token_display = format_tokens_display(tokens)
    stats = prompt_manager.get_api_token_stats()

    stats_text = "📊 **Token Statistics:**\n"
    stats_text += f"• Active Tokens: {stats.get('total_active', 0)}\n"
    stats_text += f"• Never Expire: {stats.get('never_expire', 0)}\n"
    stats_text += f"• Will Expire: {stats.get('will_expire', 0)}\n"
    stats_text += f"• Used Tokens: {stats.get('used_tokens', 0)}"

    return gr.update(value=token_display), stats_text


def format_tokens_display(tokens):
    """Format tokens for display"""
    if not tokens:
        return "No API tokens found. Create your first token to get started with API access."

    display_lines = ["🔑 **Your API Tokens:**\n"]

    for token in tokens:
        # Format expiration
        if token.expires_at:
            exp_str = f"⏰ Expires: {token.expires_at.strftime('%Y-%m-%d %H:%M')}"
            # Check if expired
            from datetime import datetime

            if token.expires_at < datetime.now():
                exp_str += " (EXPIRED)"
        else:
            exp_str = "♾️ Never expires"

        # Format last used
        if token.last_used:
            used_str = f"🕒 Last used: {token.last_used.strftime('%Y-%m-%d %H:%M')}"
        else:
            used_str = "📝 Never used"

        display_lines.append(f"**{token.name}**")
        display_lines.append(f"  🆔 ID: `{token.id[:16]}...`")
        display_lines.append(f"  🔍 Preview: `{token.token_prefix}...`")
        display_lines.append(f"  {exp_str}")
        display_lines.append(f"  {used_str}")
        display_lines.append(
            f"  📅 Created: {token.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
        display_lines.append("")

    return "\n".join(display_lines)


# Admin functions
def admin_create_tenant(name, subdomain, max_users):
    """Create new tenant"""
    try:
        max_users_int = int(max_users) if max_users else 100
        success, message = prompt_manager.create_tenant(name, subdomain, max_users_int)

        # Refresh tenant list
        tenants = prompt_manager.get_all_tenants()
        tenant_choices = [(f"{t.name} ({t.subdomain})", t.id) for t in tenants]

        return message, gr.update(choices=tenant_choices), "", "", ""
    except ValueError:
        return "Error: Max users must be a number", gr.update(), "", "", ""


def admin_create_user(tenant_id, email, password, first_name, last_name, role):
    """Create new user"""
    success, message = prompt_manager.create_user(
        tenant_id, email, password, first_name, last_name, role
    )

    # Refresh user list for selected tenant
    users = prompt_manager.get_tenant_users(tenant_id) if tenant_id else []
    user_list = "\n".join(
        [f"👤 {u.first_name} {u.last_name} ({u.email}) - {u.role}" for u in users]
    )

    return message, user_list, "", "", "", "", ""


def admin_refresh_tenant_users(tenant_id):
    """Refresh user list for selected tenant"""
    if not tenant_id:
        return "Select a tenant first"

    users = prompt_manager.get_tenant_users(tenant_id)
    user_list = "\n".join(
        [f"👤 {u.first_name} {u.last_name} ({u.email}) - {u.role}" for u in users]
    )

    return user_list


# Translation functions
def translate_prompt_to_english(prompt_text):
    """Translate prompt text to English for enhancement"""
    if not prompt_text or not prompt_text.strip():
        return "", "No text to translate"

    if not text_translator.is_translation_needed():
        return prompt_text, "Text is already in English"

    success, translated_text, error = text_translator.translate_to_english(prompt_text)

    if success:
        source_lang = text_translator.get_current_language_name()
        return translated_text, f"✅ Translated from {source_lang} to English"
    else:
        return prompt_text, f"❌ Translation failed: {error}"


def check_translation_button_visibility():
    """Check if translation button should be visible"""
    return gr.update(visible=text_translator.is_translation_needed())


# Language change handler
def change_language(language: str):
    """Handle language change and update all UI elements"""
    language_map = {
        "English": "en",
        "Español": "es",
        "Français": "fr",
        "Deutsch": "de",
        "中文": "zh",
        "日本語": "ja",
        "Português": "pt",
        "Русский": "ru",
        "العربية": "ar",
        "हिन्दी": "hi",
    }

    if language in language_map:
        # Set the new language
        i18n.set_language(language_map[language])

        # Return updated translations for visible UI elements and translation button visibility
        return (
            t("app.status.not_authenticated"),  # auth_status
            "",  # login_message - clear it
            f"Language changed to {language}",  # status message
            gr.update(
                visible=text_translator.is_translation_needed()
            ),  # translation button visibility
        )

    return gr.update(), gr.update(), "Language change failed", gr.update()


# Create modern Gradio interface
def create_interface():
    """Create modernized interface with i18n support and improved design"""
    # Check if we're in single-user mode
    is_single_user = os.getenv("MULTITENANT_MODE", "true").lower() == "false"

    with gr.Blocks(
        title=t("app.title"),
        theme=ModernTheme.create_theme(),
        css=ResponsiveCSS.get_css(),
    ) as app:
        # Store session token
        session_token = gr.State("")

        # Modern header with language selector
        UIComponents.create_header("app.title", "app.subtitle")

        # Language selector
        with gr.Row():
            with gr.Column(scale=3):
                pass  # Spacer
            with gr.Column(scale=1):
                language_selector = UIComponents.create_language_selector()

        # Authentication status with internationalization
        auth_status = gr.Markdown(t("app.status.not_authenticated"))

        # Modern login interface with internationalization
        with gr.Row(
            visible=not is_single_user, elem_classes=["login-section"]
        ) as login_section:
            with gr.Column():
                UIComponents.create_section_header("auth.login", "🔐")

                with gr.Tabs(elem_classes=["modern-tabs"]):
                    with gr.TabItem(
                        f"📧 {t('auth.login')}", elem_classes=["modern-tab"]
                    ):
                        login_email = UIComponents.create_input_group(
                            "auth.email",
                            placeholder_key="form.placeholder.email",
                            required=True,
                        )
                        login_password = UIComponents.create_input_group(
                            "auth.password", input_type="password", required=True
                        )
                        login_subdomain = UIComponents.create_input_group(
                            "auth.tenant", value="localhost"
                        )
                        login_btn = UIComponents.create_button(
                            "auth.login", variant="primary", icon="🔑", size="large"
                        )
                        login_message = UIComponents.create_status_display(
                            "status.info"
                        )

                    with gr.TabItem(f"🔗 {t('auth.sso')}", elem_classes=["modern-tab"]):
                        sso_subdomain = UIComponents.create_input_group(
                            "auth.tenant", placeholder_key="form.placeholder.name"
                        )
                        sso_btn = UIComponents.create_button(
                            "auth.sso", variant="secondary", icon="🚀", size="large"
                        )
                        sso_message = UIComponents.create_status_display("status.info")

        # Main application interface with modern design
        with gr.Row(
            visible=is_single_user, elem_classes=["main-section"]
        ) as main_section:
            with gr.Tabs(elem_classes=["modern-tabs"]):
                # Prompt Management Tab
                with gr.TabItem(f"📝 {t('nav.prompts')}", elem_classes=["modern-tab"]):
                    UIComponents.create_section_header("nav.prompts", "📝")

                    with gr.Row(elem_classes=["responsive-layout"]):
                        with gr.Column(scale=2, elem_classes=["main-content"]):
                            prompt_name = UIComponents.create_input_group(
                                "prompt.name",
                                placeholder_key="form.placeholder.name",
                                required=True,
                            )
                            prompt_title = UIComponents.create_input_group(
                                "prompt.title", placeholder_key="form.placeholder.name"
                            )
                            prompt_category = UIComponents.create_input_group(
                                "prompt.category",
                                input_type="dropdown",
                                choices=[
                                    "General",
                                    "Writing",
                                    "Analysis",
                                    "Creative",
                                    "Technical",
                                ],
                                value="General",
                            )
                            prompt_content = UIComponents.create_input_group(
                                "prompt.content",
                                input_type="textarea",
                                lines=8,
                                required=True,
                            )

                            # Test Prompt Section
                            with gr.Group():
                                gr.Markdown("#### 🧪 Test Prompt")
                                gr.Markdown(
                                    "Test your prompt with the configured LLM model"
                                )

                                with gr.Row():
                                    with gr.Column(scale=2):
                                        test_input = gr.Textbox(
                                            label="Test Input",
                                            placeholder="Enter test input or context for your prompt...",
                                            lines=2,
                                            info="This will be combined with your prompt for testing",
                                        )
                                    with gr.Column(scale=1):
                                        test_btn = UIComponents.create_button(
                                            "test.prompt",
                                            variant="secondary",
                                            icon="🧪",
                                            size="medium",
                                        )

                                test_output = gr.Textbox(
                                    label="Test Output",
                                    lines=6,
                                    interactive=False,
                                    placeholder="Test results will appear here...",
                                )
                                test_status = UIComponents.create_status_display(
                                    "test.status"
                                )

                            # Translation Section (visible only for non-English UI)
                            with gr.Group(
                                visible=text_translator.is_translation_needed()
                            ) as translation_section:
                                gr.Markdown(f"#### 🌐 {t('translate.to_english')}")
                                gr.Markdown(t("translate.help"))

                                with gr.Row():
                                    translate_btn = UIComponents.create_button(
                                        "translate.to_english",
                                        variant="secondary",
                                        icon="🌐",
                                        size="medium",
                                    )
                                    translation_status = (
                                        UIComponents.create_status_display(
                                            "translate.status"
                                        )
                                    )

                            # Token Calculator Section
                            with gr.Group():
                                gr.Markdown("#### 🧮 Token Calculator")
                                gr.Markdown(
                                    "Estimate token consumption and cost for your prompt"
                                )

                                with gr.Row():
                                    with gr.Column(scale=2):
                                        calc_model = gr.Dropdown(
                                            choices=token_calculator.get_supported_models(),
                                            value="gpt-4",
                                            label="Target Model",
                                            info="Select the AI model for accurate token calculation",
                                        )
                                    with gr.Column(scale=1):
                                        max_completion_tokens = gr.Number(
                                            label="Max Completion Tokens",
                                            value=1000,
                                            minimum=1,
                                            maximum=8000,
                                            info="Expected response length",
                                        )

                                with gr.Row():
                                    with gr.Column(scale=1):
                                        calculate_tokens_btn = gr.Button(
                                            "🧮 Calculate Tokens", variant="secondary"
                                        )
                                    with gr.Column(scale=3):
                                        token_calc_status = gr.Textbox(
                                            label="Token Estimation",
                                            interactive=False,
                                            placeholder="Token count and cost estimate will appear here...",
                                        )

                            # LangWatch Optimization Section
                            with gr.Group():
                                gr.Markdown("#### 🚀 LangWatch Optimization")
                                gr.Markdown(
                                    "Enhance your prompt using AI-powered optimization"
                                )

                                with gr.Row():
                                    with gr.Column(scale=2):
                                        optimization_context = gr.Textbox(
                                            label="Optimization Context (Optional)",
                                            placeholder="Describe the purpose or goal of this prompt...",
                                            lines=2,
                                        )
                                    with gr.Column(scale=1):
                                        target_model = gr.Dropdown(
                                            choices=[
                                                "gpt-4",
                                                "gpt-3.5-turbo",
                                                "claude-3",
                                                "gemini-pro",
                                            ],
                                            value="gpt-4",
                                            label="Target Model",
                                        )

                                with gr.Row():
                                    optimize_btn = gr.Button(
                                        "🚀 Optimize with LangWatch",
                                        variant="secondary",
                                    )
                                    langwatch_status = gr.Textbox(
                                        label="LangWatch Status",
                                        interactive=False,
                                        scale=2,
                                    )

                                # Optimization Results Display
                                with gr.Row(visible=False) as optimization_results:
                                    with gr.Column():
                                        gr.Markdown("#### Optimization Results")

                                        with gr.Row():
                                            optimization_score = gr.Number(
                                                label="Optimization Score",
                                                precision=1,
                                                interactive=False,
                                            )
                                            optimization_suggestions = gr.Textbox(
                                                label="Suggestions",
                                                lines=3,
                                                interactive=False,
                                            )

                                        optimized_prompt_display = gr.Textbox(
                                            label="Optimized Prompt",
                                            lines=6,
                                            interactive=False,
                                        )

                                        optimization_reasoning = gr.Textbox(
                                            label="Optimization Reasoning",
                                            lines=2,
                                            interactive=False,
                                        )

                                        # Action buttons for optimization results
                                        with gr.Row():
                                            accept_optimization_btn = gr.Button(
                                                "✅ Accept", variant="primary"
                                            )
                                            retry_optimization_btn = gr.Button(
                                                "🔄 Retry", variant="secondary"
                                            )
                                            reject_optimization_btn = gr.Button(
                                                "❌ Reject", variant="stop"
                                            )

                                optimization_status = gr.Textbox(
                                    label="Optimization Status", interactive=False
                                )

                            prompt_tags = gr.Textbox(
                                label="Tags (comma-separated)",
                                placeholder="creative, writing, analysis",
                            )
                            is_enhancement_prompt = gr.Checkbox(
                                label="Enhancement Prompt",
                                value=False,
                                info="Check this if this prompt is designed to enhance other prompts",
                            )

                            with gr.Row():
                                add_btn = gr.Button("➕ Add Prompt", variant="primary")
                                update_btn = gr.Button(
                                    "✏️ Update Prompt", variant="secondary"
                                )
                                clear_btn = gr.Button("🗑️ Clear Form")

                            prompt_status = gr.Textbox(
                                label="Status", interactive=False
                            )

                        with gr.Column(scale=1):
                            gr.Markdown("### Quick Actions")
                            edit_prompt_name = gr.Textbox(
                                label="Prompt Name to Edit",
                                placeholder="Enter prompt name",
                            )
                            load_edit_btn = gr.Button("📝 Load for Editing")

                            delete_prompt_name = gr.Textbox(
                                label="Prompt Name to Delete",
                                placeholder="Enter prompt name",
                            )
                            delete_btn = gr.Button("🗑️ Delete Prompt", variant="stop")

                            edit_status = gr.Textbox(
                                label="Edit Status", interactive=False
                            )

                # Prompt Library Tab
                with gr.TabItem("📚 Prompt Library"):
                    gr.Markdown("### Browse and Search Prompts")

                    with gr.Row():
                        search_box = gr.Textbox(
                            label="Search Prompts",
                            placeholder="Search by name, title, content, or tags...",
                        )
                        category_filter = gr.Dropdown(
                            choices=["All"], value="All", label="Filter by Category"
                        )
                        refresh_btn = gr.Button("🔄 Refresh")

                    prompts_display = gr.Textbox(
                        label="Prompts Tree View",
                        value="Login to view your prompts...",
                        lines=20,
                        max_lines=25,
                        interactive=False,
                    )

                # Prompt Builder Tab
                with gr.TabItem(
                    f"🧩 {t('builder.title')}", elem_classes=["modern-tab"]
                ):
                    UIComponents.create_section_header("builder.title", "🧩")
                    gr.Markdown(t("builder.subtitle"))

                    with gr.Row(elem_classes=["responsive-layout"]):
                        # Available Prompts Section
                        with gr.Column(scale=1, elem_classes=["builder-section"]):
                            with gr.Group(elem_classes=["builder-header"]):
                                gr.Markdown(f"### 📋 {t('builder.available')}")
                                builder_search, builder_filter = (
                                    UIComponents.create_search_bar(
                                        placeholder_key="builder.search.placeholder",
                                        with_filters=True,
                                    )
                                )
                                builder_refresh_btn = UIComponents.create_button(
                                    "action.refresh",
                                    variant="secondary",
                                    icon="🔄",
                                    size="small",
                                )

                            available_prompts_area = gr.HTML(
                                value="<div class='available-prompts'><p>Login to view available prompts...</p></div>",
                                elem_classes=["available-prompts"],
                            )

                        # Selected Prompts Section
                        with gr.Column(scale=1, elem_classes=["builder-section"]):
                            with gr.Group(elem_classes=["builder-header"]):
                                gr.Markdown(f"### 🎯 {t('builder.selected')}")
                                with gr.Row():
                                    clear_selection_btn = UIComponents.create_button(
                                        "builder.clear",
                                        variant="secondary",
                                        icon="🗑️",
                                        size="small",
                                    )
                                    combine_prompts_btn = UIComponents.create_button(
                                        "builder.combine",
                                        variant="primary",
                                        icon="🔗",
                                        size="medium",
                                    )

                            selected_prompts_area = UIComponents.create_drop_zone(
                                zone_type="selected", message_key="builder.drag.add"
                            )

                            selected_prompts_list = gr.State(
                                []
                            )  # Store selected prompts data

                    # Template Selection and Preview
                    with gr.Row(elem_classes=["responsive-layout"]):
                        with gr.Column(scale=1, elem_classes=["builder-section"]):
                            gr.Markdown(f"### 🎨 {t('builder.template')}")
                            template_selector = UIComponents.create_template_selector()

                            gr.Markdown("#### Custom Options")
                            custom_separator = gr.Textbox(
                                label="Custom Separator",
                                value="\\n\\n",
                                placeholder="Enter custom separator between prompts",
                            )
                            add_numbers = gr.Checkbox(
                                label="Add Numbers",
                                value=True,
                                info="Add sequence numbers to prompts",
                            )

                        with gr.Column(scale=1, elem_classes=["builder-section"]):
                            gr.Markdown(f"### 👁️ {t('builder.preview')}")
                            preview_area = gr.Textbox(
                                value=t("builder.preview.empty"),
                                lines=12,
                                interactive=False,
                                elem_classes=["preview-area"],
                            )

                            with gr.Row():
                                update_preview_btn = UIComponents.create_button(
                                    "action.refresh",
                                    variant="secondary",
                                    icon="👁️",
                                    size="small",
                                )
                                open_in_editor_btn = UIComponents.create_button(
                                    "builder.edit",
                                    variant="primary",
                                    icon="📝",
                                    size="medium",
                                )

                    # Builder Status
                    builder_status = UIComponents.create_status_display("status.info")

                    # Hidden state for builder data
                    builder_state = gr.State(
                        {
                            "available_prompts": [],
                            "selected_prompts": [],
                            "combined_prompt": None,
                        }
                    )

                # Prompt Execution Tab
                with gr.TabItem("🚀 Prompt Execution"):
                    gr.Markdown("### Execute AI Prompts")

                    with gr.Row():
                        with gr.Column():
                            execution_prompt = gr.Textbox(
                                label="Prompt to Execute",
                                lines=8,
                                placeholder="Enter a prompt or load one by name...",
                            )

                            with gr.Row():
                                load_prompt_name = gr.Textbox(
                                    label="Load Prompt by Name",
                                    placeholder="Enter prompt name",
                                )
                                load_prompt_btn = gr.Button("📋 Load Prompt")

                            execute_btn = gr.Button(
                                "🚀 Execute Prompt", variant="primary", size="lg"
                            )

                        with gr.Column():
                            ai_response = gr.Textbox(
                                label="AI Response",
                                lines=12,
                                placeholder="AI response will appear here...",
                                interactive=False,
                            )

                # Prompt Enhancement Tab
                with gr.TabItem("⚡ Prompt Enhancement"):
                    gr.Markdown("### Enhance Your Prompts")
                    gr.Markdown(
                        "Use a different AI model and enhancement prompt to improve your existing prompts."
                    )

                    with gr.Row():
                        with gr.Column():
                            original_prompt = gr.Textbox(
                                label="Original Prompt",
                                lines=6,
                                placeholder="Enter the prompt you want to enhance, or load one by name...",
                            )

                            with gr.Row():
                                load_original_name = gr.Textbox(
                                    label="Load Original Prompt by Name",
                                    placeholder="Enter prompt name",
                                )
                                load_original_btn = gr.Button("📋 Load Original")

                            enhancement_prompt_selector = gr.Dropdown(
                                choices=[],
                                label="Enhancement Prompt (optional)",
                                info="Select an enhancement prompt, or leave blank to use default",
                            )

                            enhance_btn = gr.Button(
                                "⚡ Enhance Prompt", variant="primary", size="lg"
                            )

                        with gr.Column():
                            enhanced_prompt = gr.Textbox(
                                label="Enhanced Prompt",
                                lines=12,
                                placeholder="Enhanced prompt will appear here...",
                                interactive=False,
                            )

                            with gr.Row():
                                copy_enhanced_btn = gr.Button(
                                    "📋 Copy to Execution", variant="secondary"
                                )
                                save_enhanced_name = gr.Textbox(
                                    label="Name for Enhanced Prompt",
                                    placeholder="Enter name to save enhanced prompt",
                                )
                                save_enhanced_btn = gr.Button(
                                    "💾 Save Enhanced Prompt", variant="secondary"
                                )

                    enhancement_status = gr.Textbox(
                        label="Enhancement Status", interactive=False
                    )

                # Account Settings Tab
                with gr.TabItem("👤 Account Settings"):
                    gr.Markdown("### Account & API Management")

                    with gr.Tabs():
                        with gr.TabItem("🔑 API Tokens"):
                            gr.Markdown("### API Token Management")
                            gr.Markdown(
                                "Create secure API tokens to access your prompts programmatically. These tokens allow external applications to retrieve your prompts via REST API."
                            )

                            with gr.Row():
                                with gr.Column(scale=1):
                                    gr.Markdown("#### Create New Token")

                                    token_name = gr.Textbox(
                                        label="Token Name",
                                        placeholder="e.g., My App Integration",
                                        info="Give your token a descriptive name",
                                    )

                                    token_expires_days = gr.Textbox(
                                        label="Expires in Days (optional)",
                                        placeholder="30",
                                        info="Leave empty for tokens that never expire",
                                    )

                                    with gr.Row():
                                        create_token_btn = gr.Button(
                                            "🔑 Create Token", variant="primary"
                                        )
                                        revoke_all_btn = gr.Button(
                                            "🗑️ Revoke All", variant="stop"
                                        )
                                        refresh_tokens_btn = gr.Button("🔄 Refresh")

                                    token_creation_status = gr.Textbox(
                                        label="Status", interactive=False
                                    )

                                    with gr.Group():
                                        gr.Markdown("#### ⚠️ New Token")
                                        gr.Markdown(
                                            "**Save this token immediately! You won't be able to see it again.**"
                                        )
                                        new_token_display = gr.Textbox(
                                            label="Your New API Token",
                                            interactive=True,
                                            info="Copy this token and store it securely",
                                        )

                                with gr.Column(scale=2):
                                    gr.Markdown("#### Your API Tokens")

                                    api_tokens_display = gr.Textbox(
                                        label="Active Tokens",
                                        lines=15,
                                        value="Login to view your API tokens...",
                                        interactive=False,
                                    )

                                    token_stats_display = gr.Markdown(
                                        "Token statistics will appear here..."
                                    )

                                    with gr.Row():
                                        revoke_token_id = gr.Textbox(
                                            label="Token ID to Revoke",
                                            placeholder="Enter token ID (first 16 characters)",
                                            info="Copy the ID from the token list above",
                                        )
                                        revoke_single_btn = gr.Button(
                                            "🗑️ Revoke Token", variant="secondary"
                                        )

                        with gr.TabItem("📖 API Documentation"):
                            gr.Markdown(
                                """
                            ### 🚀 API Documentation

                            Use your API tokens to access prompts programmatically via REST API.

                            #### Base URL
                            ```
                            http://localhost:7860/api
                            ```

                            #### Authentication
                            Include your API token in the Authorization header:
                            ```bash
                            Authorization: Bearer apm_your_token_here
                            ```

                            #### Available Endpoints

                            **📝 Get All Prompts**
                            ```bash
                            GET /api/prompts
                            curl -H "Authorization: Bearer apm_your_token" http://localhost:7860/api/prompts
                            ```

                            **🔍 Get Prompt by Name**
                            ```bash
                            GET /api/prompts/name/{prompt_name}
                            curl -H "Authorization: Bearer apm_your_token" http://localhost:7860/api/prompts/name/my-prompt
                            ```

                            **🆔 Get Prompt by ID**
                            ```bash
                            GET /api/prompts/{prompt_id}
                            curl -H "Authorization: Bearer apm_your_token" http://localhost:7860/api/prompts/123
                            ```

                            **📊 Search Prompts**
                            ```bash
                            GET /api/search?q=keyword
                            curl -H "Authorization: Bearer apm_your_token" "http://localhost:7860/api/search?q=creative"
                            ```

                            **📁 Get Categories**
                            ```bash
                            GET /api/categories
                            curl -H "Authorization: Bearer apm_your_token" http://localhost:7860/api/categories
                            ```

                            **📈 Get Statistics**
                            ```bash
                            GET /api/stats
                            curl -H "Authorization: Bearer apm_your_token" http://localhost:7860/api/stats
                            ```

                            #### Query Parameters
                            - `page`: Page number (default: 1)
                            - `page_size`: Items per page (default: 50, max: 100)
                            - `category`: Filter by category
                            - `include_enhancement`: Include enhancement prompts (default: true)

                            #### Example Response
                            ```json
                            {
                              "prompts": [
                                {
                                  "id": 1,
                                  "name": "creative-writing",
                                  "title": "Creative Writing Assistant",
                                  "content": "You are a creative writing assistant...",
                                  "category": "Writing",
                                  "tags": "creative,writing",
                                  "is_enhancement_prompt": false,
                                  "user_id": "user-123",
                                  "created_at": "2025-01-08T10:00:00",
                                  "updated_at": "2025-01-08T10:00:00"
                                }
                              ],
                              "total": 1,
                              "page": 1,
                              "page_size": 50
                            }
                            ```

                            #### Security Notes
                            - 🔒 Keep your API tokens secure and never commit them to version control
                            - 🔄 Rotate tokens regularly for better security
                            - ⏰ Use expiring tokens for temporary integrations
                            - 🚫 Revoke unused tokens immediately

                            #### Rate Limiting
                            - Default: 100 requests per minute per token
                            - Contact admin for higher limits if needed
                            """
                            )

                        with gr.TabItem("👤 Profile"):
                            gr.Markdown("### User Profile")

                            gr.Markdown("Login to view your profile information...")

                            gr.Markdown("### Change Password")

                            with gr.Column():
                                gr.Textbox(label="Current Password", type="password")
                                gr.Textbox(label="New Password", type="password")
                                gr.Textbox(
                                    label="Confirm New Password", type="password"
                                )

                                gr.Button("🔒 Change Password", variant="primary")
                                gr.Textbox(label="Status", interactive=False)

                # Configuration Tab
                with gr.TabItem("⚙️ Configuration"):
                    gr.Markdown("### Primary AI Service Configuration")

                    with gr.Row():
                        service_type = gr.Dropdown(
                            choices=["openai", "lmstudio", "ollama", "llamacpp"],
                            value="openai",
                            label="Service Type",
                        )
                        model_name = gr.Textbox(
                            value="gpt-3.5-turbo",
                            label="Model Name",
                            placeholder="e.g., gpt-3.5-turbo, llama2",
                        )

                    api_endpoint = gr.Textbox(
                        value="http://localhost:1234/v1",
                        label="API Endpoint",
                        placeholder="http://localhost:1234/v1",
                    )

                    api_key = gr.Textbox(
                        label="API Key (optional)",
                        type="password",
                        placeholder="Enter API key if required",
                    )

                    config_save_btn = gr.Button(
                        "💾 Save Configuration", variant="primary"
                    )
                    config_status = gr.Textbox(label="Status", interactive=False)

                    gr.Markdown("---")
                    gr.Markdown("### Enhancement Service Configuration")
                    gr.Markdown(
                        "Configure a separate AI service specifically for prompt enhancement"
                    )

                    with gr.Row():
                        enh_service_type = gr.Dropdown(
                            choices=["openai", "lmstudio", "ollama", "llamacpp"],
                            value="openai",
                            label="Enhancement Service Type",
                        )
                        enh_model_name = gr.Textbox(
                            value="gpt-4",
                            label="Enhancement Model Name",
                            placeholder="e.g., gpt-4, claude-3-sonnet",
                        )

                    enh_api_endpoint = gr.Textbox(
                        value="http://localhost:1234/v1",
                        label="Enhancement API Endpoint",
                        placeholder="http://localhost:1234/v1",
                    )

                    enh_api_key = gr.Textbox(
                        label="Enhancement API Key (optional)",
                        type="password",
                        placeholder="Enter API key if required",
                    )

                    enh_prompt_dropdown = gr.Dropdown(
                        choices=[],
                        label="Default Enhancement Prompt (optional)",
                        info="Select a stored enhancement prompt, or leave blank to use default",
                    )

                    enh_config_save_btn = gr.Button(
                        "💾 Save Enhancement Config", variant="primary"
                    )
                    enh_config_status = gr.Textbox(
                        label="Enhancement Config Status", interactive=False
                    )

                    gr.Markdown("---")
                    gr.Markdown("### Test Service Configuration")
                    gr.Markdown(
                        "Configure a separate AI service specifically for prompt testing"
                    )

                    with gr.Row():
                        test_service_type = gr.Dropdown(
                            choices=["openai", "lmstudio", "ollama", "llamacpp"],
                            value="openai",
                            label="Test Service Type",
                        )
                        test_model_name = gr.Textbox(
                            value="gpt-3.5-turbo",
                            label="Test Model Name",
                            placeholder="e.g., gpt-3.5-turbo, llama2",
                        )

                    test_api_endpoint = gr.Textbox(
                        value="http://localhost:1234/v1",
                        label="Test API Endpoint",
                        placeholder="http://localhost:1234/v1",
                    )

                    test_api_key = gr.Textbox(
                        label="Test API Key (optional)",
                        type="password",
                        placeholder="Enter API key if required",
                    )

                    test_config_save_btn = gr.Button(
                        "💾 Save Test Config", variant="primary"
                    )
                    test_config_status = gr.Textbox(
                        label="Test Config Status", interactive=False
                    )

        # Admin interface (only visible to admins)
        with gr.Row(visible=False) as admin_section:
            with gr.Tabs():
                with gr.TabItem("🛡️ Admin Panel"):
                    gr.Markdown("### System Administration")

                    with gr.Row():
                        # Tenant Management
                        with gr.Column():
                            gr.Markdown("#### Tenant Management")

                            tenant_name = gr.Textbox(
                                label="Tenant Name", placeholder="Company Name"
                            )
                            tenant_subdomain = gr.Textbox(
                                label="Subdomain", placeholder="company-slug"
                            )
                            tenant_max_users = gr.Number(
                                label="Max Users", value=100, precision=0
                            )
                            create_tenant_btn = gr.Button(
                                "🏢 Create Tenant", variant="primary"
                            )
                            tenant_status = gr.Textbox(
                                label="Tenant Status", interactive=False
                            )

                        # User Management
                        with gr.Column():
                            gr.Markdown("#### User Management")

                            user_tenant_selector = gr.Dropdown(
                                choices=[],
                                label="Select Tenant",
                                info="Choose tenant for new user",
                            )
                            user_email = gr.Textbox(
                                label="Email", placeholder="user@company.com"
                            )
                            user_password = gr.Textbox(
                                label="Password", type="password"
                            )
                            user_first_name = gr.Textbox(label="First Name")
                            user_last_name = gr.Textbox(label="Last Name")
                            user_role = gr.Dropdown(
                                choices=["user", "admin", "readonly"],
                                value="user",
                                label="Role",
                            )
                            create_user_btn = gr.Button(
                                "👤 Create User", variant="primary"
                            )
                            user_status = gr.Textbox(
                                label="User Status", interactive=False
                            )

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("#### Tenant Users")
                            refresh_users_btn = gr.Button("🔄 Refresh Users")
                            tenant_users_display = gr.Textbox(
                                label="Users in Selected Tenant",
                                lines=10,
                                interactive=False,
                                placeholder="Select a tenant to view users...",
                            )

        # Logout button
        logout_btn = gr.Button("🚪 Logout", variant="secondary", visible=False)

        # Language selector event handler
        language_selector.change(
            change_language,
            inputs=[language_selector],
            outputs=[
                auth_status,
                login_message,
                login_message,
                translation_section,
            ],  # Include translation section
        )

        # Event handlers for authentication
        login_btn.click(
            login_user,
            inputs=[login_email, login_password, login_subdomain],
            outputs=[
                login_section,
                main_section,
                admin_section,
                login_message,
                auth_status,
                session_token,
            ],
        ).then(lambda: gr.update(visible=True), outputs=logout_btn).then(
            get_langwatch_status_display, outputs=langwatch_status
        ).then(
            load_available_prompts, outputs=available_prompts_area
        )

        logout_btn.click(
            logout_user,
            inputs=[session_token],
            outputs=[
                login_section,
                main_section,
                admin_section,
                login_message,
                auth_status,
                session_token,
            ],
        ).then(lambda: gr.update(visible=False), outputs=logout_btn)

        sso_btn.click(handle_sso_login, inputs=[sso_subdomain], outputs=sso_message)

        # Event handlers for prompt management
        add_btn.click(
            add_new_prompt,
            inputs=[
                prompt_name,
                prompt_title,
                prompt_content,
                prompt_category,
                prompt_tags,
                is_enhancement_prompt,
            ],
            outputs=[
                prompt_status,
                prompts_display,
                category_filter,
                enhancement_prompt_selector,
                prompt_name,
                prompt_title,
                prompt_content,
                prompt_category,
                prompt_tags,
                is_enhancement_prompt,
            ],
        )

        load_edit_btn.click(
            load_prompt_for_editing,
            inputs=[edit_prompt_name],
            outputs=[
                prompt_name,
                prompt_title,
                prompt_content,
                prompt_category,
                prompt_tags,
                is_enhancement_prompt,
                edit_status,
            ],
        )

        update_btn.click(
            update_existing_prompt,
            inputs=[
                edit_prompt_name,
                prompt_name,
                prompt_title,
                prompt_content,
                prompt_category,
                prompt_tags,
                is_enhancement_prompt,
            ],
            outputs=[
                prompt_status,
                prompts_display,
                category_filter,
                enhancement_prompt_selector,
                prompt_name,
                prompt_title,
                prompt_content,
                prompt_category,
                prompt_tags,
                is_enhancement_prompt,
                edit_status,
            ],
        )

        delete_btn.click(
            delete_existing_prompt,
            inputs=[delete_prompt_name],
            outputs=[
                edit_status,
                prompts_display,
                category_filter,
                enhancement_prompt_selector,
            ],
        )

        clear_btn.click(
            lambda: ("", "", "", "", "", False, ""),
            outputs=[
                prompt_name,
                prompt_title,
                prompt_content,
                prompt_category,
                prompt_tags,
                is_enhancement_prompt,
                prompt_status,
            ],
        )

        # Event handler for token calculator
        calculate_tokens_btn.click(
            calculate_token_estimate,
            inputs=[prompt_content, calc_model, max_completion_tokens],
            outputs=token_calc_status,
        )

        # Event handler for translation
        translate_btn.click(
            translate_prompt_to_english,
            inputs=[prompt_content],
            outputs=[prompt_content, translation_status],
        )

        # Event handler for prompt testing
        test_btn.click(
            test_prompt_with_llm,
            inputs=[prompt_content, test_input],
            outputs=[test_output, test_status],
        )

        # Event handlers for LangWatch optimization
        optimize_btn.click(
            optimize_prompt_langwatch,
            inputs=[prompt_content, optimization_context, target_model],
            outputs=[
                optimization_results,
                optimization_status,
                optimized_prompt_display,
                optimization_score,
                optimization_suggestions,
                optimization_reasoning,
                langwatch_status,
            ],
        )

        accept_optimization_btn.click(
            accept_optimization,
            inputs=[optimized_prompt_display],
            outputs=[prompt_content, optimization_status],
        ).then(lambda: gr.update(visible=False), outputs=optimization_results)

        retry_optimization_btn.click(
            retry_optimization,
            inputs=[prompt_content, optimization_context, target_model],
            outputs=[
                optimization_results,
                optimization_status,
                optimized_prompt_display,
                optimization_score,
                optimization_suggestions,
                optimization_reasoning,
                langwatch_status,
            ],
        )

        reject_optimization_btn.click(
            reject_optimization, outputs=[optimization_results, optimization_status]
        )

        # Event handlers for library
        search_box.change(
            refresh_prompts_display,
            inputs=[search_box, category_filter],
            outputs=prompts_display,
        )

        category_filter.change(
            refresh_prompts_display,
            inputs=[search_box, category_filter],
            outputs=prompts_display,
        )

        refresh_btn.click(
            refresh_prompts_display,
            inputs=[search_box, category_filter],
            outputs=prompts_display,
        )

        # Event handlers for Prompt Builder
        builder_refresh_btn.click(
            load_available_prompts, outputs=available_prompts_area
        )

        clear_selection_btn.click(
            clear_selected_prompts,
            outputs=[selected_prompts_area, selected_prompts_list, preview_area],
        )

        combine_prompts_btn.click(
            combine_selected_prompts,
            inputs=[
                selected_prompts_list,
                template_selector,
                custom_separator,
                add_numbers,
            ],
            outputs=[builder_status, builder_state, selected_prompts_list],
        )

        update_preview_btn.click(
            update_builder_preview,
            inputs=[
                selected_prompts_list,
                template_selector,
                custom_separator,
                add_numbers,
            ],
            outputs=preview_area,
        )

        # Auto-update preview when template or options change
        template_selector.change(
            update_builder_preview,
            inputs=[
                selected_prompts_list,
                template_selector,
                custom_separator,
                add_numbers,
            ],
            outputs=preview_area,
        )

        custom_separator.change(
            update_builder_preview,
            inputs=[
                selected_prompts_list,
                template_selector,
                custom_separator,
                add_numbers,
            ],
            outputs=preview_area,
        )

        add_numbers.change(
            update_builder_preview,
            inputs=[
                selected_prompts_list,
                template_selector,
                custom_separator,
                add_numbers,
            ],
            outputs=preview_area,
        )

        open_in_editor_btn.click(
            open_combined_in_editor,
            inputs=[builder_state],
            outputs=[
                prompt_name,
                prompt_title,
                prompt_content,
                prompt_category,
                prompt_tags,
                is_enhancement_prompt,
                prompt_status,
            ],
        )

        # Event handlers for execution
        load_prompt_btn.click(
            select_prompt_for_execution,
            inputs=[load_prompt_name],
            outputs=execution_prompt,
        )

        execute_btn.click(
            execute_ai_prompt, inputs=[execution_prompt], outputs=ai_response
        )

        # Event handlers for enhancement
        load_original_btn.click(
            select_prompt_for_execution,
            inputs=[load_original_name],
            outputs=original_prompt,
        )

        enhance_btn.click(
            enhance_ai_prompt,
            inputs=[original_prompt, enhancement_prompt_selector],
            outputs=enhanced_prompt,
        )

        copy_enhanced_btn.click(
            lambda enhanced_text: enhanced_text,
            inputs=[enhanced_prompt],
            outputs=execution_prompt,
        )

        def save_enhanced_as_new(enhanced_text, name):
            if not enhanced_text.strip():
                return "No enhanced prompt to save!"

            if not name.strip():
                return "Please enter a name for the enhanced prompt!"

            if not prompt_manager.current_user:
                return "Error: User not authenticated!"

            data_manager = prompt_manager.get_data_manager()
            if not data_manager:
                return "Error: Data manager not available!"

            # Create title from name
            title = f"Enhanced: {name}"

            result = data_manager.add_prompt(
                name.strip(),
                title,
                enhanced_text,
                "Enhanced",
                "enhanced,improved",
                False,
            )
            return result

        save_enhanced_btn.click(
            save_enhanced_as_new,
            inputs=[enhanced_prompt, save_enhanced_name],
            outputs=enhancement_status,
        )

        # Event handlers for configuration
        config_save_btn.click(
            save_configuration,
            inputs=[service_type, api_endpoint, api_key, model_name],
            outputs=config_status,
        )

        enh_config_save_btn.click(
            save_enhancement_configuration,
            inputs=[
                enh_service_type,
                enh_api_endpoint,
                enh_api_key,
                enh_model_name,
                enh_prompt_dropdown,
            ],
            outputs=enh_config_status,
        )

        test_config_save_btn.click(
            save_test_configuration,
            inputs=[
                test_service_type,
                test_api_endpoint,
                test_api_key,
                test_model_name,
            ],
            outputs=test_config_status,
        )

        # Event handlers for API token management
        create_token_btn.click(
            create_new_api_token,
            inputs=[token_name, token_expires_days],
            outputs=[token_creation_status, new_token_display, api_tokens_display],
        )

        refresh_tokens_btn.click(
            refresh_api_tokens, outputs=[api_tokens_display, token_stats_display]
        )

        revoke_single_btn.click(
            revoke_api_token_by_id,
            inputs=[revoke_token_id],
            outputs=[token_creation_status, api_tokens_display],
        )

        revoke_all_btn.click(
            revoke_all_api_tokens, outputs=[token_creation_status, api_tokens_display]
        )

        # Event handlers for admin functions
        create_tenant_btn.click(
            admin_create_tenant,
            inputs=[tenant_name, tenant_subdomain, tenant_max_users],
            outputs=[
                tenant_status,
                user_tenant_selector,
                tenant_name,
                tenant_subdomain,
                tenant_max_users,
            ],
        )

        create_user_btn.click(
            admin_create_user,
            inputs=[
                user_tenant_selector,
                user_email,
                user_password,
                user_first_name,
                user_last_name,
                user_role,
            ],
            outputs=[
                user_status,
                tenant_users_display,
                user_email,
                user_password,
                user_first_name,
                user_last_name,
                user_role,
            ],
        )

        user_tenant_selector.change(
            admin_refresh_tenant_users,
            inputs=[user_tenant_selector],
            outputs=tenant_users_display,
        )

        refresh_users_btn.click(
            admin_refresh_tenant_users,
            inputs=[user_tenant_selector],
            outputs=tenant_users_display,
        )

        gr.Markdown(
            """
        ---
        **Multi-Tenant Features:**
        - 🔐 **Secure Authentication**: Email/password + SSO/ADFS support
        - 🏢 **Tenant Isolation**: Complete data separation between organizations
        - 👥 **User Management**: Role-based access control (admin, user, readonly)
        - 🛡️ **Admin Panel**: Tenant and user management for administrators
        - 🌐 **Local Development**: Localhost tenant with admin@localhost / admin123
        - 📊 **Session Management**: Secure JWT-based sessions with expiration

        **Instructions:**
        1. **Login**: Use email/password or SSO to authenticate
        2. **Tenant Context**: All prompts are isolated to your tenant
        3. **User Roles**: Admins can manage tenants and users
        4. **Configuration**: AI service configs are per-user
        5. **Data Isolation**: Complete separation between tenants

        **Local Development:**
        - Default admin: admin@localhost / admin123
        - Tenant: localhost (automatically created)
        - Access admin panel with admin credentials
        """
        )

    return app


# Launch the application
if __name__ == "__main__":
    app = create_interface()
    app.launch(
        server_name="0.0.0.0", server_port=7860, share=False, show_error=True
    )  # nosec B104: Binding to all interfaces is intentional for web application deployment
