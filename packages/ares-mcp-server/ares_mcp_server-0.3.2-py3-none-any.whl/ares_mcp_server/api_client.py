"""ARES API client implementation with full endpoint support."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Union
from enum import Enum

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests: List[datetime] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait if necessary to respect rate limits."""
        while True:
            wait_time = 0
            async with self._lock:
                now = datetime.now()
                # Remove old requests outside the time window
                self.requests = [
                    req_time for req_time in self.requests
                    if now - req_time < timedelta(seconds=self.time_window)
                ]
                
                if len(self.requests) >= self.max_requests:
                    # Calculate wait time
                    oldest_request = self.requests[0]
                    wait_time = (oldest_request + timedelta(seconds=self.time_window) - now).total_seconds()
                    if wait_time <= 0:
                        # Window has passed, we can proceed
                        self.requests.append(now)
                        return
                    else:
                        logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                else:
                    self.requests.append(now)
                    return
            
            # Sleep outside the lock if we need to wait
            if wait_time > 0:
                await asyncio.sleep(wait_time)


class SortOrder(str, Enum):
    """Sort order options."""
    ICO_ASC = "ICO"
    ICO_DESC = "ICO_DESC"
    OBCHODNI_JMENO_ASC = "OBCHODNI_JMENO"
    OBCHODNI_JMENO_DESC = "OBCHODNI_JMENO_DESC"


class AddressFilter(BaseModel):
    """Address filter for searching."""
    kodCastiObce: Optional[int] = Field(None, ge=0, le=999999)
    kodSpravnihoObvodu: Optional[int] = Field(None, ge=0, le=999)
    kodMestskeCastiObvodu: Optional[int] = Field(None, ge=0, le=999999)
    kodUlice: Optional[int] = Field(None, ge=0, le=9999999)
    cisloDomovni: Optional[int] = Field(None, ge=0, le=9999)
    kodObce: Optional[int] = Field(None, ge=0, le=999999)
    cisloOrientacni: Optional[int] = Field(None, ge=0, le=999)
    cisloOrientacniPismeno: Optional[str] = Field(None, max_length=1)
    textovaAdresa: Optional[str] = Field(None, description="Text address for searching")


class ComplexSearchFilter(BaseModel):
    """Complex search filter for economic entities."""
    start: int = Field(0, ge=0, description="Starting position")
    pocet: int = Field(20, ge=0, le=200, description="Number of results")
    razeni: Optional[List[str]] = Field(None, description="Sort order")
    ico: Optional[List[str]] = Field(None, description="List of ICOs")
    obchodniJmeno: Optional[str] = Field(None, description="Business name")
    sidlo: Optional[AddressFilter] = Field(None, description="Address filter")
    pravniForma: Optional[List[str]] = Field(None, description="Legal form codes")
    financniUrad: Optional[List[str]] = Field(None, description="Tax office codes")
    czNace: Optional[List[str]] = Field(None, description="CZ-NACE codes", max_length=5)


class BasicSearchFilter(BaseModel):
    """Basic search filter for registries."""
    start: int = Field(0, ge=0)
    pocet: int = Field(20, ge=0, le=200)
    razeni: Optional[List[str]] = Field(None)
    ico: Optional[List[str]] = Field(None)
    obchodniJmeno: Optional[str] = Field(None)
    sidlo: Optional[AddressFilter] = Field(None)
    pravniForma: Optional[List[str]] = Field(None)


class AresApiClient:
    """Client for ARES API with full endpoint support."""
    
    BASE_URL = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest"
    
    # Registry information
    REGISTRIES = {
        "vr": {
            "name": "Veřejné rejstříky",
            "name_en": "Public Registers",
            "endpoint": "ekonomicke-subjekty-vr"
        },
        "res": {
            "name": "Registr ekonomických subjektů",
            "name_en": "Economic Entities Register",
            "endpoint": "ekonomicke-subjekty-res"
        },
        "rzp": {
            "name": "Registr živnostenského podnikání",
            "name_en": "Trade Licensing Register",
            "endpoint": "ekonomicke-subjekty-rzp"
        },
        "nrpzs": {
            "name": "Národní registr poskytovatelů zdravotních služeb",
            "name_en": "National Healthcare Providers Register",
            "endpoint": "ekonomicke-subjekty-nrpzs"
        },
        "rpsh": {
            "name": "Registr politických stran a hnutí",
            "name_en": "Political Parties and Movements Register",
            "endpoint": "ekonomicke-subjekty-rpsh"
        },
        "rcns": {
            "name": "Registr církví a náboženských společenství",
            "name_en": "Churches and Religious Societies Register",
            "endpoint": "ekonomicke-subjekty-rcns"
        },
        "szr": {
            "name": "Společný zemědělský registr",
            "name_en": "Joint Agricultural Register",
            "endpoint": "ekonomicke-subjekty-szr"
        },
        "rs": {
            "name": "Registr škol",
            "name_en": "School Register",
            "endpoint": "ekonomicke-subjekty-rs"
        },
        "ceu": {
            "name": "Centrální evidence úpadců",
            "name_en": "Central Bankrupts Register",
            "endpoint": "ekonomicke-subjekty-ceu"
        }
    }
    
    def __init__(self, 
                 rate_limit_requests: int = 100, 
                 rate_limit_window: int = 60,
                 auth_token: Optional[str] = None):
        """Initialize ARES API client.
        
        Args:
            rate_limit_requests: Maximum requests per time window
            rate_limit_window: Time window in seconds
            auth_token: Optional authentication token
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "ARES-MCP-Server/0.3.2"
        }
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
            
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=30.0
        )
        self.rate_limiter = RateLimiter(rate_limit_requests, rate_limit_window)
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make rate-limited HTTP request to ARES API."""
        await self.rate_limiter.acquire()
        
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"text": response.text}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            error_detail = f"HTTP {e.response.status_code}"
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_detail += f": {error_json['detail']}"
            except:
                if e.response.text:
                    error_detail += f": {e.response.text}"
            raise Exception(f"ARES API error: {error_detail}")
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise
    
    # Main economic entities endpoints
    
    async def vyhledat_ekonomicke_subjekty(self, filters: Dict[str, Any]) -> str:
        """Search economic entities using complex filter.
        
        This is the main search endpoint for ARES.
        """
        # Build request body
        body = ComplexSearchFilter(
            start=filters.get("start", 0),
            pocet=filters.get("pocet", 20)
        )
        
        if filters.get("razeni"):
            body.razeni = filters["razeni"]
        if filters.get("ico"):
            body.ico = filters["ico"] if isinstance(filters["ico"], list) else [filters["ico"]]
        if filters.get("obchodniJmeno"):
            body.obchodniJmeno = filters["obchodniJmeno"]
        if filters.get("sidlo"):
            body.sidlo = AddressFilter(**filters["sidlo"])
        if filters.get("pravniForma"):
            body.pravniForma = filters["pravniForma"]
        if filters.get("financniUrad"):
            body.financniUrad = filters["financniUrad"]
        if filters.get("czNace"):
            body.czNace = filters["czNace"]
        
        try:
            result = await self._make_request(
                "POST",
                "/ekonomicke-subjekty/vyhledat",
                json=body.model_dump(exclude_none=True)
            )
            
            # Format response
            if isinstance(result, dict):
                return json.dumps({
                    "pocetCelkem": result.get("pocetCelkem", 0),
                    "ekonomickeSubjekty": result.get("ekonomickeSubjekty", [])
                }, indent=2, ensure_ascii=False)
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    async def najit_ekonomicky_subjekt(self, ico: str) -> str:
        """Get economic entity by ICO."""
        try:
            result = await self._make_request(
                "GET",
                f"/ekonomicke-subjekty/{ico}"
            )
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    # Registry-specific endpoints
    
    async def vyhledat_v_registru(self, registry: str, filters: Dict[str, Any]) -> str:
        """Search in specific registry."""
        if registry not in self.REGISTRIES:
            return json.dumps({
                "error": f"Unknown registry: {registry}",
                "available": list(self.REGISTRIES.keys())
            }, indent=2)
        
        endpoint = f"/{self.REGISTRIES[registry]['endpoint']}/vyhledat"
        
        # Build request body
        body = BasicSearchFilter(
            start=filters.get("start", 0),
            pocet=filters.get("pocet", 20)
        )
        
        if filters.get("razeni"):
            body.razeni = filters["razeni"]
        if filters.get("ico"):
            body.ico = filters["ico"] if isinstance(filters["ico"], list) else [filters["ico"]]
        if filters.get("obchodniJmeno"):
            body.obchodniJmeno = filters["obchodniJmeno"]
        if filters.get("sidlo"):
            body.sidlo = AddressFilter(**filters["sidlo"])
        if filters.get("pravniForma"):
            body.pravniForma = filters["pravniForma"]
        
        try:
            result = await self._make_request(
                "POST",
                endpoint,
                json=body.model_dump(exclude_none=True)
            )
            
            return json.dumps({
                "registry": self.REGISTRIES[registry],
                "data": result
            }, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    async def najit_v_registru(self, registry: str, ico: str) -> str:
        """Get entity from specific registry by ICO."""
        if registry not in self.REGISTRIES:
            return json.dumps({
                "error": f"Unknown registry: {registry}",
                "available": list(self.REGISTRIES.keys())
            }, indent=2)
        
        endpoint = f"/{self.REGISTRIES[registry]['endpoint']}/{ico}"
        
        try:
            result = await self._make_request("GET", endpoint)
            
            return json.dumps({
                "registry": self.REGISTRIES[registry],
                "data": result
            }, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    # Utility endpoints
    
    async def vyhledat_ciselniky(self, filters: Dict[str, Any]) -> str:
        """Search codebooks/nomenclatures."""
        try:
            result = await self._make_request(
                "POST",
                "/ciselniky-nazevniky/vyhledat",
                json=filters
            )
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    async def vyhledat_adresy(self, filters: Dict[str, Any]) -> str:
        """Search standardized addresses."""
        try:
            result = await self._make_request(
                "POST",
                "/standardizovane-adresy/vyhledat",
                json=filters
            )
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    async def vyhledat_notifikace(self, filters: Dict[str, Any]) -> str:
        """Search notification batches."""
        try:
            result = await self._make_request(
                "POST",
                "/ekonomicke-subjekty-notifikace/vyhledat",
                json=filters
            )
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    async def validovat_ico(self, ico: str) -> str:
        """Validate ICO format and existence."""
        try:
            # ICO validation algorithm
            if not ico or not ico.isdigit() or len(ico) != 8:
                return json.dumps({
                    "valid": False,
                    "reason": "IČO musí být přesně 8 číslic"
                }, indent=2)
            
            # Check modulo 11 algorithm
            weights = [8, 7, 6, 5, 4, 3, 2]
            total = sum(int(ico[i]) * weights[i] for i in range(7))
            check_digit = (11 - (total % 11)) % 10
            
            is_valid_format = check_digit == int(ico[7])
            
            # Check if exists
            exists = False
            if is_valid_format:
                try:
                    await self._make_request("GET", f"/ekonomicke-subjekty/{ico}")
                    exists = True
                except:
                    exists = False
            
            return json.dumps({
                "ico": ico,
                "validFormat": is_valid_format,
                "exists": exists,
                "valid": is_valid_format and exists
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()