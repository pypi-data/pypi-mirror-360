# shared_architecture/utils/redis_cache.py
"""
Simple Redis cache utility for licensing and permission caching
"""

import json
from typing import Optional, Any
import redis.asyncio as redis
from shared_architecture.utils.enhanced_logging import get_logger

logger = get_logger(__name__)


class RedisCache:
    """Simple async Redis cache wrapper"""
    
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379",
        prefix: str = "cache",
        db: int = 0
    ):
        self.redis_url = redis_url
        self.prefix = prefix
        self.db = db
        self._client = None
        
    async def _get_client(self):
        """Get or create Redis client"""
        if self._client is None:
            self._client = await redis.from_url(
                self.redis_url,
                db=self.db,
                decode_responses=True
            )
        return self._client
    
    def _make_key(self, key: str) -> str:
        """Create namespaced key"""
        return f"{self.prefix}:{key}"
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            client = await self._get_client()
            return await client.get(self._make_key(key))
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional expiry"""
        try:
            client = await self._get_client()
            key = self._make_key(key)
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if expire:
                return await client.setex(key, expire, value)
            else:
                return await client.set(key, value)
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            client = await self._get_client()
            result = await client.delete(self._make_key(key))
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False
    
    async def increment(
        self, 
        key: str, 
        amount: int = 1,
        expire: Optional[int] = None
    ) -> int:
        """Increment counter with optional expiry"""
        try:
            client = await self._get_client()
            key = self._make_key(key)
            
            # Use pipeline for atomic increment + expire
            async with client.pipeline() as pipe:
                pipe.incr(key, amount)
                if expire:
                    pipe.expire(key, expire)
                results = await pipe.execute()
                return results[0]  # Return new value
        except Exception as e:
            logger.error(f"Redis increment error: {str(e)}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            client = await self._get_client()
            return await client.exists(self._make_key(key)) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {str(e)}")
            return False
    
    async def close(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            self._client = None