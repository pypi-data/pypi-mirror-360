#!/bin/bash

# ARES MCP Server - Automated Setup and Run Script
# This script will set up the virtual environment, install dependencies, and run the server

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    echo -e "${GREEN}[ARES MCP]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Python 3 is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_error "Python $PYTHON_VERSION is installed, but Python $REQUIRED_VERSION or higher is required."
        exit 1
    fi
    
    print_message "Python $PYTHON_VERSION detected ✓"
}

# Create virtual environment if it doesn't exist
setup_venv() {
    if [ ! -d "venv" ]; then
        print_message "Creating virtual environment..."
        python3 -m venv venv
        print_message "Virtual environment created ✓"
    else
        print_message "Virtual environment already exists ✓"
    fi
}

# Activate virtual environment
activate_venv() {
    print_message "Activating virtual environment..."
    
    # Detect OS and use appropriate activation script
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows
        source venv/Scripts/activate
    else
        # macOS/Linux
        source venv/bin/activate
    fi
    
    print_message "Virtual environment activated ✓"
}

# Install or update dependencies
install_dependencies() {
    print_message "Checking dependencies..."
    
    # Check if requirements are already satisfied
    if pip freeze | grep -q "mcp" && pip freeze | grep -q "httpx"; then
        print_message "Core dependencies already installed ✓"
        
        # Ask if user wants to update
        read -p "Do you want to update dependencies? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_message "Updating dependencies..."
            pip install -U -r requirements.txt
            print_message "Dependencies updated ✓"
        fi
    else
        print_message "Installing dependencies..."
        pip install -r requirements.txt
        print_message "Dependencies installed ✓"
    fi
}

# Create .env file if it doesn't exist
setup_env() {
    if [ ! -f ".env" ]; then
        print_message "Creating .env configuration file..."
        cp .env.example .env
        print_message ".env file created ✓"
        print_warning "You can edit .env to customize server settings"
    else
        print_message "Configuration file already exists ✓"
    fi
}

# Run the server
run_server() {
    print_message "Starting ARES MCP Server..."
    echo
    echo "=========================================="
    echo "  ARES MCP Server is starting..."
    echo "  Press Ctrl+C to stop the server"
    echo "=========================================="
    echo
    
    # Run the server
    python -m ares_mcp_server.server
}

# Main execution
main() {
    echo "=========================================="
    echo "  ARES MCP Server Setup & Run"
    echo "=========================================="
    echo
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Run setup steps
    check_python
    setup_venv
    activate_venv
    install_dependencies
    setup_env
    
    echo
    print_message "Setup completed successfully!"
    echo
    
    # Ask if user wants to run the server
    read -p "Do you want to start the server now? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        run_server
    else
        print_message "Setup complete. To run the server later, use:"
        echo "  source venv/bin/activate"
        echo "  python -m ares_mcp_server.server"
    fi
}

# Handle errors
trap 'print_error "An error occurred. Setup failed."' ERR

# Run main function
main