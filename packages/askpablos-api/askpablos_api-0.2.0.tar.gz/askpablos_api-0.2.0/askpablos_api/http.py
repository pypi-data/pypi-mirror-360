"""
askpablos_api.http

HTTP communication and client functionality for the AskPablos API.

This module handles HTTP communication with the AskPablos API, including
request construction, response parsing, error handling, and provides
the main ProxyClient class for API interactions.
"""

import json
import requests
from base64 import b64decode
from typing import Dict, Optional, Any

from .auth import AuthManager
from .models import ResponseData, RequestOptions
from .validators import ParameterValidator
from .exceptions import APIConnectionError, ResponseError, RequestTimeoutError
from .config import DEFAULT_API_URL


class HTTPClient:
    """
    Handles low-level HTTP communication with the AskPablos API.

    This class manages the HTTP requests, response parsing,
    and error handling for the proxy service communication.
    """

    def __init__(self, auth_manager: AuthManager, api_url: str):
        """
        Initialize the HTTP client.

        Args:
            auth_manager: Authentication manager for request signing
            api_url: Base URL for the API service
        """
        self.auth_manager = auth_manager
        self.api_url = api_url

    def send_request(
            self,
            url: str,
            method: str = "GET",
            data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, str]] = None,
            options: Optional[RequestOptions] = None
    ) -> ResponseData:
        """
        Send an HTTP request through the proxy service.

        Args:
            url: Target URL to fetch through the proxy
            method: HTTP method (GET, POST, etc.)
            data: Request payload for POST/PUT requests
            headers: Custom headers for the target request
            params: Query parameters for the target URL
            options: Request options and proxy settings

        Returns:
            ResponseData: Parsed response from the API

        Raises:
            APIConnectionError: If connection to API fails
            ResponseError: If API returns an error response
        """
        if options is None:
            options = RequestOptions()

        # Validate options
        options.validate()

        # Build the request payload
        request_data = self._build_request_payload(
            url=url,
            method=method,
            data=data,
            headers=headers,
            params=params,
            options=options
        )

        # Convert to JSON
        payload = json.dumps(request_data, separators=(',', ':'))

        # Build authentication headers
        auth_headers = self.auth_manager.build_auth_headers(payload)

        try:
            # Send the request
            response = requests.post(
                self.api_url,
                data=payload,
                headers=auth_headers,
                timeout=options.timeout
            )

            # Handle HTTP errors
            if response.status_code != 200:
                error_msg = self._extract_error_message(response)
                raise ResponseError(response.status_code, error_msg)

            # Parse and return the response
            return self._parse_response(response)

        except requests.Timeout as e:
            raise RequestTimeoutError("The request to the AskPablos server timed out. "
                                      "Please check your network connection or try increasing the timeout setting.") from e

        except requests.RequestException as e:
            raise APIConnectionError("Failed to connect to the askpablos server it may be down or unreachable "
                                     "if the problem persists contact the administrator.") from e

    @staticmethod
    def _build_request_payload(
            url: str,
            method: str,
            data: Optional[Dict[str, Any]],
            headers: Optional[Dict[str, str]],
            params: Optional[Dict[str, str]],
            options: RequestOptions
    ) -> Dict[str, Any]:
        """
        Build the request payload for the API.

        Args:
            url: Target URL
            method: HTTP method
            data: Request data
            headers: Custom headers
            params: Query parameters
            options: Request options

        Returns:
            Dict[str, Any]: Complete request payload
        """
        request_data = {
            "url": url,
            "method": method.upper(),
            "browser": options.browser,
            "rotateProxy": options.rotate_proxy,
            "data": data if data else None,
            "headers": headers if headers else None,
            "params": params if params else None,
        }

        # Add browser-specific options if browser is enabled
        if options.browser:
            if options.wait_for_load:
                request_data["waitForLoad"] = options.wait_for_load
            if options.screenshot:
                request_data["screenshot"] = options.screenshot
            if options.js_strategy != "DEFAULT":
                request_data["jsStrategy"] = options.js_strategy

        # Add any additional options
        request_data.update(options.additional_options)

        return request_data

    @staticmethod
    def _parse_response(response: requests.Response) -> ResponseData:
        """
        Parse the API response into a ResponseData object.

        Args:
            response: Raw HTTP response from the API

        Returns:
            ResponseData: Parsed response object
        """
        # Parse the API response
        api_response = response.json()

        # Decode base64 content
        response_content = b64decode(api_response.get('responseBody', ''))

        # Decode screenshot if present
        screenshot_content = None
        if api_response.get('screenshot'):
            screenshot_content = b64decode(api_response.get('screenshot'))

        return ResponseData(
            status_code=api_response.get('statusCode', response.status_code),
            headers=api_response.get('headers', {}),
            content=response_content,
            url=api_response.get('url', response.url),
            elapsed_time=f"{response.elapsed.total_seconds():.2f}s",
            encoding=api_response.get('encoding'),
            json_data=api_response,
            screenshot=screenshot_content,
        )

    @staticmethod
    def _extract_error_message(response: requests.Response) -> str:
        """
        Extract error message from API response.

        Args:
            response: HTTP response with error

        Returns:
            str: Error message
        """
        response_body = json.loads(response.content)
        try:
            if response_body.get('error'):
                return response_body.get('error')
            else:
                return 'No error details provided'
        except (ValueError, json.JSONDecodeError):
            return f'HTTP {response.status_code} error'


class ProxyClient:
    """
    High-level client for the AskPablos proxy service.

    This class orchestrates the authentication, HTTP communication,
    and validation components to provide a clean interface for
    making proxy requests.
    """

    def __init__(self, api_key: str, secret_key: str, api_url: str = DEFAULT_API_URL):
        """
        Initialize the proxy client.

        Args:
            api_key: Your API key from the AskPablos dashboard
            secret_key: Your secret key for HMAC signing
            api_url: The proxy API base URL
        """
        # Initialize components
        self.auth_manager = AuthManager(api_key, secret_key)
        self.http_client = HTTPClient(self.auth_manager, api_url)
        self.validator = ParameterValidator()

    def request(
            self,
            url: str,
            method: str = "GET",
            data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, str]] = None,
            options: Optional[Dict[str, Any]] = None,
            timeout: int = 30
    ) -> ResponseData:
        """
        Send a request through the AskPablos proxy.

        Args:
            url: Target URL to fetch through the proxy
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            data: Request payload for POST/PUT requests
            headers: Custom headers to send to the target URL
            params: Query parameters to append to the target URL
            options: Proxy-specific options for request processing
            timeout: Request timeout in seconds

        Returns:
            ResponseData: Response object with all request results
        """
        # Convert options dict to RequestOptions object
        if options is None:
            options = {}

        request_options = RequestOptions(
            browser=options.get("browser", False),
            rotate_proxy=options.get("rotate_proxy", False),
            wait_for_load=options.get("wait_for_load", False),
            screenshot=options.get("screenshot", False),
            js_strategy=options.get("js_strategy", "DEFAULT"),
            timeout=timeout,
            **{k: v for k, v in options.items() if k not in [
                "browser", "rotate_proxy", "wait_for_load",
                "screenshot", "js_strategy"
            ]}
        )

        # Validate all parameters
        self.validator.validate_request_params(
            url=url,
            method=method,
            headers=headers,
            params=params,
            browser=request_options.browser,
            wait_for_load=request_options.wait_for_load,
            screenshot=request_options.screenshot,
            js_strategy=request_options.js_strategy,
            timeout=timeout
        )

        # Send the request
        return self.http_client.send_request(
            url=url,
            method=method,
            data=data,
            headers=headers,
            params=params,
            options=request_options
        )
