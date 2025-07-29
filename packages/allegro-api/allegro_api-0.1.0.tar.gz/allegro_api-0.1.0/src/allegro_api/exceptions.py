"""
Exceptions for Allegro API client.
"""

from typing import Optional, Dict, Any


class AllegroAPIException(Exception):
    """Base exception for all Allegro API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(AllegroAPIException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(AllegroAPIException):
    """Raised when user lacks required permissions."""
    pass


class RateLimitError(AllegroAPIException):
    """Raised when API rate limit is exceeded."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, response_data)
        self.retry_after = retry_after


class ValidationError(AllegroAPIException):
    """Raised when request validation fails."""
    pass


class NotFoundError(AllegroAPIException):
    """Raised when requested resource is not found."""
    pass


class ServerError(AllegroAPIException):
    """Raised when server returns 5xx error."""
    pass