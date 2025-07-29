# ARES MCP Server

A Model Context Protocol (MCP) server that provides access to the Czech ARES (Administrativní registr ekonomických subjektů) API - the official business registry of the Czech Republic.

## Demo

See the ARES MCP Server in action within Claude Desktop:

![ARES MCP Server Demo](docs/images/ares-mcp-demo.gif)

The demo shows:
- 🔍 Searching for companies by name (e.g., "AiMingle")
- 📋 Getting detailed company information by IČO
- ✅ Validating IČO numbers
- 🏢 Searching in specific registries
- 📊 Using advanced filters (legal form, CZ-NACE codes, etc.)

## Quick Start

1. **Install the server:**
   ```bash
   git clone https://github.com/yourusername/ares-mcp-server.git
   cd ares-mcp-server
   pip install -e .
   ```

2. **Add to Claude Desktop config:**
   ```json
   {
     "mcpServers": {
       "ares": {
         "command": "python3",
         "args": ["-m", "ares_mcp_server.server"],
         "cwd": "/path/to/ares-mcp-server"
       }
     }
   }
   ```

3. **Restart Claude Desktop and start searching Czech companies!**

## Features

- Full implementation of ARES API endpoints
- Complex search with multiple filters (IČO, name, address, legal form, CZ-NACE, etc.)
- Registry-specific searches (Public Registry, Trade Registry, Schools, etc.)
- Built-in rate limiting
- Optional authentication support
- Proper Czech naming following the API documentation

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/ares-mcp-server.git
cd ares-mcp-server

# Run automated setup
./run.sh  # macOS/Linux
# or
run.bat   # Windows
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create configuration
cp .env.example .env
```

## Configuration

Configure the server using environment variables in `.env`:

```bash
# Rate limiting (default: 100 requests per 60 seconds)
ARES_RATE_LIMIT_REQUESTS=100
ARES_RATE_LIMIT_WINDOW=60

# Optional authentication token
ARES_AUTH_TOKEN=your_token_here

# Logging level
LOG_LEVEL=INFO
```

## Claude Desktop Configuration

Add to your Claude Desktop configuration file:

### macOS
`~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
`%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ares": {
      "command": "python3",
      "args": ["-m", "ares_mcp_server.server"],
      "cwd": "/path/to/ares-mcp-server"
    }
  }
}
```

## Available Tools

### 1. vyhledat_ekonomicke_subjekty
**Main search tool** - Search economic entities using complex filters

Parameters:
- `start` (optional): Starting position (default: 0)
- `pocet` (optional): Number of results (default: 20, max: 200)
- `razeni` (optional): Sort order array ["ICO", "OBCHODNI_JMENO_DESC", etc.]
- `ico` (optional): Array of IČO numbers to search
- `obchodniJmeno` (optional): Business name
- `sidlo` (optional): Address filter object
  - `kodCastiObce`: District code
  - `kodObce`: Municipality code
  - `textovaAdresa`: Text address search
  - etc.
- `pravniForma` (optional): Array of legal form codes
- `financniUrad` (optional): Array of tax office codes
- `czNace` (optional): Array of CZ-NACE activity codes (max 5)

### 2. najit_ekonomicky_subjekt
Get detailed information about a specific economic entity

Parameters:
- `ico` (required): IČO number (8 digits)

### 3. vyhledat_v_registru
Search in a specific registry

Parameters:
- `registry` (required): Registry code
  - `vr`: Veřejné rejstříky (Public Registers)
  - `res`: Registr ekonomických subjektů (Economic Entities)
  - `rzp`: Registr živnostenského podnikání (Trade Licensing)
  - `nrpzs`: Národní registr poskytovatelů zdravotních služeb (Healthcare)
  - `rpsh`: Registr politických stran a hnutí (Political Parties)
  - `rcns`: Registr církví a náboženských společenství (Churches)
  - `szr`: Společný zemědělský registr (Agricultural)
  - `rs`: Registr škol (Schools)
  - `ceu`: Centrální evidence úpadců (Bankrupts)
- Plus same search parameters as main search

### 4. najit_v_registru
Get entity from specific registry by IČO

Parameters:
- `registry` (required): Registry code
- `ico` (required): IČO number

### 5. validovat_ico
Validate IČO format and check existence

Parameters:
- `ico` (required): IČO to validate

### 6. vyhledat_ciselniky
Search codebooks and nomenclatures

### 7. vyhledat_adresy
Search standardized addresses

### 8. vyhledat_notifikace
Search notification batches

## Example Usage in Claude Desktop

Once configured, you can interact with ARES data directly in Claude Desktop. Here are some common use cases:

### 🔍 Basic Company Search
Ask Claude: "Search for companies with name containing 'Microsoft' in ARES"

Claude will use:
```
vyhledat_ekonomicke_subjekty with:
- obchodniJmeno: "Microsoft"
- pocet: 10
```

### 📊 Get Company Details
Ask Claude: "Get details for company with IČO 26168685"

Claude will use:
```
najit_ekonomicky_subjekt with:
- ico: "26168685"
```

### ✅ Validate IČO
Ask Claude: "Is IČO 26168685 valid?"

Claude will use:
```
validovat_ico with:
- ico: "26168685"
```

### 🏭 Industry-Specific Search
Ask Claude: "Find all restaurants in Prague"

Claude will use:
```
vyhledat_ekonomicke_subjekty with:
- czNace: ["56"]  # Restaurants and food service
- sidlo: { "nazevObce": "Praha" }
- pocet: 50
```

### 📋 Search Multiple Companies
Ask Claude: "Get info for companies with IČO 26168685 and 00000019"

Claude will use:
```
vyhledat_ekonomicke_subjekty with:
- ico: ["26168685", "00000019"]
```

### 🏢 Registry-Specific Search
Ask Claude: "Search for software companies in the trade registry"

Claude will use:
```
vyhledat_v_registru with:
- registry: "rzp"
- obchodniJmeno: "software"
```

## Development

### Project Structure
```
ares-mcp-server/
├── ares_mcp_server/
│   ├── __init__.py
│   ├── server.py           # Entry point
│   ├── server_v3.py        # Main server implementation
│   ├── api_client_v3.py    # ARES API v3 client
│   └── tools_v3.py         # Tool definitions
├── tests/
├── examples/
├── requirements.txt
├── pyproject.toml
└── README.md
```

### Running Tests
```bash
source venv/bin/activate
pytest tests/
```

## API Documentation

This server implements the official ARES API. For detailed API documentation, see:
- [ARES Swagger UI](https://ares.gov.cz/swagger-ui/)
- [ARES Website](https://ares.gov.cz/)
- API Base URL: `https://ares.gov.cz/ekonomicke-subjekty-v-be/rest`

## Changelog

### v0.3.0 (2025-07-04)
- Complete rebuild based on ARES API v3 specification
- Tool names now match API endpoints (Czech names)
- Proper parameter structure matching API documentation
- Support for all search filters including address components
- Added registry-specific search endpoints
- Added utility endpoints (codebooks, addresses, notifications)

## License

MIT License

## Support

For issues or questions:
- Create an issue on GitHub
- Check the ARES API documentation

## Acknowledgments

This server integrates with the Czech ARES API provided by the Ministry of Finance of the Czech Republic.