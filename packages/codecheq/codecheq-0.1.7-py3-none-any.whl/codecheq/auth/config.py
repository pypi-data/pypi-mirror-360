"""
Authentication Configuration

Authentication-specific configuration settings for CodeCheq.
"""

import os
from typing import Optional


class AuthConfig:
    """Authentication configuration settings."""

    def __init__(
        self,
        api_token: Optional[str] = None,
        token_portal_url: Optional[str] = None,
        cache_duration: int = 300,
        timeout: int = 30,
    ):
        """Initialize authentication configuration.

        Args:
            api_token: API token for authentication
            token_portal_url: URL of the token portal
            cache_duration: Token verification cache duration in seconds
            timeout: Request timeout in seconds
        """
        self.api_token = api_token or os.getenv("CODECHEQ_API_TOKEN")
        self.token_portal_url = token_portal_url or os.getenv("CODECHEQ_TOKEN_PORTAL_URL", "http://localhost:5000")
        self.cache_duration = cache_duration
        self.timeout = timeout
        self.require_auth = True

    def has_token(self) -> bool:
        """Check if an API token is configured."""
        return bool(self.api_token)

    def is_valid(self) -> bool:
        """Check if the configuration is valid."""
        if not self.has_token():
            return False
        return True

    def get_validation_errors(self) -> list:
        """Get list of validation errors."""
        errors = []
        
        if not self.has_token():
            errors.append("Authentication is required but no API token is provided")
        
        if self.has_token() and not self.api_token.startswith("sk-"):
            errors.append("API token must start with 'sk-' prefix")
        
        return errors

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "api_token": self.api_token,
            "token_portal_url": self.token_portal_url,
            "cache_duration": self.cache_duration,
            "timeout": self.timeout,
            "has_token": self.has_token(),
            "is_valid": self.is_valid()
        } 