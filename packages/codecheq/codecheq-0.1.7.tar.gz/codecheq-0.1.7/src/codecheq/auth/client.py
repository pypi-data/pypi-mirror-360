"""
API Token Client

Handles HTTP communication with the API Token Portal for token verification.
"""

import httpx
from typing import Dict, Optional, Any
from .exceptions import NetworkError, TokenPortalError, InvalidTokenError


class APITokenClient:
    """Client for communicating with the API Token Portal."""

    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 30):
        """Initialize the API token client.

        Args:
            base_url: Base URL of the API Token Portal
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify an API token with the Token Portal.

        Args:
            token: The API token to verify

        Returns:
            Dictionary containing verification result and user info

        Raises:
            InvalidTokenError: If token is invalid or malformed
            NetworkError: If there are network issues
            TokenPortalError: If the portal returns an error
        """
        if not token:
            raise InvalidTokenError("Token cannot be empty")

        if not token.startswith("sk-"):
            raise InvalidTokenError("Token must start with 'sk-' prefix")

        try:
            response = self._client.post(
                f"{self.base_url}/api/verify-token",
                json={"token": token},
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                error_data = response.json()
                raise InvalidTokenError(f"Invalid token: {error_data.get('message', 'Unknown error')}")
            elif response.status_code == 401:
                error_data = response.json()
                raise InvalidTokenError(f"Token verification failed: {error_data.get('message', 'Invalid or inactive token')}")
            elif response.status_code >= 500:
                raise TokenPortalError(f"Token portal server error: {response.status_code}")
            else:
                raise TokenPortalError(f"Unexpected response from token portal: {response.status_code}")

        except httpx.TimeoutException:
            raise NetworkError(f"Request to token portal timed out after {self.timeout} seconds")
        except httpx.ConnectError:
            raise NetworkError(f"Failed to connect to token portal at {self.base_url}")
        except httpx.RequestError as e:
            raise NetworkError(f"Network error communicating with token portal: {str(e)}")
        except Exception as e:
            if isinstance(e, (InvalidTokenError, NetworkError, TokenPortalError)):
                raise
            raise NetworkError(f"Unexpected error during token verification: {str(e)}")

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
        except (InvalidTokenError, NetworkError, TokenPortalError):
            return None

    def check_token_status(self, token: str) -> Dict[str, Any]:
        """Check the status of a token without getting user details.

        Args:
            token: The API token

        Returns:
            Dictionary with token status information
        """
        try:
            result = self.verify_token(token)
            return {
                "valid": True,
                "token_id": result.get("token", {}).get("id"),
                "token_name": result.get("token", {}).get("name"),
                "is_active": result.get("token", {}).get("isActive", False),
                "last_used": result.get("token", {}).get("lastUsed"),
                "created_at": result.get("token", {}).get("createdAt")
            }
        except (InvalidTokenError, NetworkError, TokenPortalError) as e:
            return {
                "valid": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 