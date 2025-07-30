"""Error handling for the FileZen Python SDK."""

from typing import Any, Dict, Optional


class ZenError(Exception):
    """Base exception for FileZen SDK errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize ZenError.

        Args:
            message: Error message
            code: Error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }


class ZenUploadError(ZenError):
    """Exception raised during file upload operations."""

    pass


class ZenAuthenticationError(ZenError):
    """Exception raised for authentication failures."""

    pass


class ZenValidationError(ZenError):
    """Exception raised for validation failures."""

    pass


class ZenNetworkError(ZenError):
    """Exception raised for network-related errors."""

    pass


def build_zen_error(error: Any) -> ZenError:
    """Build a ZenError from various error types.

    Args:
        error: The original error (httpx.HTTPStatusError, httpx.RequestError, etc.)

    Returns:
        ZenError instance with appropriate details
    """
    if isinstance(error, ZenError):
        return error

    # Handle httpx HTTP status errors
    if hasattr(error, "response") and hasattr(error.response, "status_code"):
        status_code = error.response.status_code
        try:
            # Try to get error details from response body
            error_data = error.response.json()
            message = (
                error_data.get("message")
                or error_data.get("error")
                or error.response.reason_phrase
            )
            return ZenError(message=message, code=str(status_code), details=error_data)
        except (ValueError, AttributeError):
            # Fallback if response body is not JSON
            return ZenError(
                message=error.response.reason_phrase or f"HTTP {status_code}",
                code=str(status_code),
                details={"status_code": status_code},
            )

    # Handle httpx request errors (network issues)
    if hasattr(error, "request"):
        return ZenNetworkError(
            message=f"Network error: {str(error)}",
            code="-1",
            details={"error_type": "network_error"},
        )

    # Generic fallback
    return ZenError(
        message=str(error) or "Oops, something went wrong",
        code="-1",
        details={"error_type": "unknown_error"},
    )
