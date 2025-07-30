"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Internationalization (i18n) system for AI Prompt Manager
Multi-language support with dynamic label switching

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

from typing import Dict


class I18nManager:
    """
    Internationalization manager for multi-language support
    Supports dynamic language switching and fallback to English
    """

    def __init__(self, default_language: str = "en"):
        # Check for environment variable override
        import os

        env_lang = os.getenv("DEFAULT_LANGUAGE", "").lower()
        if env_lang and env_lang in [
            "en",
            "es",
            "fr",
            "de",
            "zh",
            "ja",
            "pt",
            "ru",
            "ar",
            "hi",
        ]:
            default_language = env_lang

        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_translations()

    def load_translations(self):
        """Load all available translation files"""
        # Base translations embedded in code for reliability
        self.translations = {
            "en": self._get_english_translations(),
            "es": self._get_spanish_translations(),
            "fr": self._get_french_translations(),
            "de": self._get_german_translations(),
            "zh": self._get_chinese_translations(),
            "ja": self._get_japanese_translations(),
            "pt": self._get_portuguese_translations(),
            "ru": self._get_russian_translations(),
            "ar": self._get_arabic_translations(),
            "hi": self._get_hindi_translations(),
        }

    def set_language(self, language_code: str) -> bool:
        """Set current language, returns True if successful"""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False

    def get_available_languages(self) -> Dict[str, str]:
        """Get list of available languages with native names"""
        return {
            "en": "English",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
            "zh": "中文",
            "ja": "日本語",
            "pt": "Português",
            "ru": "Русский",
            "ar": "العربية",
            "hi": "हिन्दी",
        }

    def t(self, key: str, **kwargs) -> str:
        """
        Translate a key to current language with optional formatting

        Args:
            key: Translation key (e.g., 'login.title')
            **kwargs: Optional formatting parameters

        Returns:
            Translated string or key if not found
        """
        # Get translation from current language or fallback to English
        current_trans = self.translations.get(self.current_language, {})
        english_trans = self.translations.get(self.default_language, {})

        # Try current language first, then English, then return key
        text = current_trans.get(key) or english_trans.get(key) or key

        # Format with provided kwargs if any
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass  # Return unformatted text if formatting fails

        return text

    def _get_english_translations(self) -> Dict[str, str]:
        """English translations (base language)"""
        return {
            # Application
            "app.title": "AI Prompt Manager",
            "app.subtitle": "Secure, multi-tenant AI prompt management",
            "app.status.authenticated": "✅ Authenticated as {user}",
            "app.status.not_authenticated": "❌ Not authenticated",
            # Navigation
            "nav.home": "Home",
            "nav.prompts": "Prompts",
            "nav.builder": "Builder",
            "nav.library": "Library",
            "nav.tokens": "Tokens",
            "nav.services": "Services",
            "nav.settings": "Settings",
            "nav.admin": "Admin",
            # Authentication
            "auth.login": "Login",
            "auth.logout": "Logout",
            "auth.email": "Email",
            "auth.password": "Password",
            "auth.tenant": "Tenant",
            "auth.sso": "SSO Login",
            "auth.welcome": "Welcome, {name}!",
            "auth.invalid": "Invalid credentials",
            "auth.signin": "Sign in to your account",
            "auth.error": "Authentication Error",
            "auth.organization": "Organization",
            "auth.organization_placeholder": "Organization subdomain",
            "auth.organization_help": (
                "Enter your organization's subdomain "
                "(use 'localhost' for local development)"
            ),
            "auth.email_placeholder": "you@example.com",
            "auth.password_placeholder": "Enter your password",
            "auth.remember": "Remember me",
            "auth.forgot_password": "Forgot password?",
            "auth.need_account": "Need an account?",
            "auth.create_account": "Create new account",
            # Dashboard
            "dashboard.title": "Dashboard",
            "dashboard.admin_title": "Admin Dashboard",
            "dashboard.admin_subtitle": "Manage users, tenants, and system settings",
            "dashboard.welcome_back": "Welcome back, {name}!",
            "dashboard.welcome": "Welcome to AI Prompt Manager!",
            "dashboard.subtitle": "Ready to create and manage your AI prompts",
            "dashboard.quick_actions": "Quick Actions",
            "dashboard.recent_prompts": "Recent Prompts",
            "dashboard.recent_activity": "Recent Activity",
            "dashboard.no_activity": "No recent activity",
            "dashboard.no_prompts": "No prompts yet",
            "dashboard.no_prompts_desc": "Get started by creating your first prompt",
            "dashboard.view_all": "View all",
            "dashboard.create_first": "Create Your First Prompt",
            "dashboard.create_new": "Create New",
            "dashboard.new_prompt": "New Prompt",
            "dashboard.browse": "Browse",
            "dashboard.configure": "Configure",
            "dashboard.recently_created": "Recently created",
            # Statistics
            "stats.total_users": "Total Users",
            "stats.active_tenants": "Active Tenants",
            "stats.total_prompts": "Total Prompts",
            "stats.api_tokens": "API Tokens",
            "stats.templates": "Templates",
            # Admin sections
            "admin.overview": "Overview",
            "admin.users": "Users",
            "admin.tenants": "Tenants",
            "admin.system": "System",
            "admin.user_management": "User Management",
            "admin.tenant_management": "Tenant Management",
            "admin.system_info": "System Information",
            "admin.system_actions": "System Actions",
            "admin.add_user": "Add User",
            "admin.add_tenant": "Add Tenant",
            "admin.no_users": "No users found",
            "admin.no_tenants": "No tenants found",
            # User table headers
            "table.user": "User",
            "table.role": "Role",
            "table.tenant": "Tenant",
            "table.last_login": "Last Login",
            "table.status": "Status",
            "table.actions": "Actions",
            "table.subdomain": "Subdomain",
            "table.users": "Users",
            "table.created": "Created",
            # System info
            "system.version": "Version",
            "system.database": "Database",
            "system.multitenant": "Multi-tenant",
            "system.api": "API",
            "system.uptime": "Uptime",
            "system.environment": "Environment",
            "system.enabled": "Enabled",
            "system.disabled": "Disabled",
            "system.backup": "Backup Database",
            "system.backup_desc": "Create a backup of the current database",
            "system.clear_cache": "Clear Cache",
            "system.clear_cache_desc": "Clear application cache and temporary files",
            # Getting started tips
            "tips.title": "Getting Started Tips",
            "tips.create_title": "Create Your First Prompt",
            "tips.create_desc": (
                "Start by creating a prompt for your most common AI task"
            ),
            "tips.templates_title": "Use Templates",
            "tips.templates_desc": (
                "Browse our template library for proven prompt patterns"
            ),
            "tips.test_title": "Test & Optimize",
            "tips.test_desc": "Use our built-in testing tools to refine your prompts",
            "tips.organize_title": "Organize with Categories",
            "tips.organize_desc": (
                "Keep your prompts organized using categories and tags"
            ),
            # Prompts
            "prompt.name": "Name",
            "prompt.title": "Title",
            "prompt.category": "Category",
            "prompt.content": "Content",
            "prompt.tags": "Tags",
            "prompt.description": "Description",
            "prompt.add": "Add",
            "prompt.create": "Create Prompt",
            "prompt.create_new": "Create New Prompt",
            "prompt.create_desc": "Create a new AI prompt for your library",
            "prompt.edit": "Edit Prompt",
            "prompt.edit_desc": "Update your existing prompt",
            "prompt.update": "Update Prompt",
            "prompt.delete": "Delete",
            "prompt.clear": "Clear",
            "prompt.load": "Load",
            "prompt.search": "Search",
            "prompt.enhancement": "Enhancement Prompt",
            "prompt.name_placeholder": ("Enter a descriptive name for your prompt"),
            "prompt.name_help": "Give your prompt a clear, descriptive name",
            "prompt.category_select": "Select a category",
            "prompt.category_add": "+ Add New Category",
            "prompt.category_name": "Category Name",
            "prompt.category_name_placeholder": "Enter category name",
            "prompt.tags_placeholder": "tag1, tag2, tag3",
            "prompt.tags_help": "Separate tags with commas",
            "prompt.description_placeholder": (
                "Brief description of what this prompt does..."
            ),
            "prompt.description_help": (
                "Optional: Describe the purpose and expected output of this prompt"
            ),
            "prompt.content_placeholder": (
                "Enter your AI prompt here...\n\n"
                "You can use variables like {variable_name} that will be replaced "
                "when the prompt is executed.\n\n"
                "Example:\nWrite a {tone} email to {recipient} about {topic}.\n"
                "Keep it {length} and include {key_points}."
            ),
            "prompt.variables_help": "Use {variable_name} syntax for dynamic variables",
            "prompt.insert_template": "Insert Template",
            "prompt.variables": "Variables",
            "prompt.characters": "characters",
            "prompt.tokens": "tokens",
            "prompt.variable_guide": "Variable Usage Guide",
            "prompt.basic_variables": "Basic Variables",
            "prompt.basic_variables_desc": (
                "Use curly braces to define variables: {variable_name}"
            ),
            "prompt.common_variables": "Common Variables",
            "prompt.execute": "Execute",
            "prompt.more_tags": "more",
            "prompt.no_prompts": "No prompts found",
            "prompt.no_prompts_desc": "Get started by creating your first prompt",
            "prompt.no_prompts_search_desc": (
                "Try adjusting your search or create a new prompt"
            ),
            "prompt.create_first": "Create Your First Prompt",
            "prompt.showing": "Showing",
            "prompt.to": "to",
            "prompt.of": "of",
            "prompt.results": "results",
            "prompt.manage_desc": "Manage your AI prompts and templates",
            "prompt.search_placeholder": "Search prompts...",
            "prompt.all_categories": "All Categories",
            "prompt.sort_newest": "Newest First",
            "prompt.sort_oldest": "Oldest First",
            "prompt.sort_name_asc": "Name A-Z",
            "prompt.sort_name_desc": "Name Z-A",
            "prompt.sort_category": "Category A-Z",
            # Prompt Builder
            "builder.title": "Prompt Builder",
            "builder.subtitle": (
                "Combine multiple prompts using drag-and-drop to create "
                "sophisticated workflows"
            ),
            "builder.available_prompts": "Available Prompts",
            "builder.selected_prompts": "Selected Prompts",
            "builder.selected_prompts_desc": (
                "Drag prompts here or click to select. Drag to reorder."
            ),
            "builder.combination_template": "Combination Template",
            "builder.combination_template_desc": (
                "Choose how to combine your selected prompts"
            ),
            "builder.search_prompts": "Search prompts...",
            "builder.all_categories": "All Categories",
            "builder.no_prompts": "No prompts available",
            "builder.create_first_prompt": "Create your first prompt",
            "builder.drag_here": "Drag prompts here to combine them",
            "builder.click_to_select": "Or click prompts to select them",
            "builder.prompts_selected": "prompts selected",
            "builder.prompt_selected": "prompt selected",
            "builder.clear_all": "Clear All",
            "builder.preview": "Preview",
            "builder.refresh_preview": "Refresh Preview",
            "builder.combine_prompts": "Combine Prompts",
            "builder.select_prompts_preview": "Select prompts to see preview...",
            "builder.characters": "characters",
            "builder.tokens_estimated": "tokens (estimated)",
            "builder.source_prompts": "source prompts",
            "builder.chars": "chars",
            # Builder Templates
            "builder.template.sequential": "Sequential",
            "builder.template.sequential_desc": (
                "Combine prompts one after another with clear separation"
            ),
            "builder.template.sections": "Sections",
            "builder.template.sections_desc": (
                "Create distinct sections with headers for each prompt"
            ),
            "builder.template.layered": "Layered",
            "builder.template.layered_desc": (
                "Build context in layers with base + additional layers"
            ),
            "builder.template.custom": "Custom",
            "builder.template.custom_desc": (
                "Use your own formatting template with placeholders"
            ),
            # Builder Options
            "builder.custom_separator": "Custom Separator",
            "builder.add_numbers": "Add sequence numbers",
            "builder.custom_template": "Custom Template",
            "builder.custom_template_placeholder": (
                "Use {content}, {name}, {title}, {category}, {tags} as placeholders"
            ),
            "builder.available_placeholders": (
                "Available placeholders: {content}, {name}, {title}, {category}, {tags}"
            ),
            # Builder Actions & Messages
            "builder.min_prompts_required": (
                "Please select at least 2 prompts to combine"
            ),
            "builder.combined_prompt_name": "Combined Prompt ({count} parts)",
            "builder.combined_category": "Combined",
            "builder.combined_description": "Combined prompt created from: {sources}",
            "builder.combined_tags_suffix": "combined, {count}-part",
            # Actions
            "action.save": "Save",
            "action.cancel": "Cancel",
            "action.refresh": "Refresh",
            "action.edit": "Edit",
            "action.view": "View",
            "action.copy": "Copy",
            "action.export": "Export",
            "action.import": "Import",
            "action.translate": "Translate",
            "action.optimize": "Optimize",
            "action.preview": "Preview",
            "action.test": "Test",
            "action.close": "Close",
            "action.previous": "Previous",
            "action.next": "Next",
            # Status
            "status.success": "Success",
            "status.error": "Error",
            "status.loading": "Loading...",
            "status.saved": "Saved successfully",
            "status.deleted": "Deleted successfully",
            # Calculator
            "calc.title": "Token Calculator",
            "calc.model": "Model",
            "calc.tokens": "Tokens",
            "calc.cost": "Cost",
            "calc.estimate": "Estimate",
            "calc.input": "Input",
            "calc.output": "Output",
            # Optimization
            "opt.title": "Optimization",
            "opt.context": "Context",
            "opt.target": "Target Model",
            "opt.optimize": "Optimize",
            "opt.score": "Score",
            "opt.suggestions": "Suggestions",
            "opt.accept": "Accept",
            "opt.reject": "Reject",
            "opt.retry": "Retry",
            # Forms
            "form.required": "Required",
            "form.optional": "Optional",
            "form.placeholder.name": "Enter name",
            "form.placeholder.search": "Search...",
            "form.placeholder.email": "user@domain.com",
            # Messages
            "msg.select_item": "Please select an item",
            "msg.confirm_delete": "Are you sure you want to delete this?",
            "msg.no_results": "No results found",
            "msg.loading_data": "Loading data...",
            # Translation
            "translate.to_english": "Translate to English",
            "translate.status": "Translation Status",
            "translate.help": (
                "Translate your prompt to English for better AI enhancement"
            ),
            # Testing
            "test.prompt": "Test Prompt",
            "test.status": "Test Status",
            # Prompt Builder
            "builder.title": "Prompt Builder",
            "builder.available": "Available Prompts",
            "builder.selected": "Selected Prompts",
            "builder.preview": "Preview",
            "builder.template": "Combination Template",
            "builder.template.sequential": "Sequential",
            "builder.template.sequential.desc": "Combine prompts one after another",
            "builder.template.sections": "Sections",
            "builder.template.sections.desc": "Combine prompts as distinct sections",
            "builder.template.layered": "Layered",
            "builder.template.layered.desc": "Build context in layers",
            "builder.template.custom": "Custom",
            "builder.template.custom.desc": "Use custom formatting template",
            "builder.combine": "Combine Prompts",
            "builder.clear": "Clear Selection",
            "builder.edit": "Open in Editor",
            "builder.error.no_prompts": "No prompts selected",
            "builder.error.min_prompts": "Select at least 2 prompts",
            "builder.error.duplicates": "Duplicate prompts found",
            "builder.error.too_long": "Combined prompt too long",
            "builder.error.combination": "Combination failed",
            "builder.preview.empty": "Select prompts to see preview",
            "builder.preview.error": "Preview error",
            "builder.drag.add": "Drag here to add",
            "builder.drag.reorder": "Drag to reorder",
            "builder.search.placeholder": "Search prompts...",
            "builder.filter.category": "Filter by category",
            "builder.filter.all": "All Categories",
            # Templates
            "template.title": "Template",
            "template.name": "Template Name",
            "template.description": "Description",
            "template.content": "Template Content",
            "template.variables": "Variables",
            "template.category": "Category",
            "template.create": "Create Template",
            "template.edit": "Edit Template",
            "template.delete": "Delete Template",
            "template.use": "Use Template",
            "template.preview": "Preview",
            "template.validate": "Validate",
            "template.save": "Save Template",
            "template.cancel": "Cancel",
            "template.list": "Templates",
            "template.custom": "Custom Templates",
            "template.builtin": "Built-in Templates",
            "template.new": "New Template",
            "template.empty": "No templates found",
            "template.empty_desc": "Create your first template to get started",
            "template.validation_error": "Template validation failed",
            "template.saved_success": "Template saved successfully",
            "template.deleted_success": "Template deleted successfully",
            "template.name_placeholder": "Enter template name",
            "template.description_placeholder": "Describe what this template is for",
            "template.content_placeholder": (
                "Enter your template content with variables like {variable_name}"
            ),
            "template.variables_help": (
                "Variables found in your template will appear here"
            ),
            "template.category_help": "Choose a category to organize your templates",
            # Template categories
            "template.category.business": "Business",
            "template.category.technical": "Technical",
            "template.category.creative": "Creative",
            "template.category.analytical": "Analytical",
            "template.category.custom": "Custom",
            "template.category.general": "General",
            # Settings
            "settings.profile": "Profile",
            "settings.profile_desc": "Update your personal information",
            "settings.api_tokens": "API Tokens",
            "settings.api_tokens_desc": "Manage your API access tokens",
            "settings.ai_services": "AI Services",
            "settings.ai_services_desc": "Configure AI provider settings",
            "settings.security": "Security",
            "settings.security_desc": "Password and security settings",
            "settings.preferences": "Preferences",
            "settings.preferences_desc": "UI and notification preferences",
            "settings.export_import": "Export/Import",
            "settings.export_import_desc": "Backup and restore your data",
            "settings.account_info": "Account Information",
            "settings.name": "Name",
            "settings.email": "Email",
            "settings.role": "Role",
            "settings.member_since": "Member Since",
            "settings.recently": "Recently",
        }

    def _get_spanish_translations(self) -> Dict[str, str]:
        """Spanish translations"""
        return {
            # Application
            "app.title": "Gestor de Prompts IA",
            "app.subtitle": "Gestión segura y multi-inquilino de prompts IA",
            "app.status.authenticated": "✅ Autenticado como {user}",
            "app.status.not_authenticated": "❌ No autenticado",
            # Navigation
            "nav.home": "Inicio",
            "nav.prompts": "Prompts",
            "nav.builder": "Constructor",
            "nav.library": "Biblioteca",
            "nav.tokens": "Tokens",
            "nav.services": "Servicios",
            "nav.settings": "Configuración",
            "nav.admin": "Admin",
            # Authentication
            "auth.login": "Iniciar Sesión",
            "auth.logout": "Cerrar Sesión",
            "auth.email": "Correo",
            "auth.password": "Contraseña",
            "auth.tenant": "Inquilino",
            "auth.sso": "Login SSO",
            "auth.welcome": "¡Bienvenido, {name}!",
            "auth.invalid": "Credenciales inválidas",
            "auth.signin": "Inicia sesión en tu cuenta",
            "auth.error": "Error de Autenticación",
            "auth.organization": "Organización",
            "auth.organization_placeholder": "Subdominio de la organización",
            "auth.organization_help": (
                "Ingresa el subdominio de tu organización "
                "(usa 'localhost' para desarrollo local)"
            ),
            "auth.email_placeholder": "tu@ejemplo.com",
            "auth.password_placeholder": "Ingresa tu contraseña",
            "auth.remember": "Recordarme",
            "auth.forgot_password": "¿Olvidaste tu contraseña?",
            "auth.need_account": "¿Necesitas una cuenta?",
            "auth.create_account": "Crear nueva cuenta",
            # Dashboard
            "dashboard.title": "Panel",
            "dashboard.admin_title": "Panel de Administración",
            "dashboard.admin_subtitle": (
                "Gestionar usuarios, inquilinos y configuración del sistema"
            ),
            "dashboard.welcome_back": "¡Bienvenido de nuevo, {name}!",
            "dashboard.welcome": "¡Bienvenido a AI Prompt Manager!",
            "dashboard.subtitle": "Listo para crear y gestionar tus prompts de IA",
            "dashboard.quick_actions": "Acciones Rápidas",
            "dashboard.recent_prompts": "Prompts Recientes",
            "dashboard.recent_activity": "Actividad Reciente",
            "dashboard.no_activity": "Sin actividad reciente",
            "dashboard.no_prompts": "Aún no hay prompts",
            "dashboard.no_prompts_desc": "Comienza creando tu primer prompt",
            "dashboard.view_all": "Ver todo",
            "dashboard.create_first": "Crear Tu Primer Prompt",
            "dashboard.create_new": "Crear Nuevo",
            "dashboard.new_prompt": "Nuevo Prompt",
            "dashboard.browse": "Explorar",
            "dashboard.configure": "Configurar",
            "dashboard.recently_created": "Creado recientemente",
            # Statistics
            "stats.total_users": "Total de Usuarios",
            "stats.active_tenants": "Inquilinos Activos",
            "stats.total_prompts": "Total de Prompts",
            "stats.api_tokens": "Tokens API",
            "stats.templates": "Plantillas",
            # Admin sections
            "admin.overview": "Resumen",
            "admin.users": "Usuarios",
            "admin.tenants": "Inquilinos",
            "admin.system": "Sistema",
            "admin.user_management": "Gestión de Usuarios",
            "admin.tenant_management": "Gestión de Inquilinos",
            "admin.system_info": "Información del Sistema",
            "admin.system_actions": "Acciones del Sistema",
            "admin.add_user": "Agregar Usuario",
            "admin.add_tenant": "Agregar Inquilino",
            "admin.no_users": "No se encontraron usuarios",
            "admin.no_tenants": "No se encontraron inquilinos",
            # User table headers
            "table.user": "Usuario",
            "table.role": "Rol",
            "table.tenant": "Inquilino",
            "table.last_login": "Último Acceso",
            "table.status": "Estado",
            "table.actions": "Acciones",
            "table.subdomain": "Subdominio",
            "table.users": "Usuarios",
            "table.created": "Creado",
            # System info
            "system.version": "Versión",
            "system.database": "Base de Datos",
            "system.multitenant": "Multi-inquilino",
            "system.api": "API",
            "system.uptime": "Tiempo Activo",
            "system.environment": "Entorno",
            "system.enabled": "Habilitado",
            "system.disabled": "Deshabilitado",
            "system.backup": "Respaldar Base de Datos",
            "system.backup_desc": "Crear un respaldo de la base de datos actual",
            "system.clear_cache": "Limpiar Caché",
            "system.clear_cache_desc": (
                "Limpiar caché de aplicación y archivos temporales"
            ),
            # Getting started tips
            "tips.title": "Consejos para Comenzar",
            "tips.create_title": "Crear Tu Primer Prompt",
            "tips.create_desc": (
                "Comienza creando un prompt para tu tarea de IA más común"
            ),
            "tips.templates_title": "Usar Plantillas",
            "tips.templates_desc": (
                "Explora nuestra biblioteca de plantillas con patrones probados"
            ),
            "tips.test_title": "Probar y Optimizar",
            "tips.test_desc": (
                "Usa nuestras herramientas integradas para refinar tus prompts"
            ),
            "tips.organize_title": "Organizar con Categorías",
            "tips.organize_desc": (
                "Mantén tus prompts organizados usando categorías y etiquetas"
            ),
            # Prompts
            "prompt.name": "Nombre",
            "prompt.title": "Título",
            "prompt.category": "Categoría",
            "prompt.content": "Contenido",
            "prompt.tags": "Etiquetas",
            "prompt.add": "Agregar",
            "prompt.update": "Actualizar",
            "prompt.delete": "Eliminar",
            "prompt.clear": "Limpiar",
            "prompt.load": "Cargar",
            "prompt.search": "Buscar",
            "prompt.enhancement": "Prompt de Mejora",
            # Actions
            "action.save": "Guardar",
            "action.cancel": "Cancelar",
            "action.refresh": "Actualizar",
            "action.edit": "Editar",
            "action.view": "Ver",
            "action.copy": "Copiar",
            "action.export": "Exportar",
            "action.import": "Importar",
            # Status
            "status.success": "Éxito",
            "status.error": "Error",
            "status.loading": "Cargando...",
            "status.saved": "Guardado exitosamente",
            "status.deleted": "Eliminado exitosamente",
            # Calculator
            "calc.title": "Calculadora de Tokens",
            "calc.model": "Modelo",
            "calc.tokens": "Tokens",
            "calc.cost": "Costo",
            "calc.estimate": "Estimar",
            "calc.input": "Entrada",
            "calc.output": "Salida",
            # Optimization
            "opt.title": "Optimización",
            "opt.context": "Contexto",
            "opt.target": "Modelo Objetivo",
            "opt.optimize": "Optimizar",
            "opt.score": "Puntuación",
            "opt.suggestions": "Sugerencias",
            "opt.accept": "Aceptar",
            "opt.reject": "Rechazar",
            "opt.retry": "Reintentar",
            # Forms
            "form.required": "Requerido",
            "form.optional": "Opcional",
            "form.placeholder.name": "Ingrese nombre",
            "form.placeholder.search": "Buscar...",
            "form.placeholder.email": "usuario@dominio.com",
            # Messages
            "msg.select_item": "Por favor seleccione un elemento",
            "msg.confirm_delete": "¿Está seguro de que desea eliminar esto?",
            "msg.no_results": "No se encontraron resultados",
            "msg.loading_data": "Cargando datos...",
            # Translation
            "translate.to_english": "Traducir al Inglés",
            "translate.status": "Estado de Traducción",
            "translate.help": (
                "Traduzca su prompt al inglés para una mejor mejora con IA"
            ),
            # Prompt Builder
            "builder.title": "Constructor de Prompts",
            "builder.available": "Prompts Disponibles",
            "builder.selected": "Prompts Seleccionados",
            "builder.preview": "Vista Previa",
            "builder.template": "Plantilla de Combinación",
            "builder.template.sequential": "Secuencial",
            "builder.template.sequential.desc": "Combinar prompts uno tras otro",
            "builder.template.sections": "Secciones",
            "builder.template.sections.desc": (
                "Combinar prompts como secciones distintas"
            ),
            "builder.template.layered": "Por Capas",
            "builder.template.layered.desc": "Construir contexto en capas",
            "builder.template.custom": "Personalizado",
            "builder.template.custom.desc": "Usar plantilla de formato personalizada",
            "builder.combine": "Combinar Prompts",
            "builder.clear": "Limpiar Selección",
            "builder.edit": "Abrir en Editor",
            "builder.error.no_prompts": "No hay prompts seleccionados",
            "builder.error.min_prompts": "Seleccione al menos 2 prompts",
            "builder.error.duplicates": "Se encontraron prompts duplicados",
            "builder.error.too_long": "Prompt combinado demasiado largo",
            "builder.error.combination": "Falló la combinación",
            "builder.preview.empty": "Seleccione prompts para ver vista previa",
            "builder.preview.error": "Error de vista previa",
            "builder.drag.add": "Arrastre aquí para agregar",
            "builder.drag.reorder": "Arrastre para reordenar",
            "builder.search.placeholder": "Buscar prompts...",
            "builder.filter.category": "Filtrar por categoría",
            "builder.filter.all": "Todas las Categorías",
            # Templates
            "template.title": "Plantilla",
            "template.name": "Nombre de la Plantilla",
            "template.description": "Descripción",
            "template.content": "Contenido de la Plantilla",
            "template.variables": "Variables",
            "template.category": "Categoría",
            "template.create": "Crear Plantilla",
            "template.edit": "Editar Plantilla",
            "template.delete": "Eliminar Plantilla",
            "template.use": "Usar Plantilla",
            "template.preview": "Vista Previa",
            "template.validate": "Validar",
            "template.save": "Guardar Plantilla",
            "template.cancel": "Cancelar",
            "template.list": "Plantillas",
            "template.custom": "Plantillas Personalizadas",
            "template.builtin": "Plantillas Integradas",
            "template.new": "Nueva Plantilla",
            "template.empty": "No se encontraron plantillas",
            "template.empty_desc": "Crea tu primera plantilla para comenzar",
            "template.validation_error": "Falló la validación de la plantilla",
            "template.saved_success": "Plantilla guardada exitosamente",
            "template.deleted_success": "Plantilla eliminada exitosamente",
            "template.name_placeholder": "Ingresa el nombre de la plantilla",
            "template.description_placeholder": "Describe para qué es esta plantilla",
            "template.content_placeholder": (
                "Ingresa el contenido de tu plantilla con variables como "
                "{nombre_variable}"
            ),
            "template.variables_help": (
                "Las variables encontradas en tu plantilla aparecerán aquí"
            ),
            "template.category_help": (
                "Elige una categoría para organizar tus plantillas"
            ),
            # Template categories
            "template.category.business": "Negocios",
            "template.category.technical": "Técnico",
            "template.category.creative": "Creativo",
            "template.category.analytical": "Analítico",
            "template.category.custom": "Personalizado",
            "template.category.general": "General",
            # Settings
            "settings.profile": "Perfil",
            "settings.profile_desc": "Actualiza tu información personal",
            "settings.api_tokens": "Tokens API",
            "settings.api_tokens_desc": "Gestiona tus tokens de acceso API",
            "settings.ai_services": "Servicios IA",
            "settings.ai_services_desc": "Configura los proveedores de IA",
            "settings.security": "Seguridad",
            "settings.security_desc": "Configuración de contraseña y seguridad",
            "settings.preferences": "Preferencias",
            "settings.preferences_desc": "Preferencias de UI y notificaciones",
            "settings.export_import": "Exportar/Importar",
            "settings.export_import_desc": "Respalda y restaura tus datos",
            "settings.account_info": "Información de la Cuenta",
            "settings.name": "Nombre",
            "settings.email": "Correo",
            "settings.role": "Rol",
            "settings.member_since": "Miembro Desde",
            "settings.recently": "Recientemente",
            # Prompt Builder
            "builder.title": "Constructor de Prompts",
            "builder.subtitle": (
                "Combina múltiples prompts usando arrastrar y soltar para "
                "crear flujos sofisticados"
            ),
            "builder.available_prompts": "Prompts Disponibles",
            "builder.selected_prompts": "Prompts Seleccionados",
            "builder.selected_prompts_desc": (
                "Arrastra prompts aquí o haz clic para seleccionar. "
                "Arrastra para reordenar."
            ),
            "builder.combination_template": "Plantilla de Combinación",
            "builder.combination_template_desc": (
                "Elige cómo combinar tus prompts seleccionados"
            ),
            "builder.search_prompts": "Buscar prompts...",
            "builder.all_categories": "Todas las Categorías",
            "builder.no_prompts": "No hay prompts disponibles",
            "builder.create_first_prompt": "Crea tu primer prompt",
            "builder.drag_here": "Arrastra prompts aquí para combinarlos",
            "builder.click_to_select": "O haz clic en prompts para seleccionarlos",
            "builder.prompts_selected": "prompts seleccionados",
            "builder.prompt_selected": "prompt seleccionado",
            "builder.clear_all": "Limpiar Todo",
            "builder.preview": "Vista Previa",
            "builder.refresh_preview": "Actualizar Vista Previa",
            "builder.combine_prompts": "Combinar Prompts",
            "builder.select_prompts_preview": (
                "Selecciona prompts para ver la vista previa..."
            ),
            "builder.characters": "caracteres",
            "builder.tokens_estimated": "tokens (estimado)",
            "builder.source_prompts": "prompts fuente",
            "builder.chars": "caract",
            # Builder Templates
            "builder.template.sequential": "Secuencial",
            "builder.template.sequential_desc": (
                "Combinar prompts uno tras otro con separación clara"
            ),
            "builder.template.sections": "Secciones",
            "builder.template.sections_desc": (
                "Crear secciones distintas con encabezados para cada prompt"
            ),
            "builder.template.layered": "Por Capas",
            "builder.template.layered_desc": (
                "Construir contexto en capas con base + capas adicionales"
            ),
            "builder.template.custom": "Personalizado",
            "builder.template.custom_desc": (
                "Usa tu propia plantilla de formato con marcadores de posición"
            ),
            # Builder Options
            "builder.custom_separator": "Separador Personalizado",
            "builder.add_numbers": "Agregar números de secuencia",
            "builder.custom_template": "Plantilla Personalizada",
            "builder.custom_template_placeholder": (
                "Usa {content}, {name}, {title}, {category}, {tags} como marcadores"
            ),
            "builder.available_placeholders": (
                "Marcadores disponibles: {content}, {name}, {title}, {category}, {tags}"
            ),
            # Builder Actions & Messages
            "builder.min_prompts_required": (
                "Por favor selecciona al menos 2 prompts para combinar"
            ),
            "builder.combined_prompt_name": "Prompt Combinado ({count} partes)",
            "builder.combined_category": "Combinado",
            "builder.combined_description": "Prompt combinado creado de: {sources}",
            "builder.combined_tags_suffix": "combinado, {count}-partes",
        }

    def _get_french_translations(self) -> Dict[str, str]:
        """French translations"""
        return {
            # Application
            "app.title": "Gestionnaire de Prompts IA",
            "app.subtitle": "Gestion sécurisée et multi-locataire de prompts IA",
            "app.status.authenticated": "✅ Authentifié en tant que {user}",
            "app.status.not_authenticated": "❌ Non authentifié",
            # Navigation
            "nav.home": "Accueil",
            "nav.prompts": "Prompts",
            "nav.builder": "Constructeur",
            "nav.library": "Bibliothèque",
            "nav.tokens": "Jetons",
            "nav.services": "Services",
            "nav.settings": "Paramètres",
            "nav.admin": "Admin",
            # Authentication
            "auth.login": "Connexion",
            "auth.logout": "Déconnexion",
            "auth.email": "Email",
            "auth.password": "Mot de passe",
            "auth.tenant": "Locataire",
            "auth.sso": "Connexion SSO",
            "auth.welcome": "Bienvenue, {name}!",
            "auth.invalid": "Identifiants invalides",
            # Dashboard (basic keys)
            "dashboard.welcome_back": "Bon retour, {name}!",
            "dashboard.welcome": "Bienvenue dans AI Prompt Manager!",
            "dashboard.subtitle": "Prêt à créer et gérer vos prompts IA",
            "dashboard.create_new": "Créer Nouveau",
            "dashboard.new_prompt": "Nouveau Prompt",
            "dashboard.browse": "Parcourir",
            "dashboard.configure": "Configurer",
            "dashboard.recent_prompts": "Prompts Récents",
            "dashboard.view_all": "Voir tout",
            "dashboard.recently_created": "Créé récemment",
            "stats.total_prompts": "Total Prompts",
            "stats.templates": "Modèles",
            "tips.title": "Conseils pour Commencer",
            "tips.create_title": "Créer Votre Premier Prompt",
            "tips.create_desc": (
                "Commencez par créer un prompt pour votre tâche IA la plus courante"
            ),
            "tips.templates_title": "Utiliser les Modèles",
            "tips.templates_desc": (
                "Parcourez notre bibliothèque de modèles avec des patterns éprouvés"
            ),
            "tips.test_title": "Tester et Optimiser",
            "tips.test_desc": "Utilisez nos outils intégrés pour affiner vos prompts",
            "tips.organize_title": "Organiser avec des Catégories",
            "tips.organize_desc": (
                "Gardez vos prompts organisés en utilisant des catégories et "
                "des étiquettes"
            ),
            "dashboard.no_prompts": "Aucun prompt encore",
            "dashboard.no_prompts_desc": "Commencez par créer votre premier prompt",
            "dashboard.create_first": "Créer Votre Premier Prompt",
            # Prompts
            "prompt.name": "Nom",
            "prompt.title": "Titre",
            "prompt.category": "Catégorie",
            "prompt.content": "Contenu",
            "prompt.tags": "Étiquettes",
            "prompt.add": "Ajouter",
            "prompt.update": "Mettre à jour",
            "prompt.delete": "Supprimer",
            "prompt.clear": "Effacer",
            "prompt.load": "Charger",
            "prompt.search": "Rechercher",
            "prompt.enhancement": "Prompt d'Amélioration",
            # Actions
            "action.save": "Sauvegarder",
            "action.cancel": "Annuler",
            "action.refresh": "Actualiser",
            "action.edit": "Modifier",
            "action.view": "Voir",
            "action.copy": "Copier",
            "action.export": "Exporter",
            "action.import": "Importer",
            # Status
            "status.success": "Succès",
            "status.error": "Erreur",
            "status.loading": "Chargement...",
            "status.saved": "Sauvegardé avec succès",
            "status.deleted": "Supprimé avec succès",
            # Calculator
            "calc.title": "Calculateur de Jetons",
            "calc.model": "Modèle",
            "calc.tokens": "Jetons",
            "calc.cost": "Coût",
            "calc.estimate": "Estimer",
            "calc.input": "Entrée",
            "calc.output": "Sortie",
            # Optimization
            "opt.title": "Optimisation",
            "opt.context": "Contexte",
            "opt.target": "Modèle Cible",
            "opt.optimize": "Optimiser",
            "opt.score": "Score",
            "opt.suggestions": "Suggestions",
            "opt.accept": "Accepter",
            "opt.reject": "Rejeter",
            "opt.retry": "Réessayer",
            # Forms
            "form.required": "Requis",
            "form.optional": "Optionnel",
            "form.placeholder.name": "Entrez le nom",
            "form.placeholder.search": "Rechercher...",
            "form.placeholder.email": "utilisateur@domaine.com",
            # Messages
            "msg.select_item": "Veuillez sélectionner un élément",
            "msg.confirm_delete": "Êtes-vous sûr de vouloir supprimer ceci?",
            "msg.no_results": "Aucun résultat trouvé",
            "msg.loading_data": "Chargement des données...",
            # Translation
            "translate.to_english": "Traduire en Anglais",
            "translate.status": "Statut de Traduction",
            "translate.help": (
                "Traduisez votre prompt en anglais pour une meilleure amélioration IA"
            ),
            # Prompt Builder
            "builder.title": "Constructeur de Prompts",
            "builder.available": "Prompts Disponibles",
            "builder.selected": "Prompts Sélectionnés",
            "builder.preview": "Aperçu",
            "builder.template": "Modèle de Combinaison",
            "builder.template.sequential": "Séquentiel",
            "builder.template.sequential.desc": (
                "Combiner les prompts l'un après l'autre"
            ),
            "builder.template.sections": "Sections",
            "builder.template.sections.desc": (
                "Combiner les prompts en sections distinctes"
            ),
            "builder.template.layered": "En Couches",
            "builder.template.layered.desc": "Construire le contexte en couches",
            "builder.template.custom": "Personnalisé",
            "builder.template.custom.desc": (
                "Utiliser un modèle de formatage personnalisé"
            ),
            "builder.combine": "Combiner les Prompts",
            "builder.clear": "Effacer la Sélection",
            "builder.edit": "Ouvrir dans l'Éditeur",
            "builder.error.no_prompts": "Aucun prompt sélectionné",
            "builder.error.min_prompts": "Sélectionnez au moins 2 prompts",
            "builder.error.duplicates": "Prompts en double trouvés",
            "builder.error.too_long": "Prompt combiné trop long",
            "builder.error.combination": "Échec de la combinaison",
            "builder.preview.empty": "Sélectionnez des prompts pour voir l'aperçu",
            "builder.preview.error": "Erreur d'aperçu",
            "builder.drag.add": "Glissez ici pour ajouter",
            "builder.drag.reorder": "Glissez pour réorganiser",
            "builder.search.placeholder": "Rechercher des prompts...",
            "builder.filter.category": "Filtrer par catégorie",
            "builder.filter.all": "Toutes les Catégories",
            # Templates
            "template.title": "Modèle",
            "template.name": "Nom du Modèle",
            "template.description": "Description",
            "template.content": "Contenu du Modèle",
            "template.variables": "Variables",
            "template.category": "Catégorie",
            "template.create": "Créer un Modèle",
            "template.edit": "Modifier le Modèle",
            "template.delete": "Supprimer le Modèle",
            "template.use": "Utiliser le Modèle",
            "template.preview": "Aperçu",
            "template.validate": "Valider",
            "template.save": "Sauvegarder le Modèle",
            "template.cancel": "Annuler",
            "template.list": "Modèles",
            "template.custom": "Modèles Personnalisés",
            "template.builtin": "Modèles Intégrés",
            "template.new": "Nouveau Modèle",
            "template.empty": "Aucun modèle trouvé",
            "template.empty_desc": "Créez votre premier modèle pour commencer",
            "template.validation_error": "Échec de la validation du modèle",
            "template.saved_success": "Modèle sauvegardé avec succès",
            "template.deleted_success": "Modèle supprimé avec succès",
            "template.name_placeholder": "Entrez le nom du modèle",
            "template.description_placeholder": "Décrivez à quoi sert ce modèle",
            "template.content_placeholder": (
                "Entrez le contenu de votre modèle avec des variables comme "
                "{nom_variable}"
            ),
            "template.variables_help": (
                "Les variables trouvées dans votre modèle apparaîtront ici"
            ),
            "template.category_help": (
                "Choisissez une catégorie pour organiser vos modèles"
            ),
            # Template categories
            "template.category.business": "Affaires",
            "template.category.technical": "Technique",
            "template.category.creative": "Créatif",
            "template.category.analytical": "Analytique",
            "template.category.custom": "Personnalisé",
            "template.category.general": "Général",
        }

    def _get_german_translations(self) -> Dict[str, str]:
        """German translations"""
        return {
            # Application
            "app.title": "KI-Prompt-Manager",
            "app.subtitle": "Sichere, mandantenfähige KI-Prompt-Verwaltung",
            "app.status.authenticated": "✅ Angemeldet als {user}",
            "app.status.not_authenticated": "❌ Nicht angemeldet",
            # Navigation
            "nav.home": "Startseite",
            "nav.prompts": "Prompts",
            "nav.builder": "Builder",
            "nav.library": "Bibliothek",
            "nav.tokens": "Tokens",
            "nav.services": "Services",
            "nav.settings": "Einstellungen",
            "nav.admin": "Admin",
            # Authentication
            "auth.login": "Anmelden",
            "auth.logout": "Abmelden",
            "auth.email": "E-Mail",
            "auth.password": "Passwort",
            "auth.tenant": "Mandant",
            "auth.sso": "SSO-Anmeldung",
            "auth.welcome": "Willkommen, {name}!",
            "auth.invalid": "Ungültige Anmeldedaten",
            # Dashboard (basic keys)
            "dashboard.welcome_back": "Willkommen zurück, {name}!",
            "dashboard.welcome": "Willkommen bei AI Prompt Manager!",
            "dashboard.subtitle": (
                "Bereit, Ihre KI-Prompts zu erstellen und zu verwalten"
            ),
            "dashboard.create_new": "Neu Erstellen",
            "dashboard.new_prompt": "Neuer Prompt",
            "dashboard.browse": "Durchsuchen",
            "dashboard.configure": "Konfigurieren",
            "dashboard.recent_prompts": "Aktuelle Prompts",
            "dashboard.view_all": "Alle anzeigen",
            "dashboard.recently_created": "Kürzlich erstellt",
            "stats.total_prompts": "Prompts Gesamt",
            "stats.templates": "Vorlagen",
            "tips.title": "Erste Schritte",
            "tips.create_title": "Erstellen Sie Ihren Ersten Prompt",
            "tips.create_desc": (
                "Beginnen Sie mit einem Prompt für Ihre häufigste KI-Aufgabe"
            ),
            "tips.templates_title": "Vorlagen Verwenden",
            "tips.templates_desc": (
                "Durchsuchen Sie unsere Vorlagenbibliothek mit bewährten "
                "Prompt-Patterns"
            ),
            "tips.test_title": "Testen und Optimieren",
            "tips.test_desc": (
                "Nutzen Sie unsere integrierten Tools zur Verfeinerung Ihrer Prompts"
            ),
            "tips.organize_title": "Mit Kategorien Organisieren",
            "tips.organize_desc": (
                "Halten Sie Ihre Prompts mit Kategorien und Tags organisiert"
            ),
            "dashboard.no_prompts": "Noch keine Prompts",
            "dashboard.no_prompts_desc": (
                "Beginnen Sie mit der Erstellung Ihres ersten Prompts"
            ),
            "dashboard.create_first": "Erstellen Sie Ihren Ersten Prompt",
            # Prompts
            "prompt.name": "Name",
            "prompt.title": "Titel",
            "prompt.category": "Kategorie",
            "prompt.content": "Inhalt",
            "prompt.tags": "Tags",
            "prompt.add": "Hinzufügen",
            "prompt.update": "Aktualisieren",
            "prompt.delete": "Löschen",
            "prompt.clear": "Löschen",
            "prompt.load": "Laden",
            "prompt.search": "Suchen",
            "prompt.enhancement": "Verbesserungs-Prompt",
            # Actions
            "action.save": "Speichern",
            "action.cancel": "Abbrechen",
            "action.refresh": "Aktualisieren",
            "action.edit": "Bearbeiten",
            "action.view": "Anzeigen",
            "action.copy": "Kopieren",
            "action.export": "Exportieren",
            "action.import": "Importieren",
            # Status
            "status.success": "Erfolg",
            "status.error": "Fehler",
            "status.loading": "Laden...",
            "status.saved": "Erfolgreich gespeichert",
            "status.deleted": "Erfolgreich gelöscht",
            # Calculator
            "calc.title": "Token-Rechner",
            "calc.model": "Modell",
            "calc.tokens": "Tokens",
            "calc.cost": "Kosten",
            "calc.estimate": "Schätzen",
            "calc.input": "Eingabe",
            "calc.output": "Ausgabe",
            # Optimization
            "opt.title": "Optimierung",
            "opt.context": "Kontext",
            "opt.target": "Zielmodell",
            "opt.optimize": "Optimieren",
            "opt.score": "Bewertung",
            "opt.suggestions": "Vorschläge",
            "opt.accept": "Akzeptieren",
            "opt.reject": "Ablehnen",
            "opt.retry": "Wiederholen",
            # Forms
            "form.required": "Erforderlich",
            "form.optional": "Optional",
            "form.placeholder.name": "Name eingeben",
            "form.placeholder.search": "Suchen...",
            "form.placeholder.email": "benutzer@domain.com",
            # Messages
            "msg.select_item": "Bitte wählen Sie ein Element aus",
            "msg.confirm_delete": "Sind Sie sicher, dass Sie dies löschen möchten?",
            "msg.no_results": "Keine Ergebnisse gefunden",
            "msg.loading_data": "Daten werden geladen...",
            # Translation
            "translate.to_english": "Ins Englische übersetzen",
            "translate.status": "Übersetzungsstatus",
            "translate.help": (
                "Übersetzen Sie Ihren Prompt ins Englische für bessere KI-Verbesserung"
            ),
            # Prompt Builder
            "builder.title": "Prompt-Builder",
            "builder.subtitle": "Kombinieren Sie vorhandene Prompts zu neuen",
            "builder.available": "Verfügbare Prompts",
            "builder.selected": "Ausgewählte Prompts",
            "builder.preview": "Vorschau",
            "builder.template": "Kombinationsvorlage",
            "builder.template.sequential": "Sequenziell",
            "builder.template.sequential.desc": "Prompts nacheinander kombinieren",
            "builder.template.sections": "Abschnitte",
            "builder.template.sections.desc": (
                "Prompts als unterschiedliche Abschnitte kombinieren"
            ),
            "builder.template.layered": "Geschichtet",
            "builder.template.layered.desc": "Kontext in Schichten aufbauen",
            "builder.template.custom": "Benutzerdefiniert",
            "builder.template.custom.desc": (
                "Benutzerdefinierte Formatierungsvorlage verwenden"
            ),
            "builder.combine": "Prompts kombinieren",
            "builder.clear": "Auswahl löschen",
            "builder.edit": "Im Editor öffnen",
            "builder.error.no_prompts": "Keine Prompts ausgewählt",
            "builder.error.min_prompts": "Wählen Sie mindestens 2 Prompts aus",
            "builder.error.duplicates": "Doppelte Prompts gefunden",
            "builder.error.too_long": "Kombinierter Prompt zu lang",
            "builder.error.combination": "Kombinierung fehlgeschlagen",
            "builder.preview.empty": "Wählen Sie Prompts aus, um die Vorschau zu sehen",
            "builder.preview.error": "Vorschau-Fehler",
            "builder.drag.add": "Hierher ziehen zum Hinzufügen",
            "builder.drag.reorder": "Ziehen zum Neuordnen",
            "builder.search.placeholder": "Prompts suchen...",
            "builder.filter.category": "Nach Kategorie filtern",
            "builder.filter.all": "Alle Kategorien",
        }

    def _get_chinese_translations(self) -> Dict[str, str]:
        """Chinese translations"""
        return {
            # Application
            "app.title": "AI提示管理器",
            "app.subtitle": "安全的多租户AI提示管理",
            "app.status.authenticated": "✅ 已认证为 {user}",
            "app.status.not_authenticated": "❌ 未认证",
            # Navigation
            "nav.home": "首页",
            "nav.prompts": "提示",
            "nav.builder": "构建器",
            "nav.library": "库",
            "nav.tokens": "令牌",
            "nav.services": "服务",
            "nav.settings": "设置",
            "nav.admin": "管理",
            # Authentication
            "auth.login": "登录",
            "auth.logout": "登出",
            "auth.email": "邮箱",
            "auth.password": "密码",
            "auth.tenant": "租户",
            "auth.sso": "SSO登录",
            "auth.welcome": "欢迎，{name}！",
            "auth.invalid": "无效凭据",
            # Dashboard
            "dashboard.welcome_back": "欢迎回来，{name}！",
            "dashboard.welcome": "欢迎使用AI提示管理器！",
            "dashboard.subtitle": "准备创建和管理您的AI提示",
            "dashboard.create_new": "创建新的",
            "dashboard.new_prompt": "新提示",
            "dashboard.browse": "浏览",
            "dashboard.configure": "配置",
            "dashboard.recent_prompts": "最近的提示",
            "dashboard.view_all": "查看全部",
            "dashboard.recently_created": "最近创建",
            "dashboard.no_prompts": "还没有提示",
            "dashboard.no_prompts_desc": "从创建您的第一个提示开始",
            "dashboard.create_first": "创建您的第一个提示",
            "stats.total_prompts": "提示总数",
            "stats.templates": "模板",
            "tips.title": "入门提示",
            "tips.create_title": "创建您的第一个提示",
            "tips.create_desc": "从为您最常见的AI任务创建提示开始",
            "tips.templates_title": "使用模板",
            "tips.templates_desc": "浏览我们的模板库，找到经过验证的提示模式",
            "tips.test_title": "测试和优化",
            "tips.test_desc": "使用我们的内置工具来完善您的提示",
            "tips.organize_title": "用类别组织",
            "tips.organize_desc": "使用类别和标签保持您的提示有条理",
            # Prompts
            "prompt.name": "名称",
            "prompt.title": "标题",
            "prompt.category": "类别",
            "prompt.content": "内容",
            "prompt.tags": "标签",
            "prompt.add": "添加",
            "prompt.update": "更新",
            "prompt.delete": "删除",
            "prompt.clear": "清除",
            "prompt.load": "加载",
            "prompt.search": "搜索",
            "prompt.enhancement": "增强提示",
            # Actions
            "action.save": "保存",
            "action.cancel": "取消",
            "action.refresh": "刷新",
            "action.edit": "编辑",
            "action.view": "查看",
            "action.copy": "复制",
            "action.export": "导出",
            "action.import": "导入",
            # Status
            "status.success": "成功",
            "status.error": "错误",
            "status.loading": "加载中...",
            "status.saved": "保存成功",
            "status.deleted": "删除成功",
            # Calculator
            "calc.title": "令牌计算器",
            "calc.model": "模型",
            "calc.tokens": "令牌",
            "calc.cost": "成本",
            "calc.estimate": "估算",
            "calc.input": "输入",
            "calc.output": "输出",
            # Optimization
            "opt.title": "优化",
            "opt.context": "上下文",
            "opt.target": "目标模型",
            "opt.optimize": "优化",
            "opt.score": "评分",
            "opt.suggestions": "建议",
            "opt.accept": "接受",
            "opt.reject": "拒绝",
            "opt.retry": "重试",
            # Forms
            "form.required": "必需",
            "form.optional": "可选",
            "form.placeholder.name": "输入名称",
            "form.placeholder.search": "搜索...",
            "form.placeholder.email": "用户@域名.com",
            # Messages
            "msg.select_item": "请选择一个项目",
            "msg.confirm_delete": "您确定要删除这个吗？",
            "msg.no_results": "未找到结果",
            "msg.loading_data": "正在加载数据...",
            # Translation
            "translate.to_english": "翻译为英文",
            "translate.status": "翻译状态",
            "translate.help": "将您的提示翻译为英文以获得更好的AI增强效果",
            # Prompt Builder
            "builder.title": "提示构建器",
            "builder.subtitle": "使用拖放功能组合多个提示以创建复杂工作流",
            "builder.available_prompts": "可用提示",
            "builder.selected_prompts": "选中的提示",
            "builder.selected_prompts_desc": "将提示拖拽到此处或点击选择。拖拽以重新排序。",
            "builder.combination_template": "组合模板",
            "builder.combination_template_desc": "选择如何组合您选中的提示",
            "builder.search_prompts": "搜索提示...",
            "builder.all_categories": "所有类别",
            "builder.no_prompts": "没有可用的提示",
            "builder.create_first_prompt": "创建您的第一个提示",
            "builder.drag_here": "将提示拖拽到此处以组合它们",
            "builder.click_to_select": "或点击提示以选择它们",
            "builder.prompts_selected": "个提示已选择",
            "builder.prompt_selected": "个提示已选择",
            "builder.clear_all": "全部清除",
            "builder.preview": "预览",
            "builder.refresh_preview": "刷新预览",
            "builder.combine_prompts": "组合提示",
            "builder.select_prompts_preview": "选择提示以查看预览...",
            "builder.characters": "字符",
            "builder.tokens_estimated": "tokens（估计）",
            "builder.source_prompts": "源提示",
            "builder.chars": "字符",
            # Builder Templates
            "builder.template.sequential": "顺序",
            "builder.template.sequential_desc": "按顺序组合提示，清晰分隔",
            "builder.template.sections": "分段",
            "builder.template.sections_desc": "为每个提示创建带有标题的不同段落",
            "builder.template.layered": "分层",
            "builder.template.layered_desc": "以层次构建上下文，包含基础层和附加层",
            "builder.template.custom": "自定义",
            "builder.template.custom_desc": "使用您自己的格式模板和占位符",
            # Builder Options
            "builder.custom_separator": "自定义分隔符",
            "builder.add_numbers": "添加序列号",
            "builder.custom_template": "自定义模板",
            "builder.custom_template_placeholder": (
                "使用 {content}、{name}、{title}、{category}、{tags} 作为占位符"
            ),
            "builder.available_placeholders": (
                "可用占位符：{content}、{name}、{title}、{category}、{tags}"
            ),
            # Builder Actions & Messages
            "builder.min_prompts_required": "请至少选择2个提示进行组合",
            "builder.combined_prompt_name": "组合提示（{count}部分）",
            "builder.combined_category": "组合",
            "builder.combined_description": "组合提示创建自：{sources}",
            "builder.combined_tags_suffix": "组合，{count}部分",
        }

    def _get_japanese_translations(self) -> Dict[str, str]:
        """Japanese translations"""
        return {
            # Application
            "app.title": "AIプロンプトマネージャー",
            "app.subtitle": "安全なマルチテナントAIプロンプト管理",
            "app.status.authenticated": "✅ {user}として認証済み",
            "app.status.not_authenticated": "❌ 未認証",
            # Navigation
            "nav.home": "ホーム",
            "nav.prompts": "プロンプト",
            "nav.builder": "ビルダー",
            "nav.library": "ライブラリ",
            "nav.tokens": "トークン",
            "nav.services": "サービス",
            "nav.settings": "設定",
            "nav.admin": "管理者",
            # Authentication
            "auth.login": "ログイン",
            "auth.logout": "ログアウト",
            "auth.email": "メール",
            "auth.password": "パスワード",
            "auth.tenant": "テナント",
            "auth.sso": "SSOログイン",
            "auth.welcome": "ようこそ、{name}さん！",
            "auth.invalid": "無効な認証情報",
            # Dashboard
            "dashboard.welcome_back": "おかえりなさい、{name}！",
            "dashboard.welcome": "AIプロンプトマネージャーへようこそ！",
            "dashboard.subtitle": "AIプロンプトの作成と管理の準備ができました",
            "dashboard.create_new": "新規作成",
            "dashboard.new_prompt": "新しいプロンプト",
            "dashboard.browse": "参照",
            "dashboard.configure": "設定",
            "dashboard.recent_prompts": "最近のプロンプト",
            "dashboard.view_all": "すべて表示",
            "dashboard.recently_created": "最近作成",
            "dashboard.no_prompts": "まだプロンプトがありません",
            "dashboard.no_prompts_desc": "最初のプロンプトを作成して始めましょう",
            "dashboard.create_first": "最初のプロンプトを作成",
            "stats.total_prompts": "プロンプト総数",
            "stats.templates": "テンプレート",
            "tips.title": "始め方のヒント",
            "tips.create_title": "最初のプロンプトを作成",
            "tips.create_desc": "最も一般的なAIタスクのプロンプトを作成することから始めましょう",
            "tips.templates_title": "テンプレートを使用",
            "tips.templates_desc": "実証済みのプロンプトパターンのテンプレートライブラリを参照",
            "tips.test_title": "テストと最適化",
            "tips.test_desc": "内蔵ツールを使用してプロンプトを改良",
            "tips.organize_title": "カテゴリで整理",
            "tips.organize_desc": "カテゴリとタグを使用してプロンプトを整理",
            # Prompts
            "prompt.name": "名前",
            "prompt.title": "タイトル",
            "prompt.category": "カテゴリ",
            "prompt.content": "内容",
            "prompt.tags": "タグ",
            "prompt.add": "追加",
            "prompt.update": "更新",
            "prompt.delete": "削除",
            "prompt.clear": "クリア",
            "prompt.load": "読み込み",
            "prompt.search": "検索",
            "prompt.enhancement": "拡張プロンプト",
            # Actions
            "action.save": "保存",
            "action.cancel": "キャンセル",
            "action.refresh": "更新",
            "action.edit": "編集",
            "action.view": "表示",
            "action.copy": "コピー",
            "action.export": "エクスポート",
            "action.import": "インポート",
            # Status
            "status.success": "成功",
            "status.error": "エラー",
            "status.loading": "読み込み中...",
            "status.saved": "正常に保存されました",
            "status.deleted": "正常に削除されました",
            # Calculator
            "calc.title": "トークン計算機",
            "calc.model": "モデル",
            "calc.tokens": "トークン",
            "calc.cost": "コスト",
            "calc.estimate": "推定",
            "calc.input": "入力",
            "calc.output": "出力",
            # Optimization
            "opt.title": "最適化",
            "opt.context": "コンテキスト",
            "opt.target": "対象モデル",
            "opt.optimize": "最適化",
            "opt.score": "スコア",
            "opt.suggestions": "提案",
            "opt.accept": "承認",
            "opt.reject": "拒否",
            "opt.retry": "再試行",
            # Forms
            "form.required": "必須",
            "form.optional": "任意",
            "form.placeholder.name": "名前を入力",
            "form.placeholder.search": "検索...",
            "form.placeholder.email": "ユーザー@ドメイン.com",
            # Messages
            "msg.select_item": "項目を選択してください",
            "msg.confirm_delete": "本当に削除しますか？",
            "msg.no_results": "結果が見つかりません",
            "msg.loading_data": "データを読み込み中...",
            # Translation
            "translate.to_english": "英語に翻訳",
            "translate.status": "翻訳ステータス",
            "translate.help": "より良いAI強化のためにプロンプトを英語に翻訳してください",
            # Prompt Builder
            "builder.title": "プロンプトビルダー",
            "builder.subtitle": "ドラッグ&ドロップで複数のプロンプトを組み合わせて高度なワークフローを作成",
            "builder.available_prompts": "利用可能なプロンプト",
            "builder.selected_prompts": "選択されたプロンプト",
            "builder.selected_prompts_desc": "プロンプトをここにドラッグするかクリックして選択。ドラッグして並び替え。",
            "builder.combination_template": "組み合わせテンプレート",
            "builder.combination_template_desc": "選択したプロンプトの組み合わせ方法を選択",
            "builder.search_prompts": "プロンプトを検索...",
            "builder.all_categories": "全カテゴリ",
            "builder.no_prompts": "利用可能なプロンプトがありません",
            "builder.create_first_prompt": "最初のプロンプトを作成",
            "builder.drag_here": "プロンプトをここにドラッグして組み合わせ",
            "builder.click_to_select": "またはプロンプトをクリックして選択",
            "builder.prompts_selected": "個のプロンプトが選択済み",
            "builder.prompt_selected": "個のプロンプトが選択済み",
            "builder.clear_all": "すべてクリア",
            "builder.preview": "プレビュー",
            "builder.refresh_preview": "プレビューを更新",
            "builder.combine_prompts": "プロンプトを組み合わせる",
            "builder.select_prompts_preview": "プレビューを見るためにプロンプトを選択してください...",
            "builder.characters": "文字",
            "builder.tokens_estimated": "トークン（推定）",
            "builder.source_prompts": "ソースプロンプト",
            "builder.chars": "文字",
            # Builder Templates
            "builder.template.sequential": "順次",
            "builder.template.sequential_desc": "プロンプトを順番に明確に分離して組み合わせる",
            "builder.template.sections": "セクション",
            "builder.template.sections_desc": "各プロンプトにヘッダー付きの異なるセクションを作成",
            "builder.template.layered": "階層",
            "builder.template.layered_desc": "ベース層と追加層でコンテキストを階層的に構築",
            "builder.template.custom": "カスタム",
            "builder.template.custom_desc": "プレースホルダー付きの独自フォーマットテンプレートを使用",
            # Builder Options
            "builder.custom_separator": "カスタム区切り文字",
            "builder.add_numbers": "シーケンス番号を追加",
            "builder.custom_template": "カスタムテンプレート",
            "builder.custom_template_placeholder": (
                "{content}、{name}、{title}、{category}、{tags}をプレースホルダーとして使用"
            ),
            "builder.available_placeholders": (
                "利用可能なプレースホルダー：{content}、{name}、{title}、{category}、{tags}"
            ),
            # Builder Actions & Messages
            "builder.min_prompts_required": "組み合わせるには少なくとも2つのプロンプトを選択してください",
            "builder.combined_prompt_name": "組み合わせプロンプト（{count}部分）",
            "builder.combined_category": "組み合わせ",
            "builder.combined_description": "組み合わせプロンプトの作成元：{sources}",
            "builder.combined_tags_suffix": "組み合わせ、{count}部分",
        }

    def _get_portuguese_translations(self) -> Dict[str, str]:
        """Portuguese translations"""
        return {
            # Application
            "app.title": "Gerenciador de Prompts IA",
            "app.subtitle": "Gerenciamento seguro e multi-inquilino de prompts IA",
            "app.status.authenticated": "✅ Autenticado como {user}",
            "app.status.not_authenticated": "❌ Não autenticado",
            # Navigation
            "nav.home": "Início",
            "nav.prompts": "Prompts",
            "nav.builder": "Construtor",
            "nav.library": "Biblioteca",
            "nav.tokens": "Tokens",
            "nav.services": "Serviços",
            "nav.settings": "Configurações",
            "nav.admin": "Admin",
            # Authentication
            "auth.login": "Entrar",
            "auth.logout": "Sair",
            "auth.email": "Email",
            "auth.password": "Senha",
            "auth.tenant": "Inquilino",
            "auth.sso": "Login SSO",
            "auth.welcome": "Bem-vindo, {name}!",
            "auth.invalid": "Credenciais inválidas",
            # Dashboard (basic keys)
            "dashboard.welcome_back": "Bem-vindo de volta, {name}!",
            "dashboard.welcome": "Bem-vindo ao AI Prompt Manager!",
            "dashboard.subtitle": "Pronto para criar e gerenciar seus prompts de IA",
            "dashboard.create_new": "Criar Novo",
            "dashboard.new_prompt": "Novo Prompt",
            "dashboard.browse": "Navegar",
            "dashboard.configure": "Configurar",
            "dashboard.recent_prompts": "Prompts Recentes",
            "dashboard.view_all": "Ver todos",
            "dashboard.recently_created": "Criado recentemente",
            "stats.total_prompts": "Total de Prompts",
            "stats.templates": "Modelos",
            "tips.title": "Dicas para Começar",
            "tips.create_title": "Criar Seu Primeiro Prompt",
            "tips.create_desc": (
                "Comece criando um prompt para sua tarefa de IA mais comum"
            ),
            "tips.templates_title": "Usar Modelos",
            "tips.templates_desc": (
                "Navegue em nossa biblioteca de modelos com padrões comprovados"
            ),
            "tips.test_title": "Testar e Otimizar",
            "tips.test_desc": (
                "Use nossas ferramentas integradas para refinar seus prompts"
            ),
            "tips.organize_title": "Organizar com Categorias",
            "tips.organize_desc": (
                "Mantenha seus prompts organizados usando categorias e tags"
            ),
            "dashboard.no_prompts": "Ainda não há prompts",
            "dashboard.no_prompts_desc": "Comece criando seu primeiro prompt",
            "dashboard.create_first": "Criar Seu Primeiro Prompt",
            # Prompts
            "prompt.name": "Nome",
            "prompt.title": "Título",
            "prompt.category": "Categoria",
            "prompt.content": "Conteúdo",
            "prompt.tags": "Tags",
            "prompt.add": "Adicionar",
            "prompt.update": "Atualizar",
            "prompt.delete": "Excluir",
            "prompt.clear": "Limpar",
            "prompt.load": "Carregar",
            "prompt.search": "Buscar",
            "prompt.enhancement": "Prompt de Melhoria",
            # Actions
            "action.save": "Salvar",
            "action.cancel": "Cancelar",
            "action.refresh": "Atualizar",
            "action.edit": "Editar",
            "action.view": "Ver",
            "action.copy": "Copiar",
            "action.export": "Exportar",
            "action.import": "Importar",
            # Status
            "status.success": "Sucesso",
            "status.error": "Erro",
            "status.loading": "Carregando...",
            "status.saved": "Salvo com sucesso",
            "status.deleted": "Excluído com sucesso",
            # Calculator
            "calc.title": "Calculadora de Tokens",
            "calc.model": "Modelo",
            "calc.tokens": "Tokens",
            "calc.cost": "Custo",
            "calc.estimate": "Estimar",
            "calc.input": "Entrada",
            "calc.output": "Saída",
            # Optimization
            "opt.title": "Otimização",
            "opt.context": "Contexto",
            "opt.target": "Modelo Alvo",
            "opt.optimize": "Otimizar",
            "opt.score": "Pontuação",
            "opt.suggestions": "Sugestões",
            "opt.accept": "Aceitar",
            "opt.reject": "Rejeitar",
            "opt.retry": "Tentar Novamente",
            # Forms
            "form.required": "Obrigatório",
            "form.optional": "Opcional",
            "form.placeholder.name": "Digite o nome",
            "form.placeholder.search": "Buscar...",
            "form.placeholder.email": "usuario@dominio.com",
            # Messages
            "msg.select_item": "Por favor selecione um item",
            "msg.confirm_delete": "Tem certeza que deseja excluir isso?",
            "msg.no_results": "Nenhum resultado encontrado",
            "msg.loading_data": "Carregando dados...",
            # Translation
            "translate.to_english": "Traduzir para Inglês",
            "translate.status": "Status da Tradução",
            "translate.help": (
                "Traduza seu prompt para inglês para melhor aprimoramento com IA"
            ),
            # Prompt Builder
            "builder.title": "Construtor de Prompts",
            "builder.available_prompts": "Prompts Disponíveis",
            "builder.selected_prompts": "Prompts Selecionados",
            "builder.selected_prompts_desc": (
                "Arraste prompts aqui ou clique para selecionar. "
                "Arraste para reordenar."
            ),
            "builder.combination_template": "Modelo de Combinação",
            "builder.combination_template_desc": (
                "Escolha como combinar seus prompts selecionados"
            ),
            "builder.search_prompts": "Buscar prompts...",
            "builder.all_categories": "Todas as Categorias",
            "builder.no_prompts": "Nenhum prompt disponível",
            "builder.create_first_prompt": "Crie seu primeiro prompt",
            "builder.drag_here": "Arraste prompts aqui para combiná-los",
            "builder.click_to_select": "Ou clique nos prompts para selecioná-los",
            "builder.prompts_selected": "prompts selecionados",
            "builder.prompt_selected": "prompt selecionado",
            "builder.clear_all": "Limpar Tudo",
            "builder.preview": "Visualização",
            "builder.refresh_preview": "Atualizar Visualização",
            "builder.combine_prompts": "Combinar Prompts",
            "builder.select_prompts_preview": (
                "Selecione prompts para ver a visualização..."
            ),
            "builder.characters": "caracteres",
            "builder.tokens_estimated": "tokens (estimado)",
            "builder.source_prompts": "prompts fonte",
            "builder.chars": "caract",
            # Builder Templates
            "builder.template.sequential": "Sequencial",
            "builder.template.sequential_desc": (
                "Combinar prompts um após o outro com separação clara"
            ),
            "builder.template.sections": "Seções",
            "builder.template.sections_desc": (
                "Criar seções distintas com cabeçalhos para cada prompt"
            ),
            "builder.template.layered": "Em Camadas",
            "builder.template.layered_desc": (
                "Construir contexto em camadas com base + camadas adicionais"
            ),
            "builder.template.custom": "Personalizado",
            "builder.template.custom_desc": (
                "Use seu próprio modelo de formatação com marcadores"
            ),
            # Builder Options
            "builder.custom_separator": "Separador Personalizado",
            "builder.add_numbers": "Adicionar números de sequência",
            "builder.custom_template": "Modelo Personalizado",
            "builder.custom_template_placeholder": (
                "Use {content}, {name}, {title}, {category}, {tags} como marcadores"
            ),
            "builder.available_placeholders": (
                "Marcadores disponíveis: {content}, {name}, {title}, {category}, {tags}"
            ),
            # Builder Actions & Messages
            "builder.min_prompts_required": (
                "Por favor selecione pelo menos 2 prompts para combinar"
            ),
            "builder.combined_prompt_name": "Prompt Combinado ({count} partes)",
            "builder.combined_category": "Combinado",
            "builder.combined_description": "Prompt combinado criado de: {sources}",
            "builder.combined_tags_suffix": "combinado, {count}-partes",
        }

    def _get_russian_translations(self) -> Dict[str, str]:
        """Russian translations"""
        return {
            # Application
            "app.title": "Менеджер AI-промптов",
            "app.subtitle": "Безопасное мультитенантное управление AI-промптами",
            "app.status.authenticated": "✅ Аутентифицирован как {user}",
            "app.status.not_authenticated": "❌ Не аутентифицирован",
            # Navigation
            "nav.home": "Главная",
            "nav.prompts": "Промпты",
            "nav.builder": "Построитель",
            "nav.library": "Библиотека",
            "nav.tokens": "Токены",
            "nav.services": "Сервисы",
            "nav.settings": "Настройки",
            "nav.admin": "Админ",
            # Authentication
            "auth.login": "Войти",
            "auth.logout": "Выйти",
            "auth.email": "Email",
            "auth.password": "Пароль",
            "auth.tenant": "Арендатор",
            "auth.sso": "Вход через SSO",
            "auth.welcome": "Добро пожаловать, {name}!",
            "auth.invalid": "Неверные учетные данные",
            # Dashboard
            "dashboard.welcome_back": "Добро пожаловать, {name}!",
            "dashboard.welcome": "Добро пожаловать в AI Менеджер Промптов!",
            "dashboard.subtitle": "Готовы создавать и управлять вашими AI промптами",
            "dashboard.create_new": "Создать новый",
            "dashboard.new_prompt": "Новый промпт",
            "dashboard.browse": "Просмотр",
            "dashboard.configure": "Настроить",
            "dashboard.recent_prompts": "Недавние промпты",
            "dashboard.view_all": "Показать все",
            "dashboard.recently_created": "Недавно создано",
            "dashboard.no_prompts": "Пока нет промптов",
            "dashboard.no_prompts_desc": "Начните с создания вашего первого промпта",
            "dashboard.create_first": "Создать ваш первый промпт",
            "stats.total_prompts": "Всего промптов",
            "stats.templates": "Шаблоны",
            "tips.title": "Советы для начала",
            "tips.create_title": "Создайте ваш первый промпт",
            "tips.create_desc": (
                "Начните с создания промпта для вашей самой частой AI задачи"
            ),
            "tips.templates_title": "Используйте шаблоны",
            "tips.templates_desc": (
                "Просмотрите нашу библиотеку шаблонов с проверенными "
                "паттернами промптов"
            ),
            "tips.test_title": "Тестируйте и оптимизируйте",
            "tips.test_desc": (
                "Используйте наши встроенные инструменты для улучшения ваших промптов"
            ),
            "tips.organize_title": "Организуйте по категориям",
            "tips.organize_desc": (
                "Держите ваши промпты организованными, используя категории и теги"
            ),
            # Prompts
            "prompt.name": "Имя",
            "prompt.title": "Заголовок",
            "prompt.category": "Категория",
            "prompt.content": "Содержание",
            "prompt.tags": "Теги",
            "prompt.add": "Добавить",
            "prompt.update": "Обновить",
            "prompt.delete": "Удалить",
            "prompt.clear": "Очистить",
            "prompt.load": "Загрузить",
            "prompt.search": "Поиск",
            "prompt.enhancement": "Промпт улучшения",
            # Actions
            "action.save": "Сохранить",
            "action.cancel": "Отмена",
            "action.refresh": "Обновить",
            "action.edit": "Редактировать",
            "action.view": "Просмотр",
            "action.copy": "Копировать",
            "action.export": "Экспорт",
            "action.import": "Импорт",
            # Status
            "status.success": "Успех",
            "status.error": "Ошибка",
            "status.loading": "Загрузка...",
            "status.saved": "Успешно сохранено",
            "status.deleted": "Успешно удалено",
            # Calculator
            "calc.title": "Калькулятор токенов",
            "calc.model": "Модель",
            "calc.tokens": "Токены",
            "calc.cost": "Стоимость",
            "calc.estimate": "Оценить",
            "calc.input": "Ввод",
            "calc.output": "Вывод",
            # Optimization
            "opt.title": "Оптимизация",
            "opt.context": "Контекст",
            "opt.target": "Целевая модель",
            "opt.optimize": "Оптимизировать",
            "opt.score": "Оценка",
            "opt.suggestions": "Предложения",
            "opt.accept": "Принять",
            "opt.reject": "Отклонить",
            "opt.retry": "Повторить",
            # Forms
            "form.required": "Обязательно",
            "form.optional": "Необязательно",
            "form.placeholder.name": "Введите имя",
            "form.placeholder.search": "Поиск...",
            "form.placeholder.email": "пользователь@домен.com",
            # Messages
            "msg.select_item": "Пожалуйста, выберите элемент",
            "msg.confirm_delete": "Вы уверены, что хотите удалить это?",
            "msg.no_results": "Результаты не найдены",
            "msg.loading_data": "Загрузка данных...",
            # Translation
            "translate.to_english": "Перевести на английский",
            "translate.status": "Статус перевода",
            "translate.help": (
                "Переведите ваш промпт на английский для лучшего улучшения ИИ"
            ),
            # Prompt Builder
            "builder.title": "Конструктор Промптов",
            "builder.subtitle": (
                "Объедините несколько промптов с помощью перетаскивания "
                "для создания сложных рабочих процессов"
            ),
            "builder.available_prompts": "Доступные Промпты",
            "builder.selected_prompts": "Выбранные Промпты",
            "builder.selected_prompts_desc": (
                "Перетащите промпты сюда или нажмите для выбора. "
                "Перетащите для изменения порядка."
            ),
            "builder.combination_template": "Шаблон Комбинации",
            "builder.combination_template_desc": (
                "Выберите, как объединить выбранные промпты"
            ),
            "builder.search_prompts": "Поиск промптов...",
            "builder.all_categories": "Все Категории",
            "builder.no_prompts": "Нет доступных промптов",
            "builder.create_first_prompt": "Создайте ваш первый промпт",
            "builder.drag_here": "Перетащите промпты сюда для их объединения",
            "builder.click_to_select": "Или нажмите на промпты для их выбора",
            "builder.prompts_selected": "промптов выбрано",
            "builder.prompt_selected": "промпт выбран",
            "builder.clear_all": "Очистить Все",
            "builder.preview": "Предпросмотр",
            "builder.refresh_preview": "Обновить Предпросмотр",
            "builder.combine_prompts": "Объединить Промпты",
            "builder.select_prompts_preview": (
                "Выберите промпты для просмотра предпросмотра..."
            ),
            "builder.characters": "символов",
            "builder.tokens_estimated": "токенов (оценка)",
            "builder.source_prompts": "исходных промптов",
            "builder.chars": "симв",
            # Builder Templates
            "builder.template.sequential": "Последовательный",
            "builder.template.sequential_desc": (
                "Объединить промпты один за другим с четким разделением"
            ),
            "builder.template.sections": "Секции",
            "builder.template.sections_desc": (
                "Создать отдельные секции с заголовками для каждого промпта"
            ),
            "builder.template.layered": "Слоистый",
            "builder.template.layered_desc": (
                "Строить контекст слоями с базой + дополнительными слоями"
            ),
            "builder.template.custom": "Пользовательский",
            "builder.template.custom_desc": (
                "Используйте свой собственный шаблон форматирования с заполнителями"
            ),
            # Builder Options
            "builder.custom_separator": "Пользовательский Разделитель",
            "builder.add_numbers": "Добавить номера последовательности",
            "builder.custom_template": "Пользовательский Шаблон",
            "builder.custom_template_placeholder": (
                "Используйте {content}, {name}, {title}, {category}, {tags} "
                "как заполнители"
            ),
            "builder.available_placeholders": (
                "Доступные заполнители: {content}, {name}, {title}, {category}, {tags}"
            ),
            # Builder Actions & Messages
            "builder.min_prompts_required": (
                "Пожалуйста, выберите как минимум 2 промпта для объединения"
            ),
            "builder.combined_prompt_name": "Объединенный Промпт ({count} частей)",
            "builder.combined_category": "Объединенный",
            "builder.combined_description": "Объединенный промпт создан из: {sources}",
            "builder.combined_tags_suffix": "объединенный, {count}-частей",
        }

    def _get_arabic_translations(self) -> Dict[str, str]:
        """Arabic translations"""
        return {
            # Application
            "app.title": "مدير الذكاء الاصطناعي",
            "app.subtitle": "إدارة آمنة ومتعددة المستأجرين للذكاء الاصطناعي",
            "app.status.authenticated": "✅ مصادق عليه كـ {user}",
            "app.status.not_authenticated": "❌ غير مصادق عليه",
            # Navigation
            "nav.home": "الرئيسية",
            "nav.prompts": "المطالبات",
            "nav.builder": "المنشئ",
            "nav.library": "المكتبة",
            "nav.tokens": "الرموز",
            "nav.services": "الخدمات",
            "nav.settings": "الإعدادات",
            "nav.admin": "المدير",
            # Authentication
            "auth.login": "تسجيل الدخول",
            "auth.logout": "تسجيل الخروج",
            "auth.email": "البريد الإلكتروني",
            "auth.password": "كلمة المرور",
            "auth.tenant": "المستأجر",
            "auth.sso": "تسجيل دخول SSO",
            "auth.welcome": "مرحباً، {name}!",
            "auth.invalid": "بيانات اعتماد غير صحيحة",
            # Dashboard
            "dashboard.welcome_back": "مرحباً بعودتك، {name}!",
            "dashboard.welcome": "مرحباً بكم في مدير الذكاء الاصطناعي!",
            "dashboard.subtitle": (
                "جاهز لإنشاء وإدارة مطالبات الذكاء الاصطناعي الخاصة بك"
            ),
            "dashboard.create_new": "إنشاء جديد",
            "dashboard.new_prompt": "مطالبة جديدة",
            "dashboard.browse": "تصفح",
            "dashboard.configure": "تكوين",
            "dashboard.recent_prompts": "المطالبات الأخيرة",
            "dashboard.view_all": "عرض الكل",
            "dashboard.recently_created": "تم إنشاؤها مؤخراً",
            "dashboard.no_prompts": "لا توجد مطالبات حتى الآن",
            "dashboard.no_prompts_desc": "ابدأ بإنشاء مطالبتك الأولى",
            "dashboard.create_first": "إنشاء مطالبتك الأولى",
            "stats.total_prompts": "إجمالي المطالبات",
            "stats.templates": "القوالب",
            "tips.title": "نصائح للبدء",
            "tips.create_title": "إنشاء مطالبتك الأولى",
            "tips.create_desc": (
                "ابدأ بإنشاء مطالبة لمهمة الذكاء الاصطناعي الأكثر شيوعاً لديك"
            ),
            "tips.templates_title": "استخدام القوالب",
            "tips.templates_desc": (
                "تصفح مكتبة القوالب الخاصة بنا للحصول على أنماط مطالبات مثبتة"
            ),
            "tips.test_title": "اختبار وتحسين",
            "tips.test_desc": "استخدم أدواتنا المدمجة لتحسين مطالباتك",
            "tips.organize_title": "تنظيم بالفئات",
            "tips.organize_desc": "احتفظ بمطالباتك منظمة باستخدام الفئات والعلامات",
            # Prompts
            "prompt.name": "الاسم",
            "prompt.title": "العنوان",
            "prompt.category": "الفئة",
            "prompt.content": "المحتوى",
            "prompt.tags": "العلامات",
            "prompt.add": "إضافة",
            "prompt.update": "تحديث",
            "prompt.delete": "حذف",
            "prompt.clear": "مسح",
            "prompt.load": "تحميل",
            "prompt.search": "بحث",
            "prompt.enhancement": "مطالبة التحسين",
            # Actions
            "action.save": "حفظ",
            "action.cancel": "إلغاء",
            "action.refresh": "تحديث",
            "action.edit": "تحرير",
            "action.view": "عرض",
            "action.copy": "نسخ",
            "action.export": "تصدير",
            "action.import": "استيراد",
            # Status
            "status.success": "نجح",
            "status.error": "خطأ",
            "status.loading": "جاري التحميل...",
            "status.saved": "تم الحفظ بنجاح",
            "status.deleted": "تم الحذف بنجاح",
            # Calculator
            "calc.title": "حاسبة الرموز",
            "calc.model": "النموذج",
            "calc.tokens": "الرموز",
            "calc.cost": "التكلفة",
            "calc.estimate": "تقدير",
            "calc.input": "الإدخال",
            "calc.output": "الإخراج",
            # Optimization
            "opt.title": "التحسين",
            "opt.context": "السياق",
            "opt.target": "النموذج المستهدف",
            "opt.optimize": "تحسين",
            "opt.score": "النتيجة",
            "opt.suggestions": "الاقتراحات",
            "opt.accept": "قبول",
            "opt.reject": "رفض",
            "opt.retry": "إعادة المحاولة",
            # Forms
            "form.required": "مطلوب",
            "form.optional": "اختياري",
            "form.placeholder.name": "أدخل الاسم",
            "form.placeholder.search": "بحث...",
            "form.placeholder.email": "المستخدم@النطاق.com",
            # Messages
            "msg.select_item": "يرجى تحديد عنصر",
            "msg.confirm_delete": "هل أنت متأكد من أنك تريد حذف هذا؟",
            "msg.no_results": "لم يتم العثور على نتائج",
            "msg.loading_data": "جاري تحميل البيانات...",
            # Translation
            "translate.to_english": "ترجمة إلى الإنجليزية",
            "translate.status": "حالة الترجمة",
            "translate.help": (
                "ترجم موجهك إلى الإنجليزية للحصول على تحسين أفضل للذكاء الاصطناعي"
            ),
            # Prompt Builder
            "builder.title": "منشئ المطالبات",
            "builder.subtitle": (
                "ادمج عدة مطالبات باستخدام السحب والإفلات لإنشاء تدفقات عمل معقدة"
            ),
            "builder.available_prompts": "المطالبات المتاحة",
            "builder.selected_prompts": "المطالبات المحددة",
            "builder.selected_prompts_desc": (
                "اسحب المطالبات هنا أو انقر للتحديد. اسحب لإعادة الترتيب."
            ),
            "builder.combination_template": "قالب الدمج",
            "builder.combination_template_desc": "اختر كيفية دمج مطالباتك المحددة",
            "builder.search_prompts": "البحث في المطالبات...",
            "builder.all_categories": "جميع الفئات",
            "builder.no_prompts": "لا توجد مطالبات متاحة",
            "builder.create_first_prompt": "أنشئ مطالبتك الأولى",
            "builder.drag_here": "اسحب المطالبات هنا لدمجها",
            "builder.click_to_select": "أو انقر على المطالبات لتحديدها",
            "builder.prompts_selected": "مطالبات محددة",
            "builder.prompt_selected": "مطالبة محددة",
            "builder.clear_all": "مسح الكل",
            "builder.preview": "معاينة",
            "builder.refresh_preview": "تحديث المعاينة",
            "builder.combine_prompts": "دمج المطالبات",
            "builder.select_prompts_preview": "حدد المطالبات لرؤية المعاينة...",
            "builder.characters": "حرف",
            "builder.tokens_estimated": "رمز (تقدير)",
            "builder.source_prompts": "مطالبات المصدر",
            "builder.chars": "حرف",
            # Builder Templates
            "builder.template.sequential": "تسلسلي",
            "builder.template.sequential_desc": (
                "دمج المطالبات واحدة تلو الأخرى مع فصل واضح"
            ),
            "builder.template.sections": "أقسام",
            "builder.template.sections_desc": "إنشاء أقسام متميزة مع عناوين لكل مطالبة",
            "builder.template.layered": "طبقات",
            "builder.template.layered_desc": (
                "بناء السياق في طبقات مع القاعدة + طبقات إضافية"
            ),
            "builder.template.custom": "مخصص",
            "builder.template.custom_desc": (
                "استخدم قالب التنسيق الخاص بك مع العناصر النائبة"
            ),
            # Builder Options
            "builder.custom_separator": "فاصل مخصص",
            "builder.add_numbers": "إضافة أرقام التسلسل",
            "builder.custom_template": "قالب مخصص",
            "builder.custom_template_placeholder": (
                "استخدم {content}، {name}، {title}، {category}، {tags} كعناصر نائبة"
            ),
            "builder.available_placeholders": (
                "العناصر النائبة المتاحة: {content}، {name}، {title}، {category}، {tags}"
            ),
            # Builder Actions & Messages
            "builder.min_prompts_required": "يرجى تحديد ما لا يقل عن مطالبتين للدمج",
            "builder.combined_prompt_name": "مطالبة مدمجة ({count} أجزاء)",
            "builder.combined_category": "مدمج",
            "builder.combined_description": "مطالبة مدمجة تم إنشاؤها من: {sources}",
            "builder.combined_tags_suffix": "مدمج، {count}-أجزاء",
        }

    def _get_hindi_translations(self) -> Dict[str, str]:
        """Hindi translations"""
        return {
            # Application
            "app.title": "AI प्रॉम्प्ट मैनेजर",
            "app.subtitle": "सुरक्षित, मल्टी-टेनेंट AI प्रॉम्प्ट प्रबंधन",
            "app.status.authenticated": "✅ {user} के रूप में प्रमाणित",
            "app.status.not_authenticated": "❌ प्रमाणित नहीं",
            # Navigation
            "nav.home": "होम",
            "nav.prompts": "प्रॉम्प्ट्स",
            "nav.builder": "बिल्डर",
            "nav.library": "लाइब्रेरी",
            "nav.tokens": "टोकन",
            "nav.services": "सेवाएं",
            "nav.settings": "सेटिंग्स",
            "nav.admin": "एडमिन",
            # Authentication
            "auth.login": "लॉगिन",
            "auth.logout": "लॉगआउट",
            "auth.email": "ईमेल",
            "auth.password": "पासवर्ड",
            "auth.tenant": "टेनेंट",
            "auth.sso": "SSO लॉगिन",
            "auth.welcome": "स्वागत है, {name}!",
            "auth.invalid": "अमान्य क्रेडेंशियल",
            # Dashboard
            "dashboard.welcome_back": "वापस स्वागत है, {name}!",
            "dashboard.welcome": "AI प्रॉम्प्ट मैनेजर में आपका स्वागत है!",
            "dashboard.subtitle": ("अपने AI प्रॉम्प्ट्स बनाने और प्रबंधित करने के लिए तैयार"),
            "dashboard.create_new": "नया बनाएं",
            "dashboard.new_prompt": "नया प्रॉम्प्ट",
            "dashboard.browse": "ब्राउज़ करें",
            "dashboard.configure": "कॉन्फ़िगर करें",
            "dashboard.recent_prompts": "हाल के प्रॉम्प्ट्स",
            "dashboard.view_all": "सभी देखें",
            "dashboard.recently_created": "हाल ही में बनाया गया",
            "dashboard.no_prompts": "अभी तक कोई प्रॉम्प्ट नहीं",
            "dashboard.no_prompts_desc": "अपना पहला प्रॉम्प्ट बनाकर शुरुआत करें",
            "dashboard.create_first": "अपना पहला प्रॉम्प्ट बनाएं",
            "stats.total_prompts": "कुल प्रॉम्प्ट्स",
            "stats.templates": "टेम्प्लेट्स",
            "tips.title": "शुरुआत के लिए टिप्स",
            "tips.create_title": "अपना पहला प्रॉम्प्ट बनाएं",
            "tips.create_desc": (
                "अपने सबसे सामान्य AI कार्य के लिए प्रॉम्प्ट बनाकर " "शुरुआत करें"
            ),
            "tips.templates_title": "टेम्प्लेट्स का उपयोग करें",
            "tips.templates_desc": (
                "सिद्ध प्रॉम्प्ट पैटर्न के लिए हमारी टेम्प्लेट " "लाइब्रेरी ब्राउज़ करें"
            ),
            "tips.test_title": "परीक्षण और अनुकूलन",
            "tips.test_desc": (
                "अपने प्रॉम्प्ट्स को परिष्कृत करने के लिए हमारे " "अंतर्निहित उपकरणों का उपयोग करें"
            ),
            "tips.organize_title": "श्रेणियों के साथ व्यवस्थित करें",
            "tips.organize_desc": (
                "श्रेणियों और टैग का उपयोग करके अपने प्रॉम्प्ट्स को व्यवस्थित रखें"
            ),
            # Prompts
            "prompt.name": "नाम",
            "prompt.title": "शीर्षक",
            "prompt.category": "श्रेणी",
            "prompt.content": "सामग्री",
            "prompt.tags": "टैग",
            "prompt.add": "जोड़ें",
            "prompt.update": "अपडेट",
            "prompt.delete": "हटाएं",
            "prompt.clear": "साफ करें",
            "prompt.load": "लोड करें",
            "prompt.search": "खोजें",
            "prompt.enhancement": "वृद्धि प्रॉम्प्ट",
            # Actions
            "action.save": "सेव करें",
            "action.cancel": "रद्द करें",
            "action.refresh": "रिफ्रेश",
            "action.edit": "संपादित करें",
            "action.view": "देखें",
            "action.copy": "कॉपी करें",
            "action.export": "निर्यात",
            "action.import": "आयात",
            # Status
            "status.success": "सफल",
            "status.error": "त्रुटि",
            "status.loading": "लोड हो रहा है...",
            "status.saved": "सफलतापूर्वक सेव किया गया",
            "status.deleted": "सफलतापूर्वक हटाया गया",
            # Calculator
            "calc.title": "टोकन कैलकुलेटर",
            "calc.model": "मॉडल",
            "calc.tokens": "टोकन",
            "calc.cost": "लागत",
            "calc.estimate": "अनुमान",
            "calc.input": "इनपुट",
            "calc.output": "आउटपुट",
            # Optimization
            "opt.title": "अनुकूलन",
            "opt.context": "संदर्भ",
            "opt.target": "लक्ष्य मॉडल",
            "opt.optimize": "अनुकूलित करें",
            "opt.score": "स्कोर",
            "opt.suggestions": "सुझाव",
            "opt.accept": "स्वीकार करें",
            "opt.reject": "अस्वीकार करें",
            "opt.retry": "पुनः प्रयास करें",
            # Forms
            "form.required": "आवश्यक",
            "form.optional": "वैकल्पिक",
            "form.placeholder.name": "नाम दर्ज करें",
            "form.placeholder.search": "खोजें...",
            "form.placeholder.email": "उपयोगकर्ता@डोमेन.com",
            # Messages
            "msg.select_item": "कृपया एक आइटम चुनें",
            "msg.confirm_delete": "क्या आप वाकई इसे हटाना चाहते हैं?",
            "msg.no_results": "कोई परिणाम नहीं मिला",
            "msg.loading_data": "डेटा लोड हो रहा है...",
            # Translation
            "translate.to_english": "अंग्रेजी में अनुवाद करें",
            "translate.status": "अनुवाद स्थिति",
            "translate.help": ("बेहतर AI सुधार के लिए अपने प्रॉम्प्ट को अंग्रेजी में " "अनुवाद करें"),
            # Prompt Builder
            "builder.title": "प्रॉम्प्ट बिल्डर",
            "builder.subtitle": (
                "परिष्कृत वर्कफ़्लो बनाने के लिए ड्रैग-एंड-ड्रॉप का " "उपयोग करके कई प्रॉम्प्ट्स को जोड़ें"
            ),
            "builder.available_prompts": "उपलब्ध प्रॉम्प्ट्स",
            "builder.selected_prompts": "चुने गए प्रॉम्प्ट्स",
            "builder.selected_prompts_desc": (
                "प्रॉम्प्ट्स को यहाँ खींचें या चुनने के लिए क्लिक करें। " "पुनः व्यवस्थित करने के लिए खींचें।"
            ),
            "builder.combination_template": "संयोजन टेम्प्लेट",
            "builder.combination_template_desc": (
                "चुनें कि आपके चयनित प्रॉम्प्ट्स को कैसे जोड़ा जाए"
            ),
            "builder.search_prompts": "प्रॉम्प्ट्स खोजें...",
            "builder.all_categories": "सभी श्रेणियां",
            "builder.no_prompts": "कोई प्रॉम्प्ट उपलब्ध नहीं",
            "builder.create_first_prompt": "अपना पहला प्रॉम्प्ट बनाएं",
            "builder.drag_here": "प्रॉम्प्ट्स को जोड़ने के लिए यहाँ खींचें",
            "builder.click_to_select": ("या उन्हें चुनने के लिए प्रॉम्प्ट्स पर क्लिक करें"),
            "builder.prompts_selected": "प्रॉम्प्ट्स चुने गए",
            "builder.prompt_selected": "प्रॉम्प्ट चुना गया",
            "builder.clear_all": "सभी साफ़ करें",
            "builder.preview": "पूर्वावलोकन",
            "builder.refresh_preview": "पूर्वावलोकन रिफ्रेश करें",
            "builder.combine_prompts": "प्रॉम्प्ट्स जोड़ें",
            "builder.select_prompts_preview": ("पूर्वावलोकन देखने के लिए प्रॉम्प्ट्स चुनें..."),
            "builder.characters": "अक्षर",
            "builder.tokens_estimated": "टोकन (अनुमानित)",
            "builder.source_prompts": "स्रोत प्रॉम्प्ट्स",
            "builder.chars": "अक्षर",
            # Builder Templates
            "builder.template.sequential": "क्रमिक",
            "builder.template.sequential_desc": (
                "प्रॉम्प्ट्स को स्पष्ट विभाजन के साथ एक के बाद एक जोड़ें"
            ),
            "builder.template.sections": "खंड",
            "builder.template.sections_desc": (
                "प्रत्येक प्रॉम्प्ट के लिए शीर्षकों के साथ अलग खंड बनाएं"
            ),
            "builder.template.layered": "परतदार",
            "builder.template.layered_desc": (
                "आधार + अतिरिक्त परतों के साथ संदर्भ को परतों में बनाएं"
            ),
            "builder.template.custom": "कस्टम",
            "builder.template.custom_desc": (
                "प्लेसहोल्डर के साथ अपना स्वयं का फॉर्मेटिंग टेम्प्लेट उपयोग करें"
            ),
            # Builder Options
            "builder.custom_separator": "कस्टम सेपरेटर",
            "builder.add_numbers": "अनुक्रम संख्याएं जोड़ें",
            "builder.custom_template": "कस्टम टेम्प्लेट",
            "builder.custom_template_placeholder": (
                "{content}, {name}, {title}, {category}, {tags} को "
                "प्लेसहोल्डर के रूप में उपयोग करें"
            ),
            "builder.available_placeholders": (
                "उपलब्ध प्लेसहोल्डर: {content}, {name}, {title}, {category}, {tags}"
            ),
            # Builder Actions & Messages
            "builder.min_prompts_required": ("कृपया जोड़ने के लिए कम से कम 2 प्रॉम्प्ट्स चुनें"),
            "builder.combined_prompt_name": "संयुक्त प्रॉम्प्ट ({count} भाग)",
            "builder.combined_category": "संयुक्त",
            "builder.combined_description": ("संयुक्त प्रॉम्प्ट इससे बनाया गया: {sources}"),
            "builder.combined_tags_suffix": "संयुक्त, {count}-भाग",
        }


# Global i18n instance
i18n = I18nManager()


# Convenience function for templates
def t(key: str, **kwargs) -> str:
    """Shorthand for i18n.t()"""
    return i18n.t(key, **kwargs)
