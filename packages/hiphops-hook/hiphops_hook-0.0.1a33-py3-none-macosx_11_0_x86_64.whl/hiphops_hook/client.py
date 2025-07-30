"""HipHops Hook client implementation."""

import atexit
import json
import logging
import os
import subprocess
import time
from typing import Any, Dict, Optional, TypedDict
import urllib.request

from .exceptions import (
    BinaryNotFoundError,
    RequestError,
    ResponseError,
    ServerStartupError,
    ServerTimeoutError,
)
from .platform_utils import get_binary_path


# Constants
SOCKET_PATH = "/tmp/hiphops.sock"
BINARY_ENV_VAR = "HIPHOPS_HOOK_BIN"
STARTUP_TIMEOUT = 5.0
CHECK_INTERVAL = 0.1

logger = logging.getLogger(__name__)


class LicenseInfo(TypedDict, total=False):
    """Type definition for license information."""

    valid: bool
    expires_at: Optional[str]


class HookClient:
    """
    HipHops Hook client for communicating with the Hook server.

    This client manages the lifecycle of the Hook binary process and provides
    methods to interact with the Hook server over Unix domain sockets.
    """

    def __init__(self) -> None:
        """Initialize the Hook client."""
        self._process: Optional[subprocess.Popen] = None
        self._connection_promise: Optional[bool] = None
        self._package_dir = os.path.dirname(os.path.abspath(__file__))

        # Register cleanup function
        atexit.register(self._cleanup)

    def _cleanup(self) -> None:
        """Clean up resources when the client is destroyed."""
        if self._process and self._process.poll() is None:
            logger.debug("[Hook] Cleaning up server process")
            try:
                self._process.terminate()
                self._process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                logger.warning("[Hook] Server process did not terminate, killing")
                self._process.kill()
            except Exception as e:
                logger.error(f"[Hook] Error cleaning up server process: {e}")

    def _ensure_server_running(self) -> None:
        """
        Ensure the Hook server is running.

        Raises:
            ServerStartupError: If the server fails to start
            ServerTimeoutError: If the server doesn't start within timeout
            BinaryNotFoundError: If the Hook binary is not found
        """
        if self._connection_promise is not None:
            return

        try:
            # Check if the socket already exists (another process might have started the server)
            if os.path.exists(SOCKET_PATH):
                logger.debug("[Hook] Using existing hook server")
                self._connection_promise = True
                return

            # Get binary path (should be embedded in wheel)
            try:
                binary_path = get_binary_path(self._package_dir, BINARY_ENV_VAR)
            except FileNotFoundError as e:
                raise BinaryNotFoundError(f"Hook binary not found: {e}. Binary should be embedded in wheel - this may indicate a packaging issue.")

            # Start the server
            logger.debug("[Hook] Starting hook server...")

            try:
                self._process = subprocess.Popen(
                    [binary_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                )
            except (OSError, subprocess.SubprocessError) as e:
                raise ServerStartupError(f"Failed to start hook server: {e}")

            # Wait for socket to be created
            start_time = time.time()
            while time.time() - start_time < STARTUP_TIMEOUT:
                if os.path.exists(SOCKET_PATH):
                    logger.debug("[Hook] Server is ready and accepting connections")
                    self._connection_promise = True
                    return

                # Check if process is still running
                if self._process.poll() is not None:
                    raise ServerStartupError(
                        f"Hook server exited with code {self._process.returncode}"
                    )

                time.sleep(CHECK_INTERVAL)

            # Timeout reached
            if self._process and self._process.poll() is None:
                self._process.terminate()
            raise ServerTimeoutError("Timeout waiting for hook server to start")

        except Exception as e:
            self._connection_promise = None
            raise

    def _make_request(self, path: str) -> Dict[str, Any]:
        """
        Make an HTTP request to the Hook server.

        Args:
            path: Request path

        Returns:
            Parsed JSON response

        Raises:
            RequestError: If the request fails
            ResponseError: If the response is invalid
        """
        self._ensure_server_running()

        # Create request using urllib
        url = f"http://localhost{path}"
        headers = {"Content-Type": "application/json"}

        try:
            # Create request with Unix socket
            request = urllib.request.Request(url, headers=headers)

            # We need to use a custom opener that supports Unix sockets
            # For now, we'll use a simple HTTP request approach
            # In a production implementation, you might want to use requests-unixsocket

            # Create a custom HTTPConnection that uses Unix socket
            import http.client
            import socket

            class UnixHTTPConnection(http.client.HTTPConnection):
                def __init__(self, path):
                    super().__init__("localhost")
                    self.path = path

                def connect(self):
                    self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    self.sock.connect(self.path)

            # Make the request
            conn = UnixHTTPConnection(SOCKET_PATH)
            conn.request("GET", path, headers=headers)
            response = conn.getresponse()

            if response.status != 200:
                raise ResponseError(f"HTTP error! status: {response.status}")

            data = response.read().decode("utf-8")

            try:
                parsed_data = json.loads(data)
                return parsed_data
            except json.JSONDecodeError as e:
                raise ResponseError(f"Error parsing response: {e}")

        except socket.error as e:
            raise RequestError(f"Socket error: {e}")
        except Exception as e:
            raise RequestError(f"Request error: {e}")

    def license(self) -> LicenseInfo:
        """
        Get license information.

        Returns:
            License information dictionary

        Raises:
            RequestError: If the request fails
            ResponseError: If the response is invalid
        """
        return self._make_request("/license")

    def close(self) -> None:
        """
        Close the client and clean up resources.

        This method is called automatically when the client is garbage collected
        or when the program exits.
        """
        self._cleanup()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global client instance
_hook_client: Optional[HookClient] = None


def get_client() -> HookClient:
    """
    Get the global Hook client instance.

    Returns:
        Global HookClient instance
    """
    global _hook_client
    if _hook_client is None:
        _hook_client = HookClient()
    return _hook_client


def license() -> LicenseInfo:
    """
    Get license information using the global client.

    Returns:
        License information dictionary
    """
    return get_client().license()
