"""
askpablos_api.core

Core functionality for the AskPablos proxy API client.

This module provides the main AskPablos class, which serves as a simple interface
for making GET requests through the AskPablos proxy service. The client handles
authentication, error management, and request formatting automatically.
"""

from typing import Dict, Optional, Union
import logging

from .http import ProxyClient
from .models import ResponseData
from .validators import ParameterValidator
from .exceptions import AskPablosError, ConfigurationError

logger = logging.getLogger("askpablos_api")


class AskPablos:
    """
    Simple interface for making GET requests through the AskPablos proxy API.

    This class provides a clean interface for sending GET requests through the
    AskPablos proxy service. It handles authentication, request formatting,
    and error management automatically.

    The AskPablos class is designed to be simple and focused - it only supports
    GET requests to keep the interface clean and easy to use.

    Attributes:
        client (ProxyClient): The underlying client for making API requests.
    """

    def __init__(self, api_key: str, secret_key: str):
        """
        Initialize the AskPablos API client.

        Creates a new instance of the AskPablos client with the provided
        authentication credentials. The client will use these credentials
        for all subsequent API requests.

        Args:
            api_key (str): Your unique API key from the AskPablos dashboard.
            secret_key (str): Your private secret key used for HMAC signing.

        Raises:
            AuthenticationError: If any of the required credentials are missing
                                or invalid.
        """
        self.client = ProxyClient(api_key, secret_key)
        self.validator = ParameterValidator()

    def get(
            self,
            url: str,
            params: Optional[Dict[str, str]] = None,
            headers: Optional[Dict[str, str]] = None,
            browser: bool = False,
            rotate_proxy: bool = False,
            wait_for_load: bool = False,
            screenshot: bool = False,
            js_strategy: Optional[Union[bool, str]] = None,
            timeout: int = 30,
            **options
    ) -> ResponseData:
        """
        Send a GET request through the AskPablos proxy.

        This is the main method for fetching web pages and API endpoints through
        the AskPablos proxy service. It supports various options for customizing
        the request behavior.

        Args:
            url (str): The target URL to fetch. Must be a valid HTTP/HTTPS URL.
            params (Dict[str, str], optional): URL query parameters to append.
                                             Example: {"page": "1", "limit": "10"}
            headers (Dict[str, str], optional): Custom headers for the request.
            browser (bool, optional): Whether to use browser automation for
                                    JavaScript rendering. Useful for SPAs and
                                    dynamic content. Defaults to False.
            rotate_proxy (bool, optional): Whether to use proxy rotation for this
                                         request. Helps avoid rate limiting.
                                         Defaults to False.
            wait_for_load (bool, optional): Whether to wait for page load completion.
                                          Requires browser=True. Defaults to False.
            screenshot (bool, optional): Whether to take a screenshot of the page.
                                       Requires browser=True. Defaults to False.
            js_strategy (str|bool, optional): JavaScript execution strategy when using browser.
                                       Options: True (stealth script & minimal JS),
                                       False (no stealth injection, no JS rendering),
                                       "DEFAULT" (follows our techniques).
                                       Requires browser=True. Defaults to None.
            timeout (int, optional): Request timeout in seconds. Defaults to 30.
            **options: Additional proxy options like user_agent, cookies, etc.

        Returns:
            ResponseData: The response object from the API containing:
                - status_code (int): HTTP status code from the target server
                - headers (Dict[str, str]): Response headers from target server
                - content (bytes): Response body/content
                - url (str): Final URL after any redirects
                - elapsed_time (str): Time taken to complete the request
                - encoding (Optional[str]): Response text encoding
                - json (Optional[Dict[str, Any]]): Parsed JSON data if available
                - screenshot (Optional[bytes]): Screenshot data if requested

        Raises:
            APIConnectionError: If the client cannot connect to the AskPablos API.
            ResponseError: If the API returns an error status code.
            AuthenticationError: If authentication fails.
            ConfigurationError: If there is a configuration issue with the request.
        """
        # Set default value for js_strategy if not provided
        if js_strategy is None:
            js_strategy = "DEFAULT"
            js_strategy_explicitly_set = False
        else:
            js_strategy_explicitly_set = True

        # Validate browser-specific options using the validator
        self.validator.validate_browser_dependencies(
            browser=browser,
            wait_for_load=wait_for_load,
            screenshot=screenshot,
            js_strategy=js_strategy
        )

        # Additional validation for js_strategy when explicitly set
        if not browser and js_strategy_explicitly_set:
            raise ConfigurationError(
                f"browser=True is required when using: js_strategy='{js_strategy}'. "
            )

        # Build proxy options
        proxy_options = {
            "browser": browser,
            "rotate_proxy": rotate_proxy,
            "wait_for_load": wait_for_load,
            "screenshot": screenshot,
            "js_strategy": js_strategy,
            **options
        }

        try:
            return self.client.request(
                url=url,
                headers=headers,
                params=params,
                options=proxy_options,
                timeout=timeout
            )
        except AskPablosError as e:
            logger.error(str(e))
            raise
