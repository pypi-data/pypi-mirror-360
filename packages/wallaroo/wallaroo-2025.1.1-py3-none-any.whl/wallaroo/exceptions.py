from dataclasses import dataclass
from functools import wraps
from typing import Optional, Union

import httpx
import requests


@dataclass
class APIErrorResponse:
    """
    Standardized structure for API error responses.

    Attributes:
        code: HTTP status code of the error
        status: Status message (e.g., "error", "failed")
        error: Detailed error message
        source: Source of the error (e.g., "engine", "sidekick")
        original_response: Original response object for fallback
    """

    code: Optional[int] = None
    status: Optional[str] = None
    error: Optional[str] = None
    source: Optional[str] = None
    original_response: Optional[Union[requests.Response | httpx.Response]] = None

    # TODO: we need to implement the same for mlops api client and httpx client.
    @classmethod
    def from_response(
        cls, response: Union[requests.Response | httpx.Response]
    ) -> "APIErrorResponse":
        """
        Create an APIErrorResponse from a requests.Response object.
        Falls back gracefully if expected fields are missing.
        """
        try:
            error_data = response.json()
            return cls(
                code=error_data.get("code", response.status_code),
                status=error_data.get("status"),
                error=error_data.get("error"),
                source=error_data.get("source"),
                original_response=response,
            )
        except (ValueError, AttributeError):
            # Handle non-JSON responses
            return cls(
                code=response.status_code,
                error=response.text or "Unknown error",
                original_response=response,
            )


class WallarooAPIError(Exception):
    """
    Base exception class for all Wallaroo API errors.

    Attributes:
        code: HTTP status code of the error
        status: Status message
        error: Detailed error message
        source: Source of the error
        response: Original APIErrorResponse object
    """

    def __init__(self, error_response: APIErrorResponse, prefix: str = ""):
        self.code = error_response.code
        self.status = error_response.status
        self.error = error_response.error
        self.source = error_response.source
        self.response = error_response
        self.prefix = prefix

        # Format a consistent error message
        message = self.__str__()
        super().__init__(message)

    def __str__(self) -> str:
        error_msg = (
            f"{self.prefix}: [{self.code}] {self.error}"
            if self.prefix
            else f"[{self.code}] {self.error}"
        )
        status_part = f", status: {self.status}" if self.status else ""
        return f"{error_msg} (source: {self.source}{status_part})"


def handle_errors(http_error_class=None):
    """
    Decorator to handle HTTP errors and convert them to appropriate custom errors.

    :param error_class: The specific error class to use for HTTP errors.
                       If None, uses WallarooAPIError.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (requests.HTTPError, httpx.HTTPStatusError) as e:
                if e.response is not None:
                    error_cls = http_error_class or WallarooAPIError
                    raise error_cls(e.response) from e
                raise  # Re-raise if no response available
            except requests.RequestException:
                raise requests.RequestException(
                    "An error occurred while sending the request. Check network configuration, adjust timeout if necessary and retry."
                )
            except httpx.HTTPError:
                raise httpx.HTTPError(
                    "An error occurred while sending the request. Check network configuration, adjust timeout if necessary and Retry again."
                )

        return wrapper

    return decorator


# Custom error classes
class InferenceError(WallarooAPIError):
    """Raised when inference fails"""

    def __init__(self, response: Union[requests.Response | httpx.Response]):
        error_response = APIErrorResponse.from_response(response)
        super().__init__(error_response, prefix="Inference failed")


class InferenceTimeoutError(Exception):
    """Raised when inference fails because of connection or timeout errors."""

    def __init__(self, error):
        super().__init__("Inference failed: {}".format(error))
