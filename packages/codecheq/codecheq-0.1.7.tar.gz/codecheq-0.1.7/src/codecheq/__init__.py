"""
CodeCheq

A library for analyzing code security using Large Language Models (LLMs).
"""

from .analyzer import CodeAnalyzer
from .patcher import VulnerabilityPatcher
from .models.analysis_result import AnalysisResult, Issue, Location, Severity
from .prompt import PromptTemplate, create_custom_prompt, get_default_prompt
from .auth import (
    TokenVerifier,
    APITokenClient,
    TokenVerificationError,
    InvalidTokenError,
    TokenExpiredError,
    NetworkError,
    AuthenticationError,
    AuthConfig,
)
from .config import CodeCheqConfig, get_config, set_api_token, set_token_portal_url

__version__ = "0.1.7"
__all__ = [
    "CodeAnalyzer",
    "VulnerabilityPatcher",
    "AnalysisResult",
    "Issue",
    "Location",
    "Severity",
    "PromptTemplate",
    "create_custom_prompt",
    "get_default_prompt",
    # Authentication
    "TokenVerifier",
    "APITokenClient",
    "TokenVerificationError",
    "InvalidTokenError",
    "TokenExpiredError",
    "NetworkError",
    "AuthenticationError",
    "AuthConfig",
    # Configuration
    "CodeCheqConfig",
    "get_config",
    "set_api_token",
    "set_token_portal_url",
] 