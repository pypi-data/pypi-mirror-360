# NoETL PyPI Publishing Guide

This guide provides comprehensive instructions for publishing the NoETL package to PyPI, including the React UI components that are served alongside the FastAPI server.

**Note**: This project uses `uv` for dependency management. All build tools must be installed using `uv` commands.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Build Configuration](#build-configuration)
4. [UI Build Process](#ui-build-process)
5. [Package Building](#package-building)
6. [Publishing to PyPI](#publishing-to-pypi)
7. [Verification](#verification)
8. [Automation Scripts](#automation-scripts)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

1. **Python 3.11+** with uv package manager
2. **Node.js 18+** and npm (for React UI, optional)
3. **PyPI Account** with API token
4. **Build tools** (installed via uv):
   ```bash
   uv add --dev build twine
   ```

### Environment Setup

1. Create a PyPI account at https://pypi.org/account/register/
2. Generate an API token at https://pypi.org/manage/account/token/
3. Configure the token:
   ```bash
   # Create ~/.pypirc file
   cat > ~/.pypirc << EOF
   [distutils]
   index-servers = pypi testpypi

   [pypi]
   username = __token__
   password = pypi-YOUR_API_TOKEN_HERE

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-YOUR_TEST_API_TOKEN_HERE
   EOF
   
   chmod 600 ~/.pypirc
   ```

## Project Structure

The NoETL package includes both Python backend and React UI components:

```
noetl/
├── pyproject.toml          # Package configuration
├── setup.py               # Setuptools configuration  
├── MANIFEST.in            # Package manifest
├── README.md              # Package documentation
├── uv.lock                # UV dependency lock file
├── noetl/                 # Python package
│   ├── __init__.py
│   ├── server.py          # FastAPI server
│   └── ...
├── ui/                    # React UI components
│   ├── __init__.py
│   ├── static/            # Built React assets
│   │   ├── css/
│   │   └── js/
│   └── templates/         # HTML templates
└── scripts/               # Build and publish scripts
```

## Important: UV Dependency Management

This project uses `uv` for dependency management instead of traditional pip/venv. This means:

- Use `uv add` instead of `pip install`
- Use `uv add --dev` for development dependencies
- The virtual environment is managed by `uv`
- Build tools must be installed via `uv add --dev build twine`

## Build Configuration

### 1. Update pyproject.toml

The `pyproject.toml` file is configured for PyPI publishing with UV support:

```toml
[project]
name = "noetl"
version = "0.1.18"
description = "Not Only Extract Transform Load. A framework to build and run data pipelines and workflows."
# ... other configuration
```

### 2. MANIFEST.in Configuration

Ensure all UI assets are included in the package:

```
include README.md
include LICENSE
include CHANGELOG.md
include pyproject.toml
recursive-include noetl *.py
recursive-include ui/static *
recursive-include ui/templates *
include ui/__init__.py
global-exclude __pycache__
global-exclude *.py[co]
global-exclude .DS_Store
global-exclude *.so
exclude .gitignore
exclude .env*
exclude docker-compose*.yml
exclude Dockerfile*
exclude uv.lock
```

### 3. Setup.py Integration

The `setup.py` file includes UI assets and syncs with pyproject.toml:

```python
from setuptools import setup, find_packages
from pathlib import Path

def get_version():
    import re
    pyproject_file = Path(__file__).parent / 'pyproject.toml'
    if pyproject_file.exists():
        content = pyproject_file.read_text()
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    return "0.1.18"  # fallback version

setup(
    name="noetl",
    version=get_version(),
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'ui': ['static/**/*', 'templates/**/*', '**/*'],
        'noetl': ['*.py'],
    },
    # ... other configuration
)
```

## UI Build Process

### 1. Existing UI Assets

The project includes pre-built UI assets in the `ui/` directory:
- `ui/static/css/` - Stylesheets
- `ui/static/js/` - JavaScript files  
- `ui/templates/` - HTML templates

### 2. UI Integration with FastAPI

The UI assets are automatically served by the FastAPI server in `noetl/main.py`:

```python
# UI assets are mounted at /static and served at /ui endpoint
app.mount("/static", StaticFiles(directory=str(ui_static_dir)), name="static")
templates = Jinja2Templates(directory=str(ui_templates_dir))
```

## Package Building

### 1. Install Build Dependencies

**Critical**: Use `uv` to install build tools:

```bash
# Install build dependencies using UV
uv add --dev build twine
```

### 2. Version Management

Update the version in `pyproject.toml`:

```bash
# Use the version update script
./scripts/update_version.py 0.1.19
```

### 3. Clean Previous Builds

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/
```

### 4. Build the Package

```bash
# Build source distribution and wheel
python -m build
```

This creates:
- `dist/noetl-0.1.19.tar.gz` (source distribution)
- `dist/noetl-0.1.19-py3-none-any.whl` (wheel)

## Publishing to PyPI

### 1. Validate Package

```bash
# Validate the built packages
python -m twine check dist/*
```

### 2. Test on TestPyPI First (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ noetl
```

### 3. Publish to PyPI

```bash
# Upload to PyPI with verbose output
python -m twine upload --verbose dist/*

# Verify upload
pip install noetl
```

### 4. Automated Publishing

Use the updated scripts that support UV:

```bash
# Interactive publishing workflow (recommended)
./scripts/interactive_publish.sh

# Direct publishing script
./scripts/publish_to_pypi.sh 0.1.19
```

## Verification

### 1. Installation Verification

```bash
# Create a new virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from PyPI
pip install noetl

# Test the installation
python -c "import noetl; print('NoETL installed successfully')"

# Test the server with UI
noetl server --port 8082
# Visit http://localhost:8082/ui to verify UI is working
```

### 2. Package Contents Verification

```bash
# Check package contents
pip show -f noetl

# Verify UI assets are included
python -c "
import ui
from pathlib import Path
ui_dir = Path(ui.__file__).parent
print('UI directory exists:', ui_dir.exists())
print('Static files:', list((ui_dir / 'static').glob('**/*')))
print('Templates:', list((ui_dir / 'templates').glob('**/*')))
"
```

## Automation Scripts

The following scripts automate the publishing process and support UV dependency management:

1. **`scripts/build_ui.sh`** - Builds/validates the React UI assets
2. **`scripts/update_version.py`** - Updates package version in pyproject.toml
3. **`scripts/build_package.sh`** - Builds the Python package with UV support
4. **`scripts/publish_to_pypi.sh`** - Publishes to PyPI with UV environment
5. **`scripts/interactive_publish.sh`** - Interactive publishing workflow

### Usage Examples

```bash
# Full automated release (recommended)
./scripts/interactive_publish.sh

# Manual step-by-step with UV support
uv add --dev build twine  # Install build tools
./scripts/update_version.py 0.1.19
python -m build
python -m twine upload --verbose dist/*
```

## Troubleshooting

### Common Issues

#### 1. Build Module Not Found

**Problem**: `/path/to/.venv/bin/python3: No module named build`

**Solution**: Install build tools using UV:
```bash
uv add --dev build twine
```

#### 2. UV vs Pip Conflicts

**Problem**: Scripts trying to use pip in UV-managed environment

**Solution**: Always use UV commands:
```bash
# Wrong
pip install build twine

# Correct  
uv add --dev build twine
```

#### 3. UI Assets Not Included

**Problem**: UI files not found after installation

**Solution**: 
- Verify `MANIFEST.in` includes UI files
- Check `package_data` in `setup.py`
- Rebuild the package

#### 4. Version Conflicts

**Problem**: Version already exists on PyPI

**Solution**:
```bash
# Update version
./scripts/update_version.py 0.1.20
# Rebuild and republish
```

#### 5. Authentication Issues

**Problem**: Upload fails with authentication error

**Solution**:
- Verify PyPI API token in `~/.pypirc`
- Check token has upload permissions
- Regenerate API token if needed

### Debug Commands

```bash
# Check UV environment
uv pip list

# Validate package contents
tar -tzf dist/noetl-*.tar.gz | head -20

# Validate package metadata
python -m twine check dist/*

# Verbose upload with debug info
python -m twine upload --verbose dist/*

# Check what Python is being used
which python
python -c "import sys; print(sys.executable)"
```

### Successful Publication Indicators

✅ **Build completed**: Both `.tar.gz` and `.whl` files created  
✅ **Validation passed**: `twine check` shows no errors  
✅ **Upload successful**: `200 OK` responses from PyPI  
✅ **Package available**: Can install with `pip install noetl==VERSION`  
✅ **UI works**: Server starts and UI accessible at `/ui` endpoint  

## Best Practices

### 1. Version Management

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update CHANGELOG.md for each release
- Tag releases in Git: `git tag v0.1.19`

### 2. Testing

- Always test on TestPyPI first
- Verify installation in clean environment
- Test UI functionality after installation
- Verify all playbook examples work

### 3. Documentation

- Keep README.md updated
- Include installation and usage instructions
- Document UI features and endpoints
- Update example documentation

### 4. Security

- Use API tokens, never passwords
- Rotate tokens regularly
- Use separate tokens for TestPyPI and PyPI
- Keep credentials in `~/.pypirc` with proper permissions (600)

## UV-Specific Considerations

### Dependency Management

```bash
# Add production dependencies
uv add fastapi uvicorn

# Add development dependencies  
uv add --dev build twine pytest

# Update dependencies
uv lock

# Install from lock file
uv sync
```

### Environment Isolation

UV creates isolated environments automatically. Publishing scripts work within this environment without additional virtual environment setup.

## Continuous Integration

For GitHub Actions with UV support:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install UV
      run: pip install uv
    - name: Install dependencies
      run: uv sync
    - name: Build package
      run: |
        uv add --dev build
        python -m build
    - name: Publish to PyPI
      run: |
        uv add --dev twine
        python -m twine upload dist/*
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

## Support

For issues related to PyPI publishing:

1. Check the [PyPI documentation](https://packaging.python.org/)
2. Review the [twine documentation](https://twine.readthedocs.io/)
3. Consult the [UV documentation](https://docs.astral.sh/uv/)
4. Check [setuptools documentation](https://setuptools.pypa.io/)

For NoETL-specific issues, refer to the main documentation or create an issue in the project repository.
