"""Platform detection utilities for HipHops Hook client."""

import os
import platform
from typing import Optional


def get_platform_info() -> tuple[str, str]:
    """
    Get platform and architecture information.

    Returns:
        Tuple of (platform, architecture) strings
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize platform names
    if system == "darwin":
        platform_name = "darwin"
    elif system == "linux":
        platform_name = "linux"
    elif system == "windows":
        platform_name = "windows"
    else:
        raise ValueError(f"Unsupported platform: {system}")

    # Normalize architecture names
    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        # Default to amd64 for unsupported architectures
        arch = "amd64"

    return platform_name, arch


def get_binary_name() -> str:
    """
    Get the binary name for the current platform.

    Returns:
        Binary filename for the current platform
    """
    platform_name, arch = get_platform_info()

    if platform_name == "windows":
        return "hook-windows-amd64.exe"
    elif platform_name == "darwin":
        return f"hook-darwin-{arch}"
    elif platform_name == "linux":
        return f"hook-linux-{arch}"
    else:
        raise ValueError(f"Unsupported platform: {platform_name}")


def get_binary_path(package_dir: str, env_var: str = "HIPHOPS_HOOK_BIN") -> str:
    """
    Get the path to the Hook binary.

    Args:
        package_dir: Directory containing the package
        env_var: Environment variable name for binary path override

    Returns:
        Path to the Hook binary

    Raises:
        FileNotFoundError: If binary is not found
    """
    # Check if env var is set
    env_binary_path = os.environ.get(env_var)
    if env_binary_path:
        if not os.path.exists(env_binary_path):
            raise FileNotFoundError(
                f"Binary path set in {env_var} does not exist: {env_binary_path}"
            )
        return env_binary_path

    # Construct default binary path
    binary_name = get_binary_name()
    binary_path = os.path.join(package_dir, "bin", binary_name)

    if not os.path.exists(binary_path):
        raise FileNotFoundError(f"Hook binary not found at: {binary_path}")

    return binary_path


def should_skip_download() -> bool:
    """
    Check if binary download should be skipped.

    Returns:
        True if download should be skipped
    """
    # Skip if env var is set
    if os.environ.get("HIPHOPS_HOOK_BIN"):
        return True

    # Skip if explicitly requested
    if os.environ.get("SKIP_HOOK_DOWNLOAD") == "true":
        return True

    return False
