"""
Health Check System for StocksBlitz Platform

This module provides comprehensive health checking capabilities for all microservices,
including dependency health checks, system resource monitoring, and business logic validation.

Features:
- Service dependency health checks (database, Redis, external APIs)
- System resource monitoring (CPU, memory, disk)
- Business logic health validation
- Prometheus metrics integration
- Configurable health check endpoints
- Graceful degradation support
"""

import asyncio
import logging
import time
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

# Database and cache imports
try:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:
    pass

try:
    import redis.asyncio as redis
except ImportError:
    pass

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Individual health check result"""
    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


@dataclass
class SystemHealth:
    """Overall system health status"""
    service_name: str
    status: HealthStatus
    timestamp: datetime
    uptime_seconds: float
    version: str
    environment: str
    checks: List[HealthCheckResult]
    system_metrics: Dict[str, Any]


class HealthCheckResponse(BaseModel):
    """Health check API response model"""
    service_name: str
    status: str
    timestamp: str
    uptime_seconds: float
    version: str
    environment: str
    checks: List[Dict[str, Any]]
    system_metrics: Dict[str, Any]


class HealthChecker:
    """Main health checker class"""
    
    def __init__(self, service_name: str, version: str = "1.0.0"):
        self.service_name = service_name
        self.version = version
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.start_time = time.time()
        
        # Health check registry
        self._health_checks: Dict[str, Callable] = {}
        self._dependency_checks: Dict[str, Callable] = {}
        self._business_checks: Dict[str, Callable] = {}
        
        # System components
        self.db_session = None
        self.redis_client = None
        
        # Register default system checks
        self.register_health_check("system_resources", self._check_system_resources)
        self.register_health_check("service_uptime", self._check_service_uptime)
        
        logger.info(f"Health checker initialized for {service_name}")
    
    def register_health_check(self, name: str, check_func: Callable) -> None:
        """Register a health check function"""
        self._health_checks[name] = check_func
        logger.debug(f"Registered health check: {name}")
    
    def register_dependency_check(self, name: str, check_func: Callable) -> None:
        """Register a dependency health check"""
        self._dependency_checks[name] = check_func
        logger.debug(f"Registered dependency check: {name}")
    
    def register_business_check(self, name: str, check_func: Callable) -> None:
        """Register a business logic health check"""
        self._business_checks[name] = check_func
        logger.debug(f"Registered business check: {name}")
    
    def set_database_session(self, session: Any) -> None:
        """Set database session for health checks"""
        self.db_session = session
        self.register_dependency_check("database", self._check_database)
    
    def set_redis_client(self, client: Any) -> None:
        """Set Redis client for health checks"""
        self.redis_client = client
        self.register_dependency_check("redis", self._check_redis)
    
    async def _run_check(self, name: str, check_func: Callable) -> HealthCheckResult:
        """Run an individual health check"""
        start_time = time.time()
        timestamp = datetime.utcnow()
        
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            duration_ms = (time.time() - start_time) * 1000
            
            if isinstance(result, dict):
                status = HealthStatus(result.get("status", HealthStatus.HEALTHY))
                message = result.get("message", "Check passed")
                details = result.get("details")
            elif isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = "Check passed" if result else "Check failed"
                details = None
            else:
                status = HealthStatus.HEALTHY
                message = str(result) if result else "Check passed"
                details = None
            
            return HealthCheckResult(
                name=name,
                status=status,
                message=message,
                duration_ms=duration_ms,
                timestamp=timestamp,
                details=details
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Health check {name} failed: {e}")
            
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}",
                duration_ms=duration_ms,
                timestamp=timestamp,
                details={"error": str(e)}
            )
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Determine status based on thresholds
            status = HealthStatus.HEALTHY
            messages = []
            
            if cpu_percent > 90:
                status = HealthStatus.UNHEALTHY
                messages.append(f"CPU usage critical: {cpu_percent}%")
            elif cpu_percent > 70:
                status = HealthStatus.DEGRADED
                messages.append(f"CPU usage high: {cpu_percent}%")
            
            if memory_percent > 90:
                status = HealthStatus.UNHEALTHY
                messages.append(f"Memory usage critical: {memory_percent}%")
            elif memory_percent > 80:
                status = HealthStatus.DEGRADED
                messages.append(f"Memory usage high: {memory_percent}%")
            
            if disk_percent > 95:
                status = HealthStatus.UNHEALTHY
                messages.append(f"Disk usage critical: {disk_percent}%")
            elif disk_percent > 85:
                status = HealthStatus.DEGRADED
                messages.append(f"Disk usage high: {disk_percent}%")
            
            return {
                "status": status,
                "message": "; ".join(messages) if messages else "System resources normal",
                "details": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_percent": disk_percent,
                    "memory_total_gb": round(memory.total / (1024**3), 2),
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "disk_total_gb": round(disk.total / (1024**3), 2),
                    "disk_free_gb": round(disk.free / (1024**3), 2)
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": f"Failed to check system resources: {e}",
                "details": {"error": str(e)}
            }
    
    async def _check_service_uptime(self) -> Dict[str, Any]:
        """Check service uptime and basic metrics"""
        uptime_seconds = time.time() - self.start_time
        uptime_hours = uptime_seconds / 3600
        
        status = HealthStatus.HEALTHY
        message = f"Service running for {uptime_hours:.1f} hours"
        
        # Consider service unhealthy if it just started (less than 30 seconds)
        if uptime_seconds < 30:
            status = HealthStatus.DEGRADED
            message = "Service recently started"
        
        return {
            "status": status,
            "message": message,
            "details": {
                "uptime_seconds": uptime_seconds,
                "uptime_hours": uptime_hours,
                "start_time": datetime.fromtimestamp(self.start_time).isoformat()
            }
        }
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        if not self.db_session:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": "Database session not configured"
            }
        
        try:
            start_time = time.time()
            
            # Simple connectivity test
            if hasattr(self.db_session, '__call__'):
                # AsyncSession factory
                async with self.db_session() as session:
                    result = await session.execute(text("SELECT 1"))
                    await session.commit()
            else:
                # Direct session
                result = await self.db_session.execute(text("SELECT 1"))
                await self.db_session.commit()
            
            query_time_ms = (time.time() - start_time) * 1000
            
            status = HealthStatus.HEALTHY
            message = f"Database responsive ({query_time_ms:.1f}ms)"
            
            # Consider degraded if query takes too long
            if query_time_ms > 1000:  # 1 second
                status = HealthStatus.DEGRADED
                message = f"Database slow ({query_time_ms:.1f}ms)"
            
            return {
                "status": status,
                "message": message,
                "details": {
                    "query_time_ms": query_time_ms,
                    "connection_pool_size": getattr(self.db_session, 'get_bind', lambda: None)() and 
                                          getattr(self.db_session.get_bind().pool, 'size', None)
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Database check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance"""
        if not self.redis_client:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": "Redis client not configured"
            }
        
        try:
            start_time = time.time()
            
            # Ping Redis
            pong = await self.redis_client.ping()
            ping_time_ms = (time.time() - start_time) * 1000
            
            # Get Redis info
            info = await self.redis_client.info()
            
            status = HealthStatus.HEALTHY
            message = f"Redis responsive ({ping_time_ms:.1f}ms)"
            
            # Check Redis memory usage
            used_memory = info.get('used_memory', 0)
            max_memory = info.get('maxmemory', 0)
            
            if max_memory > 0:
                used_memory_percent = (used_memory / max_memory) * 100
                if used_memory_percent > 90:
                    status = HealthStatus.DEGRADED
                    message = f"Redis memory high ({used_memory_percent:.1f}%)"
            else:
                used_memory_percent = 0  # No memory limit set
            
            # Consider degraded if ping takes too long
            if ping_time_ms > 100:  # 100ms
                status = HealthStatus.DEGRADED
                message = f"Redis slow ({ping_time_ms:.1f}ms)"
            
            return {
                "status": status,
                "message": message,
                "details": {
                    "ping_time_ms": ping_time_ms,
                    "connected_clients": info.get('connected_clients', 0),
                    "used_memory_mb": round(info.get('used_memory', 0) / (1024*1024), 2),
                    "memory_usage_percent": round(used_memory_percent, 1),
                    "uptime_seconds": info.get('uptime_in_seconds', 0)
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Redis check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            
            # Process info
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "network_bytes_sent": net_io.bytes_sent,
                "network_bytes_recv": net_io.bytes_recv,
                "process_memory_mb": round(process_memory.rss / (1024*1024), 2),
                "process_cpu_percent": process.cpu_percent(),
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {"error": str(e)}
    
    async def run_all_checks(self) -> SystemHealth:
        """Run all registered health checks"""
        all_checks = {}
        all_checks.update(self._health_checks)
        all_checks.update(self._dependency_checks)
        all_checks.update(self._business_checks)
        
        # Run all checks concurrently
        check_tasks = [
            self._run_check(name, check_func)
            for name, check_func in all_checks.items()
        ]
        
        check_results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        # Filter out exceptions and create results
        valid_results = []
        for result in check_results:
            if isinstance(result, HealthCheckResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Health check exception: {result}")
        
        # Determine overall status
        overall_status = HealthStatus.HEALTHY
        for result in valid_results:
            if result.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
                break
            elif result.status == HealthStatus.DEGRADED:
                overall_status = HealthStatus.DEGRADED
        
        return SystemHealth(
            service_name=self.service_name,
            status=overall_status,
            timestamp=datetime.utcnow(),
            uptime_seconds=time.time() - self.start_time,
            version=self.version,
            environment=self.environment,
            checks=valid_results,
            system_metrics=self._get_system_metrics()
        )
    
    def create_router(self) -> APIRouter:
        """Create FastAPI router with health endpoints"""
        router = APIRouter()
        
        @router.get("/health", response_model=HealthCheckResponse)
        async def health_check(response: Response):
            """Main health check endpoint"""
            health = await self.run_all_checks()
            
            # Set HTTP status code based on health
            if health.status == HealthStatus.UNHEALTHY:
                response.status_code = 503  # Service Unavailable
            elif health.status == HealthStatus.DEGRADED:
                response.status_code = 200  # OK but degraded
            else:
                response.status_code = 200  # OK
            
            return HealthCheckResponse(
                service_name=health.service_name,
                status=health.status.value,
                timestamp=health.timestamp.isoformat(),
                uptime_seconds=health.uptime_seconds,
                version=health.version,
                environment=health.environment,
                checks=[asdict(check) for check in health.checks],
                system_metrics=health.system_metrics
            )
        
        @router.get("/health/live")
        async def liveness_check():
            """Kubernetes liveness probe endpoint"""
            # Simple check - if the service is running, it's alive
            return {
                "status": "alive",
                "timestamp": datetime.utcnow().isoformat(),
                "service": self.service_name
            }
        
        @router.get("/health/ready")
        async def readiness_check(response: Response):
            """Kubernetes readiness probe endpoint"""
            health = await self.run_all_checks()
            
            # Service is ready if not unhealthy
            if health.status == HealthStatus.UNHEALTHY:
                response.status_code = 503
                return {
                    "status": "not_ready",
                    "timestamp": health.timestamp.isoformat(),
                    "service": self.service_name
                }
            
            return {
                "status": "ready",
                "timestamp": health.timestamp.isoformat(),
                "service": self.service_name
            }
        
        @router.get("/health/dependencies")
        async def dependencies_check():
            """Check only dependency health"""
            dependency_tasks = [
                self._run_check(name, check_func)
                for name, check_func in self._dependency_checks.items()
            ]
            
            if not dependency_tasks:
                return {"status": "no_dependencies", "checks": []}
            
            results = await asyncio.gather(*dependency_tasks, return_exceptions=True)
            valid_results = [r for r in results if isinstance(r, HealthCheckResult)]
            
            # Determine dependency status
            status = "healthy"
            for result in valid_results:
                if result.status == HealthStatus.UNHEALTHY:
                    status = "unhealthy"
                    break
                elif result.status == HealthStatus.DEGRADED:
                    status = "degraded"
            
            return {
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "checks": [asdict(check) for check in valid_results]
            }
        
        return router


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> Optional[HealthChecker]:
    """Get the global health checker instance"""
    return _health_checker


def initialize_health_checker(service_name: str, version: str = "1.0.0") -> HealthChecker:
    """Initialize the global health checker"""
    global _health_checker
    _health_checker = HealthChecker(service_name, version)
    return _health_checker


def register_health_check(name: str, check_func: Callable) -> None:
    """Register a health check with the global checker"""
    if _health_checker:
        _health_checker.register_health_check(name, check_func)


def register_dependency_check(name: str, check_func: Callable) -> None:
    """Register a dependency check with the global checker"""
    if _health_checker:
        _health_checker.register_dependency_check(name, check_func)