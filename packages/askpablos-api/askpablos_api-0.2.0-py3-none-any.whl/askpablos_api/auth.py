"""
askpablos_api.auth

Authentication and security utilities for the AskPablos API client.

This module handles all authentication-related functionality including
HMAC signature generation, credential validation, and request signing.
Separating auth logic improves security and maintainability.
"""

import hmac
import hashlib
from base64 import b64encode
from typing import Dict

from .exceptions import AuthenticationError


class AuthManager:
    """
    Handles authentication and request signing for the AskPablos API.

    This class manages API credentials and provides methods for generating
    HMAC-SHA256 signatures required for API authentication.
    """

    def __init__(self, api_key: str, secret_key: str):
        """
        Initialize the authentication manager.

        Args:
            api_key: Your API key from the AskPablos dashboard
            secret_key: Your secret key for HMAC signing

        Raises:
            AuthenticationError: If credentials are missing or invalid
        """
        self.api_key = api_key
        self.secret_key = secret_key

        self._validate_credentials()

    def _validate_credentials(self) -> None:
        """
        Validate that all required credentials are provided.

        Raises:
            AuthenticationError: If any required credential is missing
        """
        if not self.api_key:
            raise AuthenticationError("API key is required and cannot be empty")

        if not self.secret_key:
            raise AuthenticationError("Secret key is required and cannot be empty")

        if not isinstance(self.api_key, str):
            raise AuthenticationError("API key must be a string")

        if not isinstance(self.secret_key, str):
            raise AuthenticationError("Secret key must be a string")

    def generate_signature(self, payload: str) -> str:
        """
        Generate a base64-encoded HMAC SHA256 signature.

        Creates a cryptographic signature of the request payload using the client's
        secret key. This signature is used by the API server to verify that the
        request came from an authorized client and hasn't been tampered with.

        Args:
            payload: JSON string of the request body that will be signed.
                    This should be the exact JSON that will be sent in the
                    HTTP request body.

        Returns:
            str: Base64 encoded HMAC-SHA256 signature of the payload.

        Note:
            The signature is generated using HMAC-SHA256 with the client's secret key.
            The resulting binary signature is then base64-encoded for transmission
            in HTTP headers.
        """
        signature = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).digest()
        return b64encode(signature).decode()

    def build_auth_headers(self, payload: str) -> Dict[str, str]:
        """
        Construct authentication headers for API requests.

        Builds the complete set of HTTP headers needed for API authentication,
        including the content type, API key, and request signature.

        Args:
            payload: JSON string of the request body. Used to generate
                    the authentication signature.

        Returns:
            Dict[str, str]: HTTP headers dictionary containing:
                - Content-Type: Set to "application/json"
                - X-API-Key: Your API key for identification
                - X-Signature: HMAC-SHA256 signature of the payload
        """
        return {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key,
            'X-Signature': self.generate_signature(payload)
        }

    def __repr__(self) -> str:
        """String representation that doesn't expose sensitive data."""
        return f"AuthManager(api_key='{self.api_key[:8]}...', secret_key='***')"
