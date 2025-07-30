# shared_architecture/connections/autotrader_pool.py
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Try to import real AutoTrader
try:
    from com.dakshata.autotrader.api.AutoTrader import AutoTrader as RealAutoTrader
    AUTOTRADER_AVAILABLE = True
except ImportError:
    AUTOTRADER_AVAILABLE = False
    RealAutoTrader = None

class AutoTraderConnection:
    """Wrapper for AutoTrader connection with metadata"""
    
    def __init__(self, connection: Any, api_key: str, organization_id: str):
        self.connection = connection
        self.api_key = api_key
        self.organization_id = organization_id
        self.created_at = datetime.utcnow()
        self.last_used = datetime.utcnow()
        self.request_count = 0
        self.error_count = 0
        self.is_healthy = True
    
    def mark_used(self):
        """Update last used timestamp and increment request count"""
        self.last_used = datetime.utcnow()
        self.request_count += 1
    
    def mark_error(self):
        """Increment error count and check health"""
        self.error_count += 1
        # Mark unhealthy if too many errors
        if self.error_count > 5:
            self.is_healthy = False
    
    def is_stale(self, max_age_hours: int = 24) -> bool:
        """Check if connection is too old"""
        age = datetime.utcnow() - self.created_at
        return age > timedelta(hours=max_age_hours)

class AutoTraderConnectionPool:
    """
    Manages a pool of AutoTrader connections for multiple organizations.
    Features:
    - Connection reuse per organization
    - Automatic midnight reset
    - Health checking
    - Thread-safe operations
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure one pool across the application"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.connections: Dict[str, AutoTraderConnection] = {}
        self.api_key_cache: Dict[str, tuple[str, datetime]] = {}  # org_id -> (api_key, cached_at)
        self.last_reset = datetime.utcnow()
        self._lock = threading.Lock()
        self._initialized = True
        
        # Configuration
        self.max_connection_age_hours = 24
        self.api_key_cache_ttl_hours = 24
        self.server_url = RealAutoTrader.SERVER_URL if RealAutoTrader else "https://mock-autotrader.com"
        
        logger.info("AutoTraderConnectionPool initialized")
    
    def _should_reset(self) -> bool:
        """Check if it's time for midnight reset"""
        now = datetime.utcnow()
        # Reset at midnight UTC
        if now.hour == 0 and (now - self.last_reset).total_seconds() > 3600:
            return True
        return False
    
    def _create_connection(self, api_key: str, organization_id: str) -> AutoTraderConnection:
        """Create a new AutoTrader connection"""
        try:
            if AUTOTRADER_AVAILABLE and RealAutoTrader:
                # Always try real AutoTrader first
                logger.info(f"Creating real AutoTrader connection for org {organization_id} with API key {api_key[:8]}...")
                connection = RealAutoTrader.create_instance(api_key, self.server_url)
                
                # Test the connection immediately to ensure it's valid
                test_response = connection.read_platform_positions('TEST_CONNECTION')
                if not test_response.success() and 'unauthorized' in test_response.message.lower():
                    raise ConnectionError(f"AutoTrader authentication failed for API key {api_key[:8]}...: {test_response.message}")
                
                logger.info(f"✅ Real AutoTrader connection created and validated for org {organization_id}")
                return AutoTraderConnection(connection, api_key, organization_id)
            else:
                # AutoTrader library not available - this is a critical error
                error_msg = f"❌ AutoTrader library not installed! Cannot create connection for org {organization_id}"
                logger.error(error_msg)
                raise ImportError(error_msg)
            
        except Exception as e:
            error_msg = f"❌ Failed to create AutoTrader connection for org {organization_id}: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
    
    def get_connection(self, organization_id: str, api_key: Optional[str] = None) -> Any:
        """
        Get or create a connection for an organization.
        
        Args:
            organization_id: The organization ID
            api_key: API key (optional if cached)
            
        Returns:
            AutoTrader connection instance
            
        Raises:
            ConnectionError: If connection fails or is invalid
            ValueError: If API key is missing
            ImportError: If AutoTrader library is not available
        """
        with self._lock:
            # Check for midnight reset
            if self._should_reset():
                self.reset_all()
            
            # Check existing connection
            if organization_id in self.connections:
                conn_wrapper = self.connections[organization_id]
                
                # Validate connection health and age
                if conn_wrapper.is_healthy and not conn_wrapper.is_stale(self.max_connection_age_hours):
                    conn_wrapper.mark_used()
                    logger.debug(f"♻️ Reusing connection for org {organization_id} (requests: {conn_wrapper.request_count})")
                    return conn_wrapper.connection
                else:
                    # Remove unhealthy or stale connection and force recreation
                    reason = 'unhealthy' if not conn_wrapper.is_healthy else 'stale'
                    logger.warning(f"🗑️ Removing {reason} connection for org {organization_id}, will create new one")
                    del self.connections[organization_id]
            
            # Need to create new connection
            if not api_key:
                # Check cache
                if organization_id in self.api_key_cache:
                    cached_key, cached_at = self.api_key_cache[organization_id]
                    if (datetime.utcnow() - cached_at).total_seconds() < self.api_key_cache_ttl_hours * 3600:
                        api_key = cached_key
                    else:
                        del self.api_key_cache[organization_id]
                
                if not api_key:
                    error_msg = f"❌ API key required for organization {organization_id} but not found in cache"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            
            # Cache the API key
            self.api_key_cache[organization_id] = (api_key, datetime.utcnow())
            
            # Create new connection - this will raise exceptions on failure
            try:
                conn_wrapper = self._create_connection(api_key, organization_id)
                self.connections[organization_id] = conn_wrapper
                logger.info(f"🔗 Successfully created and cached new connection for org {organization_id}")
                return conn_wrapper.connection
            except Exception as e:
                # Remove from cache if connection creation fails
                if organization_id in self.api_key_cache:
                    del self.api_key_cache[organization_id]
                logger.error(f"💥 Failed to create connection for org {organization_id}: {e}")
                raise
    
    @contextmanager
    def get_connection_context(self, organization_id: str, api_key: Optional[str] = None):
        """
        Context manager for AutoTrader connections with automatic error tracking.
        
        Usage:
            with pool.get_connection_context(org_id, api_key) as conn:
                response = conn.place_order(...)
        """
        conn = self.get_connection(organization_id, api_key)
        try:
            yield conn
        except Exception as e:
            # Mark connection as having an error
            with self._lock:
                if organization_id in self.connections:
                    self.connections[organization_id].mark_error()
            raise
    
    def invalidate_connection(self, organization_id: str):
        """Manually invalidate a connection (e.g., on authentication failure)"""
        with self._lock:
            if organization_id in self.connections:
                logger.info(f"Invalidating connection for org {organization_id}")
                del self.connections[organization_id]
            if organization_id in self.api_key_cache:
                del self.api_key_cache[organization_id]
    
    def get_connection_stats(self) -> Dict:
        """Get statistics about the connection pool"""
        with self._lock:
            stats = {
                "total_connections": len(self.connections),
                "healthy_connections": sum(1 for c in self.connections.values() if c.is_healthy),
                "cached_api_keys": len(self.api_key_cache),
                "last_reset": self.last_reset.isoformat(),
                "connections": {}
            }
            
            for org_id, conn in self.connections.items():
                stats["connections"][org_id] = {
                    "created_at": conn.created_at.isoformat(),
                    "last_used": conn.last_used.isoformat(),
                    "request_count": conn.request_count,
                    "error_count": conn.error_count,
                    "is_healthy": conn.is_healthy
                }
            
            return stats
    
    def reset_all(self):
        """Reset all connections (called at midnight or manually)"""
        with self._lock:
            logger.info(f"Resetting all {len(self.connections)} connections")
            self.connections.clear()
            self.api_key_cache.clear()
            self.last_reset = datetime.utcnow()
    
    def cleanup_stale_connections(self):
        """Remove stale connections (can be called periodically)"""
        with self._lock:
            stale_orgs = [
                org_id for org_id, conn in self.connections.items()
                if conn.is_stale(self.max_connection_age_hours)
            ]
            
            for org_id in stale_orgs:
                logger.info(f"Removing stale connection for org {org_id}")
                del self.connections[org_id]
            
            return len(stale_orgs)

# Global instance
autotrader_pool = AutoTraderConnectionPool()