"""
Tests for the LocalInstrumentManager class
"""

import pytest
import asyncio
from decimal import Decimal

from ..managers.local_manager import LocalInstrumentManager
from ..utils.factory import InstrumentKeyFactory
from ..core.enums import AssetProductType, Exchange, OptionType


class TestLocalInstrumentManager:
    """Test cases for LocalInstrumentManager"""
    
    @pytest.fixture
    def manager(self):
        """Create a test manager instance"""
        return LocalInstrumentManager(cache_size=100, cache_ttl=3600)
    
    def test_manager_initialization(self, manager):
        """Test manager initializes correctly"""
        assert manager.cache_size == 100
        assert manager.cache_ttl == 3600
        assert len(manager._hot_cache) > 0  # Should have common instruments
        
        # Check that common instruments are preloaded
        nifty_key = "NSE@NIFTY@index_spot"
        assert nifty_key in manager._hot_cache
    
    def test_get_instrument_from_cache(self, manager):
        """Test getting instrument from cache"""
        # Should find NIFTY in hot cache
        nifty = manager.get_instrument("NSE@NIFTY@index_spot")
        
        assert nifty is not None
        assert nifty.attributes.symbol == "NIFTY"
        assert nifty.attributes.exchange == Exchange.NSE
        
        # Should increment cache hits
        assert manager._cache_hits > 0
    
    def test_get_instrument_parse_new(self, manager):
        """Test getting instrument that needs parsing"""
        # This should not be in cache initially
        custom_key = "NSE@TESTSTOCK@equity_spot"
        instrument = manager.get_instrument(custom_key)
        
        assert instrument is not None
        assert instrument.attributes.symbol == "TESTSTOCK"
        
        # Should be added to warm cache
        assert custom_key in manager._warm_cache
        
        # Should increment cache misses
        assert manager._cache_misses > 0
    
    def test_get_instrument_invalid_key(self, manager):
        """Test getting invalid instrument key"""
        invalid_key = "INVALID_KEY_FORMAT"
        instrument = manager.get_instrument(invalid_key)
        
        assert instrument is None
        assert manager._cache_misses > 0
    
    def test_get_instruments_bulk(self, manager):
        """Test bulk instrument retrieval"""
        keys = [
            "NSE@NIFTY@index_spot",
            "NSE@RELIANCE@equity_spot", 
            "NSE@TCS@equity_spot",
            "INVALID_KEY"
        ]
        
        results = manager.get_instruments_bulk(keys)
        
        assert len(results) == 4
        assert results["NSE@NIFTY@index_spot"] is not None
        assert results["NSE@RELIANCE@equity_spot"] is not None
        assert results["INVALID_KEY"] is None
    
    @pytest.mark.asyncio
    async def test_get_instrument_async(self, manager):
        """Test async instrument retrieval"""
        instrument = await manager.get_instrument_async("NSE@NIFTY@index_spot")
        
        assert instrument is not None
        assert instrument.attributes.symbol == "NIFTY"
    
    def test_validate_instrument(self, manager):
        """Test instrument validation"""
        # Valid key
        assert manager.validate_instrument("NSE@NIFTY@index_spot") == True
        
        # Invalid key
        assert manager.validate_instrument("INVALID") == False
        
        # Check validation cache
        assert "NSE@NIFTY@index_spot" in manager._validation_cache
        assert manager._validation_cache["NSE@NIFTY@index_spot"] == True
    
    def test_search_instruments(self, manager):
        """Test instrument search"""
        # Search for NIFTY
        results = manager.search_instruments("NIFTY")
        
        assert len(results) > 0
        assert any(inst.attributes.symbol == "NIFTY" for inst in results)
        
        # Search with filters
        equity_results = manager.search_instruments(
            "RELIANCE", 
            exchange=Exchange.NSE,
            asset_product_type=AssetProductType.EQUITY_SPOT
        )
        
        assert len(equity_results) > 0
        assert all(inst.attributes.exchange == Exchange.NSE for inst in equity_results)
    
    def test_cache_promotion(self, manager):
        """Test cache promotion from warm to hot"""
        # Add instrument to warm cache
        test_key = "NSE@TESTSTOCK@equity_spot"
        manager.get_instrument(test_key)  # Adds to warm cache
        
        assert test_key in manager._warm_cache
        assert test_key not in manager._hot_cache
        
        # Access again to promote
        manager.get_instrument(test_key)
        
        # Should be promoted to hot cache
        assert test_key in manager._hot_cache
        assert test_key not in manager._warm_cache
    
    def test_cache_eviction(self, manager):
        """Test cache eviction when full"""
        # Fill up the cache
        for i in range(manager.cache_size + 10):
            key = f"NSE@STOCK{i}@equity_spot"
            manager.get_instrument(key)
        
        # Cache should not exceed size limits
        total_cache_size = len(manager._hot_cache) + len(manager._warm_cache)
        assert total_cache_size <= manager.cache_size
    
    def test_preload_instruments(self, manager):
        """Test preloading instruments"""
        keys_to_preload = [
            "NSE@HDFC@equity_spot",
            "NSE@ICICIBANK@equity_spot",
            "BSE@SENSEX@index_spot"
        ]
        
        manager.preload_instruments(keys_to_preload)
        
        # All should be in hot cache
        for key in keys_to_preload:
            assert key in manager._hot_cache
    
    def test_create_option_chain(self, manager):
        """Test creating and caching option chain"""
        strikes = [Decimal("24000"), Decimal("25000"), Decimal("26000")]
        
        chain = manager.create_option_chain(
            "NIFTY", "31-Jul-2025", strikes, Exchange.NSE
        )
        
        assert "calls" in chain
        assert "puts" in chain
        assert len(chain["calls"]) == 3
        assert len(chain["puts"]) == 3
        
        # All options should be cached
        for call in chain["calls"]:
            assert call.to_string() in manager._hot_cache
        
        for put in chain["puts"]:
            assert put.to_string() in manager._hot_cache
    
    def test_cache_stats(self, manager):
        """Test cache statistics"""
        # Generate some activity
        manager.get_instrument("NSE@NIFTY@index_spot")  # Hit
        manager.get_instrument("NSE@NEWSTOCK@equity_spot")  # Miss
        
        stats = manager.get_cache_stats()
        
        assert "hot_cache_size" in stats
        assert "warm_cache_size" in stats
        assert "total_requests" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "hit_rate_percent" in stats
        assert "top_instruments" in stats
        
        assert stats["total_requests"] > 0
        assert stats["hit_rate_percent"] >= 0
    
    def test_clear_cache(self, manager):
        """Test cache clearing"""
        # Add some instruments
        manager.get_instrument("NSE@TEST1@equity_spot")
        manager.get_instrument("NSE@TEST2@equity_spot")
        
        # Clear cache
        manager.clear_cache()
        
        # Should have common instruments again, but test instruments should be gone
        assert len(manager._hot_cache) > 0  # Common instruments reloaded
        assert "NSE@TEST1@equity_spot" not in manager._hot_cache
        assert "NSE@TEST2@equity_spot" not in manager._warm_cache
        
        # Stats should be reset
        assert manager._cache_hits == 0
        assert manager._cache_misses == 0
    
    def test_cleanup_expired_cache(self, manager):
        """Test expired cache cleanup"""
        # This is a basic test - in real scenario we'd mock datetime
        # For now, just ensure the method doesn't crash
        manager.cleanup_expired_cache()
        
        # Cache should still have common instruments
        assert len(manager._hot_cache) > 0
    
    def test_shutdown(self, manager):
        """Test manager shutdown"""
        manager.shutdown()
        
        # Cache should be cleared
        assert len(manager._hot_cache) == 0
        assert len(manager._warm_cache) == 0
    
    def test_concurrent_access(self, manager):
        """Test concurrent access to manager"""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                for i in range(10):
                    key = f"NSE@WORKER{worker_id}_STOCK{i}@equity_spot"
                    instrument = manager.get_instrument(key)
                    if instrument:
                        results.append(instrument.to_string())
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should have no errors and some results
        assert len(errors) == 0
        assert len(results) > 0
        
        # Cache should be consistent
        stats = manager.get_cache_stats()
        assert stats["total_requests"] > 0