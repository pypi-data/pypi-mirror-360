"""MCP tool definitions for ARES API."""

from typing import List
from mcp.types import Tool


def create_ares_tools() -> List[Tool]:
    """Create and return ARES API tools for MCP."""
    
    return [
        # Main search tool
        Tool(
            name="vyhledat_ekonomicke_subjekty",
            description="Vyhledání seznamu ekonomických subjektů ARES podle komplexního filtru (Search economic entities using complex filter)",
            inputSchema={
                "type": "object",
                "properties": {
                    "start": {
                        "type": "integer",
                        "description": "Starting position (default: 0)",
                        "minimum": 0
                    },
                    "pocet": {
                        "type": "integer",
                        "description": "Number of results (default: 20, max: 200)",
                        "minimum": 0,
                        "maximum": 200
                    },
                    "razeni": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Sort order: ICO, ICO_DESC, OBCHODNI_JMENO, OBCHODNI_JMENO_DESC"
                    },
                    "ico": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of IČO numbers to search"
                    },
                    "obchodniJmeno": {
                        "type": "string",
                        "description": "Business name to search"
                    },
                    "sidlo": {
                        "type": "object",
                        "description": "Address filter",
                        "properties": {
                            "kodCastiObce": {"type": "integer"},
                            "kodSpravnihoObvodu": {"type": "integer"},
                            "kodMestskeCastiObvodu": {"type": "integer"},
                            "kodUlice": {"type": "integer"},
                            "cisloDomovni": {"type": "integer"},
                            "kodObce": {"type": "integer"},
                            "cisloOrientacni": {"type": "integer"},
                            "cisloOrientacniPismeno": {"type": "string", "maxLength": 1},
                            "textovaAdresa": {"type": "string"}
                        }
                    },
                    "pravniForma": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Legal form codes"
                    },
                    "financniUrad": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tax office codes"
                    },
                    "czNace": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "CZ-NACE economic activity codes (max 5)",
                        "maxItems": 5
                    }
                }
            }
        ),
        
        # Get entity by ICO
        Tool(
            name="najit_ekonomicky_subjekt",
            description="Vyhledání ekonomického subjektu ARES podle zadaného IČA (Get economic entity by ICO)",
            inputSchema={
                "type": "object",
                "properties": {
                    "ico": {
                        "type": "string",
                        "description": "IČO (8 digits)",
                        "pattern": "^[0-9]{8}$"
                    }
                },
                "required": ["ico"]
            }
        ),
        
        # Registry search
        Tool(
            name="vyhledat_v_registru",
            description="Vyhledání v konkrétním registru (Search in specific registry)",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry": {
                        "type": "string",
                        "description": "Registry code",
                        "enum": ["vr", "res", "rzp", "nrpzs", "rpsh", "rcns", "szr", "rs", "ceu"]
                    },
                    "start": {
                        "type": "integer",
                        "description": "Starting position",
                        "minimum": 0
                    },
                    "pocet": {
                        "type": "integer",
                        "description": "Number of results",
                        "minimum": 0,
                        "maximum": 200
                    },
                    "razeni": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Sort order"
                    },
                    "ico": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of IČO numbers"
                    },
                    "obchodniJmeno": {
                        "type": "string",
                        "description": "Business name"
                    },
                    "sidlo": {
                        "type": "object",
                        "description": "Address filter"
                    },
                    "pravniForma": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Legal form codes"
                    }
                },
                "required": ["registry"]
            }
        ),
        
        # Get from registry by ICO
        Tool(
            name="najit_v_registru",
            description="Získání subjektu z konkrétního registru podle IČO (Get entity from specific registry by ICO)",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry": {
                        "type": "string",
                        "description": "Registry code: vr (Public), res (Economic), rzp (Trade), rpsh (Political), rcns (Church), szr (Agricultural), rs (School), ceu (Bankrupt)",
                        "enum": ["vr", "res", "rzp", "rpsh", "rcns", "szr", "rs", "ceu"]
                    },
                    "ico": {
                        "type": "string",
                        "description": "IČO (8 digits)",
                        "pattern": "^[0-9]{8}$"
                    }
                },
                "required": ["registry", "ico"]
            }
        ),
        
        # Validate ICO
        Tool(
            name="validovat_ico",
            description="Ověření validity IČO (Validate ICO format and existence)",
            inputSchema={
                "type": "object",
                "properties": {
                    "ico": {
                        "type": "string",
                        "description": "IČO to validate"
                    }
                },
                "required": ["ico"]
            }
        ),
        
        # Search codebooks
        Tool(
            name="vyhledat_ciselniky",
            description="Vyhledání v číselnících a názvnících (Search codebooks and nomenclatures)",
            inputSchema={
                "type": "object",
                "properties": {
                    "start": {"type": "integer", "minimum": 0},
                    "pocet": {"type": "integer", "minimum": 0, "maximum": 200},
                    "kod": {"type": "string"},
                    "nazev": {"type": "string"}
                }
            }
        ),
        
        # Search addresses
        Tool(
            name="vyhledat_adresy",
            description="Vyhledání standardizovaných adres (Search standardized addresses)",
            inputSchema={
                "type": "object",
                "properties": {
                    "start": {"type": "integer", "minimum": 0},
                    "pocet": {"type": "integer", "minimum": 0, "maximum": 200},
                    "obec": {"type": "string"},
                    "castObce": {"type": "string"},
                    "ulice": {"type": "string"}
                }
            }
        ),
        
        # Search notifications
        Tool(
            name="vyhledat_notifikace",
            description="Vyhledání notifikačních dávek (Search notification batches)",
            inputSchema={
                "type": "object",
                "properties": {
                    "start": {"type": "integer", "minimum": 0},
                    "pocet": {"type": "integer", "minimum": 0, "maximum": 200},
                    "datumOd": {"type": "string", "format": "date"},
                    "datumDo": {"type": "string", "format": "date"}
                }
            }
        )
    ]