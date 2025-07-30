#!/usr/bin/env python3
"""
Binary download script for HipHops Hook Python client.

This script downloads the appropriate Hook binary for the current platform
during package installation.
"""

import os
import stat
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Add the parent directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from hiphops_hook.platform_utils import get_binary_name, should_skip_download
from hiphops_hook.exceptions import DownloadError


def get_version() -> str:
    """Get the package version."""
    # This version is automatically updated by the release script
    return "0.0.1-alpha32"


def download_binary() -> None:
    """Download the Hook binary for the current platform."""

    # Check if we should skip the download
    if should_skip_download():
        if os.environ.get("HIPHOPS_HOOK_BIN"):
            print(
                f"Using hook binary from HIPHOPS_HOOK_BIN: {os.environ['HIPHOPS_HOOK_BIN']}"
            )
        else:
            print("Skipping hook binary download in development mode")
        return

    try:
        # Get version and binary name
        version = get_version()
        binary_name = get_binary_name()

        # Create bin directory if it doesn't exist
        # When called from setup.py, we need to find the hiphops_hook package directory
        import hiphops_hook
        package_dir = Path(hiphops_hook.__file__).parent
        bin_dir = package_dir / "bin"
        bin_dir.mkdir(exist_ok=True)

        binary_path = bin_dir / binary_name

        # URL to download the binary
        download_url = f"https://github.com/hiphops-io/hook/releases/download/v{version}/{binary_name}"

        print(f"Downloading hook binary from: {download_url}")

        # Download the binary
        try:
            with urllib.request.urlopen(download_url) as response:
                if response.status != 200:
                    raise DownloadError(
                        f"Failed to download binary. Status code: {response.status}"
                    )

                # Write binary to file
                with open(binary_path, "wb") as f:
                    f.write(response.read())

            # Make binary executable on Unix-like systems
            if os.name != "nt":  # Not Windows
                current_mode = binary_path.stat().st_mode
                binary_path.chmod(current_mode | stat.S_IEXEC)

            print(f"Successfully downloaded hook binary to {binary_path}")

        except urllib.error.HTTPError as e:
            raise DownloadError(f"HTTP error downloading binary: {e}")
        except urllib.error.URLError as e:
            raise DownloadError(f"URL error downloading binary: {e}")
        except Exception as e:
            raise DownloadError(f"Error downloading binary: {e}")

    except Exception as e:
        print(f"Error downloading hook binary: {e}", file=sys.stderr)
        # Don't exit with error code to avoid breaking pip install
        # The client will handle missing binaries gracefully
        return


def main() -> None:
    """Main entry point for the install script."""
    try:
        download_binary()
    except Exception as e:
        print(f"Installation error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
