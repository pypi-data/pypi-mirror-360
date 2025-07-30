"""
Enhanced AI Model Configuration System

This module provides a comprehensive configuration system for managing
multiple AI models and service providers across different operations in the
prompt manager.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AIProvider(Enum):
    """Supported AI service providers."""

    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    LLAMACPP = "llamacpp"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    TOGETHER = "together"
    MISTRAL = "mistral"
    PERPLEXITY = "perplexity"
    REPLICATE = "replicate"


class OperationType(Enum):
    """Different types of operations that can use AI models."""

    DEFAULT = "default"  # Default operations within the application
    PROMPT_ENHANCEMENT = "prompt_enhancement"  # Improving prompt quality
    PROMPT_OPTIMIZATION = "prompt_optimization"  # Optimizing prompts for performance
    PROMPT_TESTING = "prompt_testing"  # Testing prompts with models
    PROMPT_COMBINING = "prompt_combining"  # Combining multiple prompts
    TRANSLATION = "translation"  # Text translation
    TOKEN_CALCULATION = "token_calculation"  # Token counting and cost estimation
    GENERATION = "generation"  # Content generation
    ANALYSIS = "analysis"  # Content analysis and insights
    CATEGORIZATION = "categorization"  # Content categorization
    SUMMARIZATION = "summarization"  # Content summarization


@dataclass
class ModelConfig:
    """Configuration for a specific AI model."""

    name: str
    provider: AIProvider
    model_id: str
    display_name: Optional[str] = None
    description: Optional[str] = None

    # Connection settings
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_version: Optional[str] = None
    deployment_name: Optional[str] = None  # For Azure

    # Model parameters
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    # Cost and performance
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0
    max_context_length: Optional[int] = None

    # Features
    supports_streaming: bool = False
    supports_function_calling: bool = False
    supports_vision: bool = False
    supports_json_mode: bool = False

    # Status
    is_enabled: bool = True
    is_available: bool = False  # Determined by health checks
    last_health_check: Optional[str] = None

    def get_display_name(self) -> str:
        """Get the display name for the model."""
        return self.display_name or self.name

    def get_full_name(self) -> str:
        """Get the full name including provider."""
        return f"{self.provider.value}/{self.model_id}"

    def estimate_cost(self, input_tokens: int, output_tokens: int = 0) -> float:
        """Estimate the cost for given token usage."""
        input_cost = (input_tokens / 1000) * self.cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * self.cost_per_1k_output_tokens
        return input_cost + output_cost

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "name": self.name,
            "provider": self.provider.value,
            "model_id": self.model_id,
            "display_name": self.display_name,
            "description": self.description,
            "api_endpoint": self.api_endpoint,
            "api_version": self.api_version,
            "deployment_name": self.deployment_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "cost_per_1k_input_tokens": self.cost_per_1k_input_tokens,
            "cost_per_1k_output_tokens": self.cost_per_1k_output_tokens,
            "max_context_length": self.max_context_length,
            "supports_streaming": self.supports_streaming,
            "supports_function_calling": self.supports_function_calling,
            "supports_vision": self.supports_vision,
            "supports_json_mode": self.supports_json_mode,
            "is_enabled": self.is_enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelConfig":
        """Create from dictionary."""
        provider = AIProvider(data["provider"])
        return cls(
            name=data["name"],
            provider=provider,
            model_id=data["model_id"],
            display_name=data.get("display_name"),
            description=data.get("description"),
            api_endpoint=data.get("api_endpoint"),
            api_version=data.get("api_version"),
            deployment_name=data.get("deployment_name"),
            max_tokens=data.get("max_tokens"),
            temperature=data.get("temperature", 0.7),
            top_p=data.get("top_p", 1.0),
            frequency_penalty=data.get("frequency_penalty", 0.0),
            presence_penalty=data.get("presence_penalty", 0.0),
            cost_per_1k_input_tokens=data.get("cost_per_1k_input_tokens", 0.0),
            cost_per_1k_output_tokens=data.get("cost_per_1k_output_tokens", 0.0),
            max_context_length=data.get("max_context_length"),
            supports_streaming=data.get("supports_streaming", False),
            supports_function_calling=data.get("supports_function_calling", False),
            supports_vision=data.get("supports_vision", False),
            supports_json_mode=data.get("supports_json_mode", False),
            is_enabled=data.get("is_enabled", True),
        )


@dataclass
class OperationConfig:
    """Configuration for AI model usage in specific operations."""

    operation_type: OperationType
    primary_model: Optional[str] = None  # Model name
    fallback_models: List[str] = field(default_factory=list)
    is_enabled: bool = True
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

    def get_model_sequence(self) -> List[str]:
        """Get the sequence of models to try for this operation."""
        models = []
        if self.primary_model:
            models.append(self.primary_model)
        models.extend(self.fallback_models)
        return models


@dataclass
class AIModelConfiguration:
    """Main configuration class for AI models and operations."""

    # Available models
    models: Dict[str, ModelConfig] = field(default_factory=dict)

    # Operation configurations
    operations: Dict[OperationType, OperationConfig] = field(default_factory=dict)

    # Global settings
    default_timeout: int = 30
    max_retries: int = 3
    health_check_interval: int = 300  # seconds

    def add_model(self, model: ModelConfig) -> None:
        """Add a model to the configuration."""
        self.models[model.name] = model

    def remove_model(self, model_name: str) -> None:
        """Remove a model from the configuration."""
        if model_name in self.models:
            del self.models[model_name]
            # Remove from operations
            for op_config in self.operations.values():
                if op_config.primary_model == model_name:
                    op_config.primary_model = None
                if model_name in op_config.fallback_models:
                    op_config.fallback_models.remove(model_name)

    def get_model(self, model_name: str) -> Optional[ModelConfig]:
        """Get a model by name."""
        return self.models.get(model_name)

    def get_enabled_models(self) -> List[ModelConfig]:
        """Get all enabled models."""
        return [model for model in self.models.values() if model.is_enabled]

    def get_available_models(self) -> List[ModelConfig]:
        """Get all available (enabled and healthy) models."""
        return [
            model
            for model in self.models.values()
            if model.is_enabled and model.is_available
        ]

    def get_models_by_provider(self, provider: AIProvider) -> List[ModelConfig]:
        """Get all models for a specific provider."""
        return [model for model in self.models.values() if model.provider == provider]

    def set_operation_model(
        self,
        operation: OperationType,
        primary_model: Optional[str] = None,
        fallback_models: Optional[List[str]] = None,
    ) -> None:
        """Set the model configuration for an operation."""
        if operation not in self.operations:
            self.operations[operation] = OperationConfig(operation_type=operation)

        op_config = self.operations[operation]
        if primary_model is not None:
            op_config.primary_model = primary_model
        if fallback_models is not None:
            op_config.fallback_models = fallback_models

    def get_operation_models(self, operation: OperationType) -> List[ModelConfig]:
        """Get the models configured for a specific operation."""
        if operation not in self.operations:
            # Return default operation models if specific operation not configured
            operation = OperationType.DEFAULT

        if operation not in self.operations:
            return []

        op_config = self.operations[operation]
        model_sequence = op_config.get_model_sequence()

        return [
            self.models[model_name]
            for model_name in model_sequence
            if model_name in self.models and self.models[model_name].is_enabled
        ]

    def get_best_model_for_operation(
        self, operation: OperationType
    ) -> Optional[ModelConfig]:
        """Get the best available model for a specific operation."""
        models = self.get_operation_models(operation)
        available_models = [model for model in models if model.is_available]
        return available_models[0] if available_models else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "models": {name: model.to_dict() for name, model in self.models.items()},
            "operations": {
                op_type.value: {
                    "primary_model": op_config.primary_model,
                    "fallback_models": op_config.fallback_models,
                    "is_enabled": op_config.is_enabled,
                    "custom_parameters": op_config.custom_parameters,
                }
                for op_type, op_config in self.operations.items()
            },
            "default_timeout": self.default_timeout,
            "max_retries": self.max_retries,
            "health_check_interval": self.health_check_interval,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIModelConfiguration":
        """Create from dictionary."""
        config = cls(
            default_timeout=data.get("default_timeout", 30),
            max_retries=data.get("max_retries", 3),
            health_check_interval=data.get("health_check_interval", 300),
        )

        # Load models
        for name, model_data in data.get("models", {}).items():
            model = ModelConfig.from_dict(model_data)
            config.models[name] = model

        # Load operations
        for op_type_str, op_data in data.get("operations", {}).items():
            op_type = OperationType(op_type_str)
            op_config = OperationConfig(
                operation_type=op_type,
                primary_model=op_data.get("primary_model"),
                fallback_models=op_data.get("fallback_models", []),
                is_enabled=op_data.get("is_enabled", True),
                custom_parameters=op_data.get("custom_parameters", {}),
            )
            config.operations[op_type] = op_config

        return config


def get_default_models() -> List[ModelConfig]:
    """Get a list of default model configurations."""
    return [
        # OpenAI Models
        ModelConfig(
            name="gpt-4-turbo",
            provider=AIProvider.OPENAI,
            model_id="gpt-4-turbo-preview",
            display_name="GPT-4 Turbo",
            description="Most capable GPT-4 model with 128k context",
            max_context_length=128000,
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03,
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_json_mode=True,
        ),
        ModelConfig(
            name="gpt-4",
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            display_name="GPT-4",
            description="High-quality reasoning and instruction following",
            max_context_length=8192,
            cost_per_1k_input_tokens=0.03,
            cost_per_1k_output_tokens=0.06,
            supports_streaming=True,
            supports_function_calling=True,
        ),
        ModelConfig(
            name="gpt-3.5-turbo",
            provider=AIProvider.OPENAI,
            model_id="gpt-3.5-turbo",
            display_name="GPT-3.5 Turbo",
            description="Fast and efficient model for most tasks",
            max_context_length=16385,
            cost_per_1k_input_tokens=0.0005,
            cost_per_1k_output_tokens=0.0015,
            supports_streaming=True,
            supports_function_calling=True,
        ),
        # Anthropic Models
        ModelConfig(
            name="claude-3-opus",
            provider=AIProvider.ANTHROPIC,
            model_id="claude-3-opus-20240229",
            display_name="Claude 3 Opus",
            description="Most capable Claude model for complex tasks",
            max_context_length=200000,
            cost_per_1k_input_tokens=0.015,
            cost_per_1k_output_tokens=0.075,
            supports_streaming=True,
            supports_vision=True,
        ),
        ModelConfig(
            name="claude-3-sonnet",
            provider=AIProvider.ANTHROPIC,
            model_id="claude-3-sonnet-20240229",
            display_name="Claude 3 Sonnet",
            description="Balanced performance and speed",
            max_context_length=200000,
            cost_per_1k_input_tokens=0.003,
            cost_per_1k_output_tokens=0.015,
            supports_streaming=True,
            supports_vision=True,
        ),
        ModelConfig(
            name="claude-3-haiku",
            provider=AIProvider.ANTHROPIC,
            model_id="claude-3-haiku-20240307",
            display_name="Claude 3 Haiku",
            description="Fast and cost-effective model",
            max_context_length=200000,
            cost_per_1k_input_tokens=0.00025,
            cost_per_1k_output_tokens=0.00125,
            supports_streaming=True,
            supports_vision=True,
        ),
        # Google Models
        ModelConfig(
            name="gemini-pro",
            provider=AIProvider.GOOGLE,
            model_id="gemini-pro",
            display_name="Gemini Pro",
            description="Google's advanced multimodal model",
            max_context_length=32768,
            cost_per_1k_input_tokens=0.0005,
            cost_per_1k_output_tokens=0.0015,
            supports_streaming=True,
            supports_vision=True,
        ),
        # Mistral Models
        ModelConfig(
            name="mistral-large",
            provider=AIProvider.MISTRAL,
            model_id="mistral-large-latest",
            display_name="Mistral Large",
            description="Mistral's most capable model",
            max_context_length=32768,
            cost_per_1k_input_tokens=0.008,
            cost_per_1k_output_tokens=0.024,
            supports_streaming=True,
            supports_function_calling=True,
            supports_json_mode=True,
        ),
        ModelConfig(
            name="mistral-medium",
            provider=AIProvider.MISTRAL,
            model_id="mistral-medium",
            display_name="Mistral Medium",
            description="Balanced performance and cost",
            max_context_length=32768,
            cost_per_1k_input_tokens=0.0027,
            cost_per_1k_output_tokens=0.0081,
            supports_streaming=True,
            supports_function_calling=True,
        ),
        # Perplexity Models
        ModelConfig(
            name="perplexity-sonar",
            provider=AIProvider.PERPLEXITY,
            model_id="llama-3.1-sonar-large-128k-online",
            display_name="Perplexity Sonar Large",
            description="Online model with web search capabilities",
            max_context_length=131072,
            cost_per_1k_input_tokens=0.001,
            cost_per_1k_output_tokens=0.001,
            supports_streaming=True,
        ),
        # Local Models (Templates)
        ModelConfig(
            name="ollama-llama2",
            provider=AIProvider.OLLAMA,
            model_id="llama2:7b",
            display_name="Llama 2 7B (Ollama)",
            description="Local Llama 2 model via Ollama",
            api_endpoint="http://localhost:11434/api/generate",
            max_context_length=4096,
            cost_per_1k_input_tokens=0.0,
            cost_per_1k_output_tokens=0.0,
            supports_streaming=True,
        ),
        ModelConfig(
            name="lmstudio-local",
            provider=AIProvider.LMSTUDIO,
            model_id="local-model",
            display_name="Local Model (LM Studio)",
            description="Local model served by LM Studio",
            api_endpoint="http://localhost:1234/v1/chat/completions",
            max_context_length=4096,
            cost_per_1k_input_tokens=0.0,
            cost_per_1k_output_tokens=0.0,
            supports_streaming=True,
        ),
    ]


def get_default_operation_configs() -> Dict[OperationType, OperationConfig]:
    """Get default operation configurations."""
    return {
        OperationType.DEFAULT: OperationConfig(
            operation_type=OperationType.DEFAULT,
            primary_model="gpt-3.5-turbo",
            fallback_models=["gpt-4", "claude-3-haiku"],
        ),
        OperationType.PROMPT_ENHANCEMENT: OperationConfig(
            operation_type=OperationType.PROMPT_ENHANCEMENT,
            primary_model="gpt-4-turbo",
            fallback_models=["claude-3-opus", "gpt-4"],
        ),
        OperationType.PROMPT_OPTIMIZATION: OperationConfig(
            operation_type=OperationType.PROMPT_OPTIMIZATION,
            primary_model="claude-3-opus",
            fallback_models=["gpt-4-turbo", "claude-3-sonnet"],
        ),
        OperationType.PROMPT_TESTING: OperationConfig(
            operation_type=OperationType.PROMPT_TESTING,
            primary_model="gpt-3.5-turbo",
            fallback_models=["claude-3-haiku", "gemini-pro"],
        ),
        OperationType.TRANSLATION: OperationConfig(
            operation_type=OperationType.TRANSLATION,
            primary_model="gpt-4",
            fallback_models=["claude-3-sonnet", "gemini-pro"],
        ),
        OperationType.GENERATION: OperationConfig(
            operation_type=OperationType.GENERATION,
            primary_model="gpt-4-turbo",
            fallback_models=["claude-3-opus", "gpt-4"],
        ),
        OperationType.ANALYSIS: OperationConfig(
            operation_type=OperationType.ANALYSIS,
            primary_model="claude-3-opus",
            fallback_models=["gpt-4-turbo", "claude-3-sonnet"],
        ),
    }


def create_default_configuration() -> AIModelConfiguration:
    """Create a default AI model configuration."""
    config = AIModelConfiguration()

    # Add default models
    for model in get_default_models():
        config.add_model(model)

    # Set default operations
    for op_type, op_config in get_default_operation_configs().items():
        config.operations[op_type] = op_config

    return config
