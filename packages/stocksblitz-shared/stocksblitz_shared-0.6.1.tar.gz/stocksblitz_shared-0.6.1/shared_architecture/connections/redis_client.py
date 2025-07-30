# shared_architecture/connections/redis_client.py

import redis.asyncio as redis
from redis.cluster import RedisCluster
import logging
import os
from typing import Optional, Union
from shared_architecture.config.config_loader import config_loader
from shared_architecture.connections.service_discovery import service_discovery, ServiceType

logger = logging.getLogger(__name__)

def get_redis_client() -> Union[redis.Redis, RedisCluster]:
    """Create a Redis client with connection pooling and service discovery
    
    Supports both single Redis container (dev) and Redis cluster (prod)
    """
    try:
        # Ensure config is loaded
        if not hasattr(config_loader, 'common_config') or not config_loader.common_config:
            # Try to load config with a default service name
            try:
                config_loader.load("ticker_service")
            except Exception:
                pass  # Config might already be loaded or unavailable
        
        # Check environment and Redis mode
        environment = config_loader.get("ENVIRONMENT", "local", scope="all").lower()
        redis_mode = config_loader.get("REDIS_MODE", "single", scope="all").lower()  # single or cluster
        
        redis_host_config = config_loader.get("REDIS_HOST", os.getenv("REDIS_HOST", "localhost"), scope="all")
        redis_port = int(config_loader.get("REDIS_PORT", os.getenv("REDIS_PORT", "6379"), scope="all"))
        redis_password = config_loader.get("REDIS_PASSWORD", None, scope="all")
        redis_username = config_loader.get("REDIS_USERNAME", None, scope="all")

        # Resolve the actual host to use
        redis_host = service_discovery.resolve_service_host(redis_host_config, ServiceType.REDIS)
        
        # Log connection info
        connection_info = service_discovery.get_connection_info(redis_host_config, ServiceType.REDIS)
        logger.info(f"Redis connection info: {connection_info}")
        
        # Determine Redis client type based on environment and configuration
        if redis_mode == "cluster" and environment in ["production", "staging"]:
            # Production: Use Redis Cluster
            cluster_nodes = config_loader.get("REDIS_CLUSTER_NODES", f"{redis_host}:{redis_port}", scope="all")
            nodes = []
            
            for node in cluster_nodes.split(","):
                node = node.strip()
                if ":" in node:
                    host, port = node.split(":")
                    nodes.append({"host": host, "port": int(port)})
                else:
                    nodes.append({"host": node, "port": redis_port})
            
            cluster_auth_params = {
                "startup_nodes": nodes,
                "decode_responses": True,
                "socket_connect_timeout": 5,
                "socket_timeout": 5,
                "retry_on_timeout": True,
                "health_check_interval": 0,  # Disable health check to avoid recursion
                "max_connections": 20,
                "skip_full_coverage_check": True  # Allow partial cluster for dev/test
            }
            
            # Add authentication if configured
            if redis_password:
                cluster_auth_params["password"] = redis_password
            if redis_username:
                cluster_auth_params["username"] = redis_username
                
            client = RedisCluster(**cluster_auth_params)
            logger.info(f"✅ Redis cluster client created with nodes: {nodes}")
            
        else:
            # Development: Use single Redis instance
            single_auth_params = {
                "host": redis_host,
                "port": redis_port,
                "decode_responses": True,
                "socket_connect_timeout": 5,
                "socket_timeout": 5,
                "retry_on_timeout": True,
                "health_check_interval": 0,  # Disable health check to avoid recursion
                "max_connections": 20  # Connection pool size
            }
            
            # Add authentication if configured
            if redis_password:
                single_auth_params["password"] = redis_password
            if redis_username:
                single_auth_params["username"] = redis_username
            
            client = redis.Redis(**single_auth_params)
            auth_info = f" (with auth)" if redis_password else " (no auth)"
            logger.info(f"✅ Redis single-node client created for {redis_host}:{redis_port}{auth_info}")
        
        return client
        
    except Exception as e:
        logger.error(f"❌ Failed to create Redis client: {e}")
        return None