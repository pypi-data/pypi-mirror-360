"""
Local instrument manager for high-performance operations
"""

import asyncio
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
from decimal import Decimal
import json
import logging
from concurrent.futures import ThreadPoolExecutor

from ..core.instrument_key import InstrumentKey, InstrumentAttributes
from ..core.enums import AssetProductType, Exchange, OptionType, Moneyness
from ..core.exceptions import InstrumentNotFoundError, CacheError
from ..utils.factory import InstrumentKeyFactory


class LocalInstrumentManager:
    """
    High-performance local instrument manager with caching
    
    This manager provides:
    - In-memory caching for frequently accessed instruments
    - Bulk operations for performance
    - Async operations for non-blocking behavior
    - Fallback to service when needed
    """
    
    def __init__(self, cache_size: int = 10000, cache_ttl: int = 3600):
        """
        Initialize local manager
        
        Args:
            cache_size: Maximum number of instruments to cache
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
        """
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl
        self.logger = logging.getLogger(__name__)
        
        # L1 Cache: Hot instruments (most frequently accessed)
        self._hot_cache: Dict[str, InstrumentKey] = {}
        self._hot_cache_access: Dict[str, datetime] = {}
        self._hot_cache_hits: Dict[str, int] = {}
        # L2 Cache: Warm instruments (recently accessed)
        self._warm_cache: Dict[str, InstrumentKey] = {}
        self._warm_cache_access: Dict[str, datetime] = {}
        
        # Validation cache
        self._validation_cache: Dict[str, bool] = {}
        
        # Stats
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_requests = 0
        
        # Thread pool for async operations
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize with common instruments
        self._initialize_common_instruments()
    
    def _initialize_common_instruments(self):
        """Initialize cache with common instruments"""
        common_instruments = [
            # Popular indices
            InstrumentKeyFactory.index_spot("NIFTY", Exchange.NSE),
            InstrumentKeyFactory.index_spot("BANKNIFTY", Exchange.NSE),
            InstrumentKeyFactory.index_spot("SENSEX", Exchange.BSE),
            
            # Popular stocks
            InstrumentKeyFactory.equity_spot("RELIANCE", Exchange.NSE),
            InstrumentKeyFactory.equity_spot("TCS", Exchange.NSE),
            InstrumentKeyFactory.equity_spot("HDFCBANK", Exchange.NSE),
            InstrumentKeyFactory.equity_spot("INFY", Exchange.NSE),
            InstrumentKeyFactory.equity_spot("ICICIBANK", Exchange.NSE),
        ]
        
        for instrument in common_instruments:
            self._add_to_hot_cache(instrument.to_string(), instrument)
    
    def get_instrument(self, instrument_key: str) -> Optional[InstrumentKey]:
        """
        Get instrument with caching
        
        Args:
            instrument_key: Instrument key string
            
        Returns:
            InstrumentKey if found, None otherwise
        """
        self._total_requests += 1
        
        # Check hot cache first
        if instrument_key in self._hot_cache:
            self._cache_hits += 1
            self._hot_cache_hits[instrument_key] = self._hot_cache_hits.get(instrument_key, 0) + 1
            self._hot_cache_access[instrument_key] = datetime.now()
            return self._hot_cache[instrument_key]
        
        # Check warm cache
        if instrument_key in self._warm_cache:
            self._cache_hits += 1
            instrument = self._warm_cache[instrument_key]
            
            # Promote to hot cache if accessed frequently
            self._promote_to_hot_cache(instrument_key, instrument)
            return instrument
        
        # Cache miss - try to parse from string
        try:
            instrument = InstrumentKey.from_string(instrument_key)
            self._add_to_warm_cache(instrument_key, instrument)
            self._cache_misses += 1
            return instrument
        except Exception as e:
            self.logger.warning(f"Failed to parse instrument key {instrument_key}: {e}")
            self._cache_misses += 1
            return None
    
    def get_instruments_bulk(self, instrument_keys: List[str]) -> Dict[str, Optional[InstrumentKey]]:
        """
        Get multiple instruments efficiently
        
        Args:
            instrument_keys: List of instrument key strings
            
        Returns:
            Dictionary mapping keys to instruments
        """
        result = {}
        
        for key in instrument_keys:
            result[key] = self.get_instrument(key)
        
        return result
    
    async def get_instrument_async(self, instrument_key: str) -> Optional[InstrumentKey]:
        """
        Async version of get_instrument
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.get_instrument, instrument_key)
    
    def validate_instrument(self, instrument_key: str) -> bool:
        """
        Validate instrument key format
        
        Args:
            instrument_key: Instrument key string
            
        Returns:
            True if valid, False otherwise
        """
        # Check validation cache first
        if instrument_key in self._validation_cache:
            return self._validation_cache[instrument_key]
        
        try:
            instrument = InstrumentKey.from_string(instrument_key)
            self._validation_cache[instrument_key] = True
            return True
        except Exception:
            self._validation_cache[instrument_key] = False
            return False
    
    def search_instruments(self, symbol: str, exchange: Optional[Exchange] = None,
                          asset_product_type: Optional[AssetProductType] = None,
                          limit: int = 10) -> List[InstrumentKey]:
        """
        Search instruments in cache
        
        Args:
            symbol: Symbol to search for
            exchange: Filter by exchange
            asset_product_type: Filter by asset product type
            limit: Maximum results to return
            
        Returns:
            List of matching instruments
        """
        matches = []
        
        # Search in hot cache first
        for key, instrument in self._hot_cache.items():
            if self._matches_criteria(instrument, symbol, exchange, asset_product_type):
                matches.append(instrument)
                if len(matches) >= limit:
                    break
        
        # Search in warm cache if needed
        if len(matches) < limit:
            for key, instrument in self._warm_cache.items():
                if key not in self._hot_cache:  # Avoid duplicates
                    if self._matches_criteria(instrument, symbol, exchange, asset_product_type):
                        matches.append(instrument)
                        if len(matches) >= limit:
                            break
        
        return matches[:limit]
    
    def _matches_criteria(self, instrument: InstrumentKey, symbol: str,
                         exchange: Optional[Exchange], 
                         asset_product_type: Optional[AssetProductType]) -> bool:
        """Check if instrument matches search criteria"""
        # Symbol match (case-insensitive, partial match)
        if symbol.upper() not in instrument.attributes.symbol.upper():
            return False
        
        # Exchange filter
        if exchange and instrument.attributes.exchange != exchange:
            return False
        
        # Asset product type filter
        if asset_product_type and instrument.attributes.asset_product_type != asset_product_type:
            return False
        
        return True
    
    def _add_to_hot_cache(self, key: str, instrument: InstrumentKey):
        """Add instrument to hot cache"""
        # Check if hot cache is full
        if len(self._hot_cache) >= self.cache_size // 2:
            self._evict_from_hot_cache()
        
        self._hot_cache[key] = instrument
        self._hot_cache_access[key] = datetime.now()
        self._hot_cache_hits[key] = 0
    
    def _add_to_warm_cache(self, key: str, instrument: InstrumentKey):
        """Add instrument to warm cache"""
        # Check if warm cache is full
        if len(self._warm_cache) >= self.cache_size // 2:
            self._evict_from_warm_cache()
        
        self._warm_cache[key] = instrument
        self._warm_cache_access[key] = datetime.now()
    
    def _promote_to_hot_cache(self, key: str, instrument: InstrumentKey):
        """Promote instrument from warm to hot cache"""
        # Remove from warm cache
        self._warm_cache.pop(key, None)
        self._warm_cache_access.pop(key, None)
        
        # Add to hot cache
        self._add_to_hot_cache(key, instrument)
    
    def _evict_from_hot_cache(self):
        """Evict least recently used items from hot cache"""
        # Sort by access time
        sorted_items = sorted(
            self._hot_cache_access.items(),
            key=lambda x: x[1]
        )
        
        # Evict oldest 10% of items
        evict_count = max(1, len(sorted_items) // 10)
        
        for i in range(evict_count):
            key = sorted_items[i][0]
            
            # Move to warm cache if still valid
            if key in self._hot_cache:
                instrument = self._hot_cache[key]
                self._add_to_warm_cache(key, instrument)
                
                # Remove from hot cache
                self._hot_cache.pop(key, None)
                self._hot_cache_access.pop(key, None)
                self._hot_cache_hits.pop(key, None)
    
    def _evict_from_warm_cache(self):
        """Evict least recently used items from warm cache"""
        # Sort by access time
        sorted_items = sorted(
            self._warm_cache_access.items(),
            key=lambda x: x[1]
        )
        
        # Evict oldest 10% of items
        evict_count = max(1, len(sorted_items) // 10)
        
        for i in range(evict_count):
            key = sorted_items[i][0]
            self._warm_cache.pop(key, None)
            self._warm_cache_access.pop(key, None)
    
    def clear_cache(self):
        """Clear all caches"""
        self._hot_cache.clear()
        self._hot_cache_access.clear()
        self._hot_cache_hits.clear()
        self._warm_cache.clear()
        self._warm_cache_access.clear()
        self._validation_cache.clear()
        
        # Reset stats
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_requests = 0
        
        # Re-initialize common instruments
        self._initialize_common_instruments()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = (self._cache_hits / self._total_requests * 100) if self._total_requests > 0 else 0
        
        return {
            "hot_cache_size": len(self._hot_cache),
            "warm_cache_size": len(self._warm_cache),
            "validation_cache_size": len(self._validation_cache),
            "total_requests": self._total_requests,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate_percent": round(hit_rate, 2),
            "top_instruments": self._get_top_instruments(5)
        }
    
    def _get_top_instruments(self, limit: int) -> List[Dict[str, Any]]:
        """Get top accessed instruments"""
        sorted_instruments = sorted(
            self._hot_cache_hits.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {
                "instrument_key": key,
                "hits": hits,
                "last_access": self._hot_cache_access.get(key, datetime.now()).isoformat()
            }
            for key, hits in sorted_instruments[:limit]
        ]
    
    def preload_instruments(self, instrument_keys: List[str]):
        """
        Preload instruments into cache
        
        Args:
            instrument_keys: List of instrument keys to preload
        """
        for key in instrument_keys:
            try:
                instrument = InstrumentKey.from_string(key)
                self._add_to_hot_cache(key, instrument)
            except Exception as e:
                self.logger.warning(f"Failed to preload instrument {key}: {e}")
    
    def create_option_chain(self, symbol: str, expiry_date: str,
                           strikes: List[Decimal], 
                           exchange: Exchange = Exchange.NSE) -> Dict[str, List[InstrumentKey]]:
        """
        Create option chain and cache it
        
        Args:
            symbol: Underlying symbol
            expiry_date: Expiry date string
            strikes: List of strike prices
            exchange: Exchange
            
        Returns:
            Dictionary with 'calls' and 'puts' lists
        """
        calls = []
        puts = []
        
        for strike in strikes:
            # Create call option
            call_key = f"{exchange.value}@{symbol}@equity_options@{expiry_date}@call@{strike}"
            try:
                call = InstrumentKey.from_string(call_key)
                calls.append(call)
                self._add_to_hot_cache(call_key, call)
            except Exception as e:
                self.logger.warning(f"Failed to create call option {call_key}: {e}")
            
            # Create put option
            put_key = f"{exchange.value}@{symbol}@equity_options@{expiry_date}@put@{strike}"
            try:
                put = InstrumentKey.from_string(put_key)
                puts.append(put)
                self._add_to_hot_cache(put_key, put)
            except Exception as e:
                self.logger.warning(f"Failed to create put option {put_key}: {e}")
        
        return {"calls": calls, "puts": puts}
    
    def cleanup_expired_cache(self):
        """Remove expired items from cache"""
        current_time = datetime.now()
        expired_keys = []
        
        # Check hot cache
        for key, access_time in self._hot_cache_access.items():
            if current_time - access_time > timedelta(seconds=self.cache_ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            self._hot_cache.pop(key, None)
            self._hot_cache_access.pop(key, None)
            self._hot_cache_hits.pop(key, None)
        
        # Check warm cache
        expired_keys = []
        for key, access_time in self._warm_cache_access.items():
            if current_time - access_time > timedelta(seconds=self.cache_ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            self._warm_cache.pop(key, None)
            self._warm_cache_access.pop(key, None)
    
    def shutdown(self):
        """Shutdown the manager and cleanup resources"""
        self._executor.shutdown(wait=True)
        self.clear_cache()