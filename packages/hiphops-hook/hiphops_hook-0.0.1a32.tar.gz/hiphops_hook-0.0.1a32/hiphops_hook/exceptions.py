"""Custom exception classes for HipHops Hook client."""


class HookError(Exception):
    """Base exception for HipHops Hook client errors."""
    pass


class BinaryNotFoundError(HookError):
    """Raised when the Hook binary cannot be found."""
    pass


class ServerStartupError(HookError):
    """Raised when the Hook server fails to start."""
    pass


class ServerTimeoutError(HookError):
    """Raised when the Hook server fails to start within timeout."""
    pass


class RequestError(HookError):
    """Raised when an HTTP request to the Hook server fails."""
    pass


class ResponseError(HookError):
    """Raised when the Hook server returns an error response."""
    pass


class DownloadError(HookError):
    """Raised when binary download fails."""
    pass