import random
import string
import secrets
import uuid
import os
from typing import List, Optional, Any


class RandomUtils:
    """
    A collection of utility functions for generating random strings, integers,
    tokens, UUIDs, and other randomized data commonly needed in tool development
    and testing scenarios.
    """

    @staticmethod
    def uuid4() -> str:
        """Generate a random UUID version 4."""
        return str(uuid.uuid4())

    @staticmethod
    def random_int(min_val: int = 0, max_val: int = 100) -> int:
        """Return a random integer between min_val and max_val (inclusive)."""
        return random.randint(min_val, max_val)

    @staticmethod
    def random_float(min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Return a random float between min_val and max_val."""
        return random.uniform(min_val, max_val)

    @staticmethod
    def random_choice(choices: List[Any]) -> Any:
        """Return a random element from the given list."""
        if not choices:
            raise ValueError("Choices list cannot be empty")
        return random.choice(choices)

    @staticmethod
    def random_string(length: int = 12, charset: Optional[str] = None) -> str:
        """
        Generate a random string of the given length.
        Default charset includes ASCII letters and digits.
        """
        charset = charset or (string.ascii_letters + string.digits)
        return ''.join(secrets.choice(charset) for _ in range(length))

    @staticmethod
    def random_lowercase(length: int = 8) -> str:
        """Generate a random lowercase string of the given length."""
        return ''.join(secrets.choice(string.ascii_lowercase) for _ in range(length))

    @staticmethod
    def random_uppercase(length: int = 8) -> str:
        """Generate a random uppercase string of the given length."""
        return ''.join(secrets.choice(string.ascii_uppercase) for _ in range(length))

    @staticmethod
    def random_hex(length: int = 16) -> str:
        """
        Generate a random hexadecimal string.
        Length must be even (each byte = 2 hex characters).
        """
        return secrets.token_hex(length // 2)

    @staticmethod
    def random_bytes(length: int = 16) -> bytes:
        """Return secure random bytes of the specified length."""
        return os.urandom(length)

    @staticmethod
    def secure_token(length: int = 32) -> str:
        """Generate a URL-safe secure random token."""
        return secrets.token_urlsafe(length)

    @staticmethod
    def random_bool() -> bool:
        """Return True or False at random."""
        return random.choice([True, False])

    @staticmethod
    def random_password(length: int = 12, use_symbols: bool = True) -> str:
        """
        Generate a secure random password.
        Includes letters, digits, and optionally symbols.
        """
        charset = string.ascii_letters + string.digits
        if use_symbols:
            charset += string.punctuation
        return ''.join(secrets.choice(charset) for _ in range(length))
