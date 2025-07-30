# HipHops Hook Python Client

Python client library for integrating with HipHops Hook.

## Installation

```bash
pip install hiphops-hook
```

The package will automatically download the appropriate Hook binary for your platform during installation.

## Quick Start

```python
from hiphops_hook import license

# Get license information
info = license()
print(info)
```

## Usage

### Basic Usage

```python
from hiphops_hook import license

# Get license information
license_info = license()
print(f"License verified: {license_info['verified']}")
```

### Error Handling

```python
from hiphops_hook import license, HookError, RequestError

try:
    info = license()
except RequestError as e:
    print(f"Request failed: {e}")
except HookError as e:
    print(f"Hook error: {e}")
```

## API Reference

### Functions

#### `license() -> LicenseInfo`

Get license information using the global client instance.

**Returns:**

- `LicenseInfo`: Dictionary containing license information

**Raises:**

- `RequestError`: If the request fails
- `ResponseError`: If the response is invalid
- `ServerStartupError`: If the server fails to start

### Types

#### `LicenseInfo`

TypedDict containing license information:

```python
class LicenseInfo(TypedDict):
    verified: bool
    verify_failures: List[str]
    license: Optional[Dict[str, Any]]
    hiphops: Dict[str, str]
    # Additional fields may be present
```

### Exceptions

- `HookError`: Base exception for all Hook-related errors
- `BinaryNotFoundError`: Raised when the Hook binary cannot be found
- `ServerStartupError`: Raised when the Hook server fails to start
- `ServerTimeoutError`: Raised when the server startup times out
- `RequestError`: Raised when an HTTP request fails
- `ResponseError`: Raised when the server returns an invalid response
- `DownloadError`: Raised when binary download fails

## Configuration

### Environment Variables

- `HIPHOPS_HOOK_BIN`: Override the path to the Hook binary
- `SKIP_HOOK_DOWNLOAD=true`: Force skip binary download

### Development Mode

When `SKIP_HOOK_DOWNLOAD=true`, the client will skip downloading the Hook binary during installation. This is useful for development environments where you want to use a custom binary.

## Platform Support

The client supports the same platforms as the Hook binary:

- **macOS**: `hook-darwin-amd64`, `hook-darwin-arm64`
- **Linux**: `hook-linux-amd64`, `hook-linux-arm64`
- **Windows**: `hook-windows-amd64.exe`

## Development

### Local Development (Source Code)

#### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/hiphops-io/hook.git
cd hook/clients/python

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

#### Testing Locally (Without Installation)

Test the source code directly without installing the package:

```bash
# Set PYTHONPATH and run the test script
PYTHONPATH=. python scripts/test.py

# Test with custom binary path
HIPHOPS_HOOK_BIN=/path/to/hook/binary PYTHONPATH=. python scripts/test.py

# Skip binary download during development
SKIP_HOOK_DOWNLOAD=true PYTHONPATH=. python scripts/test.py

# Test platform detection
PYTHONPATH=. python -c "from hiphops_hook.platform_utils import get_platform_info, get_binary_name; print(f'Platform: {get_platform_info()}'); print(f'Binary: {get_binary_name()}')"

# Test with license token (if available)
LICENSE_TOKEN=your_token_here PYTHONPATH=. python scripts/test.py
```

#### Installing for Local Development

```bash
# Install in development mode (editable install)
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Then test the installed package
python scripts/test.py
```

**Note**: If you encounter network/SSL issues with pip, you can work around them by:

1. Using the PYTHONPATH approach for testing (shown above)
2. Installing dependencies individually if needed
3. Using `--no-build-isolation` flag: `pip install -e . --no-build-isolation`

#### Binary Management During Development

```bash
# Skip binary download during development
export SKIP_HOOK_DOWNLOAD=true
pip install -e .

# Use a custom binary path
export HIPHOPS_HOOK_BIN=/path/to/your/hook/binary
pip install -e .
```

### Package Building and Distribution

#### Building the Package

```bash
python setup.py sdist
```

This creates a source distribution in the `dist/` directory:

- `hiphops-hook-<version>.tar.gz` - Ready for distribution

### Testing the Pip Package

#### Test Installation from Built Package

```bash
# Create a clean test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from built package
pip install dist/hiphops-hook-*.tar.gz

# Test the installed package
python -c "from hiphops_hook import license; print('Package installed successfully')"

# Run comprehensive test
python -c "
from hiphops_hook import license
try:
    info = license()
    print('✅ Package works correctly')
    print(f'License info: {info}')
except Exception as e:
    print(f'❌ Package test failed: {e}')
"

# Test with license token (if available)
LICENSE_TOKEN=your_token_here python -c "
from hiphops_hook import license
try:
    info = license()
    print('✅ License verification test:')
    print(f'Verified: {info.get(\"verified\", False)}')
    print(f'License info: {info}')
except Exception as e:
    print(f'❌ License test failed: {e}')
"

# Clean up
deactivate
rm -rf test_env
```

#### Test Installation from PyPI (Future)

Once published to PyPI:

```bash
# Create clean environment
python -m venv test_pypi
source test_pypi/bin/activate

# Install from PyPI
pip install hiphops-hook

# Test functionality
LICENSE_TOKEN=your_token_here python -c "
from hiphops_hook import license
info = license()
print('PyPI package works correctly')
print(info)
"

# Test with different environment variables
SKIP_HOOK_DOWNLOAD=true pip install --force-reinstall hiphops-hook
HIPHOPS_HOOK_BIN=/custom/path python -c "from hiphops_hook import license"

# Clean up
deactivate
rm -rf test_pypi
```

#### Testing Binary Download Process

```bash
# Test automatic binary download
python -c "
import os
import subprocess
import tempfile

# Create temporary directory
with tempfile.TemporaryDirectory() as tmpdir:
    # Install package in clean environment
    env = os.environ.copy()
    env['VIRTUAL_ENV'] = tmpdir

    result = subprocess.run([
        'pip', 'install', 'dist/hiphops-hook-*.tar.gz'
    ], env=env, capture_output=True, text=True)

    if 'Successfully downloaded hook binary' in result.stdout:
        print('✅ Binary download works correctly')
    else:
        print('❌ Binary download may have issues')
        print(result.stdout)
        print(result.stderr)
"
```

### Development Workflow

#### Complete Development Cycle

```bash
# 1. Make code changes
# Edit files in hiphops_hook/

# 2. Test locally without installation
PYTHONPATH=. python scripts/test.py

# 3. Test with editable installation
pip install -e .
python scripts/test.py

# 4. Build package
python setup.py sdist

# 5. Test built package in clean environment
python -m venv test_clean
source test_clean/bin/activate
pip install dist/hiphops-hook-*.tar.gz
python -c "from hiphops_hook import license; print(license())"
deactivate
rm -rf test_clean

# 6. Code quality checks
black hiphops_hook/ scripts/
flake8 hiphops_hook/ scripts/
mypy hiphops_hook/
```

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from hiphops_hook import license
info = license()
```

### Code Quality Tools

```bash
# Format code (requires black)
pip install black
black hiphops_hook/ scripts/

# Lint code (requires flake8)
pip install flake8
flake8 hiphops_hook/ scripts/

# Type checking (requires mypy)
pip install mypy
mypy hiphops_hook/

# Install all quality tools
pip install black flake8 mypy
```

## Publishing to PyPI

### Prerequisites

1. **PyPI Account**: Create account at [pypi.org](https://pypi.org)
2. **Trusted Publisher**: Configure trusted publisher for `hiphops-hook` on PyPI
3. **GitHub Environment**: Create `pypi` environment in repository settings

### Automated Publishing (Recommended)

Publishing is automated via GitHub Actions and triggered during the release process:

1. **Individual PyPI publish**: Use `publish-pypi.yml` workflow
2. **Automatic release publishing**: Both `publish-npm.yml` and `publish-pypi.yml` are triggered automatically during releases

The workflow automatically:
- Sets up Python environment
- Installs dependencies (skips binary download)
- Builds the package
- Publishes to PyPI using trusted publishing (no API tokens needed)

### Manual Publishing (Development)

For testing or manual releases:

```bash
# Install publishing tools
pip install build twine

# Build the package
python setup.py sdist

# Check the package (optional but recommended)
twine check dist/*

# Publish to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Publish to PyPI (production)
twine upload dist/*
```

### Version Management

- Python package version is synchronized with npm package
- Version is set in `pyproject.toml` and `setup.py`
- Must match the Hook binary version for compatibility

## Support

For issues and questions, please visit: https://github.com/hiphops-io/hook/issues
