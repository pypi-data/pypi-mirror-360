"""
askpablos_api.models

Data models and response objects for the AskPablos API client.

This module contains all data structures used to represent API responses
and internal data objects. Keeping models separate improves maintainability
and makes it easier to extend data structures.
"""

from typing import Optional, Dict, Any


class ResponseData:
    """
    Response object that provides structured access to HTTP response data.

    This class encapsulates all response information from a proxy request,
    including headers, content, timing, and optional screenshot data.

    Attributes:
        status_code (int): HTTP status code from the target server
        headers (Dict[str, str]): Response headers from target server
        content (bytes): Response body/content as bytes
        url (str): Final URL after any redirects
        elapsed_time (str): Time taken to complete the request (formatted string)
        encoding (Optional[str]): Response text encoding
        json (Optional[Dict[str, Any]]): Parsed JSON data if available
        screenshot (Optional[bytes]): Base64 decoded screenshot if requested
    """

    def __init__(
        self,
        status_code: int,
        headers: Dict[str, str],
        content: bytes,
        url: str,
        elapsed_time: str,
        encoding: Optional[str],
        json_data: Optional[Dict[str, Any]] = None,
        screenshot: Optional[bytes] = None
    ):
        """Initialize a ResponseData object."""
        self.status_code = status_code
        self.headers = headers
        self.content = content
        self.url = url
        self.elapsed_time = elapsed_time
        self.encoding = encoding
        self.json = json_data
        self.screenshot = screenshot

    def __repr__(self) -> str:
        """String representation of the response."""
        return (
            f"ResponseData(status_code={self.status_code}, "
            f"url='{self.url}', elapsed_time='{self.elapsed_time}')"
        )

    @property
    def text(self) -> str:
        """
        Get response content as text.

        Returns:
            str: Response content decoded as text using the response encoding
        """
        if self.content:
            encoding = self.encoding or 'utf-8'
            return self.content.decode(encoding, errors='replace')
        return ""

    @property
    def ok(self) -> bool:
        """
        Check if the response was successful.

        Returns:
            bool: True if status code is between 200-299
        """
        return 200 <= self.status_code < 300

    def raise_for_status(self) -> None:
        """
        Raise an exception if the response was unsuccessful.

        Raises:
            HTTPError: If the status code indicates an error
        """
        if not self.ok:
            from .exceptions import ResponseError
            raise ResponseError(
                self.status_code,
                f"HTTP {self.status_code} error for URL: {self.url}"
            )


class RequestOptions:
    """
    Container for request options and parameters.

    This class encapsulates all options that can be passed to a proxy request,
    providing validation and default values.
    """

    def __init__(
        self,
        browser: bool = False,
        rotate_proxy: bool = False,
        wait_for_load: bool = False,
        screenshot: bool = False,
        js_strategy: str = "DEFAULT",
        timeout: int = 30,
        **additional_options
    ):
        """
        Initialize request options.

        Args:
            browser: Enable browser automation
            rotate_proxy: Use proxy rotation
            wait_for_load: Wait for page load completion
            screenshot: Take page screenshot
            js_strategy: JavaScript execution strategy
            timeout: Request timeout in seconds
            **additional_options: Additional proxy options
        """
        self.browser = browser
        self.rotate_proxy = rotate_proxy
        self.wait_for_load = wait_for_load
        self.screenshot = screenshot
        self.js_strategy = js_strategy
        self.timeout = timeout
        self.additional_options = additional_options

    def validate(self) -> None:
        """
        Validate the request options.

        Raises:
            ValueError: If invalid parameter combinations are detected
        """
        if not self.browser:
            browser_features = []

            if self.wait_for_load:
                browser_features.append("wait_for_load=True")
            if self.screenshot:
                browser_features.append("screenshot=True")
            if self.js_strategy != "DEFAULT":
                browser_features.append(f"js_strategy={self.js_strategy}")

            if browser_features:
                features_str = ", ".join(browser_features)
                raise ValueError(f"browser=True is required for these actions: {features_str}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert options to dictionary format.

        Returns:
            Dict[str, Any]: Options as dictionary
        """
        options = {
            "browser": self.browser,
            "rotate_proxy": self.rotate_proxy,
            "timeout": self.timeout,
        }

        if self.browser:
            if self.wait_for_load:
                options["wait_for_load"] = self.wait_for_load
            if self.screenshot:
                options["screenshot"] = self.screenshot
            if self.js_strategy != "DEFAULT":
                options["js_strategy"] = self.js_strategy

        # Add any additional options
        options.update(self.additional_options)

        return options
