"""
Token Verifier

Manages API token verification with caching and validation rules.
"""

import time
from typing import Dict, Optional, Any
from .client import APITokenClient
from .exceptions import TokenVerificationError, InvalidTokenError


class TokenVerifier:
    """Manages API token verification with caching and validation."""

    def __init__(self, base_url: str = "http://localhost:5000", cache_duration: int = 300):
        """Initialize the token verifier.

        Args:
            base_url: Base URL of the API Token Portal
            cache_duration: Cache duration in seconds (default: 5 minutes)
        """
        self.client = APITokenClient(base_url)
        self.cache_duration = cache_duration
        self._cache: Dict[str, Dict[str, Any]] = {}

    def verify_token(self, token: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Verify an API token with caching.

        Args:
            token: The API token to verify
            force_refresh: Force refresh the cache

        Returns:
            Dictionary containing verification result

        Raises:
            TokenVerificationError: If token verification fails
        """
        if not token:
            raise InvalidTokenError("Token cannot be empty")

        # Check cache first (unless force refresh)
        if not force_refresh and token in self._cache:
            cached_result = self._cache[token]
            if time.time() - cached_result["timestamp"] < self.cache_duration:
                return cached_result["data"]

        try:
            # Verify token with the portal
            result = self.client.verify_token(token)
            
            # Cache the result
            self._cache[token] = {
                "data": result,
                "timestamp": time.time()
            }
            
            return result

        except Exception as e:
            # Remove from cache if verification fails
            self._cache.pop(token, None)
            raise TokenVerificationError(f"Token verification failed: {str(e)}")

    def is_token_valid(self, token: str) -> bool:
        """Check if a token is valid without raising exceptions.

        Args:
            token: The API token to check

        Returns:
            True if token is valid, False otherwise
        """
        try:
            self.verify_token(token)
            return True
        except TokenVerificationError:
            return False

    def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information for a valid token.

        Args:
            token: The API token

        Returns:
            User information dictionary or None if verification fails
        """
        try:
            result = self.verify_token(token)
            return result.get("user")
        except TokenVerificationError:
            return None

    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token information without user details.

        Args:
            token: The API token

        Returns:
            Token information dictionary or None if verification fails
        """
        try:
            result = self.verify_token(token)
            return result.get("token")
        except TokenVerificationError:
            return None

    def clear_cache(self):
        """Clear the verification cache."""
        self._cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        
        for entry in self._cache.values():
            if current_time - entry["timestamp"] < self.cache_duration:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_duration": self.cache_duration
        }

    def cleanup_expired_cache(self):
        """Remove expired entries from the cache."""
        current_time = time.time()
        expired_tokens = [
            token for token, entry in self._cache.items()
            if current_time - entry["timestamp"] >= self.cache_duration
        ]
        
        for token in expired_tokens:
            del self._cache[token]

    def close(self):
        """Close the underlying client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 