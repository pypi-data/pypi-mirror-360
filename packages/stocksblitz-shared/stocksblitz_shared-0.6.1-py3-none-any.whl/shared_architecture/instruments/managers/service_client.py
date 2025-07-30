"""
Service client for instrument management service
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import json
from decimal import Decimal

from ..core.instrument_key import InstrumentKey
from ..core.enums import AssetProductType, Exchange
from ..core.exceptions import (
    InstrumentNotFoundError, ServiceUnavailableError, 
    ValidationError, ConversionError
)


class InstrumentServiceClient:
    """
    Client for communicating with the Instrument Management Service
    """
    
    def __init__(self, base_url: str = "http://localhost:8008", 
                 timeout: int = 30, max_retries: int = 3):
        """
        Initialize service client
        
        Args:
            base_url: Base URL of the instrument service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        
        # HTTP client with connection pooling
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
    
    async def get_instrument(self, instrument_key: str) -> Optional[InstrumentKey]:
        """
        Get instrument by key
        
        Args:
            instrument_key: Instrument key string
            
        Returns:
            InstrumentKey if found, None otherwise
        """
        try:
            url = f"/api/v1/instruments/{instrument_key}"
            response = await self._make_request("GET", url)
            
            if response.status_code == 404:
                return None
            elif response.status_code == 200:
                data = response.json()
                return InstrumentKey.from_dict(data)
            else:
                response.raise_for_status()
                
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error getting instrument {instrument_key}: {e}")
            raise ServiceUnavailableError(f"Service unavailable: {e}")
        except Exception as e:
            self.logger.error(f"Error getting instrument {instrument_key}: {e}")
            raise
    
    async def validate_instrument(self, instrument_key: str) -> Dict[str, Any]:
        """
        Validate instrument key
        
        Args:
            instrument_key: Instrument key string
            
        Returns:
            Validation result with details
        """
        try:
            url = "/api/v1/instruments/validate"
            payload = {"instrument_key": instrument_key}
            
            response = await self._make_request("POST", url, json=payload)
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error validating instrument {instrument_key}: {e}")
            raise ServiceUnavailableError(f"Service unavailable: {e}")
    
    async def enrich_instrument(self, instrument_key: str, 
                              include_market_data: bool = True) -> Dict[str, Any]:
        """
        Enrich instrument with additional data
        
        Args:
            instrument_key: Instrument key string
            include_market_data: Whether to include market data
            
        Returns:
            Enriched instrument data
        """
        try:
            url = "/api/v1/instruments/enrich"
            payload = {
                "instrument_key": instrument_key,
                "include_market_data": include_market_data
            }
            
            response = await self._make_request("POST", url, json=payload)
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error enriching instrument {instrument_key}: {e}")
            raise ServiceUnavailableError(f"Service unavailable: {e}")
    
    async def search_instruments(self, query: str, 
                               exchange: Optional[str] = None,
                               asset_product_type: Optional[str] = None,
                               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search instruments
        
        Args:
            query: Search query
            exchange: Filter by exchange
            asset_product_type: Filter by asset product type
            limit: Maximum results
            
        Returns:
            List of matching instruments
        """
        try:
            url = "/api/v1/instruments/search"
            params = {"q": query, "limit": limit}
            
            if exchange:
                params["exchange"] = exchange
            if asset_product_type:
                params["asset_product_type"] = asset_product_type
            
            response = await self._make_request("GET", url, params=params)
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error searching instruments: {e}")
            raise ServiceUnavailableError(f"Service unavailable: {e}")
    
    async def parse_isin(self, isin: str) -> Dict[str, Any]:
        """
        Parse ISIN and get classification
        
        Args:
            isin: ISIN code
            
        Returns:
            ISIN parsing result
        """
        try:
            url = "/api/v1/isin/parse"
            payload = {"isin": isin}
            
            response = await self._make_request("POST", url, json=payload)
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error parsing ISIN {isin}: {e}")
            raise ServiceUnavailableError(f"Service unavailable: {e}")
    
    async def get_moneyness(self, instrument_key: str, 
                           spot_price: Optional[Decimal] = None) -> Dict[str, Any]:
        """
        Get moneyness for option instrument
        
        Args:
            instrument_key: Option instrument key
            spot_price: Current spot price (optional)
            
        Returns:
            Moneyness data
        """
        try:
            url = f"/api/v1/moneyness/{instrument_key}"
            params = {}
            
            if spot_price:
                params["spot_price"] = str(spot_price)
            
            response = await self._make_request("GET", url, params=params)
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error getting moneyness for {instrument_key}: {e}")
            raise ServiceUnavailableError(f"Service unavailable: {e}")
    
    async def get_moneyness_history(self, instrument_key: str,
                                   start_date: datetime,
                                   end_date: datetime) -> Dict[str, Any]:
        """
        Get historical moneyness data
        
        Args:
            instrument_key: Option instrument key
            start_date: Start date
            end_date: End date
            
        Returns:
            Historical moneyness data
        """
        try:
            url = f"/api/v1/moneyness/{instrument_key}/history"
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            response = await self._make_request("GET", url, params=params)
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error getting moneyness history for {instrument_key}: {e}")
            raise ServiceUnavailableError(f"Service unavailable: {e}")
    
    async def convert_to_broker_format(self, instrument_keys: List[str], 
                                     broker_name: str) -> Dict[str, Any]:
        """
        Convert instruments to broker format
        
        Args:
            instrument_keys: List of instrument keys
            broker_name: Target broker name
            
        Returns:
            Conversion results
        """
        try:
            url = f"/api/v1/convert/to-broker/{broker_name}"
            payload = {"instrument_keys": instrument_keys}
            
            response = await self._make_request("POST", url, json=payload)
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error converting to broker format: {e}")
            raise ServiceUnavailableError(f"Service unavailable: {e}")
    
    async def convert_from_broker_format(self, broker_symbols: List[str], 
                                       broker_name: str) -> Dict[str, Any]:
        """
        Convert from broker format to universal format
        
        Args:
            broker_symbols: List of broker symbols
            broker_name: Source broker name
            
        Returns:
            Conversion results
        """
        try:
            url = f"/api/v1/convert/from-broker/{broker_name}"
            payload = {"broker_symbols": broker_symbols}
            
            response = await self._make_request("POST", url, json=payload)
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error converting from broker format: {e}")
            raise ServiceUnavailableError(f"Service unavailable: {e}")
    
    async def get_option_chain(self, underlying_symbol: str, 
                             expiry_date: str,
                             exchange: str = "NSE") -> Dict[str, Any]:
        """
        Get option chain for underlying
        
        Args:
            underlying_symbol: Underlying symbol
            expiry_date: Expiry date
            exchange: Exchange
            
        Returns:
            Option chain data
        """
        try:
            url = "/api/v1/option-chains"
            params = {
                "underlying_symbol": underlying_symbol,
                "expiry_date": expiry_date,
                "exchange": exchange
            }
            
            response = await self._make_request("GET", url, params=params)
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error getting option chain: {e}")
            raise ServiceUnavailableError(f"Service unavailable: {e}")
    
    async def get_service_health(self) -> Dict[str, Any]:
        """
        Get service health status
        
        Returns:
            Health status data
        """
        try:
            url = "/health"
            response = await self._make_request("GET", url)
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error getting service health: {e}")
            raise ServiceUnavailableError(f"Service unavailable: {e}")
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """
        Get service metrics
        
        Returns:
            Service metrics data
        """
        try:
            url = "/metrics"
            response = await self._make_request("GET", url)
            return response.json()
            
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error getting service metrics: {e}")
            raise ServiceUnavailableError(f"Service unavailable: {e}")
    
    async def _make_request(self, method: str, url: str, 
                          params: Optional[Dict] = None,
                          json: Optional[Dict] = None) -> httpx.Response:
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            json: JSON payload
            
        Returns:
            HTTP response
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json
                )
                
                # Check for specific error status codes
                if response.status_code == 404:
                    return response  # Let caller handle 404
                elif response.status_code == 400:
                    error_data = response.json() if response.content else {}
                    raise ValidationError(error_data.get("detail", "Validation error"))
                elif response.status_code >= 500:
                    response.raise_for_status()
                
                return response
                
            except httpx.HTTPError as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Request failed after {self.max_retries + 1} attempts: {e}")
        
        # If we get here, all retries failed
        raise ServiceUnavailableError(f"Service unavailable after {self.max_retries + 1} attempts: {last_exception}")
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.create_task(self.close())
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()