"""
Password handling utilities for secure password operations.

This module provides modern password hashing and validation using
industry-standard techniques to replace the legacy PBKDF2 implementation.
"""

import secrets
from typing import Optional, Tuple

try:
    import bcrypt

    BCRYPT_AVAILABLE = True
except ImportError:
    bcrypt = None
    BCRYPT_AVAILABLE = False

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError

    ARGON2_AVAILABLE = True
except ImportError:
    PasswordHasher = None
    VerifyMismatchError = None
    ARGON2_AVAILABLE = False

# Fallback to PBKDF2 if modern libraries not available
import hashlib

from ...core.exceptions.base import AuthenticationException
from ...utils.logging_config import get_logger


class PasswordHandler:
    """
    Modern password handling with support for multiple hashing algorithms.

    Provides secure password hashing and verification with automatic
    algorithm selection based on available libraries.
    """

    def __init__(self, algorithm: Optional[str] = None):
        """
        Initialize password handler.

        Args:
            algorithm: Preferred algorithm ('argon2', 'bcrypt', 'pbkdf2')
                      If None, selects best available algorithm
        """
        self.logger = get_logger(self.__class__.__name__)
        self.algorithm = self._select_algorithm(algorithm)

        # Initialize algorithm-specific handlers
        if self.algorithm == "argon2" and ARGON2_AVAILABLE:
            try:
                from argon2 import PasswordHasher

                self.argon2_hasher = PasswordHasher()
            except ImportError:
                # Fallback if argon2 is not actually available
                self.algorithm = "bcrypt" if BCRYPT_AVAILABLE else "pbkdf2"

        self.logger.info(
            f"Password handler initialized with {self.algorithm} algorithm"
        )

    def _select_algorithm(self, preferred: Optional[str] = None) -> str:
        """
        Select the best available password hashing algorithm.

        Args:
            preferred: Preferred algorithm name

        Returns:
            Selected algorithm name
        """
        if preferred:
            if preferred == "argon2" and ARGON2_AVAILABLE:
                return "argon2"
            elif preferred == "bcrypt" and BCRYPT_AVAILABLE:
                return "bcrypt"
            elif preferred == "pbkdf2":
                return "pbkdf2"
            else:
                self.logger.warning(
                    f"Preferred algorithm '{preferred}' not available, falling back"
                )

        # Select best available algorithm
        if ARGON2_AVAILABLE:
            return "argon2"
        elif BCRYPT_AVAILABLE:
            return "bcrypt"
        else:
            self.logger.warning(
                "Modern password hashing libraries not available, using PBKDF2"
            )
            return "pbkdf2"

    def hash_password(self, password: str) -> Tuple[str, str]:
        """
        Hash a password using the configured algorithm.

        Args:
            password: Plain text password to hash

        Returns:
            Tuple of (hashed_password, salt_or_metadata)

        Raises:
            AuthenticationException: If hashing fails
        """
        if not password:
            raise AuthenticationException("Password cannot be empty")

        try:
            if self.algorithm == "argon2":
                return self._hash_argon2(password)
            elif self.algorithm == "bcrypt":
                return self._hash_bcrypt(password)
            else:
                return self._hash_pbkdf2(password)

        except Exception as e:
            self.logger.error(f"Password hashing failed: {str(e)}")
            raise AuthenticationException(f"Password hashing failed: {str(e)}")

    def verify_password(
        self, password: str, hashed_password: str, salt_or_metadata: str
    ) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password to verify
            hashed_password: Stored password hash
            salt_or_metadata: Salt or algorithm metadata

        Returns:
            True if password matches

        Raises:
            AuthenticationException: If verification fails
        """
        if not password or not hashed_password:
            return False

        try:
            # Detect algorithm from hash format
            algorithm = self._detect_algorithm(hashed_password, salt_or_metadata)

            if algorithm == "argon2":
                return self._verify_argon2(password, hashed_password)
            elif algorithm == "bcrypt":
                return self._verify_bcrypt(password, hashed_password)
            else:
                return self._verify_pbkdf2(password, hashed_password, salt_or_metadata)

        except Exception as e:
            self.logger.error(f"Password verification failed: {str(e)}")
            return False

    def _detect_algorithm(self, hashed_password: str, salt_or_metadata: str) -> str:
        """
        Detect the algorithm used for a hash.

        Args:
            hashed_password: Password hash
            salt_or_metadata: Salt or metadata

        Returns:
            Detected algorithm name
        """
        if hashed_password.startswith("$argon2"):
            return "argon2"
        elif hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
            return "bcrypt"
        else:
            return "pbkdf2"

    def _hash_argon2(self, password: str) -> Tuple[str, str]:
        """Hash password using Argon2."""
        hashed = self.argon2_hasher.hash(password)
        return hashed, "argon2"

    def _verify_argon2(self, password: str, hashed_password: str) -> bool:
        """Verify password using Argon2."""
        if not ARGON2_AVAILABLE:
            return False
        try:
            self.argon2_hasher.verify(hashed_password, password)
            return True
        except Exception:  # Catch any exception including VerifyMismatchError
            return False

    def _hash_bcrypt(self, password: str) -> Tuple[str, str]:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8"), "bcrypt"

    def _verify_bcrypt(self, password: str, hashed_password: str) -> bool:
        """Verify password using bcrypt."""
        return bool(
            bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
        )

    def _hash_pbkdf2(self, password: str) -> Tuple[str, str]:
        """Hash password using PBKDF2 (fallback method)."""
        salt = secrets.token_hex(32)
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000,  # iterations
        )
        return hashed.hex(), salt

    def _verify_pbkdf2(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verify password using PBKDF2."""
        new_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return new_hash.hex() == hashed_password

    def needs_rehash(self, hashed_password: str, salt_or_metadata: str) -> bool:
        """
        Check if password hash needs to be updated to a newer algorithm.

        Args:
            hashed_password: Current password hash
            salt_or_metadata: Current salt or metadata

        Returns:
            True if hash should be updated
        """
        current_algorithm = self._detect_algorithm(hashed_password, salt_or_metadata)

        # If using a different algorithm than current preference, rehash
        if current_algorithm != self.algorithm:
            return True

        # For Argon2, check if parameters are outdated
        if current_algorithm == "argon2" and ARGON2_AVAILABLE:
            try:
                return bool(self.argon2_hasher.check_needs_rehash(hashed_password))
            except Exception:
                return False

        return False

    def generate_secure_password(
        self, length: int = 16, include_symbols: bool = True
    ) -> str:
        """
        Generate a cryptographically secure password.

        Args:
            length: Password length
            include_symbols: Whether to include special symbols

        Returns:
            Generated password
        """
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")

        # Character sets
        lowercase = "abcdefghijklmnopqrstuvwxyz"
        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        digits = "0123456789"
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"

        # Build character set
        chars = lowercase + uppercase + digits
        if include_symbols:
            chars += symbols

        # Ensure password contains at least one character from each required set
        password_chars = []

        # Add required characters
        password_chars.append(secrets.choice(lowercase))
        password_chars.append(secrets.choice(uppercase))
        password_chars.append(secrets.choice(digits))

        if include_symbols:
            password_chars.append(secrets.choice(symbols))

        # Fill remaining length with random characters
        for _ in range(length - len(password_chars)):
            password_chars.append(secrets.choice(chars))

        # Shuffle the password
        secrets.SystemRandom().shuffle(password_chars)

        return "".join(password_chars)

    def get_algorithm_info(self) -> dict:
        """
        Get information about the current algorithm configuration.

        Returns:
            Dictionary with algorithm information
        """
        return {
            "current_algorithm": self.algorithm,
            "available_algorithms": {
                "argon2": ARGON2_AVAILABLE,
                "bcrypt": BCRYPT_AVAILABLE,
                "pbkdf2": True,  # Always available
            },
            "recommended": (
                "argon2"
                if ARGON2_AVAILABLE
                else "bcrypt" if BCRYPT_AVAILABLE else "pbkdf2"
            ),
        }
