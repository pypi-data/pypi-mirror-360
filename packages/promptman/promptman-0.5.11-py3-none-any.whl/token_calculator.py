"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Token Calculator for AI Prompt Manager
Estimates token consumption for different AI models and tokenization methods

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

# Try to import tiktoken for OpenAI tokenization
try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("ℹ️  tiktoken not available. Install with: pip install tiktoken")


class TokenizerType(Enum):
    """Supported tokenizer types"""

    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE = "claude"
    GEMINI = "gemini"
    LLAMA = "llama"
    AZURE_OPENAI = "azure-openai"
    AZURE_AI = "azure-ai"
    SIMPLE_WORD = "word-based"
    SIMPLE_CHAR = "char-based"


@dataclass
class TokenEstimate:
    """Token estimation result"""

    prompt_tokens: int
    max_completion_tokens: int
    total_tokens: int
    tokenizer_used: str
    cost_estimate: Optional[float] = None
    currency: str = "USD"
    model_name: str = ""


class TokenCalculator:
    """Token calculator for various AI models"""

    # Model pricing per 1K tokens (input/output) in USD
    MODEL_PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "gemini-pro": {"input": 0.0005, "output": 0.0015},
        "gemini-1.5-pro": {"input": 0.003, "output": 0.015},
        # Azure OpenAI pricing (same as OpenAI)
        "azure-gpt-4": {"input": 0.03, "output": 0.06},
        "azure-gpt-35-turbo": {"input": 0.0015, "output": 0.002},
        # Azure AI Studio models (approximate pricing)
        "azure-ai-phi-3": {"input": 0.001, "output": 0.002},
        "azure-ai-mistral": {"input": 0.002, "output": 0.004},
    }

    def __init__(self):
        self.tiktoken_available = TIKTOKEN_AVAILABLE
        self._encoders = {}

        if self.tiktoken_available:
            # Initialize common encoders
            try:
                self._encoders["gpt-4"] = tiktoken.encoding_for_model("gpt-4")
                self._encoders["gpt-3.5-turbo"] = tiktoken.encoding_for_model(
                    "gpt-3.5-turbo"
                )
                logging.info("✅ tiktoken encoders initialized")
            except Exception as e:
                logging.warning(f"⚠️  Could not initialize tiktoken encoders: {e}")
                self.tiktoken_available = False

    def estimate_tokens(
        self, text: str, model: str = "gpt-4", max_completion_tokens: int = 1000
    ) -> TokenEstimate:
        """
        Estimate token count for given text and model

        Args:
            text: The input text to tokenize
            model: Target model name
            max_completion_tokens: Expected completion length

        Returns:
            TokenEstimate with detailed breakdown
        """

        if not text:
            return TokenEstimate(
                prompt_tokens=0,
                max_completion_tokens=0,
                total_tokens=0,
                tokenizer_used="none",
                model_name=model,
            )

        # Determine tokenizer type
        tokenizer_type = self._get_tokenizer_type(model)

        # Calculate prompt tokens
        prompt_tokens = self._count_tokens(text, tokenizer_type, model)

        # Calculate total tokens
        total_tokens = prompt_tokens + max_completion_tokens

        # Calculate cost estimate
        cost_estimate = self._calculate_cost(
            prompt_tokens, max_completion_tokens, model
        )

        return TokenEstimate(
            prompt_tokens=prompt_tokens,
            max_completion_tokens=max_completion_tokens,
            total_tokens=total_tokens,
            tokenizer_used=tokenizer_type.value,
            cost_estimate=cost_estimate,
            model_name=model,
        )

    def _get_tokenizer_type(self, model: str) -> TokenizerType:
        """Determine appropriate tokenizer for model"""
        model_lower = model.lower()

        if "azure-gpt-4" in model_lower or "azure-openai-gpt-4" in model_lower:
            return TokenizerType.AZURE_OPENAI
        elif "azure-gpt-3.5" in model_lower or "azure-openai-gpt-35" in model_lower:
            return TokenizerType.AZURE_OPENAI
        elif "azure-ai" in model_lower or "azure-studio" in model_lower:
            return TokenizerType.AZURE_AI
        elif "gpt-4" in model_lower:
            return TokenizerType.GPT4
        elif "gpt-3.5" in model_lower or "gpt-35" in model_lower:
            return TokenizerType.GPT35_TURBO
        elif "claude" in model_lower:
            return TokenizerType.CLAUDE
        elif "gemini" in model_lower:
            return TokenizerType.GEMINI
        elif "llama" in model_lower:
            return TokenizerType.LLAMA
        else:
            return TokenizerType.SIMPLE_WORD

    def _count_tokens(
        self, text: str, tokenizer_type: TokenizerType, model: str
    ) -> int:
        """Count tokens using appropriate tokenizer"""

        # Try tiktoken for OpenAI models (including Azure OpenAI)
        if self.tiktoken_available and tokenizer_type in [
            TokenizerType.GPT4,
            TokenizerType.GPT35_TURBO,
            TokenizerType.AZURE_OPENAI,
        ]:

            try:
                if tokenizer_type == TokenizerType.AZURE_OPENAI:
                    # Azure OpenAI uses same tokenization as OpenAI
                    encoder_key = (
                        "gpt-4" if "gpt-4" in model.lower() else "gpt-3.5-turbo"
                    )
                else:
                    encoder_key = (
                        "gpt-4"
                        if tokenizer_type == TokenizerType.GPT4
                        else "gpt-3.5-turbo"
                    )

                if encoder_key in self._encoders:
                    return len(self._encoders[encoder_key].encode(text))
            except Exception as e:
                logging.warning(f"tiktoken encoding failed: {e}")

        # Fallback to estimation methods
        if tokenizer_type == TokenizerType.CLAUDE:
            return self._estimate_claude_tokens(text)
        elif tokenizer_type == TokenizerType.GEMINI:
            return self._estimate_gemini_tokens(text)
        elif tokenizer_type == TokenizerType.LLAMA:
            return self._estimate_llama_tokens(text)
        elif tokenizer_type == TokenizerType.AZURE_AI:
            return self._estimate_azure_ai_tokens(text)
        elif tokenizer_type == TokenizerType.SIMPLE_CHAR:
            return len(text) // 4  # Rough estimate: 4 chars per token
        else:
            return self._estimate_word_based_tokens(text)

    def _estimate_word_based_tokens(self, text: str) -> int:
        """Word-based token estimation (fallback method)"""
        # Split on whitespace and punctuation
        words = re.findall(r"\w+|[^\w\s]", text)

        # Estimate tokens (accounting for subword tokenization)
        token_count = 0
        for word in words:
            if len(word) <= 4:
                token_count += 1
            elif len(word) <= 8:
                token_count += 2
            else:
                token_count += max(1, len(word) // 4)

        return token_count

    def _estimate_claude_tokens(self, text: str) -> int:
        """Estimate tokens for Claude models"""
        # Claude uses a similar tokenization to GPT models
        # Rough estimation: 1 token ≈ 3.5 characters
        return max(1, int(len(text) / 3.5))

    def _estimate_gemini_tokens(self, text: str) -> int:
        """Estimate tokens for Gemini models"""
        # Gemini tokenization estimation
        # Rough estimation: 1 token ≈ 4 characters
        return max(1, int(len(text) / 4))

    def _estimate_llama_tokens(self, text: str) -> int:
        """Estimate tokens for LLaMA models"""
        # LLaMA uses SentencePiece tokenization
        # Rough estimation based on word count with subword adjustment
        words = text.split()

        # LLaMA tends to split words more aggressively
        token_count = 0
        for word in words:
            if len(word) <= 3:
                token_count += 1
            elif len(word) <= 6:
                token_count += 2
            else:
                token_count += max(1, len(word) // 3)

        # Add tokens for punctuation and special characters
        punctuation_count = len(re.findall(r"[^\w\s]", text))

        return token_count + punctuation_count

    def _estimate_azure_ai_tokens(self, text: str) -> int:
        """Estimate tokens for Azure AI models"""
        # Azure AI models may use different tokenization approaches
        # depending on the specific model (Phi, small language models, etc.)
        # Conservative estimation similar to GPT models
        return max(1, int(len(text) / 3.8))

    def _calculate_cost(
        self, prompt_tokens: int, completion_tokens: int, model: str
    ) -> Optional[float]:
        """Calculate estimated cost in USD"""

        # Find matching pricing
        pricing = None
        for model_key, model_pricing in self.MODEL_PRICING.items():
            if model_key in model.lower():
                pricing = model_pricing
                break

        if not pricing:
            return None

        # Calculate cost per 1K tokens
        input_cost = (prompt_tokens / 1000) * pricing["input"]
        output_cost = (completion_tokens / 1000) * pricing["output"]

        return input_cost + output_cost

    def get_supported_models(self) -> List[str]:
        """Get list of supported models"""
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
            "gemini-pro",
            "gemini-1.5-pro",
            "llama-2-70b",
            "llama-2-13b",
            # Azure OpenAI models
            "azure-gpt-4",
            "azure-gpt-35-turbo",
            # Azure AI Studio models
            "azure-ai-phi-3",
            "azure-ai-mistral",
            "custom",
        ]

    def get_tokenizer_info(self) -> Dict[str, Any]:
        """Get information about available tokenizers"""
        return {
            "tiktoken_available": self.tiktoken_available,
            "supported_models": self.get_supported_models(),
            "estimation_methods": [t.value for t in TokenizerType],
            "pricing_available": list(self.MODEL_PRICING.keys()),
        }

    def analyze_prompt_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze prompt complexity and provide insights"""

        if not text:
            return {"complexity": "empty", "suggestions": []}

        character_count = len(text)
        word_count = len(text.split())
        line_count = len(text.splitlines())
        suggestions = []

        # Analyze complexity
        if word_count > 1000:
            complexity = "very_high"
            suggestions.append("Consider breaking into smaller prompts")
        elif word_count > 500:
            complexity = "high"
            suggestions.append("Large prompt may be expensive")
        elif word_count > 200:
            complexity = "medium"
        else:
            complexity = "simple"

        analysis = {
            "character_count": character_count,
            "word_count": word_count,
            "line_count": line_count,
            "complexity": complexity,
            "suggestions": suggestions,
        }

        # Check for repetitive content
        words = text.lower().split()
        if len(words) != len(set(words)) and len(words) > 20:
            repetition_ratio = 1 - (len(set(words)) / len(words))
            if repetition_ratio > 0.3:
                suggestions.append("High repetition detected - consider consolidating")

        # Check for very long lines
        long_lines = [line for line in text.splitlines() if len(line) > 200]
        if long_lines:
            suggestions.append(f"{len(long_lines)} very long line(s) detected")

        # Update analysis with final suggestions
        analysis["suggestions"] = suggestions

        return analysis


# Global token calculator instance
token_calculator = TokenCalculator()
