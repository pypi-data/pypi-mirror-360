# shared_architecture/connections/redis_cluster_manager.py

import redis.asyncio as redis
from redis.cluster import RedisCluster
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DataType(Enum):
    """Data types for optimal cluster distribution"""
    TICKER_REALTIME = "ticker_realtime"  # High-frequency price updates
    TICKER_HISTORICAL = "ticker_historical"  # Historical data cache
    USER_SESSION = "user_session"  # User sessions and auth
    PORTFOLIO = "portfolio"  # Portfolio and positions
    SIGNALS = "signals"  # Trading signals and alerts
    ORDERS = "orders"  # Order management
    MARKET_DATA = "market_data"  # Market-wide aggregations

@dataclass
class ClusterKeyPattern:
    """Optimized key patterns for Redis cluster"""
    prefix: str
    hash_tag: str
    data_type: DataType
    
    def format_key(self, **kwargs) -> str:
        """Format key with hash tag for optimal clustering"""
        key_parts = [self.prefix]
        
        # Add hash tag for data locality
        if self.hash_tag:
            tag_value = kwargs.get(self.hash_tag)
            if tag_value:
                key_parts.append(f"{{{tag_value}}}")
        
        # Add remaining key parts
        for key, value in kwargs.items():
            if key != self.hash_tag:
                key_parts.append(str(value))
        
        return ":".join(key_parts)

class RedisClusterManager:
    """High-performance Redis cluster manager optimized for ticker data"""
    
    # Predefined key patterns for optimal clustering
    KEY_PATTERNS = {
        # Ticker data patterns (co-locate by symbol)
        "ticker_stream": ClusterKeyPattern("tick", "symbol", DataType.TICKER_REALTIME),
        "ticker_latest": ClusterKeyPattern("tick", "symbol", DataType.TICKER_REALTIME),
        "ticker_volume": ClusterKeyPattern("tick", "symbol", DataType.TICKER_REALTIME),
        "ticker_ohlc": ClusterKeyPattern("ohlc", "symbol", DataType.TICKER_HISTORICAL),
        
        # Signal patterns (co-locate with ticker data)
        "signal_alerts": ClusterKeyPattern("signal", "symbol", DataType.SIGNALS),
        "signal_history": ClusterKeyPattern("signal", "symbol", DataType.SIGNALS),
        "strategy_signals": ClusterKeyPattern("strategy", "strategy_id", DataType.SIGNALS),
        
        # Portfolio patterns (co-locate by user)
        "user_portfolio": ClusterKeyPattern("portfolio", "user_id", DataType.PORTFOLIO),
        "user_positions": ClusterKeyPattern("positions", "user_id", DataType.PORTFOLIO),
        "user_orders": ClusterKeyPattern("orders", "user_id", DataType.ORDERS),
        "user_watchlist": ClusterKeyPattern("watchlist", "user_id", DataType.PORTFOLIO),
        
        # Market data patterns (co-locate by exchange/index)
        "market_index": ClusterKeyPattern("market", "index", DataType.MARKET_DATA),
        "exchange_data": ClusterKeyPattern("exchange", "exchange", DataType.MARKET_DATA),
        
        # Session patterns (co-locate by user)
        "user_session": ClusterKeyPattern("session", "user_id", DataType.USER_SESSION),
        "user_auth": ClusterKeyPattern("auth", "user_id", DataType.USER_SESSION),
    }
    
    def __init__(self, cluster_client: Union[redis.Redis, RedisCluster]):
        self.client = cluster_client
        self.is_cluster = isinstance(cluster_client, RedisCluster)
        
    def get_key(self, pattern_name: str, **kwargs) -> str:
        """Generate optimized key for cluster distribution"""
        if pattern_name not in self.KEY_PATTERNS:
            raise ValueError(f"Unknown key pattern: {pattern_name}")
        
        pattern = self.KEY_PATTERNS[pattern_name]
        return pattern.format_key(**kwargs)
    
    async def get_node_for_key(self, key: str) -> Optional[Dict]:
        """Get the cluster node responsible for a key"""
        if not self.is_cluster:
            return None
        
        try:
            slot = self.client.cluster_keyslot(key)
            nodes = await self.client.cluster_nodes()
            
            for node in nodes:
                slots = node.get("slots", [])
                for slot_range in slots:
                    if slot_range[0] <= slot <= slot_range[1]:
                        return {
                            "node_id": node["id"],
                            "host": node["host"], 
                            "port": node["port"],
                            "slot": slot,
                            "role": node["role"]
                        }
        except Exception as e:
            logger.warning(f"Could not determine node for key {key}: {e}")
        
        return None
    
    async def pipeline_for_keys(self, keys: List[str]) -> redis.client.Pipeline:
        """Create pipeline optimized for multi-key operations"""
        if not self.is_cluster:
            return self.client.pipeline()
        
        # Group keys by hash slot for optimal pipeline performance
        slot_groups = {}
        for key in keys:
            slot = self.client.cluster_keyslot(key)
            if slot not in slot_groups:
                slot_groups[slot] = []
            slot_groups[slot].append(key)
        
        # Log pipeline optimization info
        if len(slot_groups) > 1:
            logger.debug(f"Pipeline spans {len(slot_groups)} slots for {len(keys)} keys")
        
        return self.client.pipeline()
    
    # High-level operations optimized for ticker data
    
    async def stream_ticker_data(self, symbol: str, data: Dict[str, Any]) -> str:
        """Add ticker data to stream with optimal clustering"""
        stream_key = self.get_key("ticker_stream", symbol=symbol, data_type="stream")
        latest_key = self.get_key("ticker_latest", symbol=symbol)
        
        # Use pipeline for atomic updates
        pipe = await self.pipeline_for_keys([stream_key, latest_key])
        
        # Add to stream and update latest
        message_id = await pipe.xadd(stream_key, data)
        await pipe.set(latest_key, data.get("price", 0))
        await pipe.execute()
        
        return message_id
    
    async def get_ticker_latest(self, symbols: List[str]) -> Dict[str, float]:
        """Get latest prices for multiple symbols efficiently"""
        keys = [self.get_key("ticker_latest", symbol=symbol) for symbol in symbols]
        
        # Use pipeline for batch operations
        pipe = await self.pipeline_for_keys(keys)
        for key in keys:
            pipe.get(key)
        
        results = await pipe.execute()
        
        # Map results back to symbols
        price_data = {}
        for symbol, price in zip(symbols, results):
            if price is not None:
                try:
                    price_data[symbol] = float(price)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid price data for {symbol}: {price}")
        
        return price_data
    
    async def add_signal_alert(self, symbol: str, signal_data: Dict[str, Any]) -> None:
        """Add trading signal with symbol co-location"""
        alerts_key = self.get_key("signal_alerts", symbol=symbol)
        history_key = self.get_key("signal_history", symbol=symbol)
        
        # Store both alert and history on same node
        pipe = await self.pipeline_for_keys([alerts_key, history_key])
        
        # Add to sorted set for alerts (score = timestamp)
        timestamp = signal_data.get("timestamp", 0)
        await pipe.zadd(alerts_key, {str(signal_data): timestamp})
        
        # Add to history stream
        await pipe.xadd(history_key, signal_data)
        
        await pipe.execute()
    
    async def get_user_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Get complete user portfolio data efficiently"""
        portfolio_key = self.get_key("user_portfolio", user_id=user_id)
        positions_key = self.get_key("user_positions", user_id=user_id)
        orders_key = self.get_key("user_orders", user_id=user_id)
        
        # All user data co-located on same node
        pipe = await self.pipeline_for_keys([portfolio_key, positions_key, orders_key])
        
        pipe.hgetall(portfolio_key)  # Portfolio metadata
        pipe.hgetall(positions_key)  # Current positions
        pipe.lrange(orders_key, 0, -1)  # Recent orders
        
        portfolio, positions, orders = await pipe.execute()
        
        return {
            "portfolio": portfolio or {},
            "positions": positions or {},
            "orders": orders or []
        }
    
    async def cluster_stats(self) -> Dict[str, Any]:
        """Get cluster performance statistics"""
        if not self.is_cluster:
            return {"mode": "single_node"}
        
        try:
            nodes = await self.client.cluster_nodes()
            info = await self.client.cluster_info()
            
            # Calculate distribution statistics
            master_nodes = [n for n in nodes if n.get("role") == "master"]
            replica_nodes = [n for n in nodes if n.get("role") == "slave"]
            
            return {
                "mode": "cluster",
                "cluster_state": info.get("cluster_state", "unknown"),
                "cluster_slots_assigned": info.get("cluster_slots_assigned", 0),
                "cluster_slots_ok": info.get("cluster_slots_ok", 0),
                "master_nodes": len(master_nodes),
                "replica_nodes": len(replica_nodes),
                "total_nodes": len(nodes),
                "cluster_known_nodes": info.get("cluster_known_nodes", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get cluster stats: {e}")
            return {"mode": "cluster", "error": str(e)}

# Global cluster manager instance
cluster_manager: Optional[RedisClusterManager] = None

def get_cluster_manager() -> RedisClusterManager:
    """Get the global cluster manager instance"""
    global cluster_manager
    if cluster_manager is None:
        from .redis_client import get_redis_client
        cluster_manager = RedisClusterManager(get_redis_client())
    return cluster_manager