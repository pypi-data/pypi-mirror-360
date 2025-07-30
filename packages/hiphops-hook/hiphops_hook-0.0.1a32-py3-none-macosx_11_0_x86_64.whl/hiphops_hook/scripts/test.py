#!/usr/bin/env python3
"""
Test script for the HipHops Hook Python client.

This script tests the basic functionality of the Hook client.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from hiphops_hook import license, HookError


def test_client():
    """Test the Hook client functionality."""
    try:
        hook_bin_path = os.environ.get("HIPHOPS_HOOK_BIN", "default binary path")

        print("=" * 50)
        print("Testing Hook Python client")
        print("-" * 50)
        print(f"Using binary from: {hook_bin_path}")
        print(f"Current directory: {os.getcwd()}")
        print("=" * 50)

        print("\nFetching license information...")
        info = license()

        print("\nLicense info:")
        print(json.dumps(info, indent=2))

        print("\n✅ Test completed successfully!")
        return True

    except HookError as e:
        print(f"\n❌ Hook error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False


def main():
    """Main entry point for the test script."""
    success = test_client()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
