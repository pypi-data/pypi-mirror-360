"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

Dynamic Internationalization (i18n) system for AI Prompt Manager
File-based language loading with caching and management tools

This software is licensed for non-commercial use only. See LICENSE file for details.
"""

import glob
import json
import logging
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Set

logger = logging.getLogger(__name__)


class LanguageManager:
    """
    File-based internationalization manager with dynamic loading and caching

    Features:
    - Dynamic language file loading
    - LRU caching for performance
    - Lazy loading (load only when first selected)
    - Language file validation
    - Translation generation tools
    - Thread-safe operations
    """

    def __init__(self, languages_dir: str = "languages", default_language: str = "en"):
        self.languages_dir = Path(languages_dir)
        self.default_language = default_language
        self.current_language = default_language
        self._loaded_languages: Dict[str, Dict[str, Any]] = {}
        self._available_languages: Dict[str, Dict[str, str]] = {}
        self._language_cache_lock = threading.RLock()

        # Ensure languages directory exists
        self.languages_dir.mkdir(exist_ok=True)

        # Load available languages list (metadata only)
        self._discover_available_languages()

        # Load default language immediately
        self._load_language(self.default_language)

    def _discover_available_languages(self) -> None:
        """Discover available language files and load their metadata"""
        self._available_languages.clear()

        # Find all JSON files in languages directory
        language_files = glob.glob(str(self.languages_dir / "*.json"))

        for file_path in language_files:
            try:
                lang_code = Path(file_path).stem

                # Load only metadata for discovery
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    metadata = data.get("_metadata", {})

                    self._available_languages[lang_code] = {
                        "code": lang_code,
                        "name": metadata.get("language_name", lang_code.upper()),
                        "native_name": metadata.get("native_name", lang_code.upper()),
                        "version": metadata.get("version", "1.0.0"),
                        "author": metadata.get("author", "Unknown"),
                        "last_updated": metadata.get("last_updated", "Unknown"),
                        "file_path": file_path,
                    }

            except Exception as e:
                logger.warning(f"Failed to load metadata for {file_path}: {e}")

        # Ensure default language is available
        if self.default_language not in self._available_languages:
            logger.warning(f"Default language '{self.default_language}' not found")

    def _load_language(self, language_code: str) -> bool:
        """Load a specific language file into memory with caching"""
        if language_code in self._loaded_languages:
            return True

        if language_code not in self._available_languages:
            logger.error(f"Language '{language_code}' not available")
            return False

        try:
            file_path = self._available_languages[language_code]["file_path"]

            with self._language_cache_lock:
                # Double-check after acquiring lock
                if language_code in self._loaded_languages:
                    return True

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Remove metadata from translations
                translations = {k: v for k, v in data.items() if k != "_metadata"}

                self._loaded_languages[language_code] = translations
                logger.info(f"Loaded language: {language_code}")
                return True

        except Exception as e:
            logger.error(f"Failed to load language '{language_code}': {e}")
            return False

    def get_available_languages(self) -> Dict[str, Dict[str, str]]:
        """Get list of available languages with metadata"""
        return self._available_languages.copy()

    def set_language(self, language_code: str) -> bool:
        """Set current language, loading it if necessary"""
        if language_code == self.current_language:
            return True

        # Load language if not already loaded
        if not self._load_language(language_code):
            return False

        self.current_language = language_code
        logger.info(f"Switched to language: {language_code}")
        return True

    def get_current_language(self) -> str:
        """Get current language code"""
        return self.current_language

    def _get_nested_value(self, data: Dict[str, Any], key_path: str) -> Optional[str]:
        """Get nested dictionary value using dot notation"""
        try:
            keys = key_path.split(".")
            value = data

            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None

            return str(value) if value is not None else None

        except Exception:
            return None

    def t(self, key: str, **kwargs) -> str:
        """
        Translate a key to current language with optional formatting

        Args:
            key: Translation key using dot notation (e.g., 'auth.login')
            **kwargs: Optional formatting parameters

        Returns:
            Translated string or key if not found
        """
        # Ensure current language is loaded
        if self.current_language not in self._loaded_languages:
            if not self._load_language(self.current_language):
                self.current_language = self.default_language
                self._load_language(self.default_language)

        # Get current language translations
        current_translations = self._loaded_languages.get(self.current_language, {})

        # Try current language first
        text = self._get_nested_value(current_translations, key)

        # Fallback to default language if not found
        if text is None and self.current_language != self.default_language:
            default_translations = self._loaded_languages.get(self.default_language, {})
            text = self._get_nested_value(default_translations, key)

        # Return key if no translation found
        if text is None:
            text = key

        # Apply formatting if provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError) as e:
                logger.warning(f"Translation formatting failed for key '{key}': {e}")
                pass  # Return unformatted text

        return text

    def get_all_translation_keys(self, language_code: Optional[str] = None) -> Set[str]:
        """Get all translation keys for a language (flattened dot notation)"""
        if language_code is None:
            language_code = self.default_language

        if not self._load_language(language_code):
            return set()

        translations = self._loaded_languages.get(language_code, {})
        return self._flatten_keys(translations)

    def _flatten_keys(self, data: Dict[str, Any], prefix: str = "") -> Set[str]:
        """Recursively flatten nested dictionary keys using dot notation"""
        keys = set()

        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                keys.update(self._flatten_keys(value, full_key))
            else:
                keys.add(full_key)

        return keys

    def validate_language_file(self, language_code: str) -> Dict[str, Any]:
        """
        Validate a language file against the default language

        Returns:
            Dictionary with validation results:
            - 'valid': boolean
            - 'missing_keys': list of missing keys
            - 'extra_keys': list of extra keys
            - 'total_keys': total number of keys
            - 'coverage': percentage coverage
        """
        default_keys = self.get_all_translation_keys(self.default_language)
        target_keys = self.get_all_translation_keys(language_code)

        missing_keys = list(default_keys - target_keys)
        extra_keys = list(target_keys - default_keys)

        total_keys = len(default_keys)
        covered_keys = len(target_keys & default_keys)
        coverage = (covered_keys / total_keys * 100) if total_keys > 0 else 0

        return {
            "valid": len(missing_keys) == 0,
            "missing_keys": missing_keys,
            "extra_keys": extra_keys,
            "total_keys": total_keys,
            "covered_keys": covered_keys,
            "coverage": coverage,
        }

    def save_language_file(
        self,
        language_code: str,
        translations: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Save a language file with validation"""
        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}

            default_metadata = {
                "language_code": language_code,
                "language_name": language_code.upper(),
                "native_name": language_code.upper(),
                "version": "1.0.0",
                "author": "AI Prompt Manager",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
            }

            # Merge with provided metadata
            final_metadata = {**default_metadata, **metadata}

            # Prepare final data structure
            language_data = {"_metadata": final_metadata, **translations}

            # Save to file
            file_path = self.languages_dir / f"{language_code}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    language_data, f, indent=2, ensure_ascii=False, sort_keys=True
                )

            # Clear cache and reload
            with self._language_cache_lock:
                if language_code in self._loaded_languages:
                    del self._loaded_languages[language_code]

            # Update available languages
            self._discover_available_languages()

            logger.info(f"Saved language file: {language_code}")
            return True

        except Exception as e:
            logger.error(f"Failed to save language file '{language_code}': {e}")
            return False

    def create_language_template(
        self,
        language_code: str,
        language_name: str,
        native_name: str,
        author: str = "AI Prompt Manager",
    ) -> Dict[str, Any]:
        """Create a new language template based on the default language"""
        if not self._load_language(self.default_language):
            raise ValueError(f"Cannot load default language: {self.default_language}")

        # Get default translations structure
        default_translations = self._loaded_languages[self.default_language]

        # Create empty template with same structure
        template = self._create_empty_structure(default_translations)

        # Add metadata
        metadata = {
            "language_code": language_code,
            "language_name": language_name,
            "native_name": native_name,
            "version": "1.0.0",
            "author": author,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
        }

        return {"translations": template, "metadata": metadata}

    def _create_empty_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create empty structure maintaining the same hierarchy"""
        result: Dict[str, Any] = {}

        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._create_empty_structure(value)
            else:
                result[key] = ""  # Empty string for translation

        return result

    def delete_language_file(self, language_code: str) -> bool:
        """Delete a language file (cannot delete default language)"""
        if language_code == self.default_language:
            logger.error(f"Cannot delete default language: {language_code}")
            return False

        try:
            if language_code in self._available_languages:
                file_path = self._available_languages[language_code]["file_path"]
                os.remove(file_path)

                # Clean up memory
                with self._language_cache_lock:
                    if language_code in self._loaded_languages:
                        del self._loaded_languages[language_code]

                # Update available languages
                self._discover_available_languages()

                # Switch to default if current language was deleted
                if self.current_language == language_code:
                    self.set_language(self.default_language)

                logger.info(f"Deleted language file: {language_code}")
                return True

        except Exception as e:
            logger.error(f"Failed to delete language file '{language_code}': {e}")

        return False

    def reload_languages(self) -> None:
        """Reload all language files and clear cache"""
        with self._language_cache_lock:
            self._loaded_languages.clear()

        self._discover_available_languages()

        # Reload current language
        self._load_language(self.current_language)

        logger.info("Reloaded all language files")

    def get_language_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded languages"""
        stats = {
            "total_available": len(self._available_languages),
            "total_loaded": len(self._loaded_languages),
            "current_language": self.current_language,
            "default_language": self.default_language,
        }

        # Add per-language stats
        language_stats = {}
        for lang_code in self._available_languages:
            validation = self.validate_language_file(lang_code)
            language_stats[lang_code] = {
                "loaded": lang_code in self._loaded_languages,
                "coverage": validation["coverage"],
                "total_keys": validation["total_keys"],
                "missing_keys": len(validation["missing_keys"]),
            }

        stats["languages"] = language_stats
        return stats


# Global instance
_language_manager = None
_manager_lock = threading.RLock()


def get_language_manager() -> LanguageManager:
    """Get global language manager instance (singleton)"""
    global _language_manager

    if _language_manager is None:
        with _manager_lock:
            if _language_manager is None:
                # Check for user preference or environment variable
                default_lang = os.getenv("DEFAULT_LANGUAGE", "en").lower()
                _language_manager = LanguageManager(default_language=default_lang)

    return _language_manager


def t(key: str, **kwargs) -> str:
    """Convenience function for translation"""
    return get_language_manager().t(key, **kwargs)


def set_language(language_code: str) -> bool:
    """Convenience function to set language"""
    return get_language_manager().set_language(language_code)


def get_available_languages() -> Dict[str, Dict[str, str]]:
    """Convenience function to get available languages"""
    return get_language_manager().get_available_languages()
