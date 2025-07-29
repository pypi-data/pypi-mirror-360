"""
Exception classes for the Maylng Python SDK.

This module defines all custom exceptions that can be raised by the SDK,
providing structured error handling for different types of failures.
"""

from typing import Optional


class MaylError(Exception):
    """Base class for all Mayl errors."""
    
    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        status_code: Optional[int] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.request_id = request_id
        self.status_code = status_code
        self.code = self.__class__.__name__.replace("Error", "").upper() + "_ERROR"
    
    def __str__(self) -> str:
        base = f"{self.code}: {self.message}"
        if self.request_id:
            base += f" (Request ID: {self.request_id})"
        return base
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', request_id='{self.request_id}')"


class AuthenticationError(MaylError):
    """Authentication related errors (401)."""
    
    def __init__(
        self,
        message: str = "Invalid API key or authentication failed",
        request_id: Optional[str] = None
    ) -> None:
        super().__init__(message, request_id, 401)


class AuthorizationError(MaylError):
    """Authorization related errors (403)."""
    
    def __init__(
        self,
        message: str = "Insufficient permissions to perform this action",
        request_id: Optional[str] = None
    ) -> None:
        super().__init__(message, request_id, 403)


class NotFoundError(MaylError):
    """Resource not found errors (404)."""
    
    def __init__(
        self,
        resource: str,
        resource_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> None:
        if resource_id:
            message = f"{resource} with ID '{resource_id}' not found"
        else:
            message = f"{resource} not found"
        super().__init__(message, request_id, 404)


class ValidationError(MaylError):
    """Validation errors for invalid input (400)."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> None:
        super().__init__(message, request_id, 400)
        self.field = field
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.field:
            base += f" (Field: {self.field})"
        return base


class RateLimitError(MaylError):
    """Rate limiting errors (429)."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        request_id: Optional[str] = None
    ) -> None:
        super().__init__(message, request_id, 429)
        self.retry_after = retry_after
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.retry_after:
            base += f" (Retry after: {self.retry_after} seconds)"
        return base


class NetworkError(MaylError):
    """Network or connection errors."""
    
    def __init__(
        self,
        message: str = "Network request failed",
        request_id: Optional[str] = None
    ) -> None:
        super().__init__(message, request_id, 0)  # No HTTP status for network errors


class ServerError(MaylError):
    """Server errors (5xx responses)."""
    
    def __init__(
        self,
        message: str = "Internal server error",
        status_code: int = 500,
        request_id: Optional[str] = None
    ) -> None:
        super().__init__(message, request_id, status_code)


class TimeoutError(MaylError):
    """Timeout errors."""
    
    def __init__(
        self,
        message: str = "Request timeout",
        request_id: Optional[str] = None
    ) -> None:
        super().__init__(message, request_id, 408)


class EmailAddressError(MaylError):
    """Email address related errors."""
    
    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None
    ) -> None:
        super().__init__(message, request_id, 400)


class EmailSendError(MaylError):
    """Email sending related errors."""
    
    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None
    ) -> None:
        super().__init__(message, request_id, 400)
