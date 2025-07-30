"""
HipHops Hook Python Client

A Python client library for integrating with HipHops Hook.
"""

from .client import HookClient, LicenseInfo, get_client, license
from .exceptions import (
    BinaryNotFoundError,
    DownloadError,
    HookError,
    RequestError,
    ResponseError,
    ServerStartupError,
    ServerTimeoutError,
)
from .platform_utils import get_binary_name, get_binary_path, get_platform_info

__version__ = "0.0.1-alpha33"
__all__ = [
    # Main client and functions
    "HookClient",
    "get_client",
    "license",
    # Type definitions
    "LicenseInfo",
    # Exceptions
    "HookError",
    "BinaryNotFoundError",
    "ServerStartupError",
    "ServerTimeoutError",
    "RequestError",
    "ResponseError",
    "DownloadError",
    # Utilities
    "get_platform_info",
    "get_binary_name",
    "get_binary_path",
]