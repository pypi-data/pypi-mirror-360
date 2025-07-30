from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from shared_architecture.connections.redis_cluster_manager import get_cluster_manager
from shared_architecture.config.redis_cluster_config import format_key

class BaseRedisServiceManager(ABC):
    """Base Redis manager for all microservices with common patterns."""
    
    def __init__(self, service_name: str):
        self.cluster_manager = get_cluster_manager()
        self.service_name = service_name
        self.key_prefix = f"{service_name}:"
    
    def format_service_key(self, key_type: str, identifier: str) -> str:
        """Format Redis key with service prefix."""
        return format_key(f"{self.service_name}:{key_type}", identifier)
    
    async def store_user_data(self, user_id: str, data_type: str, 
                             data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Standard user data storage pattern used by all services."""
        key = self.format_service_key(f"user:{data_type}", user_id)
        return await self.cluster_manager.store_json_with_expiry(key, data, ttl)
    
    async def get_user_data(self, user_id: str, data_type: str) -> Optional[Dict[str, Any]]:
        """Standard user data retrieval pattern used by all services."""
        key = self.format_service_key(f"user:{data_type}", user_id)
        return await self.cluster_manager.get_json(key)
    
    async def delete_user_data(self, user_id: str, data_type: str) -> bool:
        """Standard user data deletion pattern."""
        key = self.format_service_key(f"user:{data_type}", user_id)
        return await self.cluster_manager.delete_key(key)
    
    async def store_session_data(self, session_id: str, session_data: Dict[str, Any], 
                                ttl: int = 3600) -> bool:
        """Standard session storage pattern."""
        key = self.format_service_key("session", session_id)
        return await self.cluster_manager.store_json_with_expiry(key, session_data, ttl)
    
    async def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Standard session retrieval pattern."""
        key = self.format_service_key("session", session_id)
        return await self.cluster_manager.get_json(key)
    
    async def store_cache_data(self, cache_key: str, data: Any, ttl: int = 300) -> bool:
        """Standard cache storage pattern."""
        key = self.format_service_key("cache", cache_key)
        return await self.cluster_manager.store_json_with_expiry(key, data, ttl)
    
    async def get_cache_data(self, cache_key: str) -> Optional[Any]:
        """Standard cache retrieval pattern."""
        key = self.format_service_key("cache", cache_key)
        return await self.cluster_manager.get_json(key)
    
    async def increment_counter(self, counter_name: str, increment: int = 1) -> int:
        """Standard counter pattern for metrics/rate limiting."""
        key = self.format_service_key("counter", counter_name)
        return await self.cluster_manager.increment(key, increment)
    
    async def set_expiry(self, key_type: str, identifier: str, ttl: int) -> bool:
        """Set expiry on existing key."""
        key = self.format_service_key(key_type, identifier)
        return await self.cluster_manager.set_expiry(key, ttl)
    
    @abstractmethod
    async def initialize_service_data(self):
        """Service-specific initialization - must be implemented by each service."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Standard Redis health check for all services."""
        try:
            # Test basic connectivity
            await self.cluster_manager.ping()
            
            # Test key operations
            test_key = self.format_service_key("health", "test")
            await self.cluster_manager.store_json_with_expiry(test_key, {"test": True}, 10)
            test_data = await self.cluster_manager.get_json(test_key)
            await self.cluster_manager.delete_key(test_key)
            
            if test_data and test_data.get("test"):
                return {"status": "healthy", "service": self.service_name}
            else:
                return {"status": "unhealthy", "error": "Key operations failed"}
                
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}