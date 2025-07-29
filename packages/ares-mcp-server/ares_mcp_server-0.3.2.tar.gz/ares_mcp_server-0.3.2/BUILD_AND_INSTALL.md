# Build and Installation Guide for ARES MCP Server

## Installation Methods

### 1. Install from Source (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/ares-mcp-server.git
cd ares-mcp-server

# Install in editable/development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### 2. Install from Source (Production)

```bash
# Clone the repository
git clone https://github.com/yourusername/ares-mcp-server.git
cd ares-mcp-server

# Install the package
pip install .
```

### 3. Install from Git

```bash
# Install directly from GitHub
pip install git+https://github.com/yourusername/ares-mcp-server.git

# Install a specific branch or tag
pip install git+https://github.com/yourusername/ares-mcp-server.git@main
pip install git+https://github.com/yourusername/ares-mcp-server.git@v0.3.2
```

### 4. Build and Install from Wheel

```bash
# Build the package
pip install build
python -m build

# This creates files in the dist/ directory:
# - ares_mcp_server-0.3.2-py3-none-any.whl
# - ares-mcp-server-0.3.2.tar.gz

# Install from the wheel file
pip install dist/ares_mcp_server-0.3.2-py3-none-any.whl
```

## Testing the Installation

After installation, verify it works:

```bash
# Check if the command is available
which ares-mcp-server

# Run the server (requires MCP client)
ares-mcp-server

# Or use Python module directly
python -m ares_mcp_server.server
```

## Configuration

1. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

2. Edit `.env` to add your ARES API authentication token (if you have one):
```
ARES_AUTH_TOKEN=your_token_here
```

## Development Setup

For development, install with dev dependencies:

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
black --check .
mypy .

# Format code
black .
ruff check --fix .
```

## Publishing to PyPI

When ready to publish to PyPI:

```bash
# Build the distribution
pip install build twine
python -m build

# Check the distribution
twine check dist/*

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (for production)
twine upload dist/*
```

## Uninstallation

```bash
pip uninstall ares-mcp-server
```

## Troubleshooting

1. **Import errors**: Make sure you're in the correct virtual environment
2. **Command not found**: Ensure your Python scripts directory is in PATH
3. **Permission errors**: Use `pip install --user` or a virtual environment
4. **Build errors**: Ensure you have Python 3.8+ and pip is up to date

## Requirements

- Python 3.8 or higher
- pip (latest version recommended)
- Virtual environment (recommended)

## Platform Support

This package works on:
- Linux
- macOS  
- Windows

The package is distributed as a universal wheel that works on all platforms.