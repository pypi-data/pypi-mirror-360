"""
askpablos_api.exceptions

This module defines exceptions specific to the AskPablos API client.

The exception hierarchy is designed to provide clear and specific error handling
for different types of failures that can occur when interacting with the AskPablos
API service.
"""


class AskPablosError(Exception):
    """
    Base exception for all AskPablos API errors.

    This is the root exception class for all errors that can occur within the
    AskPablos API client. All other exceptions inherit from this base class.
    """
    pass


class AuthenticationError(AskPablosError):
    """
    Raised when there is an authentication problem with the API.

    This exception is raised when:
    - API key is missing or empty
    - Secret key is missing or empty
    - Authentication credentials are invalid
    - HMAC signature verification fails
    """
    pass


class APIConnectionError(AskPablosError):
    """
    Raised when the client fails to connect to the API.

    This exception is raised when:
    - Network connectivity issues prevent reaching the API
    - DNS resolution fails for the API URL
    - Connection timeouts occur
    - The API server is unreachable or down
    """
    pass


class ResponseError(AskPablosError):
    """
    Raised when there is an error in the API response.

    This exception is raised when the AskPablos API returns an HTTP error
    status code (4xx or 5xx). It includes both the status code and the
    error message from the API response.

    Common scenarios:
    - 400 Bad Request: Invalid request parameters
    - 401 Unauthorized: Authentication failed
    - 403 Forbidden: Access denied
    - 404 Not Found: Endpoint not found
    - 429 Too Many Requests: Rate limit exceeded
    - 500 Internal Server Error: Server error

    Attributes:
        status_code (int): The HTTP status code from the API response
        message (str): The error message from the API response
    """

    def __init__(self, status_code: int, message: str):
        """
        Initialize a ResponseError with status code and message.

        Args:
            status_code (int): The HTTP status code from the API response
            message (str): The error message describing what went wrong
        """
        self.status_code = status_code
        self.message = message
        super().__init__(f"API response error (status {status_code}): {message}")


class RequestTimeoutError(AskPablosError):
    """
    Exception raised when a request to the AskPablos API times out.

    This exception indicates that the operation exceeded the allowed time limit.
    """
    pass


class ConfigurationError(AskPablosError):
    """
    Raised when there is a configuration problem with request parameters.

    This exception is raised when:
    - Browser-specific features are used without browser=True
    - Invalid parameter combinations are detected
    - Required dependencies between parameters are not met
    """
    pass
