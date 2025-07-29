#!/bin/bash

# ARES MCP Server - Global Installation Script
# This script installs the MCP server in the global Python environment

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_message() {
    echo -e "${GREEN}[ARES MCP]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "=========================================="
echo "  ARES MCP Server Global Installation"
echo "=========================================="
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_message "Python $PYTHON_VERSION detected"

# Warning about global installation
print_warning "This will install packages in your global Python environment!"
print_warning "This may affect other Python applications on your system."
echo
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_message "Installation cancelled."
    exit 0
fi

# Check for pip
if ! python3 -m pip --version &> /dev/null; then
    print_error "pip is not installed. Please install pip first."
    exit 1
fi

# Install only the core dependencies needed to run the server
print_message "Installing core dependencies globally..."

# On macOS with Homebrew Python, you might need --break-system-packages
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_warning "Detected macOS. May need to use --break-system-packages flag."
    python3 -m pip install --break-system-packages \
        mcp>=1.0.0 \
        httpx>=0.24.0 \
        pydantic>=2.0.0 \
        python-dotenv>=1.0.0 || \
    python3 -m pip install \
        mcp>=1.0.0 \
        httpx>=0.24.0 \
        pydantic>=2.0.0 \
        python-dotenv>=1.0.0
else
    python3 -m pip install \
        mcp>=1.0.0 \
        httpx>=0.24.0 \
        pydantic>=2.0.0 \
        python-dotenv>=1.0.0
fi

print_message "Core dependencies installed ✓"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_message "Creating .env configuration file..."
    cp .env.example .env
    print_message ".env file created ✓"
fi

echo
print_message "Global installation completed!"
echo
print_message "To use with Claude Desktop, add this to your config:"
echo
echo "macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "Windows: %APPDATA%\Claude\claude_desktop_config.json"
echo
echo '{'
echo '  "mcpServers": {'
echo '    "ares": {'
echo '      "command": "python3",'
echo '      "args": ["-m", "ares_mcp_server.server"],'
echo "      \"cwd\": \"$(pwd)\""
echo '    }'
echo '  }'
echo '}'
echo
print_warning "Note: Using global Python (python3) instead of virtual environment"
print_message "You can test the server with: python3 -m ares_mcp_server.server"