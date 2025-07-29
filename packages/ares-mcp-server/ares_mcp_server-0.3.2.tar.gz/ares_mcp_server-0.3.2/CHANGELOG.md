# Changelog

## [0.3.2] - 2025-07-04

### Added
- Demo GIF showing ARES MCP Server in action within Claude Desktop
- Quick Start section in README for easier setup
- Enhanced example usage with emoji icons and clearer descriptions

### Changed
- Consolidated v3 implementation as the main version
- Removed `_v3` suffix from all files and classes
- Simplified imports and class names:
  - `AresApiV3Client` → `AresApiClient`
  - `AresMcpServerV3` → `AresMcpServer`
  - `create_ares_tools_v3` → `create_ares_tools`
- Fixed Pydantic deprecation warning (max_items → max_length)
- Improved README structure with better visual hierarchy

## [0.3.1] - 2025-07-04

### Fixed
- Corrected API base URL - removed `/v3` suffix that was causing 404 errors
- The correct base URL is: `https://ares.gov.cz/ekonomicke-subjekty-v-be/rest`

## [0.3.0] - 2025-07-04

### Changed - BREAKING
- **Complete rebuild** of the MCP server based on official ARES API documentation
- **Tool names now use Czech names** matching the API endpoints:
  - `ares_search_subject` → `vyhledat_ekonomicke_subjekty`
  - `ares_get_subject` → `najit_ekonomicky_subjekt`
  - `ares_search_in_registry` → `vyhledat_v_registru`
  - `ares_get_from_registry` → `najit_v_registru`
  - `ares_validate_ico` → `validovat_ico`
- **Parameter structure** now exactly matches API specification
- Main search uses proper filter structure with all available options

### Added
- Full address filter support in searches (municipality codes, street codes, etc.)
- Tax office filter (`financniUrad`) in main search
- Sort order support (`razeni`) with proper enum values
- New utility endpoints:
  - `vyhledat_ciselniky` - Search codebooks
  - `vyhledat_adresy` - Search standardized addresses
  - `vyhledat_notifikace` - Search notification batches
- Optional authentication support via `ARES_AUTH_TOKEN`
- Proper error messages in Czech/English

### Fixed
- Request body structure now properly matches API documentation
- ICO parameter correctly handled as array where required
- All numeric limits properly enforced (e.g., max 5 CZ-NACE codes)

## [0.2.1] - 2025-07-04

### Changed
- **IMPORTANT**: Default search (`ares_search_subject`) now uses POST endpoint `/ekonomicke-subjekty/vyhledat`
  - ICO parameter is converted to array format as required by the API
  - Request body includes `start` and `pocet` parameters for pagination
  - Response now includes pagination info: `total_found`, `returned`, `start`, `limit`
- Example usage updated to demonstrate correct parameter usage

### Fixed
- Default search now properly follows ARES API specification
- Search requests use correct parameter names (`obchodniJmeno` instead of query params)

## [0.2.0] - 2025-07-04

### Added
- **ARES API Support**: Updated base URL to use the new API endpoints
- **Advanced Search**: Added search with POST endpoint support
  - Multiple ICO search
  - Date range filtering (establishment/termination dates)
  - CZ-NACE economic activity code filtering
  - Legal form filtering
  - Active/inactive entity filtering
  - Pagination support (start, count parameters)
- **Registry-Specific Operations**: Added support for searching in specific registries
  - Get entity from specific registry (VR, RES, RZP, RPSH, RCNS, SZR, RS, CEU)
  - Search within specific registry with custom filters
  - List all available registries with descriptions
- **Enhanced Registry Information**: 
  - Added detailed Czech and English names for all registries
  - Registry descriptions now included in responses
  - Clear indication of what data each registry contains
- **Enhanced Data Models**: Added SearchFilters class for better type safety

### Changed
- Enhanced search response to include more fields (CZ-NACE codes, establishment/termination dates)
- Improved error handling and response formatting

### Fixed
- Fixed server initialization error with InitializationOptions
- Fixed rate limiter recursive call issue
- Improved global installation support

## [0.1.0] - 2025-07-04

### Initial Release
- Basic ARES API integration
- Simple search by ICO, name, or address
- Get detailed entity information
- ICO validation
- Rate limiting support
- MCP server implementation