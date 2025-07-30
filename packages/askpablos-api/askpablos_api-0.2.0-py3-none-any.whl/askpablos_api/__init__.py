"""
askpablos_api

A Python client library for interacting with the AskPablos proxy API service.
"""

# Core classes - main user interfaces
from .core import AskPablos
from .http import ProxyClient

# Data models and response objects
from .models import ResponseData, RequestOptions

# Authentication components
from .auth import AuthManager

# HTTP communication
from .http import HTTPClient

# Validation utilities
from .validators import ParameterValidator

# Exception classes
from .exceptions import (
    AskPablosError,
    AuthenticationError,
    APIConnectionError,
    RequestTimeoutError,
    ResponseError,
    ConfigurationError
)

# Utility functions
from .utils import configure_logging

__version__ = "0.2.0"

# Main public API - what most users will import
__all__ = [
    # Primary interfaces
    "AskPablos",
    "ProxyClient",

    # Data models
    "ResponseData",
    "RequestOptions",

    # Advanced components (for power users)
    "AuthManager",
    "HTTPClient",
    "ParameterValidator",

    # Exception handling
    "AskPablosError",
    "AuthenticationError",
    "APIConnectionError",
    "RequestTimeoutError",
    "ResponseError",
    "ConfigurationError",

    # Utilities
    "configure_logging",
]
