"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Text Translation Service for AI Prompt Manager
Provides translation capabilities from various languages to English

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

import json
import os
from typing import Dict, Optional, Tuple

import requests

from i18n import i18n


class TextTranslator:
    """
    Text translation service for converting non-English prompts to English
    Supports multiple translation services with fallbacks
    """

    def __init__(self):
        self.translation_services = {
            "openai": self._translate_with_openai,
            "google": self._translate_with_google,
            "libre": self._translate_with_libre,
            "mock": self._translate_with_mock,  # For testing/fallback
        }
        self.preferred_service = os.getenv("TRANSLATION_SERVICE", "mock")

    def translate_to_english(
        self, text: str, source_language: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Translate text to English

        Args:
            text: Text to translate
            source_language: Source language code (auto-detected if None)

        Returns:
            Tuple of (success, translated_text, error_message)
        """
        if not text or not text.strip():
            return False, "", "No text provided for translation"

        # If already in English UI, no translation needed
        if i18n.current_language == "en":
            return True, text, ""

        # Detect source language if not provided
        if not source_language:
            source_language = i18n.current_language

        # Try preferred service first, then fallbacks
        services_to_try = [self.preferred_service]
        if self.preferred_service != "mock":
            services_to_try.append("mock")

        for service in services_to_try:
            if service in self.translation_services:
                try:
                    success, translated_text, error = self.translation_services[
                        service
                    ](text, source_language)
                    if success:
                        return True, translated_text, ""
                except Exception:
                    # nosec B112: Continuing to try next translation service
                    # is intentional
                    continue

        return False, text, "All translation services failed"

    def _translate_with_openai(
        self, text: str, source_language: str
    ) -> Tuple[bool, str, str]:
        """Translate using OpenAI API"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return False, text, "OpenAI API key not configured"

        # Map language codes to full names
        language_names = {
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "zh": "Chinese",
            "ja": "Japanese",
            "pt": "Portuguese",
            "ru": "Russian",
            "ar": "Arabic",
            "hi": "Hindi",
        }

        source_lang_name = language_names.get(source_language, source_language)

        prompt = f"""Translate the following {source_lang_name} text to English.
Preserve the meaning and intent as accurately as possible.
Only return the translated text, no explanations.

Text to translate:
{text}"""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1000,
        }

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            result = response.json()
            translated_text = result["choices"][0]["message"]["content"].strip()
            return True, translated_text, ""

        except requests.exceptions.RequestException as e:
            return False, text, f"OpenAI API error: {str(e)}"
        except (KeyError, json.JSONDecodeError) as e:
            return False, text, f"OpenAI response parsing error: {str(e)}"

    def _translate_with_google(
        self, text: str, source_language: str
    ) -> Tuple[bool, str, str]:
        """Translate using Google Translate API"""
        api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")
        if not api_key:
            return False, text, "Google Translate API key not configured"

        url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"

        payload = {
            "q": text,
            "source": source_language,
            "target": "en",
            "format": "text",
        }

        try:
            response = requests.post(url, data=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            translated_text = result["data"]["translations"][0]["translatedText"]
            return True, translated_text, ""

        except requests.exceptions.RequestException as e:
            return False, text, f"Google Translate API error: {str(e)}"
        except (KeyError, json.JSONDecodeError) as e:
            return False, text, f"Google Translate response parsing error: {str(e)}"

    def _translate_with_libre(
        self, text: str, source_language: str
    ) -> Tuple[bool, str, str]:
        """Translate using LibreTranslate API"""
        api_url = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.de/translate")
        api_key = os.getenv("LIBRETRANSLATE_API_KEY")

        payload = {
            "q": text,
            "source": source_language,
            "target": "en",
            "format": "text",
        }

        if api_key:
            payload["api_key"] = api_key

        try:
            response = requests.post(api_url, data=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            translated_text = result["translatedText"]
            return True, translated_text, ""

        except requests.exceptions.RequestException as e:
            return False, text, f"LibreTranslate API error: {str(e)}"
        except (KeyError, json.JSONDecodeError) as e:
            return False, text, f"LibreTranslate response parsing error: {str(e)}"

    def _translate_with_mock(
        self, text: str, source_language: str
    ) -> Tuple[bool, str, str]:
        """Mock translation for testing and fallback"""
        # Simple mock that adds a prefix to indicate it was "translated"
        if source_language == "en":
            return True, text, ""

        # For non-English, add a note that this is a mock translation
        mock_translated = f"[Mock Translation from {source_language.upper()}] {text}"
        return True, mock_translated, ""

    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported source languages for translation"""
        return {
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "zh": "Chinese",
            "ja": "Japanese",
            "pt": "Portuguese",
            "ru": "Russian",
            "ar": "Arabic",
            "hi": "Hindi",
        }

    def is_translation_needed(self) -> bool:
        """Check if translation is needed based on current UI language"""
        return i18n.current_language != "en"

    def get_current_language_name(self) -> str:
        """Get the name of the current UI language"""
        language_names = self.get_supported_languages()
        return language_names.get(i18n.current_language, i18n.current_language.upper())


# Global translator instance
text_translator = TextTranslator()
