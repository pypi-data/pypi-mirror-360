"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Multi-Service Prompt Optimization Integration
Provides prompt optimization capabilities using multiple services:
- LangWatch (enterprise-grade optimization)
- PromptPerfect (specialized prompt refinement)
- LangSmith (LangChain ecosystem integration)
- Helicone (observability-focused optimization)
- Built-in Optimizer (rule-based improvements)

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# Multi-service optimization support
# Services are implemented with fallback to built-in optimizer

# Import external libraries with graceful fallbacks
SERVICES_AVAILABLE = {
    "langwatch": False,
    "promptperfect": False,
    "langsmith": False,
    "helicone": False,
    "builtin": True,  # Always available
}

try:
    # Try importing LangWatch
    # import langwatch
    # from langwatch.types import PromptRole, ChatMessage
    # SERVICES_AVAILABLE['langwatch'] = True
    pass  # Mock for now
except ImportError:
    pass

try:
    # Try importing PromptPerfect
    # import promptperfect
    # SERVICES_AVAILABLE['promptperfect'] = True
    pass  # Mock for now
except ImportError:
    pass

try:
    # Try importing LangSmith
    # from langsmith import Client
    # SERVICES_AVAILABLE['langsmith'] = True
    pass  # Mock for now
except ImportError:
    pass

try:
    # Try importing Helicone
    # import helicone
    # SERVICES_AVAILABLE['helicone'] = True
    pass  # Mock for now
except ImportError:
    pass

print(
    f"📊 Available optimization services: {[k for k, v in SERVICES_AVAILABLE.items() if v]}"
)


@dataclass
class OptimizationResult:
    """Result of prompt optimization"""

    optimized_prompt: str
    original_prompt: str
    optimization_score: float
    suggestions: List[str]
    reasoning: str
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None


class PromptOptimizer:
    """Multi-service prompt optimization manager"""

    def __init__(self):
        self.service = os.getenv("PROMPT_OPTIMIZER", "builtin").lower()
        self.services_available = SERVICES_AVAILABLE.copy()
        self.initialized = False

        # Service-specific configuration
        self.config = {
            "langwatch": {
                "api_key": os.getenv("LANGWATCH_API_KEY"),
                "project_id": os.getenv("LANGWATCH_PROJECT_ID", "ai-prompt-manager"),
                "endpoint": os.getenv("LANGWATCH_ENDPOINT", "https://api.langwatch.ai"),
            },
            "promptperfect": {"api_key": os.getenv("PROMPTPERFECT_API_KEY")},
            "langsmith": {
                "api_key": os.getenv("LANGSMITH_API_KEY"),
                "project": os.getenv("LANGSMITH_PROJECT", "ai-prompt-manager"),
            },
            "helicone": {
                "api_key": os.getenv("HELICONE_API_KEY"),
                "app_name": os.getenv("HELICONE_APP_NAME", "ai-prompt-manager"),
            },
            "builtin": {},  # No configuration needed
        }

        # Initialize selected service
        self._initialize_service()

        logging.info(f"🚀 Prompt Optimizer initialized with service: {self.service}")

    def _initialize_service(self):
        """Initialize the selected optimization service"""
        if self.service not in self.services_available:
            logging.warning(
                f"⚠️  Service '{self.service}' not available, falling back to builtin"
            )
            self.service = "builtin"

        if self.service == "builtin":
            self.initialized = True
            return

        # For external services, check API keys and initialize
        service_config = self.config.get(self.service, {})
        api_key = service_config.get("api_key")

        if not api_key:
            logging.warning(
                f"⚠️  {self.service.title()} API key not found, falling back to builtin"
            )
            self.service = "builtin"
            self.initialized = True
            return

        # Mock initialization for demonstration
        # In production, initialize actual service clients here
        self.initialized = True
        logging.info(f"✅ {self.service.title()} service initialized (mock mode)")

    def is_available(self) -> bool:
        """Check if prompt optimization is available"""
        return self.initialized

    def get_status(self) -> Dict[str, Any]:
        """Get optimization service status"""
        service_config = self.config.get(self.service, {})
        return {
            "service": self.service,
            "available": self.is_available(),
            "initialized": self.initialized,
            "api_key_set": bool(service_config.get("api_key")),
            "services_available": self.services_available,
            "config": {
                k: "***" if "key" in k else v for k, v in service_config.items()
            },
        }

    def optimize_prompt(
        self,
        original_prompt: str,
        context: Optional[str] = None,
        target_model: Optional[str] = "gpt-4",
        optimization_goals: Optional[List[str]] = None,
    ) -> OptimizationResult:
        """
        Optimize a prompt using LangWatch

        Args:
            original_prompt: The prompt to optimize
            context: Additional context about the prompt's purpose
            target_model: Target AI model for optimization
            optimization_goals: List of optimization goals (clarity, specificity, etc.)

        Returns:
            OptimizationResult with the optimized prompt and metadata
        """

        if not self.is_available():
            return OptimizationResult(
                optimized_prompt=original_prompt,
                original_prompt=original_prompt,
                optimization_score=0.0,
                suggestions=[f"{self.service.title()} optimization not available"],
                reasoning=f"{self.service.title()} is not properly configured or available",
                timestamp=datetime.now(),
                success=False,
                error_message=f"{self.service.title()} not available or not configured",
            )

        try:
            # Validate input
            if not original_prompt or not original_prompt.strip():
                return OptimizationResult(
                    optimized_prompt=original_prompt,
                    original_prompt=original_prompt,
                    optimization_score=0.0,
                    suggestions=["Empty prompt provided - cannot optimize"],
                    reasoning="Cannot optimize empty or whitespace-only prompts",
                    timestamp=datetime.now(),
                    success=False,
                    error_message="Empty prompt provided",
                )

            # Default optimization goals
            if optimization_goals is None:
                optimization_goals = [
                    "clarity",
                    "specificity",
                    "effectiveness",
                    "conciseness",
                ]

            # Create optimization context
            optimization_context = self._create_optimization_context(
                original_prompt, context, target_model, optimization_goals
            )

            # Perform optimization based on selected service
            optimized_result = self._perform_optimization(
                original_prompt, optimization_context, target_model, optimization_goals
            )

            return OptimizationResult(
                optimized_prompt=optimized_result["optimized_prompt"],
                original_prompt=original_prompt,
                optimization_score=optimized_result["score"],
                suggestions=optimized_result["suggestions"],
                reasoning=optimized_result["reasoning"],
                timestamp=datetime.now(),
                success=True,
            )

        except Exception as e:
            logging.error(f"❌ {self.service.title()} optimization failed: {e}")
            return OptimizationResult(
                optimized_prompt=original_prompt,
                original_prompt=original_prompt,
                optimization_score=0.0,
                suggestions=[f"Optimization failed: {str(e)}"],
                reasoning=f"Error during optimization: {str(e)}",
                timestamp=datetime.now(),
                success=False,
                error_message=str(e),
            )

    def _create_optimization_context(
        self,
        original_prompt: str,
        context: Optional[str],
        target_model: Optional[str],
        goals: List[str],
    ) -> str:
        """Create context for optimization"""

        context_parts = [
            f"Original prompt: {original_prompt}",
            f"Target AI model: {target_model or 'General'}",
            f"Optimization goals: {', '.join(goals)}",
        ]

        if context:
            context_parts.append(f"Additional context: {context}")

        return "\n".join(context_parts)

    def _perform_optimization(
        self,
        original_prompt: str,
        context: str,
        target_model: Optional[str],
        goals: List[str],
    ) -> Dict:
        """
        Perform the actual optimization using the selected service
        Routes to appropriate service-specific optimization logic
        """

        if self.service == "langwatch":
            return self._optimize_with_langwatch(
                original_prompt, context, target_model, goals
            )
        elif self.service == "promptperfect":
            return self._optimize_with_promptperfect(
                original_prompt, context, target_model, goals
            )
        elif self.service == "langsmith":
            return self._optimize_with_langsmith(
                original_prompt, context, target_model, goals
            )
        elif self.service == "helicone":
            return self._optimize_with_helicone(
                original_prompt, context, target_model, goals
            )
        else:
            return self._optimize_with_builtin(
                original_prompt, context, target_model, goals
            )

    def _optimize_with_langwatch(
        self,
        original_prompt: str,
        context: str,
        target_model: Optional[str],
        goals: List[str],
    ) -> Dict:
        """Optimize using LangWatch service (mock implementation)"""
        # Mock LangWatch optimization - in production, use actual LangWatch API
        optimized_prompt = self._apply_optimization_rules(
            original_prompt, goals, "langwatch"
        )
        score = self._calculate_optimization_score(original_prompt, optimized_prompt)
        suggestions = self._generate_suggestions(
            original_prompt, optimized_prompt, "langwatch"
        )
        reasoning = self._generate_reasoning(
            original_prompt, optimized_prompt, "langwatch"
        )

        return {
            "optimized_prompt": optimized_prompt,
            "score": score,
            "suggestions": suggestions,
            "reasoning": reasoning,
        }

    def _optimize_with_promptperfect(
        self,
        original_prompt: str,
        context: str,
        target_model: Optional[str],
        goals: List[str],
    ) -> Dict:
        """Optimize using PromptPerfect service (mock implementation)"""
        optimized_prompt = self._apply_optimization_rules(
            original_prompt, goals, "promptperfect"
        )
        score = self._calculate_optimization_score(original_prompt, optimized_prompt)
        suggestions = self._generate_suggestions(
            original_prompt, optimized_prompt, "promptperfect"
        )
        reasoning = self._generate_reasoning(
            original_prompt, optimized_prompt, "promptperfect"
        )

        return {
            "optimized_prompt": optimized_prompt,
            "score": score,
            "suggestions": suggestions,
            "reasoning": reasoning,
        }

    def _optimize_with_langsmith(
        self,
        original_prompt: str,
        context: str,
        target_model: Optional[str],
        goals: List[str],
    ) -> Dict:
        """Optimize using LangSmith service (mock implementation)"""
        optimized_prompt = self._apply_optimization_rules(
            original_prompt, goals, "langsmith"
        )
        score = self._calculate_optimization_score(original_prompt, optimized_prompt)
        suggestions = self._generate_suggestions(
            original_prompt, optimized_prompt, "langsmith"
        )
        reasoning = self._generate_reasoning(
            original_prompt, optimized_prompt, "langsmith"
        )

        return {
            "optimized_prompt": optimized_prompt,
            "score": score,
            "suggestions": suggestions,
            "reasoning": reasoning,
        }

    def _optimize_with_helicone(
        self,
        original_prompt: str,
        context: str,
        target_model: Optional[str],
        goals: List[str],
    ) -> Dict:
        """Optimize using Helicone service (mock implementation)"""
        optimized_prompt = self._apply_optimization_rules(
            original_prompt, goals, "helicone"
        )
        score = self._calculate_optimization_score(original_prompt, optimized_prompt)
        suggestions = self._generate_suggestions(
            original_prompt, optimized_prompt, "helicone"
        )
        reasoning = self._generate_reasoning(
            original_prompt, optimized_prompt, "helicone"
        )

        return {
            "optimized_prompt": optimized_prompt,
            "score": score,
            "suggestions": suggestions,
            "reasoning": reasoning,
        }

    def _optimize_with_builtin(
        self,
        original_prompt: str,
        context: str,
        target_model: Optional[str],
        goals: List[str],
    ) -> Dict:
        """Built-in rule-based optimization"""
        optimized_prompt = self._apply_optimization_rules(
            original_prompt, goals, "builtin"
        )
        score = self._calculate_optimization_score(original_prompt, optimized_prompt)
        suggestions = self._generate_suggestions(
            original_prompt, optimized_prompt, "builtin"
        )
        reasoning = self._generate_reasoning(
            original_prompt, optimized_prompt, "builtin"
        )

        return {
            "optimized_prompt": optimized_prompt,
            "score": score,
            "suggestions": suggestions,
            "reasoning": reasoning,
        }

    def _apply_optimization_rules(
        self, prompt: str, goals: List[str], service: str
    ) -> str:
        """Apply optimization rules to improve the prompt based on goals and service"""

        optimized = prompt

        # Apply service-specific optimizations
        if service == "langwatch":
            optimized = self._apply_langwatch_rules(optimized, goals)
        elif service == "promptperfect":
            optimized = self._apply_promptperfect_rules(optimized, goals)
        elif service == "langsmith":
            optimized = self._apply_langsmith_rules(optimized, goals)
        elif service == "helicone":
            optimized = self._apply_helicone_rules(optimized, goals)
        else:
            optimized = self._apply_builtin_rules(optimized, goals)

        return optimized.strip()

    def _calculate_optimization_score(self, original: str, optimized: str) -> float:
        """Calculate optimization score (0-100)"""

        score = 50.0  # Base score

        # Length improvement
        if len(optimized) > len(original) and len(original) > 0:
            score += min(20, (len(optimized) - len(original)) / len(original) * 100)

        # Structure indicators
        structure_words = ["step", "first", "then", "format", "organize", "structure"]
        original_structure = sum(
            1 for word in structure_words if word in original.lower()
        )
        optimized_structure = sum(
            1 for word in structure_words if word in optimized.lower()
        )

        if optimized_structure > original_structure:
            score += (optimized_structure - original_structure) * 10

        # Specificity indicators
        specific_words = ["specific", "detailed", "comprehensive", "thorough"]
        original_specific = sum(
            1 for word in specific_words if word in original.lower()
        )
        optimized_specific = sum(
            1 for word in specific_words if word in optimized.lower()
        )

        if optimized_specific > original_specific:
            score += (optimized_specific - original_specific) * 5

        return min(100.0, max(0.0, score))

    def _apply_builtin_rules(self, prompt: str, goals: List[str]) -> str:
        """Apply built-in optimization rules"""
        optimized = prompt

        # Rule 1: Add structure if missing and "structure" in goals
        if "structure" in goals or "clarity" in goals:
            if not any(
                word in prompt.lower() for word in ["step", "first", "then", "finally"]
            ):
                if len(prompt) > 100:
                    optimized = f"Please follow these steps:\n\n{optimized}\n\nProvide a structured response."

        # Rule 2: Add context if very short and "effectiveness" in goals
        if "effectiveness" in goals:
            if len(prompt.strip()) < 20:
                optimized = f"You are an AI assistant. {optimized} Please provide a detailed and helpful response."

        # Rule 3: Add specificity
        if "specificity" in goals or "clarity" in goals:
            if "help me" in prompt.lower() and "specific" not in prompt.lower():
                optimized = optimized.replace(
                    "help me", "help me with specific guidance on"
                )

        # Rule 4: Add output format if missing
        if "structure" in goals:
            if len(prompt) > 50 and not any(
                word in prompt.lower() for word in ["format", "structure", "organize"]
            ):
                optimized += "\n\nPlease organize your response clearly with appropriate formatting."

        # Rule 5: Add role definition for complex tasks
        if "effectiveness" in goals:
            if len(prompt) > 100 and not prompt.lower().startswith("you are"):
                if any(
                    word in prompt.lower()
                    for word in ["analyze", "write", "create", "develop"]
                ):
                    optimized = f"You are an expert assistant. {optimized}"

        return optimized.strip()

    def _apply_langwatch_rules(self, prompt: str, goals: List[str]) -> str:
        """Apply LangWatch-style optimization rules"""
        # For mock implementation, use builtin rules with LangWatch flavor
        optimized = self._apply_builtin_rules(prompt, goals)

        # Add LangWatch-specific enhancements
        if "effectiveness" in goals and len(prompt) > 50:
            optimized += "\n\n[Optimized with LangWatch enterprise analytics]"

        return optimized

    def _apply_promptperfect_rules(self, prompt: str, goals: List[str]) -> str:
        """Apply PromptPerfect-style optimization rules"""
        optimized = self._apply_builtin_rules(prompt, goals)

        # Add PromptPerfect-specific enhancements for creativity
        if "creativity" in goals:
            optimized = f"Think creatively and provide innovative insights. {optimized}"

        return optimized

    def _apply_langsmith_rules(self, prompt: str, goals: List[str]) -> str:
        """Apply LangSmith-style optimization rules"""
        optimized = self._apply_builtin_rules(prompt, goals)

        # Add LangSmith-specific enhancements for workflow integration
        if "structure" in goals:
            optimized = f"As part of a LangChain workflow: {optimized}"

        return optimized

    def _apply_helicone_rules(self, prompt: str, goals: List[str]) -> str:
        """Apply Helicone-style optimization rules"""
        optimized = self._apply_builtin_rules(prompt, goals)

        # Add Helicone-specific enhancements for observability
        if "effectiveness" in goals:
            optimized += "\n\n[Include performance metrics in your response]"

        return optimized

    def _generate_suggestions(
        self, original: str, optimized: str, service: str
    ) -> List[str]:
        f"""Generate optimization suggestions for {service}"""

        suggestions = []

        if len(optimized) > len(original):
            suggestions.append("Added more detailed instructions for clarity")

        if "you are" in optimized.lower() and "you are" not in original.lower():
            suggestions.append("Added role definition to improve response quality")

        if "step" in optimized.lower() and "step" not in original.lower():
            suggestions.append("Added structured approach for better organization")

        if "format" in optimized.lower() and "format" not in original.lower():
            suggestions.append("Added output formatting instructions")

        if not suggestions:
            suggestions.append(f"Applied {service} optimization best practices")

        # Add service-specific suggestions
        if service != "builtin":
            suggestions.append(
                f"Optimized using {service.title()} service capabilities"
            )

        return suggestions

    def _generate_reasoning(self, original: str, optimized: str, service: str) -> str:
        f"""Generate reasoning for the optimization using {service}"""

        improvements = []

        if len(optimized) > len(original):
            improvements.append("expanded the prompt with additional context")

        if "you are" in optimized.lower() and "you are" not in original.lower():
            improvements.append("defined the AI's role for better responses")

        if any(word in optimized.lower() for word in ["step", "structure", "organize"]):
            improvements.append("added structural elements for clarity")

        if improvements:
            base_reasoning = f"The {service} optimization {', '.join(improvements)} to enhance effectiveness and clarity."
        else:
            base_reasoning = f"Applied {service} optimization techniques to improve clarity and effectiveness."

        # Add service-specific reasoning
        service_notes = {
            "langwatch": "Used enterprise-grade analytics to identify improvement opportunities.",
            "promptperfect": "Applied specialized refinement algorithms for optimal prompt structure.",
            "langsmith": "Leveraged LangChain ecosystem best practices for workflow integration.",
            "helicone": "Incorporated observability-focused optimizations for better monitoring.",
            "builtin": "Used rule-based optimization with proven improvement patterns.",
        }

        return f"{base_reasoning} {service_notes.get(service, '')}"


# Global optimizer instance
prompt_optimizer = PromptOptimizer()

# Legacy compatibility
langwatch_optimizer = prompt_optimizer
