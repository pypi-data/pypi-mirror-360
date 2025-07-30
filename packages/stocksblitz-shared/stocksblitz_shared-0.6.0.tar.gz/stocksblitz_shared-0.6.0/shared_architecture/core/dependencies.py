"""
Shared database and service dependencies for all microservices
Provides standardized database session management and common dependencies
"""

from typing import AsyncGenerator, Generator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from fastapi import Depends, Request, HTTPException
from redis.asyncio import Redis
import logging

from shared_architecture.utils.logging_utils import log_warning, log_exception

async def get_async_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session from connection manager
    
    This dependency provides access to the async TimescaleDB session
    for database operations that support async/await patterns.
    
    Usage in FastAPI endpoints:
        async def my_endpoint(db: AsyncSession = Depends(get_async_db)):
            # Use db for async database operations
    """
    if hasattr(request.app.state, 'connections') and request.app.state.connections.get('timescaledb'):
        session_factory = request.app.state.connections['timescaledb']
        async with session_factory() as session:
            try:
                yield session
            except Exception as e:
                log_exception(f"Error in async database session: {e}")
                await session.rollback()
                raise
            finally:
                await session.close()
    else:
        log_warning("Async database connection not available")
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )

def get_sync_db(request: Request) -> Generator[Session, None, None]:
    """
    Get synchronous database session from connection manager
    
    This dependency provides access to the sync TimescaleDB session
    for database operations that use traditional synchronous patterns.
    
    Usage in FastAPI endpoints:
        def my_endpoint(db: Session = Depends(get_sync_db)):
            # Use db for sync database operations
    """
    if hasattr(request.app.state, 'connections') and request.app.state.connections.get('timescaledb_sync'):
        session_factory = request.app.state.connections['timescaledb_sync']
        db = session_factory()
        try:
            yield db
        except Exception as e:
            log_exception(f"Error in sync database session: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    else:
        log_warning("Sync database connection not available")
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )

async def get_redis(request: Request) -> Redis:
    """
    Get Redis connection from connection manager
    
    This dependency provides access to the Redis connection for
    caching, session storage, and other Redis operations.
    
    Usage in FastAPI endpoints:
        async def my_endpoint(redis: Redis = Depends(get_redis)):
            # Use redis for cache operations
    """
    if hasattr(request.app.state, 'connections') and request.app.state.connections.get('redis'):
        redis_client = request.app.state.connections['redis']
        if redis_client:
            return redis_client
    
    log_warning("Redis connection not available")
    raise HTTPException(
        status_code=503,
        detail="Redis connection not available"
    )

def get_redis_cluster_manager(request: Request):
    """
    Get Redis cluster manager from connection manager
    
    This dependency provides access to the Redis cluster manager for
    advanced Redis operations across cluster nodes.
    
    Usage in FastAPI endpoints:
        def my_endpoint(cluster_mgr = Depends(get_redis_cluster_manager)):
            # Use cluster manager for advanced Redis operations
    """
    if hasattr(request.app.state, 'connections') and request.app.state.connections.get('redis_cluster_manager'):
        return request.app.state.connections['redis_cluster_manager']
    
    log_warning("Redis cluster manager not available")
    raise HTTPException(
        status_code=503,
        detail="Redis cluster manager not available"
    )

def get_service_config(request: Request):
    """
    Get service configuration from app state
    
    This dependency provides access to the service's configuration
    settings and environment variables.
    
    Usage in FastAPI endpoints:
        def my_endpoint(config = Depends(get_service_config)):
            # Use config for service settings
    """
    if hasattr(request.app.state, 'config'):
        return request.app.state.config
    elif hasattr(request.app.state, 'settings'):
        return request.app.state.settings
    
    log_warning("Service configuration not available")
    raise HTTPException(
        status_code=503,
        detail="Service configuration not available"
    )

def get_broker_instance(request: Request):
    """
    Get broker instance from app state (for ticker/trade services)
    
    This dependency provides access to the broker instance for
    services that need to interact with trading brokers.
    
    Usage in FastAPI endpoints:
        def my_endpoint(broker = Depends(get_broker_instance)):
            # Use broker for trading operations
    """
    if hasattr(request.app.state, 'broker_instance'):
        return request.app.state.broker_instance
    
    log_warning("Broker instance not available")
    raise HTTPException(
        status_code=503,
        detail="Broker instance not available"
    )

def get_market_data_manager(request: Request):
    """
    Get market data manager from app state (for ticker service)
    
    This dependency provides access to the market data manager for
    services that need to handle real-time market data.
    
    Usage in FastAPI endpoints:
        def my_endpoint(mdm = Depends(get_market_data_manager)):
            # Use market data manager for tick processing
    """
    if hasattr(request.app.state, 'market_data_manager'):
        return request.app.state.market_data_manager
    
    log_warning("Market data manager not available")
    raise HTTPException(
        status_code=503,
        detail="Market data manager not available"
    )

def get_rate_limiter_manager(request: Request):
    """
    Get rate limiter manager from app state
    
    This dependency provides access to the rate limiter manager for
    services that need to implement rate limiting.
    
    Usage in FastAPI endpoints:
        def my_endpoint(rate_limiter = Depends(get_rate_limiter_manager)):
            # Use rate limiter for API throttling
    """
    if hasattr(request.app.state, 'rate_limiter_manager'):
        return request.app.state.rate_limiter_manager
    
    # Fallback to global rate limiter
    from shared_architecture.resilience.rate_limiter import get_rate_limiter_manager
    return get_rate_limiter_manager()

# Service-specific dependency factories
class DependencyFactory:
    """Factory for creating service-specific dependencies"""
    
    @staticmethod
    def create_service_dependencies(service_name: str):
        """Create a set of dependencies customized for a specific service"""
        
        dependencies = {
            'get_async_db': get_async_db,
            'get_sync_db': get_sync_db,
            'get_redis': get_redis,
            'get_config': get_service_config,
            'get_rate_limiter': get_rate_limiter_manager,
        }
        
        # Add service-specific dependencies
        if service_name == "ticker_service":
            dependencies.update({
                'get_broker': get_broker_instance,
                'get_market_data_manager': get_market_data_manager,
            })
        elif service_name == "trade_service":
            dependencies.update({
                'get_broker': get_broker_instance,
            })
        elif service_name in ["signal_service", "subscription_service"]:
            dependencies.update({
                'get_redis_cluster': get_redis_cluster_manager,
            })
        
        return dependencies

# Backward compatibility aliases
get_db = get_sync_db  # For services still using sync patterns

# Health check dependencies
def get_health_check_dependencies(request: Request):
    """
    Get all available dependencies for health check endpoints
    
    Returns a dict with the status of all available services/connections.
    """
    health_status = {}
    
    try:
        # Check async database
        if hasattr(request.app.state, 'connections') and request.app.state.connections.get('timescaledb'):
            health_status['async_database'] = 'available'
        else:
            health_status['async_database'] = 'unavailable'
        
        # Check sync database
        if hasattr(request.app.state, 'connections') and request.app.state.connections.get('timescaledb_sync'):
            health_status['sync_database'] = 'available'
        else:
            health_status['sync_database'] = 'unavailable'
        
        # Check Redis
        if hasattr(request.app.state, 'connections') and request.app.state.connections.get('redis'):
            health_status['redis'] = 'available'
        else:
            health_status['redis'] = 'unavailable'
        
        # Check configuration
        if hasattr(request.app.state, 'config') or hasattr(request.app.state, 'settings'):
            health_status['configuration'] = 'available'
        else:
            health_status['configuration'] = 'unavailable'
        
        # Check service-specific components
        if hasattr(request.app.state, 'broker_instance'):
            health_status['broker'] = 'available'
        
        if hasattr(request.app.state, 'market_data_manager'):
            health_status['market_data_manager'] = 'available'
            
    except Exception as e:
        log_exception(f"Error checking health dependencies: {e}")
        health_status['error'] = str(e)
    
    return health_status