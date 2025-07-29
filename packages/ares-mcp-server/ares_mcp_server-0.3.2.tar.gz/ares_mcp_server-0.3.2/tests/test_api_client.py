"""Tests for ARES API client."""

import pytest
import json
from unittest.mock import AsyncMock, patch

from ares_mcp_server.api_client import AresApiClient, RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter():
    """Test rate limiter functionality."""
    limiter = RateLimiter(max_requests=2, time_window=0.5)  # Shorter window for testing
    
    # First two requests should go through immediately
    await limiter.acquire()
    await limiter.acquire()
    
    # Third request should be delayed
    import time
    start = time.time()
    await limiter.acquire()
    elapsed = time.time() - start
    
    # Should have waited approximately 0.5 seconds
    assert elapsed >= 0.4  # Allow some margin


@pytest.mark.asyncio
async def test_vyhledat_ekonomicke_subjekty():
    """Test main search functionality."""
    client = AresApiClient()
    
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {
            "pocetCelkem": 1,
            "ekonomickeSubjekty": [
                {
                    "ico": "12345678",
                    "obchodniJmeno": "Test Company s.r.o.",
                    "sidlo": {
                        "nazevUlice": "Test Street",
                        "cisloDomovni": "123",
                        "nazevObce": "Prague",
                        "psc": "11000"
                    },
                    "pravniForma": "112",
                    "stavSubjektu": "AKTIVNI"
                }
            ]
        }
        
        result = await client.vyhledat_ekonomicke_subjekty({
            "obchodniJmeno": "Test Company",
            "pocet": 10
        })
        result_data = json.loads(result)
        
        assert result_data["pocetCelkem"] == 1
        assert result_data["ekonomickeSubjekty"][0]["ico"] == "12345678"
        
        mock_request.assert_called_once_with(
            "POST",
            "/ekonomicke-subjekty/vyhledat",
            json={
                "start": 0,
                "pocet": 10,
                "obchodniJmeno": "Test Company"
            }
        )


@pytest.mark.asyncio
async def test_najit_ekonomicky_subjekt():
    """Test get entity by ICO."""
    client = AresApiClient()
    
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {
            "ico": "12345678",
            "obchodniJmeno": "Test Company s.r.o.",
            "sidlo": {
                "nazevUlice": "Test Street",
                "cisloDomovni": "123",
                "nazevObce": "Prague"
            }
        }
        
        result = await client.najit_ekonomicky_subjekt("12345678")
        result_data = json.loads(result)
        
        assert result_data["ico"] == "12345678"
        assert result_data["obchodniJmeno"] == "Test Company s.r.o."
        
        mock_request.assert_called_once_with(
            "GET",
            "/ekonomicke-subjekty/12345678"
        )


@pytest.mark.asyncio
async def test_validovat_ico():
    """Test IČO validation."""
    client = AresApiClient()
    
    # Test invalid format
    result = await client.validovat_ico("123")
    result_data = json.loads(result)
    assert result_data["valid"] == False
    assert "8 číslic" in result_data["reason"]
    
    # Test valid format
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"ico": "00000019"}
        
        result = await client.validovat_ico("00000019")  # Valid checksum
        result_data = json.loads(result)
        
        assert result_data["validFormat"] == True
        assert result_data["exists"] == True
        assert result_data["valid"] == True


@pytest.mark.asyncio
async def test_vyhledat_v_registru():
    """Test registry-specific search."""
    client = AresApiClient()
    
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {
            "pocetCelkem": 1,
            "ekonomickeSubjekty": [{"ico": "12345678"}]
        }
        
        result = await client.vyhledat_v_registru("rzp", {
            "obchodniJmeno": "Test"
        })
        result_data = json.loads(result)
        
        assert "registry" in result_data
        assert result_data["registry"]["endpoint"] == "ekonomicke-subjekty-rzp"
        assert result_data["data"]["pocetCelkem"] == 1
        
        mock_request.assert_called_once_with(
            "POST",
            "/ekonomicke-subjekty-rzp/vyhledat",
            json={
                "start": 0,
                "pocet": 20,
                "obchodniJmeno": "Test"
            }
        )


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling."""
    client = AresApiClient()
    
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("API Error")
        
        result = await client.najit_ekonomicky_subjekt("12345678")
        result_data = json.loads(result)
        
        assert "error" in result_data
        assert "API Error" in result_data["error"]


@pytest.mark.asyncio
async def test_ico_array_conversion():
    """Test that ICO is properly converted to array in search."""
    client = AresApiClient()
    
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"pocetCelkem": 0, "ekonomickeSubjekty": []}
        
        # Test single ICO string
        await client.vyhledat_ekonomicke_subjekty({"ico": "12345678"})
        
        call_args = mock_request.call_args[1]["json"]
        assert call_args["ico"] == ["12345678"]
        
        # Test ICO array
        await client.vyhledat_ekonomicke_subjekty({"ico": ["12345678", "87654321"]})
        
        call_args = mock_request.call_args[1]["json"]
        assert call_args["ico"] == ["12345678", "87654321"]


if __name__ == "__main__":
    pytest.main([__file__])