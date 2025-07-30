from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import asyncio

class BaseServiceEndpoints:
    """Standard API endpoints for all microservices."""
    
    @staticmethod
    def create_health_router(service_name: str, redis_manager=None, additional_checks=None) -> APIRouter:
        """Create standard health check endpoints."""
        router = APIRouter(prefix="/health", tags=["health"])
        
        @router.get("/")
        async def get_health() -> Dict[str, Any]:
            """Overall service health check."""
            checks = {
                "service": service_name,
                "status": "healthy",
                "checks": {}
            }
            
            # Database check
            try:
                from shared_architecture.core.connections import get_async_db
                async with get_async_db() as db:
                    await db.execute("SELECT 1")
                checks["checks"]["database"] = "healthy"
            except Exception as e:
                checks["checks"]["database"] = f"unhealthy: {str(e)}"
                checks["status"] = "unhealthy"
            
            # Redis check
            if redis_manager:
                redis_health = await redis_manager.health_check()
                checks["checks"]["redis"] = redis_health["status"]
                if redis_health["status"] != "healthy":
                    checks["status"] = "unhealthy"
            
            # Additional service-specific checks
            if additional_checks:
                for check_name, check_func in additional_checks.items():
                    try:
                        check_result = await check_func()
                        checks["checks"][check_name] = "healthy" if check_result else "unhealthy"
                        if not check_result:
                            checks["status"] = "unhealthy"
                    except Exception as e:
                        checks["checks"][check_name] = f"unhealthy: {str(e)}"
                        checks["status"] = "unhealthy"
            
            return checks
        
        @router.get("/live")
        async def get_liveness() -> Dict[str, str]:
            """Kubernetes liveness probe."""
            return {"status": "alive", "service": service_name}
        
        @router.get("/ready")
        async def get_readiness() -> Dict[str, Any]:
            """Kubernetes readiness probe."""
            # Simple readiness check - can the service handle requests?
            try:
                # Quick database connectivity check
                from shared_architecture.core.connections import get_async_db
                async with get_async_db() as db:
                    await db.execute("SELECT 1")
                
                return {
                    "status": "ready",
                    "service": service_name,
                    "message": "Service is ready to handle requests"
                }
            except Exception as e:
                raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")
        
        return router
    
    @staticmethod
    def create_info_router(service_name: str, version: str = "1.0.0") -> APIRouter:
        """Create service info endpoint."""
        router = APIRouter(tags=["info"])
        
        @router.get("/")
        async def service_info() -> Dict[str, str]:
            """Service information."""
            return {
                "service": service_name,
                "version": version,
                "status": "running"
            }
        
        @router.get("/docs-info")
        async def docs_info() -> Dict[str, str]:
            """API documentation information."""
            return {
                "service": service_name,
                "docs_url": "/docs",
                "redoc_url": "/redoc",
                "openapi_url": "/openapi.json"
            }
        
        return router