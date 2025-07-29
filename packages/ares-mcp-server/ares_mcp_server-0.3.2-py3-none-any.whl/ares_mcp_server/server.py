"""MCP server implementation for ARES API."""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from . import __version__
from .api_client import AresApiClient
from .tools import create_ares_tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AresMcpServer:
    """MCP Server for ARES API."""
    
    def __init__(self):
        self.server = Server("ares-mcp-server")
        
        # Get optional auth token from environment
        auth_token = os.getenv("ARES_AUTH_TOKEN")
        
        # Initialize API client
        self.api_client = AresApiClient(
            rate_limit_requests=int(os.getenv("ARES_RATE_LIMIT_REQUESTS", "100")),
            rate_limit_window=int(os.getenv("ARES_RATE_LIMIT_WINDOW", "60")),
            auth_token=auth_token
        )
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP protocol handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Return available ARES API tools."""
            return create_ares_tools()
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]] = None) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Handle tool execution requests."""
            if arguments is None:
                arguments = {}
            
            try:
                # Main endpoints
                if name == "vyhledat_ekonomicke_subjekty":
                    result = await self.api_client.vyhledat_ekonomicke_subjekty(arguments)
                    return [TextContent(type="text", text=result)]
                
                elif name == "najit_ekonomicky_subjekt":
                    result = await self.api_client.najit_ekonomicky_subjekt(
                        ico=arguments["ico"]
                    )
                    return [TextContent(type="text", text=result)]
                
                # Registry endpoints
                elif name == "vyhledat_v_registru":
                    registry = arguments.pop("registry")
                    result = await self.api_client.vyhledat_v_registru(
                        registry=registry,
                        filters=arguments
                    )
                    return [TextContent(type="text", text=result)]
                
                elif name == "najit_v_registru":
                    result = await self.api_client.najit_v_registru(
                        registry=arguments["registry"],
                        ico=arguments["ico"]
                    )
                    return [TextContent(type="text", text=result)]
                
                # Utility endpoints
                elif name == "validovat_ico":
                    result = await self.api_client.validovat_ico(
                        ico=arguments["ico"]
                    )
                    return [TextContent(type="text", text=result)]
                
                elif name == "vyhledat_ciselniky":
                    result = await self.api_client.vyhledat_ciselniky(arguments)
                    return [TextContent(type="text", text=result)]
                
                elif name == "vyhledat_adresy":
                    result = await self.api_client.vyhledat_adresy(arguments)
                    return [TextContent(type="text", text=result)]
                
                elif name == "vyhledat_notifikace":
                    result = await self.api_client.vyhledat_notifikace(arguments)
                    return [TextContent(type="text", text=result)]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        logger.info("Starting ARES MCP Server...")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ares-mcp-server",
                    server_version=__version__,
                    capabilities={}
                )
            )


def main():
    """Main entry point."""
    server = AresMcpServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()