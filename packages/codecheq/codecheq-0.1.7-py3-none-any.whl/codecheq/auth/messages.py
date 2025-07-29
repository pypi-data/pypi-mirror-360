"""
Authentication Messages

User-friendly error messages and help text for authentication issues.
"""


class AuthMessages:
    """Collection of user-friendly authentication messages."""
    
    @staticmethod
    def get_token_help() -> str:
        """Get help text for obtaining API tokens."""
        return """
To use CodeCheq with authentication, you need an API token from the Token Portal:

1. Visit the Token Portal at: http://localhost:5000
2. Sign in with your account
3. Go to the API Tokens section
4. Create a new API token
5. Copy the token (it starts with 'sk-')
6. Set it as an environment variable: CODECHEQ_API_TOKEN=your_token_here

Or pass it directly to commands using --api-token parameter.
"""

    @staticmethod
    def get_portal_help() -> str:
        """Get help text for Token Portal configuration."""
        return """
The Token Portal URL can be configured in several ways:

1. Environment variable: CODECHEQ_TOKEN_PORTAL_URL=http://your-portal.com
2. Command line: --token-portal-url http://your-portal.com
3. Default: http://localhost:5000

Make sure the Token Portal is running and accessible from your machine.
"""

    @staticmethod
    def get_auth_required_help() -> str:
        """Get help text for when authentication is required."""
        return """
Authentication is required for this operation. Please:

1. Obtain an API token from the Token Portal
2. Set it as CODECHEQ_API_TOKEN environment variable
3. Or pass it using --api-token parameter
4. Ensure the Token Portal is running and accessible

For more help, run: codecheq verify-token --help
"""

    @staticmethod
    def get_network_error_help() -> str:
        """Get help text for network errors."""
        return """
Network error connecting to Token Portal. Please check:

1. Is the Token Portal running?
2. Is the URL correct? (default: http://localhost:5000)
3. Are there any firewall or network restrictions?
4. Can you access the portal in your browser?

Try: codecheq verify-token your_token --token-portal-url http://localhost:5000
"""

    @staticmethod
    def get_invalid_token_help() -> str:
        """Get help text for invalid tokens."""
        return """
Invalid API token. Please check:

1. Token format: should start with 'sk-' followed by 48 characters
2. Token validity: ensure it hasn't been revoked or expired
3. Token ownership: make sure you're using your own token

You can verify your token with: codecheq verify-token your_token
"""

    @staticmethod
    def get_auth_success_message(user_email: str = None) -> str:
        """Get success message for authentication."""
        if user_email:
            return f"✓ Successfully authenticated as: {user_email}"
        return "✓ Authentication successful"

    @staticmethod
    def get_auth_failed_message(error: str) -> str:
        """Get failure message for authentication."""
        return f"✗ Authentication failed: {error}"

    @staticmethod
    def get_setup_instructions() -> str:
        """Get complete setup instructions."""
        return """
CodeCheq Authentication Setup
============================

1. Start the Token Portal:
   - Navigate to the APITokenPortal directory
   - Run: npm install && npm run dev
   - Portal will be available at: http://localhost:5000

2. Create an API Token:
   - Visit http://localhost:5000 in your browser
   - Sign in with your account
   - Go to API Tokens section
   - Create a new token
   - Copy the token (starts with 'sk-')

3. Configure CodeCheq:
   - Set environment variable: CODECHEQ_API_TOKEN=your_token
   - Or use --api-token parameter in commands

4. Test Authentication:
   - Run: codecheq verify-token your_token
   - Should show successful verification

5. Use with Authentication:
   - Run: codecheq patch --require-auth your_file.py
   - Or: codecheq analyze --require-auth your_directory/

For more help, visit the Token Portal documentation.
""" 