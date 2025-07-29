"""
CodeCheq Configuration

Manages configuration for the CodeCheq library including authentication settings.
"""

import os
from typing import Optional
from pathlib import Path


class CodeCheqConfig:
    """Configuration manager for CodeCheq library."""

    def __init__(self):
        """Initialize configuration with default values."""
        self._api_token: Optional[str] = None
        self._token_portal_url: Optional[str] = None

    @property
    def api_token(self) -> Optional[str]:
        """Get the API token from environment or set value."""
        if self._api_token:
            return self._api_token
        return os.getenv("CODECHEQ_API_TOKEN")

    @api_token.setter
    def api_token(self, value: Optional[str]):
        """Set the API token."""
        self._api_token = value

    @property
    def token_portal_url(self) -> str:
        """Get the token portal URL from environment or set value."""
        if self._token_portal_url:
            return self._token_portal_url
        return os.getenv("CODECHEQ_TOKEN_PORTAL_URL", "http://localhost:5000")

    @token_portal_url.setter
    def token_portal_url(self, value: Optional[str]):
        """Set the token portal URL."""
        self._token_portal_url = value

    def has_api_token(self) -> bool:
        """Check if an API token is available."""
        return bool(self.api_token)

    def is_authenticated(self) -> bool:
        """Check if authentication is properly configured."""
        return self.has_api_token()

    def get_auth_config(self) -> dict:
        """Get authentication configuration as a dictionary."""
        return {
            "api_token": self.api_token,
            "token_portal_url": self.token_portal_url,
            "has_token": self.has_api_token(),
            "is_authenticated": self.is_authenticated()
        }

    def load_from_env(self):
        """Load configuration from environment variables."""
        # These are already handled by properties, but this method
        # can be used to explicitly load and validate configuration
        pass

    def load_from_file(self, config_file: Path):
        """Load configuration from a file (future enhancement)."""
        # TODO: Implement configuration file loading
        pass

    def save_to_file(self, config_file: Path):
        """Save configuration to a file (future enhancement)."""
        # TODO: Implement configuration file saving
        pass


# Global configuration instance
_config = CodeCheqConfig()


def get_config() -> CodeCheqConfig:
    """Get the global configuration instance."""
    return _config


def set_api_token(token: str):
    """Set the API token globally."""
    _config.api_token = token


def set_token_portal_url(url: str):
    """Set the token portal URL globally."""
    _config.token_portal_url = url 