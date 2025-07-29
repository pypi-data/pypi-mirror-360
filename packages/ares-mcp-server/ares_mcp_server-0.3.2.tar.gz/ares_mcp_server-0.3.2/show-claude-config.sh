#!/bin/bash

echo "Add this configuration to your Claude Desktop config file:"
echo
echo "macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo
echo "{"
echo "  \"mcpServers\": {"
echo "    \"ares\": {"
echo "      \"command\": \"/opt/homebrew/bin/python3\","
echo "      \"args\": [\"-m\", \"ares_mcp_server.server\"],"
echo "      \"cwd\": \"$(pwd)\""
echo "    }"
echo "  }"
echo "}"
echo
echo "Current working directory: $(pwd)"
echo "Python path: /opt/homebrew/bin/python3"
echo
echo "Testing server startup..."
/opt/homebrew/bin/python3 -c "import ares_mcp_server.server; print('✓ Module imports successfully')" || echo "✗ Module import failed"