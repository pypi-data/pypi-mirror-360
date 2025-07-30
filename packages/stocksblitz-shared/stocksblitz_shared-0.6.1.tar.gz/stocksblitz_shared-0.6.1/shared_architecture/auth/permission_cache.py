# shared_architecture/auth/permission_cache.py
"""
Redis-based permission caching system for high-performance permission checking.
Reduces load on user_service and provides fast permission validation.
"""

import json
import redis
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import asyncio
from ..utils.enhanced_logging import get_logger
from ..config.global_settings import get_settings

logger = get_logger(__name__)

class PermissionCache:
    """Redis-based permission caching for performance optimization."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self._initialized = False
        
    async def initialize(self):
        """Initialize Redis connection."""
        if self._initialized:
            return
            
        try:
            if not self.redis_client:
                settings = get_settings()
                import os
                redis_host = os.getenv("REDIS_HOST", "localhost")
                redis_port = os.getenv("REDIS_PORT", "6379")
                redis_password = os.getenv("REDIS_PASSWORD", "")
                if redis_password:
                    redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}"
                else:
                    redis_url = f"redis://{redis_host}:{redis_port}"
                redis_url = settings.REDIS_URL or redis_url
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Test connection
            self.redis_client.ping()
            self._initialized = True
            logger.info("Permission cache initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize permission cache: {e}")
            self._initialized = False
    
    async def get_cached_permissions(
        self, 
        user_id: str, 
        organization_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get permissions from cache."""
        if not self._initialized:
            await self.initialize()
            
        if not self._initialized:
            return None
            
        try:
            cache_key = self._get_cache_key(user_id, organization_id)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                permissions = json.loads(cached_data)
                
                # Check if cache is still valid
                cached_time = datetime.fromisoformat(permissions.get('cached_at', ''))
                ttl_minutes = permissions.get('ttl_minutes', 5)
                
                if datetime.now() - cached_time < timedelta(minutes=ttl_minutes):
                    logger.debug(f"Cache hit for user {user_id}")
                    return permissions['data']
                else:
                    # Cache expired, remove it
                    self.redis_client.delete(cache_key)
                    logger.debug(f"Cache expired for user {user_id}")
            
            return None
            
        except Exception as e:
            logger.exception(f"Error reading from permission cache: {e}")
            return None
    
    async def set_cached_permissions(
        self, 
        user_id: str, 
        organization_id: Optional[str], 
        permissions: Dict[str, Any], 
        ttl_minutes: int = 5
    ):
        """Cache permissions with TTL."""
        if not self._initialized:
            await self.initialize()
            
        if not self._initialized:
            return
            
        try:
            cache_key = self._get_cache_key(user_id, organization_id)
            
            cache_data = {
                'data': permissions,
                'cached_at': datetime.now().isoformat(),
                'ttl_minutes': ttl_minutes,
                'user_id': user_id,
                'organization_id': organization_id
            }
            
            # Set with Redis TTL as backup
            redis_ttl_seconds = ttl_minutes * 60 + 60  # Add 1 minute buffer
            
            self.redis_client.setex(
                cache_key,
                redis_ttl_seconds,
                json.dumps(cache_data)
            )
            
            logger.debug(f"Cached permissions for user {user_id}")
            
        except Exception as e:
            logger.exception(f"Error writing to permission cache: {e}")
    
    async def invalidate_user_permissions(self, user_id: str):
        """Invalidate all cached permissions for user."""
        if not self._initialized:
            return
            
        try:
            # Get all keys for this user
            pattern = f"permissions:user:{user_id}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} permission cache entries for user {user_id}")
            
        except Exception as e:
            logger.exception(f"Error invalidating user permissions cache: {e}")
    
    async def invalidate_organization_permissions(self, organization_id: str):
        """Invalidate permissions for entire organization."""
        if not self._initialized:
            return
            
        try:
            # Get all keys for this organization
            pattern = f"permissions:user:*:org:{organization_id}"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} permission cache entries for organization {organization_id}")
            
        except Exception as e:
            logger.exception(f"Error invalidating organization permissions cache: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get permission cache statistics."""
        if not self._initialized:
            return {'status': 'not_initialized'}
            
        try:
            pattern = "permissions:user:*"
            keys = self.redis_client.keys(pattern)
            
            total_entries = len(keys)
            
            # Get memory usage info
            info = self.redis_client.info('memory')
            
            return {
                'status': 'healthy',
                'total_cached_permissions': total_entries,
                'redis_memory_used': info.get('used_memory_human', 'unknown'),
                'redis_connected_clients': self.redis_client.info().get('connected_clients', 0)
            }
            
        except Exception as e:
            logger.exception(f"Error getting cache stats: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def warm_cache_for_users(self, user_ids: List[str], organization_id: str):
        """Pre-warm cache for multiple users (useful for startup)."""
        if not self._initialized:
            return
            
        logger.info(f"Warming permission cache for {len(user_ids)} users")
        
        # This would typically fetch from user_service in batch
        # For now, we'll just mark the intent
        for user_id in user_ids:
            cache_key = self._get_cache_key(user_id, organization_id)
            
            # Set a placeholder to indicate cache warming is needed
            warm_data = {
                'status': 'warming',
                'user_id': user_id,
                'organization_id': organization_id,
                'created_at': datetime.now().isoformat()
            }
            
            try:
                self.redis_client.setex(
                    f"warm:{cache_key}",
                    300,  # 5 minutes
                    json.dumps(warm_data)
                )
            except Exception as e:
                logger.exception(f"Error warming cache for user {user_id}: {e}")
    
    def _get_cache_key(self, user_id: str, organization_id: Optional[str] = None) -> str:
        """Generate cache key for user permissions."""
        if organization_id:
            return f"permissions:user:{user_id}:org:{organization_id}"
        else:
            return f"permissions:user:{user_id}:default"
    
    async def cleanup_expired_cache(self):
        """Clean up expired cache entries (called periodically)."""
        if not self._initialized:
            return
            
        try:
            pattern = "permissions:user:*"
            keys = self.redis_client.keys(pattern)
            
            expired_count = 0
            for key in keys:
                try:
                    cached_data = self.redis_client.get(key)
                    if cached_data:
                        permissions = json.loads(cached_data)
                        cached_time = datetime.fromisoformat(permissions.get('cached_at', ''))
                        ttl_minutes = permissions.get('ttl_minutes', 5)
                        
                        if datetime.now() - cached_time >= timedelta(minutes=ttl_minutes):
                            self.redis_client.delete(key)
                            expired_count += 1
                            
                except Exception as e:
                    logger.warning(f"Error checking cache entry {key}: {e}")
                    # Delete problematic entries
                    self.redis_client.delete(key)
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired permission cache entries")
                
        except Exception as e:
            logger.exception(f"Error during cache cleanup: {e}")

# Global cache instance
permission_cache = PermissionCache()


# Permission cache monitoring
class PermissionCacheMonitor:
    """Monitor permission cache performance and health."""
    
    def __init__(self, cache: PermissionCache):
        self.cache = cache
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_errors': 0,
            'last_cleanup': None
        }
    
    async def record_hit(self):
        """Record cache hit."""
        self.stats['cache_hits'] += 1
    
    async def record_miss(self):
        """Record cache miss."""
        self.stats['cache_misses'] += 1
    
    async def record_error(self):
        """Record cache error."""
        self.stats['cache_errors'] += 1
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_ratio = self.stats['cache_hits'] / max(total_requests, 1)
        
        cache_stats = await self.cache.get_cache_stats()
        
        return {
            'performance': {
                'cache_hits': self.stats['cache_hits'],
                'cache_misses': self.stats['cache_misses'],
                'cache_errors': self.stats['cache_errors'],
                'hit_ratio': round(hit_ratio * 100, 2),
                'total_requests': total_requests
            },
            'cache_info': cache_stats,
            'last_cleanup': self.stats['last_cleanup']
        }
    
    async def periodic_cleanup(self):
        """Perform periodic cache cleanup."""
        await self.cache.cleanup_expired_cache()
        self.stats['last_cleanup'] = datetime.now().isoformat()

# Global monitor instance
cache_monitor = PermissionCacheMonitor(permission_cache)