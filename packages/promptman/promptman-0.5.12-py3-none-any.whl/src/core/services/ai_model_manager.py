"""
AI Model Manager Service

This service manages AI models, their configurations, and provides intelligent
model selection for different operations.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..config.ai_model_config import (
    AIModelConfiguration,
    AIProvider,
    ModelConfig,
    OperationType,
    create_default_configuration,
)
from ..exceptions.base import ConfigurationException

logger = logging.getLogger(__name__)


class ModelHealthChecker:
    """Handles health checking for AI models."""

    def __init__(self, config: AIModelConfiguration):
        self.config = config
        self._health_cache: Dict[str, Tuple[bool, datetime, str]] = {}

    async def check_model_health(self, model: ModelConfig) -> Tuple[bool, str, float]:
        """
        Check the health of a specific model.

        Returns:
            Tuple of (is_healthy, status_message, response_time)
        """
        start_time = time.time()

        try:
            # Perform health check based on provider
            if model.provider == AIProvider.OPENAI:
                result = await self._check_openai_health(model)
            elif model.provider == AIProvider.AZURE_OPENAI:
                result = await self._check_azure_openai_health(model)
            elif model.provider == AIProvider.ANTHROPIC:
                result = await self._check_anthropic_health(model)
            elif model.provider == AIProvider.GOOGLE:
                result = await self._check_google_health(model)
            elif model.provider in [
                AIProvider.OLLAMA,
                AIProvider.LMSTUDIO,
                AIProvider.LLAMACPP,
            ]:
                result = await self._check_local_health(model)
            else:
                result = (False, f"Unsupported provider: {model.provider.value}")

            response_time = time.time() - start_time

            # Update cache
            self._health_cache[model.name] = (result[0], datetime.now(), result[1])

            # Update model availability
            model.is_available = result[0]
            model.last_health_check = datetime.now().isoformat()

            return result[0], result[1], response_time

        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Health check failed: {str(e)}"

            self._health_cache[model.name] = (False, datetime.now(), error_msg)
            model.is_available = False
            model.last_health_check = datetime.now().isoformat()

            logger.error(f"Health check failed for {model.name}: {e}")
            return False, error_msg, response_time

    async def _check_openai_health(self, model: ModelConfig) -> Tuple[bool, str]:
        """Check OpenAI model health."""
        if not model.api_key:
            return False, "API key not configured"

        try:
            # Mock health check - replace with actual OpenAI API call
            import httpx

            headers = {
                "Authorization": f"Bearer {model.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": model.model_id,
                "messages": [{"role": "user", "content": "Health check"}],
                "max_tokens": 5,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=10,
                )

                if response.status_code == 200:
                    return True, "Healthy"
                else:
                    return False, f"API error: {response.status_code}"

        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    async def _check_azure_openai_health(self, model: ModelConfig) -> Tuple[bool, str]:
        """Check Azure OpenAI model health."""
        if not model.api_key or not model.api_endpoint:
            return False, "API key or endpoint not configured"

        try:
            import httpx

            headers = {"api-key": model.api_key, "Content-Type": "application/json"}

            data = {
                "messages": [{"role": "user", "content": "Health check"}],
                "max_tokens": 5,
            }

            url = (
                f"{model.api_endpoint}/openai/deployments/"
                f"{model.deployment_name}/chat/completions"
            )
            if model.api_version:
                url += f"?api-version={model.api_version}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, headers=headers, json=data, timeout=10
                )

                if response.status_code == 200:
                    return True, "Healthy"
                else:
                    return False, f"API error: {response.status_code}"

        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    async def _check_anthropic_health(self, model: ModelConfig) -> Tuple[bool, str]:
        """Check Anthropic model health."""
        if not model.api_key:
            return False, "API key not configured"

        try:
            import httpx

            headers = {
                "x-api-key": model.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            }

            data = {
                "model": model.model_id,
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "Health check"}],
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=10,
                )

                if response.status_code == 200:
                    return True, "Healthy"
                else:
                    return False, f"API error: {response.status_code}"

        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    async def _check_google_health(self, model: ModelConfig) -> Tuple[bool, str]:
        """Check Google model health."""
        # Mock implementation - replace with actual Google API call
        return True, "Mock: Healthy"

    async def _check_local_health(self, model: ModelConfig) -> Tuple[bool, str]:
        """Check local model health (Ollama, LM Studio, etc.)."""
        if not model.api_endpoint:
            return False, "API endpoint not configured"

        try:
            import httpx

            # Try to ping the endpoint
            async with httpx.AsyncClient() as client:
                if model.provider == AIProvider.OLLAMA:
                    response = await client.get(
                        f"{model.api_endpoint.rstrip('/api/generate')}/api/tags",
                        timeout=5,
                    )
                else:
                    # Generic health check for other local services
                    response = await client.get(model.api_endpoint, timeout=5)

                if response.status_code == 200:
                    return True, "Healthy"
                else:
                    return False, f"Service error: {response.status_code}"

        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    async def check_all_models(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all enabled models."""
        results = {}
        tasks = []

        for model in self.config.get_enabled_models():
            task = self.check_model_health(model)
            tasks.append((model.name, task))

        # Run health checks concurrently
        for model_name, task in tasks:
            try:
                is_healthy, status, response_time = await task
                results[model_name] = {
                    "healthy": is_healthy,
                    "status": status,
                    "response_time": response_time,
                    "last_check": datetime.now().isoformat(),
                }
            except Exception as e:
                results[model_name] = {
                    "healthy": False,
                    "status": f"Check failed: {str(e)}",
                    "response_time": 0,
                    "last_check": datetime.now().isoformat(),
                }

        return results


class ModelSelector:
    """Handles intelligent model selection for different operations."""

    def __init__(self, config: AIModelConfiguration):
        self.config = config

    def select_model_for_operation(
        self, operation: OperationType, requirements: Optional[Dict[str, Any]] = None
    ) -> Optional[ModelConfig]:
        """
        Select the best model for a specific operation.

        Args:
            operation: The type of operation
            requirements: Optional requirements (e.g., max_tokens, supports_vision)

        Returns:
            The best available model for the operation
        """
        # Get models configured for this operation
        candidate_models = self.config.get_operation_models(operation)

        if not candidate_models:
            # Fall back to default operation models
            candidate_models = self.config.get_operation_models(OperationType.DEFAULT)

        if not candidate_models:
            logger.warning(f"No models configured for operation: {operation}")
            return None

        # Filter by requirements
        if requirements:
            candidate_models = self._filter_by_requirements(
                candidate_models, requirements
            )

        # Filter by availability
        available_models = [model for model in candidate_models if model.is_available]

        if not available_models:
            logger.warning(f"No available models for operation: {operation}")
            # Return the first configured model even if not available
            return candidate_models[0] if candidate_models else None

        # Return the first available model (they're already ordered by preference)
        return available_models[0]

    def _filter_by_requirements(
        self, models: List[ModelConfig], requirements: Dict[str, Any]
    ) -> List[ModelConfig]:
        """Filter models based on requirements."""
        filtered = []

        for model in models:
            if self._model_meets_requirements(model, requirements):
                filtered.append(model)

        return filtered

    def _model_meets_requirements(
        self, model: ModelConfig, requirements: Dict[str, Any]
    ) -> bool:
        """Check if a model meets the given requirements."""
        for key, value in requirements.items():
            if key == "max_tokens" and model.max_context_length:
                if value > model.max_context_length:
                    return False
            elif key == "supports_vision" and value:
                if not model.supports_vision:
                    return False
            elif key == "supports_function_calling" and value:
                if not model.supports_function_calling:
                    return False
            elif key == "supports_streaming" and value:
                if not model.supports_streaming:
                    return False
            elif key == "supports_json_mode" and value:
                if not model.supports_json_mode:
                    return False
            elif key == "max_cost_per_1k_tokens" and value:
                total_cost = (
                    model.cost_per_1k_input_tokens + model.cost_per_1k_output_tokens
                )
                if total_cost > value:
                    return False

        return True

    def get_fallback_models(
        self, operation: OperationType, failed_model: str
    ) -> List[ModelConfig]:
        """Get fallback models for an operation, excluding the failed model."""
        candidate_models = self.config.get_operation_models(operation)

        # Remove the failed model
        candidate_models = [
            model for model in candidate_models if model.name != failed_model
        ]

        # Filter by availability
        return [model for model in candidate_models if model.is_available]


class AIModelManager:
    """Main service for managing AI models and their usage."""

    def __init__(self, config: Optional[AIModelConfiguration] = None):
        self.config = config or create_default_configuration()
        self.health_checker = ModelHealthChecker(self.config)
        self.selector = ModelSelector(self.config)
        self._usage_stats: Dict[str, Dict[str, Any]] = {}

    async def initialize(self) -> None:
        """Initialize the model manager."""
        logger.info("Initializing AI Model Manager")

        # Run initial health checks
        await self.run_health_checks()

        logger.info(f"Initialized with {len(self.config.models)} models")

    def add_model(self, model: ModelConfig) -> None:
        """Add a new model to the configuration."""
        self.config.add_model(model)
        logger.info(f"Added model: {model.name}")

    def remove_model(self, model_name: str) -> None:
        """Remove a model from the configuration."""
        self.config.remove_model(model_name)
        logger.info(f"Removed model: {model_name}")

    def update_model(self, model_name: str, updates: Dict[str, Any]) -> None:
        """Update a model's configuration."""
        model = self.config.get_model(model_name)
        if not model:
            raise ConfigurationException(f"Model not found: {model_name}")

        # Update model properties
        for key, value in updates.items():
            if hasattr(model, key):
                setattr(model, key, value)

        logger.info(f"Updated model: {model_name}")

    async def select_model(
        self, operation: OperationType, requirements: Optional[Dict[str, Any]] = None
    ) -> Optional[ModelConfig]:
        """Select the best model for an operation."""
        return self.selector.select_model_for_operation(operation, requirements)

    async def run_health_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run health checks on all enabled models."""
        logger.info("Running health checks on all models")
        return await self.health_checker.check_all_models()

    async def check_model_health(self, model_name: str) -> Tuple[bool, str, float]:
        """Check health of a specific model."""
        model = self.config.get_model(model_name)
        if not model:
            raise ConfigurationException(f"Model not found: {model_name}")

        return await self.health_checker.check_model_health(model)

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all models."""
        total_requests = sum(
            stats.get("requests", 0) for stats in self._usage_stats.values()
        )
        total_tokens = sum(
            stats.get("tokens", 0) for stats in self._usage_stats.values()
        )
        total_cost = sum(stats.get("cost", 0.0) for stats in self._usage_stats.values())

        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "models": self._usage_stats.copy(),
        }

    def record_usage(
        self, model_name: str, tokens_used: int, cost: float, response_time: float
    ) -> None:
        """Record usage statistics for a model."""
        if model_name not in self._usage_stats:
            self._usage_stats[model_name] = {
                "requests": 0,
                "tokens": 0,
                "cost": 0.0,
                "total_response_time": 0.0,
                "last_used": None,
            }

        stats = self._usage_stats[model_name]
        stats["requests"] += 1
        stats["tokens"] += tokens_used
        stats["cost"] += cost
        stats["total_response_time"] += response_time
        stats["last_used"] = datetime.now().isoformat()
        stats["avg_response_time"] = stats["total_response_time"] / stats["requests"]

    def get_model_recommendations(
        self, operation: OperationType
    ) -> List[Dict[str, Any]]:
        """Get model recommendations for an operation."""
        available_models = self.config.get_available_models()

        recommendations = []
        for model in available_models:
            score = self._calculate_model_score(model, operation)
            recommendations.append(
                {
                    "model": model,
                    "score": score,
                    "reason": self._get_recommendation_reason(model, operation, score),
                }
            )

        # Sort by score (higher is better)
        recommendations.sort(
            key=lambda x: x["score"] if isinstance(x["score"], (int, float)) else 0.0,
            reverse=True,
        )

        return recommendations[:5]  # Return top 5 recommendations

    def _calculate_model_score(
        self, model: ModelConfig, operation: OperationType
    ) -> float:
        """Calculate a score for how well a model fits an operation."""
        score = 0.0

        # Base availability score
        if model.is_available:
            score += 10.0

        # Operation-specific scoring
        if operation == OperationType.PROMPT_ENHANCEMENT:
            if model.max_context_length and model.max_context_length >= 16000:
                score += 5.0
            if model.supports_function_calling:
                score += 3.0
        elif operation == OperationType.PROMPT_TESTING:
            # Prefer faster, cheaper models for testing
            total_cost = (
                model.cost_per_1k_input_tokens + model.cost_per_1k_output_tokens
            )
            if total_cost <= 0.002:
                score += 5.0
            elif total_cost <= 0.01:
                score += 3.0
            elif total_cost <= 0.05:
                score += 1.0
        elif operation == OperationType.ANALYSIS:
            if model.max_context_length and model.max_context_length >= 32000:
                score += 5.0

        # Usage history bonus
        if model.name in self._usage_stats:
            stats = self._usage_stats[model.name]
            # Models with good performance get bonus points
            if stats.get("avg_response_time", 0) < 2.0:
                score += 2.0

        return score

    def _get_recommendation_reason(
        self, model: ModelConfig, operation: OperationType, score: float
    ) -> str:
        """Get a human-readable reason for the recommendation."""
        reasons = []

        if not model.is_available:
            return "Model is currently unavailable"

        if operation == OperationType.PROMPT_ENHANCEMENT:
            if model.max_context_length and model.max_context_length >= 16000:
                reasons.append("Large context window")
            if model.supports_function_calling:
                reasons.append("Function calling support")
        elif operation == OperationType.PROMPT_TESTING:
            total_cost = (
                model.cost_per_1k_input_tokens + model.cost_per_1k_output_tokens
            )
            if total_cost < 0.002:
                reasons.append("Cost-effective for testing")

        if score >= 15.0:
            reasons.append("Excellent fit")
        elif score >= 10.0:
            reasons.append("Good fit")
        else:
            reasons.append("Available option")

        return ", ".join(reasons) if reasons else "Available model"

    def export_configuration(self) -> Dict[str, Any]:
        """Export the current configuration."""
        return self.config.to_dict()

    def import_configuration(self, config_data: Dict[str, Any]) -> None:
        """Import a configuration."""
        try:
            new_config = AIModelConfiguration.from_dict(config_data)
            self.config = new_config
            self.health_checker = ModelHealthChecker(self.config)
            self.selector = ModelSelector(self.config)
            logger.info("Configuration imported successfully")
        except Exception as e:
            raise ConfigurationException(f"Failed to import configuration: {str(e)}")


# Global instance
_model_manager: Optional[AIModelManager] = None


async def get_model_manager() -> AIModelManager:
    """Get the global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = AIModelManager()
        await _model_manager.initialize()
    return _model_manager


def reset_model_manager() -> None:
    """Reset the global model manager (useful for testing)."""
    global _model_manager
    _model_manager = None
