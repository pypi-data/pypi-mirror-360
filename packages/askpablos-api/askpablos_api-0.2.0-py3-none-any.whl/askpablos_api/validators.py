"""
askpablos_api.validators

Parameter validation utilities for the AskPablos API client.

This module contains validation logic for request parameters, ensuring
proper parameter combinations and providing clear error messages.
Separating validation logic improves code clarity and reusability.
"""

from typing import Dict, Any, Optional
from .exceptions import ConfigurationError


class ParameterValidator:
    """
    Validates request parameters and options for API calls.

    This class provides centralized validation logic to ensure that
    parameter combinations are valid and provide helpful error messages
    when invalid combinations are detected.
    """

    @staticmethod
    def validate_browser_dependencies(
            browser: bool,
            wait_for_load: bool = False,
            screenshot: bool = False,
            js_strategy: str = "DEFAULT"
    ) -> None:
        """
        Validate that browser-dependent features are only used with browser=True.

        The following parameters require browser=True to function:
        - wait_for_load: Requires browser automation to detect page load completion
        - screenshot: Requires browser automation to capture page screenshots
        - js_strategy: Requires browser automation to execute JavaScript strategies

        Args:
            browser: Whether browser mode is enabled
            wait_for_load: Whether page load waiting is requested
            screenshot: Whether screenshot capture is requested
            js_strategy: JavaScript execution strategy

        Raises:
            ConfigurationError: If browser features are requested without browser=True
        """
        if browser:
            return  # All features are valid when browser is enabled

        # Collect invalid features that require browser=True
        invalid_features = []

        if wait_for_load:
            invalid_features.append("wait_for_load=True")

        if screenshot:
            invalid_features.append("screenshot=True")

        if invalid_features:
            features_str = ", ".join(invalid_features)
            raise ConfigurationError(
                f"CONFIGURATION ERROR: browser=True is required when using: {features_str}."
            )

    @staticmethod
    def validate_url(url: str) -> None:
        """
        Validate that the URL is properly formatted.

        Args:
            url: URL to validate

        Raises:
            ValueError: If URL is invalid
        """
        if not url:
            raise ValueError("URL is required and cannot be empty")

        if not isinstance(url, str):
            raise ValueError("URL must be a string")

        # Basic URL validation
        if not (url.startswith('http://') or url.startswith('https://')):
            raise ValueError("URL must start with 'http://' or 'https://'")

    @staticmethod
    def validate_timeout(timeout: int) -> None:
        """
        Validate timeout parameter.

        Args:
            timeout: Timeout value in seconds

        Raises:
            ValueError: If timeout is invalid
        """
        if not isinstance(timeout, int):
            raise ValueError("Timeout must be an integer")

        if timeout <= 0:
            raise ValueError("Timeout must be greater than 0")

        if timeout > 300:  # 5 minutes max
            raise ValueError("Timeout cannot exceed 300 seconds")

    @staticmethod
    def validate_headers(headers: Optional[Dict[str, str]]) -> None:
        """
        Validate headers parameter.

        Args:
            headers: Headers dictionary to validate

        Raises:
            ValueError: If headers are invalid
        """
        if headers is None:
            return

        if not isinstance(headers, dict):
            raise ValueError("Headers must be a dictionary")

        for key, value in headers.items():
            if not isinstance(key, str):
                raise ValueError(f"Header key must be string, got {type(key)}")
            if not isinstance(value, str):
                raise ValueError(f"Header value must be string, got {type(value)}")

    @classmethod
    def validate_request_params(
            cls,
            url: str,
            method: str = "GET",
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, str]] = None,
            browser: bool = False,
            wait_for_load: bool = False,
            screenshot: bool = False,
            js_strategy: str = "DEFAULT",
            timeout: int = 30,
            **kwargs
    ) -> None:
        """
        Validate all request parameters at once.

        Args:
            url: Target URL
            method: HTTP method
            headers: Custom headers
            params: Query parameters
            browser: Browser mode flag
            wait_for_load: Page load waiting flag
            screenshot: Screenshot capture flag
            js_strategy: JavaScript strategy
            timeout: Request timeout
            **kwargs: Additional parameters

        Raises:
            ValueError: If any parameter is invalid
        """
        cls.validate_url(url)
        cls.validate_headers(headers)
        cls.validate_timeout(timeout)
        cls.validate_browser_dependencies(
            browser=browser,
            wait_for_load=wait_for_load,
            screenshot=screenshot,
            js_strategy=js_strategy
        )
