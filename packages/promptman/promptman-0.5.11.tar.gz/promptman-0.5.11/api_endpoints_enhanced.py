"""
Enhanced API Endpoints for AI Model Configuration

This module provides FastAPI endpoints for managing AI models and their configurations
across different operations in the prompt manager.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from auth_manager import AuthManager
from prompt_data_manager import PromptDataManager
from src.core.config.ai_model_config import (
    AIProvider,
    ModelConfig,
    OperationType,
)
from src.core.services.ai_model_manager import get_model_manager
from src.prompts.models.prompt import Prompt
from src.utils.github_format import GitHubFormatHandler

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses


class ModelConfigRequest(BaseModel):
    name: str
    display_name: Optional[str] = None
    provider: str
    model_id: str
    description: Optional[str] = None
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_version: Optional[str] = None
    deployment_name: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0
    max_context_length: Optional[int] = None
    supports_streaming: bool = False
    supports_function_calling: bool = False
    supports_vision: bool = False
    supports_json_mode: bool = False
    is_enabled: bool = True


class ModelUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_version: Optional[str] = None
    deployment_name: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    cost_per_1k_input_tokens: Optional[float] = None
    cost_per_1k_output_tokens: Optional[float] = None
    max_context_length: Optional[int] = None
    supports_streaming: Optional[bool] = None
    supports_function_calling: Optional[bool] = None
    supports_vision: Optional[bool] = None
    supports_json_mode: Optional[bool] = None
    is_enabled: Optional[bool] = None


class OperationConfigRequest(BaseModel):
    primary_model: Optional[str] = None
    fallback_models: List[str] = []
    is_enabled: bool = True
    custom_parameters: Dict[str, Any] = {}


class TestModelRequest(BaseModel):
    test_prompt: str = "Hello! This is a test message to verify the model connection."


def get_current_user(request: Request) -> Dict[str, Any]:
    """Get current user from session or create default for single-user mode."""
    auth_manager = AuthManager()

    if not auth_manager.is_multitenant_mode():
        # Single-user mode
        return {
            "tenant_id": "single-user",
            "user_id": "single-user",
            "email": "user@localhost",
        }

    # Multi-tenant mode - get from session
    session_token = request.session.get("auth_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Validate session token and get user
    is_valid, user = auth_manager.validate_session(session_token)
    if not is_valid or not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    return {
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "email": user.email,
        "role": user.role,
    }


def get_data_manager(
    user_info: Dict[str, Any] = Depends(get_current_user)
) -> PromptDataManager:
    """Get data manager with user context."""
    # Get current DB_PATH from environment (for testing)
    db_path = os.getenv("DB_PATH", "prompts.db")
    return PromptDataManager(
        db_path=db_path, tenant_id=user_info["tenant_id"], user_id=user_info["user_id"]
    )


# Create router
router = APIRouter(prefix="/api/ai-models", tags=["AI Models"])


@router.get("/")
async def get_models(
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Get all AI models for the current tenant."""
    try:
        models = data_manager.get_ai_models()
        return {"success": True, "models": models, "count": len(models)}
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve models")


@router.post("/")
async def add_model(
    model_request: ModelConfigRequest,
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Add a new AI model configuration."""
    try:
        # Validate provider
        try:
            AIProvider(model_request.provider)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid provider: {model_request.provider}"
            )

        # Convert to dict
        model_data = model_request.model_dump()

        # Add model to database
        success = data_manager.add_ai_model(model_data)

        if success:
            return {"success": True, "message": "Model added successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to add model")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding model: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{model_name}")
async def update_model(
    model_name: str,
    update_request: ModelUpdateRequest,
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Update an AI model configuration."""
    try:
        # Filter out None values
        updates = {
            k: v for k, v in update_request.model_dump().items() if v is not None
        }

        if not updates:
            return {"success": True, "message": "No updates provided"}

        success = data_manager.update_ai_model(model_name, updates)

        if success:
            return {"success": True, "message": "Model updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Model not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating model {model_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{model_name}")
async def delete_model(
    model_name: str, data_manager: PromptDataManager = Depends(get_data_manager)
) -> Dict[str, Any]:
    """Delete an AI model configuration."""
    try:
        success = data_manager.delete_ai_model(model_name)

        if success:
            return {"success": True, "message": "Model deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Model not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting model {model_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{model_name}/test")
async def test_model(
    model_name: str,
    test_request: TestModelRequest,
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Test an AI model configuration."""
    try:
        # Get model configuration from database
        models = data_manager.get_ai_models()
        model_config = next((m for m in models if m["name"] == model_name), None)

        if not model_config:
            raise HTTPException(status_code=404, detail="Model not found")

        # Get model manager and perform health check
        model_manager = await get_model_manager()

        # Create ModelConfig object
        model = ModelConfig(
            name=model_config["name"],
            provider=AIProvider(model_config["provider"]),
            model_id=model_config["model_id"],
            api_key=model_config.get("api_key"),
            api_endpoint=model_config.get("api_endpoint"),
            api_version=model_config.get("api_version"),
            deployment_name=model_config.get("deployment_name"),
        )

        # Perform health check
        is_healthy, status_message, response_time = (
            await model_manager.health_checker.check_model_health(model)
        )

        return {
            "success": is_healthy,
            "status": status_message,
            "response_time": response_time,
            "model_name": model_name,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


@router.post("/health-check")
async def run_health_checks(
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Run health checks on all models."""
    try:
        model_manager = await get_model_manager()
        results = await model_manager.run_health_checks()

        return {
            "success": True,
            "results": results,
            "message": "Health checks completed",
        }

    except Exception as e:
        logger.error(f"Error running health checks: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/operations")
async def get_operation_configs(
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Get AI operation configurations."""
    try:
        configs = data_manager.get_ai_operation_configs()

        # Add default configurations for operations that don't exist
        existing_ops = {config["operation_type"] for config in configs}
        all_ops = [op.value for op in OperationType]

        for op in all_ops:
            if op not in existing_ops:
                configs.append(
                    {
                        "operation_type": op,
                        "primary_model": None,
                        "fallback_models": None,
                        "is_enabled": True,
                        "custom_parameters": None,
                    }
                )

        return {"success": True, "configurations": configs}

    except Exception as e:
        logger.error(f"Error getting operation configs: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve operation configurations"
        )


@router.put("/operations/{operation_type}")
async def update_operation_config(
    operation_type: str,
    config_request: OperationConfigRequest,
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Update an AI operation configuration."""
    try:
        # Validate operation type
        try:
            OperationType(operation_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid operation type: {operation_type}"
            )

        # Convert fallback models list to JSON string
        config_data = config_request.model_dump()
        config_data["fallback_models"] = json.dumps(config_data["fallback_models"])
        config_data["custom_parameters"] = json.dumps(config_data["custom_parameters"])

        success = data_manager.update_ai_operation_config(operation_type, config_data)

        if success:
            return {
                "success": True,
                "message": "Operation configuration updated successfully",
            }
        else:
            raise HTTPException(
                status_code=400, detail="Failed to update operation configuration"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating operation config {operation_type}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/providers")
async def get_providers() -> Dict[str, Any]:
    """Get available AI providers and their information."""
    providers = []

    for provider in AIProvider:
        provider_info: Dict[str, Any] = {
            "id": provider.value,
            "name": provider.value.replace("_", " ").title(),
            "supported_features": [],
            "configuration_fields": [],
        }

        # Add provider-specific information
        if provider == AIProvider.OPENAI:
            provider_info.update(
                {
                    "name": "OpenAI",
                    "supported_features": [
                        "streaming",
                        "function_calling",
                        "vision",
                        "json_mode",
                    ],
                    "configuration_fields": ["api_key"],
                }
            )
        elif provider == AIProvider.AZURE_OPENAI:
            provider_info.update(
                {
                    "name": "Azure OpenAI",
                    "supported_features": [
                        "streaming",
                        "function_calling",
                        "vision",
                        "json_mode",
                    ],
                    "configuration_fields": [
                        "api_key",
                        "api_endpoint",
                        "deployment_name",
                        "api_version",
                    ],
                }
            )
        elif provider == AIProvider.ANTHROPIC:
            provider_info.update(
                {
                    "name": "Anthropic",
                    "supported_features": ["streaming", "vision"],
                    "configuration_fields": ["api_key"],
                }
            )
        elif provider == AIProvider.GOOGLE:
            provider_info.update(
                {
                    "name": "Google AI",
                    "supported_features": ["streaming", "vision"],
                    "configuration_fields": ["api_key"],
                }
            )
        elif provider in [AIProvider.OLLAMA, AIProvider.LMSTUDIO, AIProvider.LLAMACPP]:
            provider_info.update(
                {
                    "supported_features": ["streaming"],
                    "configuration_fields": ["api_endpoint"],
                }
            )

        providers.append(provider_info)

    return {"success": True, "providers": providers}


@router.get("/operation-types")
async def get_operation_types() -> Dict[str, Any]:
    """Get available operation types and their descriptions."""
    operation_types = []

    descriptions = {
        OperationType.DEFAULT: "Default operations within the application",
        OperationType.PROMPT_ENHANCEMENT: "Improving prompt quality and effectiveness",
        OperationType.PROMPT_OPTIMIZATION: "Optimizing prompts for performance",
        OperationType.PROMPT_TESTING: "Testing prompts with different models",
        OperationType.PROMPT_COMBINING: "Combining multiple prompts intelligently",
        OperationType.TRANSLATION: "Text translation between languages",
        OperationType.TOKEN_CALCULATION: "Token counting and cost estimation",
        OperationType.GENERATION: "Content generation tasks",
        OperationType.ANALYSIS: "Content analysis and insights",
        OperationType.CATEGORIZATION: "Content categorization and tagging",
        OperationType.SUMMARIZATION: "Content summarization tasks",
    }

    for op_type in OperationType:
        operation_types.append(
            {
                "id": op_type.value,
                "name": op_type.value.replace("_", " ").title(),
                "description": descriptions.get(op_type, "AI operation"),
            }
        )

    return {"success": True, "operation_types": operation_types}


@router.get("/recommendations/{operation_type}")
async def get_model_recommendations(
    operation_type: str, data_manager: PromptDataManager = Depends(get_data_manager)
) -> Dict[str, Any]:
    """Get model recommendations for a specific operation."""
    try:
        # Validate operation type
        try:
            op_type = OperationType(operation_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid operation type: {operation_type}"
            )

        model_manager = await get_model_manager()
        recommendations = model_manager.get_model_recommendations(op_type)

        # Convert recommendations to serializable format
        serializable_recommendations = []
        for rec in recommendations:
            model_data = rec["model"].to_dict()
            serializable_recommendations.append(
                {"model": model_data, "score": rec["score"], "reason": rec["reason"]}
            )

        return {
            "success": True,
            "recommendations": serializable_recommendations,
            "operation_type": operation_type,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations for {operation_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")


@router.get("/usage-stats")
async def get_usage_stats() -> Dict[str, Any]:
    """Get usage statistics for all models."""
    try:
        model_manager = await get_model_manager()
        stats = model_manager.get_usage_stats()

        return {"success": True, "stats": stats}

    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage statistics")


@router.post("/export")
async def export_configuration(
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Export AI model configuration."""
    try:
        models = data_manager.get_ai_models()
        operation_configs = data_manager.get_ai_operation_configs()

        export_data = {
            "models": models,
            "operation_configs": operation_configs,
            "export_timestamp": "2025-01-06T12:00:00Z",
            "version": "1.0",
        }

        return {"success": True, "configuration": export_data}

    except Exception as e:
        logger.error(f"Error exporting configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to export configuration")


@router.post("/import")
async def import_configuration(
    configuration: Dict[str, Any],
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Import AI model configuration."""
    try:
        imported_models = 0
        imported_configs = 0

        # Import models
        if "models" in configuration:
            for model_data in configuration["models"]:
                # Remove tenant/user specific fields
                model_data.pop("id", None)
                model_data.pop("tenant_id", None)
                model_data.pop("user_id", None)
                model_data.pop("created_at", None)
                model_data.pop("updated_at", None)

                if data_manager.add_ai_model(model_data):
                    imported_models += 1

        # Import operation configs
        if "operation_configs" in configuration:
            for config_data in configuration["operation_configs"]:
                operation_type = config_data.get("operation_type")
                if operation_type:
                    # Remove tenant/user specific fields
                    config_data.pop("id", None)
                    config_data.pop("tenant_id", None)
                    config_data.pop("user_id", None)
                    config_data.pop("created_at", None)
                    config_data.pop("updated_at", None)

                    if data_manager.update_ai_operation_config(
                        operation_type, config_data
                    ):
                        imported_configs += 1

        return {
            "success": True,
            "message": (
                f"Imported {imported_models} models and "
                f"{imported_configs} operation configurations"
            ),
        }

    except Exception as e:
        logger.error(f"Error importing configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to import configuration")


# GitHub Format Endpoints
class GitHubFormatRequest(BaseModel):
    """Request model for GitHub format operations."""

    yaml_content: str
    name: Optional[str] = None
    title: Optional[str] = None
    category: str = "GitHub Import"


class GitHubFormatResponse(BaseModel):
    """Response model for GitHub format operations."""

    success: bool
    message: str
    prompt_id: Optional[int] = None
    yaml_content: Optional[str] = None


@router.post("/github/import")
async def import_github_format(
    request: GitHubFormatRequest,
    data_manager: PromptDataManager = Depends(get_data_manager),
    user_info: Dict[str, Any] = Depends(get_current_user),
) -> GitHubFormatResponse:
    """
    Import a prompt from GitHub YAML format.

    Args:
        request: GitHub format import request
        data_manager: Data manager instance
        user_info: Current user information

    Returns:
        Import result with prompt ID
    """
    try:
        # Create prompt from GitHub format
        prompt = Prompt.from_github_yaml(
            request.yaml_content,
            tenant_id=user_info["tenant_id"],
            user_id=user_info["user_id"],
            name=request.name,
            title=request.title,
            category=request.category,
        )

        # Save to database
        data_manager.add_prompt(
            name=prompt.name,
            title=prompt.title,
            content=prompt.content,
            category=prompt.category,
            tags=prompt.tags,
            is_enhancement_prompt=prompt.is_enhancement_prompt,
        )

        # Extract prompt ID from result (add_prompt returns a success message)
        # For now, we'll get the prompt by name to get its data
        prompt_data = data_manager.get_prompt_by_name(prompt.name)
        prompt_id = prompt_data.get("id") if prompt_data else None

        # Store GitHub-specific metadata if prompt was created successfully
        if prompt_id and prompt.metadata:
            # Note: This would require extending the database schema
            # to store metadata, for now we'll just return success
            pass

        return GitHubFormatResponse(
            success=True,
            message=f"Successfully imported prompt '{prompt.name}'",
            prompt_id=prompt_id,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error importing GitHub format: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to import GitHub format prompt"
        )


@router.get("/github/export/{prompt_id}")
async def export_github_format(
    prompt_id: int,
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> GitHubFormatResponse:
    """
    Export a prompt to GitHub YAML format.

    Args:
        prompt_id: ID of prompt to export
        data_manager: Data manager instance

    Returns:
        Export result with YAML content
    """
    try:
        # Get prompt from database - first get all prompts and find by ID
        all_prompts = data_manager.get_all_prompts()
        prompt_data = None
        for p in all_prompts:
            if p.get("id") == prompt_id:
                prompt_data = p
                break

        if not prompt_data:
            raise HTTPException(status_code=404, detail="Prompt not found")

        # Convert to Prompt object
        prompt = Prompt.from_legacy_dict(
            prompt_data,
            tenant_id=prompt_data.get("tenant_id", ""),
            user_id=prompt_data.get("user_id", ""),
        )

        # Convert to GitHub format
        yaml_content = prompt.to_github_yaml()

        return GitHubFormatResponse(
            success=True,
            message=f"Successfully exported prompt '{prompt.name}'",
            yaml_content=yaml_content,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting GitHub format: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to export prompt to GitHub format"
        )


@router.get("/github/info")
async def get_github_format_info() -> Dict[str, Any]:
    """
    Get information about the GitHub format.

    Returns:
        GitHub format specification and example
    """
    try:
        github_handler = GitHubFormatHandler()
        return {"success": True, "format_info": github_handler.get_format_info()}
    except Exception as e:
        logger.error(f"Error getting GitHub format info: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get GitHub format information"
        )


# Tag Management Endpoints


class TagSearchRequest(BaseModel):
    """Request model for tag-based search operations."""

    tags: List[str]
    entity_type: str = "prompts"  # "prompts", "templates", "all"
    match_all: bool = False  # True for AND logic, False for OR logic
    include_enhancement_prompts: bool = True


class TagSuggestionRequest(BaseModel):
    """Request model for tag suggestions."""

    partial_tag: str
    limit: int = 5


class TagStatisticsResponse(BaseModel):
    """Response model for tag statistics."""

    success: bool
    statistics: Dict[str, Dict] = {}
    popular_tags: List[Dict] = []


@router.get("/tags")
async def get_all_tags(
    entity_type: str = "all",
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Get all unique tags across prompts and/or templates."""
    try:
        tags = data_manager.get_all_tags(entity_type)
        return {
            "success": True,
            "tags": tags,
            "count": len(tags),
            "entity_type": entity_type,
        }
    except Exception as e:
        logger.error(f"Error getting tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tags")


@router.post("/tags/search")
async def search_by_tags(
    request: TagSearchRequest,
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Search entities by tags with AND/OR logic."""
    try:
        results = data_manager.search_by_tags(
            tags=request.tags,
            entity_type=request.entity_type,
            match_all=request.match_all,
            include_enhancement_prompts=request.include_enhancement_prompts,
        )

        return {
            "success": True,
            "results": results,
            "count": len(results),
            "search_params": {
                "tags": request.tags,
                "entity_type": request.entity_type,
                "match_all": request.match_all,
                "logic": "AND" if request.match_all else "OR",
            },
        }
    except Exception as e:
        logger.error(f"Error searching by tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to search by tags")


@router.get("/tags/statistics")
async def get_tag_statistics(
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> TagStatisticsResponse:
    """Get comprehensive tag usage statistics."""
    try:
        statistics: Dict[str, Any] = data_manager.get_tag_statistics()
        popular_tags = data_manager.get_popular_tags(entity_type="all", limit=10)

        return TagStatisticsResponse(
            success=True, statistics=statistics, popular_tags=popular_tags
        )
    except Exception as e:
        logger.error(f"Error getting tag statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tag statistics")


@router.get("/tags/popular")
async def get_popular_tags(
    entity_type: str = "all",
    limit: int = 10,
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Get most popular tags with usage counts."""
    try:
        popular_tags = data_manager.get_popular_tags(entity_type, limit)

        return {
            "success": True,
            "popular_tags": popular_tags,
            "entity_type": entity_type,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Error getting popular tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to get popular tags")


@router.post("/tags/suggest")
async def suggest_tags(
    request: TagSuggestionRequest,
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Get tag suggestions based on partial input."""
    try:
        suggestions = data_manager.suggest_tags(request.partial_tag, request.limit)

        return {
            "success": True,
            "suggestions": suggestions,
            "partial_tag": request.partial_tag,
            "count": len(suggestions),
        }
    except Exception as e:
        logger.error(f"Error getting tag suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tag suggestions")


@router.get("/tags/analysis")
async def analyze_tags(
    data_manager: PromptDataManager = Depends(get_data_manager),
) -> Dict[str, Any]:
    """Get comprehensive tag analysis with insights."""
    try:
        statistics: Dict[str, Any] = data_manager.get_tag_statistics()
        popular_tags = data_manager.get_popular_tags(entity_type="all", limit=20)

        # Calculate insights
        total_tags = len(statistics)
        total_usage = sum(stats["total"] for stats in statistics.values())
        avg_usage = total_usage / total_tags if total_tags > 0 else 0

        # Find most versatile tags (used in both prompts and templates)
        versatile_tags = [
            {"tag": tag, "stats": stats}
            for tag, stats in statistics.items()
            if stats["prompts"] > 0 and stats["templates"] > 0
        ]
        versatile_tags.sort(key=lambda x: x["stats"]["total"], reverse=True)

        # Find underutilized tags (used only once)
        underutilized_tags = [
            {"tag": tag, "stats": stats}
            for tag, stats in statistics.items()
            if stats["total"] == 1
        ]

        return {
            "success": True,
            "overview": {
                "total_unique_tags": total_tags,
                "total_tag_usage": total_usage,
                "average_usage_per_tag": round(avg_usage, 2),
            },
            "popular_tags": popular_tags[:10],
            "versatile_tags": versatile_tags[:5],
            "underutilized_tags": len(underutilized_tags),
            "tag_distribution": {
                "prompt_only": len(
                    [
                        t
                        for t in statistics.values()
                        if t["prompts"] > 0 and t["templates"] == 0
                    ]
                ),
                "template_only": len(
                    [
                        t
                        for t in statistics.values()
                        if t["templates"] > 0 and t["prompts"] == 0
                    ]
                ),
                "both": len(versatile_tags),
            },
        }
    except Exception as e:
        logger.error(f"Error analyzing tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze tags")


# Function to include router in main app
def get_ai_models_router() -> APIRouter:
    """Get the AI models router for inclusion in the main FastAPI app."""
    return router
