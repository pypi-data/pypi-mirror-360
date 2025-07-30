#!/usr/bin/env python3
"""
Setup script for HipHops Hook Python client.

This script handles package installation. Binary download is handled
automatically at runtime when the client is first used.
"""

from pathlib import Path
from setuptools import setup
from setuptools.dist import Distribution
from wheel.bdist_wheel import bdist_wheel


class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name."""

    def has_ext_modules(self):
        return True

    def is_pure(self):
        return False


class UniversalBdistWheel(bdist_wheel):
    """Custom bdist_wheel command that creates universal py3 wheels."""

    def get_tag(self):
        # Get the default tag
        impl, abi, plat = super().get_tag()
        # Override to create universal py3 wheels
        return "py3", "none", plat


# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(distclass=BinaryDistribution, cmdclass={"bdist_wheel": UniversalBdistWheel})
