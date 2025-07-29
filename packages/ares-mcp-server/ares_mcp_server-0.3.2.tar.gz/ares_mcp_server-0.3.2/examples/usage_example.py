"""Example usage of ARES MCP Server tools."""

import asyncio
import json
from ares_mcp_server.api_client import AresAPIClient


async def main():
    """Demonstrate ARES API client usage."""
    client = AresAPIClient()
    
    try:
        print("=== ARES API Client Examples ===\n")
        
        # Example 1: Search by company name
        print("1. Searching for companies with 'Microsoft' in name:")
        result = await client.search_subject(name="Microsoft")
        print(result)
        print()
        
        # Example 2: Search by ICO
        print("2. Searching for company with IČO 26168685:")
        result = await client.search_subject(ico="26168685")
        print(result)
        print()
        
        # Example 3: Advanced search with multiple ICOs
        print("3. Advanced search with multiple ICOs:")
        result = await client.search_advanced({
            "ico": ["26168685", "00000019"],
            "count": 10
        })
        print(result)
        print()
        
        # Example 4: Validate IČO
        print("4. Validating IČO 00000019:")
        result = await client.validate_ico("00000019")
        print(result)
        print()
        
        # Example 5: Get detailed information (will fail if IČO doesn't exist)
        print("5. Getting details for IČO 26168685:")
        result = await client.get_subject("26168685")
        result_data = json.loads(result)
        if "error" not in result_data:
            print(json.dumps(result_data, indent=2, ensure_ascii=False))
        else:
            print(result)
        print()
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())