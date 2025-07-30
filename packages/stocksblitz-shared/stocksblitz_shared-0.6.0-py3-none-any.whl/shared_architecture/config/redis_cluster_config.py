# shared_architecture/config/redis_cluster_config.py

from enum import Enum
from typing import Dict, List
from dataclasses import dataclass

class RedisDataDomain(Enum):
    """Redis data domains for optimal cluster distribution"""
    REALTIME_TICKERS = "realtime_tickers"    # Slots 0-4095: High-frequency ticker data
    HISTORICAL_DATA = "historical_data"      # Slots 4096-8191: OHLC, historical cache  
    USER_SESSIONS = "user_sessions"          # Slots 8192-10239: User auth, sessions
    PORTFOLIOS = "portfolios"                # Slots 10240-12287: Portfolio, positions
    SIGNALS_ALERTS = "signals_alerts"        # Slots 12288-14335: Trading signals
    ORDERS_TRADES = "orders_trades"          # Slots 14336-16383: Order management

@dataclass
class ServiceRedisConfig:
    """Redis configuration for each microservice"""
    service_name: str
    primary_domains: List[RedisDataDomain]
    key_patterns: Dict[str, str]
    cluster_nodes: List[str]
    connection_pool_size: int = 20
    
# Global Redis cluster configuration
REDIS_CLUSTER_CONFIG = {
    "cluster_nodes": [
        "localhost:7001", "localhost:7002", "localhost:7003",
        "localhost:7004", "localhost:7005", "localhost:7006"
    ],
    "proxy_endpoint": "localhost:6379",
    "environment_mode": "development",  # Will be "production" in prod
    
    # Service-specific configurations
    "services": {
        "ticker_service": ServiceRedisConfig(
            service_name="ticker_service",
            primary_domains=[RedisDataDomain.REALTIME_TICKERS, RedisDataDomain.HISTORICAL_DATA],
            key_patterns={
                # Real-time ticker streams (co-locate by symbol)
                "ticker_stream": "tick:{symbol}:stream",
                "ticker_latest": "tick:{symbol}:latest", 
                "ticker_volume": "tick:{symbol}:volume",
                "ticker_ohlc": "tick:{symbol}:ohlc",
                
                # Market-wide data (co-locate by exchange)
                "market_index": "market:{index}:data",
                "exchange_status": "exchange:{exchange}:status",
                
                # Historical data cache
                "historical_ohlc": "hist:{symbol}:{timeframe}:ohlc",
                "historical_volume": "hist:{symbol}:{timeframe}:volume"
            },
            cluster_nodes=["localhost:7001", "localhost:7002", "localhost:7003"]
        ),
        
        "signal_service": ServiceRedisConfig(
            service_name="signal_service", 
            primary_domains=[RedisDataDomain.SIGNALS_ALERTS, RedisDataDomain.REALTIME_TICKERS],
            key_patterns={
                # Signal processing (co-locate with ticker data)
                "signal_alerts": "signal:{symbol}:alerts",
                "signal_history": "signal:{symbol}:history",
                "strategy_signals": "strategy:{strategy_id}:signals",
                "indicator_cache": "indicator:{symbol}:{indicator}:cache",
                
                # Alert management (co-locate by user)
                "user_alerts": "alerts:{user_id}:active",
                "alert_history": "alerts:{user_id}:history"
            },
            cluster_nodes=["localhost:7001", "localhost:7004", "localhost:7005"]
        ),
        
        "trade_service": ServiceRedisConfig(
            service_name="trade_service",
            primary_domains=[RedisDataDomain.ORDERS_TRADES, RedisDataDomain.PORTFOLIOS],
            key_patterns={
                # Order management (co-locate by user)
                "user_orders": "orders:{user_id}:active",
                "order_history": "orders:{user_id}:history", 
                "order_status": "order:{order_id}:status",
                
                # Trade execution
                "trade_queue": "trades:{symbol}:queue",
                "trade_history": "trades:{user_id}:history",
                
                # Risk management
                "position_limits": "limits:{user_id}:positions",
                "daily_limits": "limits:{user_id}:daily"
            },
            cluster_nodes=["localhost:7004", "localhost:7005", "localhost:7006"]
        ),
        
        "user_service": ServiceRedisConfig(
            service_name="user_service",
            primary_domains=[RedisDataDomain.USER_SESSIONS, RedisDataDomain.PORTFOLIOS],
            key_patterns={
                # User authentication (co-locate by user)
                "user_session": "session:{user_id}:data",
                "user_auth": "auth:{user_id}:token",
                "user_permissions": "perm:{user_id}:cache",
                
                # Portfolio data (co-locate by user)
                "user_portfolio": "portfolio:{user_id}:data",
                "user_positions": "positions:{user_id}:current",
                "user_watchlist": "watchlist:{user_id}:symbols",
                
                # Rate limiting
                "rate_limit": "rate:{user_id}:{action}:limit"
            },
            cluster_nodes=["localhost:7003", "localhost:7004", "localhost:7006"]
        ),
        
        "subscription_service": ServiceRedisConfig(
            service_name="subscription_service",
            primary_domains=[RedisDataDomain.REALTIME_TICKERS, RedisDataDomain.USER_SESSIONS],
            key_patterns={
                # Subscription management (co-locate by user)
                "user_subscriptions": "subs:{user_id}:symbols",
                "subscription_limits": "subs:{user_id}:limits",
                
                # Real-time data distribution
                "symbol_subscribers": "subs:symbol:{symbol}:users",
                "active_streams": "streams:{user_id}:active",
                
                # Broker API management
                "broker_limits": "broker:{broker}:limits",
                "api_quotas": "quota:{user_id}:{broker}:usage"
            },
            cluster_nodes=["localhost:7001", "localhost:7002", "localhost:7005"]
        ),
        
        "execution_engine": ServiceRedisConfig(
            service_name="execution_engine", 
            primary_domains=[RedisDataDomain.ORDERS_TRADES, RedisDataDomain.SIGNALS_ALERTS],
            key_patterns={
                # Strategy execution
                "strategy_state": "strategy:{strategy_id}:state",
                "strategy_positions": "strategy:{strategy_id}:positions",
                "execution_queue": "exec:{strategy_id}:queue",
                
                # Performance tracking
                "strategy_metrics": "metrics:{strategy_id}:performance",
                "execution_history": "exec:{strategy_id}:history"
            },
            cluster_nodes=["localhost:7005", "localhost:7006", "localhost:7001"]
        )
    }
}

def get_service_redis_config(service_name: str) -> ServiceRedisConfig:
    """Get Redis configuration for a specific service"""
    if service_name not in REDIS_CLUSTER_CONFIG["services"]:
        raise ValueError(f"Unknown service: {service_name}")
    return REDIS_CLUSTER_CONFIG["services"][service_name]

def get_key_pattern(service_name: str, pattern_name: str) -> str:
    """Get key pattern for a service"""
    config = get_service_redis_config(service_name)
    if pattern_name not in config.key_patterns:
        raise ValueError(f"Unknown pattern '{pattern_name}' for service '{service_name}'")
    return config.key_patterns[pattern_name]

def format_key(service_name: str, pattern_name: str, **kwargs) -> str:
    """Format a Redis key with the service's pattern"""
    pattern = get_key_pattern(service_name, pattern_name)
    return pattern.format(**kwargs)

# Domain-to-slot mapping for cluster optimization
DOMAIN_SLOT_RANGES = {
    RedisDataDomain.REALTIME_TICKERS: (0, 4095),       # 25% - High write throughput
    RedisDataDomain.HISTORICAL_DATA: (4096, 8191),     # 25% - Read-heavy cache
    RedisDataDomain.USER_SESSIONS: (8192, 10239),      # 12.5% - Session management
    RedisDataDomain.PORTFOLIOS: (10240, 12287),        # 12.5% - Portfolio data
    RedisDataDomain.SIGNALS_ALERTS: (12288, 14335),    # 12.5% - Signal processing
    RedisDataDomain.ORDERS_TRADES: (14336, 16383),     # 12.5% - Order management
}