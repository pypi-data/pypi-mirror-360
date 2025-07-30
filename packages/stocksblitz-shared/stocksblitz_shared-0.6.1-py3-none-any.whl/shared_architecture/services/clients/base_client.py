"""
Base service client for inter-service communication
Provides standardized HTTP client patterns with retry, timeout, and authentication
"""

import asyncio
import json
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timedelta
import httpx
from fastapi import HTTPException, status
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from shared_architecture.utils.logging_utils import log_info, log_warning, log_exception
from shared_architecture.resilience.rate_limiter import get_rate_limiter_manager, RateLimitConfig, RateLimitAlgorithm

class ClientError(Exception):
    """Base exception for service client errors"""
    pass

class ServiceUnavailableError(ClientError):
    """Exception raised when target service is unavailable"""
    pass

class AuthenticationError(ClientError):
    """Exception raised when authentication fails"""
    pass

class ValidationError(ClientError):
    """Exception raised when request validation fails"""
    pass

@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    retry_on_status_codes: List[int] = field(default_factory=lambda: [500, 502, 503, 504])

@dataclass 
class ClientConfig:
    """Configuration for service client"""
    base_url: str
    service_name: str
    timeout: float = 30.0
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    auth_token: Optional[str] = None
    api_key: Optional[str] = None
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 100

class BaseServiceClient(ABC):
    """
    Base class for all service clients
    
    Provides common functionality for:
    - HTTP requests with retry logic
    - Authentication handling  
    - Rate limiting
    - Error handling and logging
    - Request/response serialization
    """
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.client: Optional[httpx.AsyncClient] = None
        self.rate_limiter = None
        
        # Initialize rate limiting if enabled
        if config.rate_limit_enabled:
            rate_config = RateLimitConfig(
                requests_per_window=config.rate_limit_requests_per_minute,
                window_size=60,
                algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
                name=f"{config.service_name}_client"
            )
            self.rate_limiter = get_rate_limiter_manager()
            self.rate_limiter.add_limiter(f"{config.service_name}_client", rate_config)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Initialize HTTP client"""
        if not self.client:
            headers = self._get_default_headers()
            self.client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers=headers
            )
            log_info(f"Connected to {self.config.service_name} at {self.config.base_url}")
    
    async def disconnect(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None
            log_info(f"Disconnected from {self.config.service_name}")
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"stocksblitz-{self.config.service_name}-client/1.0"
        }
        
        # Add authentication headers
        if self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"
        
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
        
        return headers
    
    async def _apply_rate_limiting(self):
        """Apply rate limiting if enabled"""
        if self.rate_limiter:
            await self.rate_limiter.wait_for_capacity(f"{self.config.service_name}_client", 1)
    
    async def _retry_request(self, request_func, *args, **kwargs):
        """Execute request with retry logic"""
        last_exception = None
        
        for attempt in range(self.config.retry_config.max_retries + 1):
            try:
                return await request_func(*args, **kwargs)
            except httpx.HTTPStatusError as e:
                if e.response.status_code not in self.config.retry_config.retry_on_status_codes:
                    raise
                last_exception = e
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
            
            if attempt < self.config.retry_config.max_retries:
                delay = min(
                    self.config.retry_config.initial_delay * (
                        self.config.retry_config.exponential_base ** attempt
                    ),
                    self.config.retry_config.max_delay
                )
                log_warning(f"Request failed, retrying in {delay}s (attempt {attempt + 1})")
                await asyncio.sleep(delay)
        
        # All retries exhausted
        if last_exception:
            raise ServiceUnavailableError(f"Service {self.config.service_name} unavailable after {self.config.retry_config.max_retries} retries: {last_exception}")
    
    async def _make_request(self, 
                           method: str, 
                           endpoint: str,
                           data: Optional[Dict[str, Any]] = None,
                           params: Optional[Dict[str, Any]] = None,
                           headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        
        if not self.client:
            await self.connect()
        
        # Apply rate limiting
        await self._apply_rate_limiting()
        
        # Prepare request
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)
        
        # Execute request with retry
        async def make_request():
            response = await self.client.request(
                method=method,
                url=endpoint,
                json=data,
                params=params,
                headers=request_headers
            )
            response.raise_for_status()
            return response
        
        try:
            response = await self._retry_request(make_request)
            
            # Log successful request
            log_info(f"{method} {endpoint} -> {response.status_code}")
            
            # Parse response
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"data": response.text, "status": response.status_code}
                
        except httpx.HTTPStatusError as e:
            await self._handle_http_error(e)
        except Exception as e:
            log_exception(f"Unexpected error calling {self.config.service_name}: {e}")
            raise ClientError(f"Client error: {e}")
    
    async def _handle_http_error(self, error: httpx.HTTPStatusError):
        """Handle HTTP errors and convert to appropriate exceptions"""
        status_code = error.response.status_code
        
        try:
            error_detail = error.response.json()
        except:
            error_detail = {"detail": error.response.text}
        
        log_warning(f"HTTP {status_code} from {self.config.service_name}: {error_detail}")
        
        if status_code == 401:
            raise AuthenticationError(f"Authentication failed: {error_detail}")
        elif status_code == 400:
            raise ValidationError(f"Validation error: {error_detail}")
        elif status_code == 404:
            raise ClientError(f"Resource not found: {error_detail}")
        elif status_code >= 500:
            raise ServiceUnavailableError(f"Server error: {error_detail}")
        else:
            raise ClientError(f"HTTP {status_code}: {error_detail}")
    
    # Convenience methods for common HTTP verbs
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make GET request"""
        return await self._make_request("GET", endpoint, params=params, **kwargs)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make POST request"""
        return await self._make_request("POST", endpoint, data=data, **kwargs)
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make PUT request"""
        return await self._make_request("PUT", endpoint, data=data, **kwargs)
    
    async def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make PATCH request"""
        return await self._make_request("PATCH", endpoint, data=data, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request"""
        return await self._make_request("DELETE", endpoint, **kwargs)
    
    # Abstract methods for service-specific implementations
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check if the target service is healthy"""
        pass
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the target service"""
        pass

# Factory function for creating service clients
def create_service_client(service_name: str, 
                         base_url: Optional[str] = None,
                         auth_token: Optional[str] = None,
                         **kwargs) -> BaseServiceClient:
    """
    Factory function to create service client instances
    
    Args:
        service_name: Name of the target service
        base_url: Base URL of the service (auto-detected from env if not provided)
        auth_token: Authentication token
        **kwargs: Additional configuration options
    
    Returns:
        Configured service client instance
    """
    
    # Auto-detect base URL from environment if not provided
    if not base_url:
        env_var = f"{service_name.upper()}_URL"
        base_url = os.getenv(env_var, f"http://{service_name}:8000")
    
    # Create configuration
    config = ClientConfig(
        base_url=base_url,
        service_name=service_name,
        auth_token=auth_token,
        **kwargs
    )
    
    # Import and return specific client class based on service name
    if service_name == "user_service":
        from .user_service_client import UserServiceClient
        return UserServiceClient(config)
    elif service_name == "ticker_service":
        from .ticker_service_client import TickerServiceClient
        return TickerServiceClient(config)
    elif service_name == "trade_service":
        from .trade_service_client import TradeServiceClient
        return TradeServiceClient(config)
    elif service_name == "signal_service":
        from .signal_service_client import SignalServiceClient
        return SignalServiceClient(config)
    elif service_name == "subscription_service":
        from .subscription_service_client import SubscriptionServiceClient
        return SubscriptionServiceClient(config)
    else:
        # Return generic client for unknown services
        return GenericServiceClient(config)

class GenericServiceClient(BaseServiceClient):
    """Generic service client for any HTTP service"""
    
    async def health_check(self) -> Dict[str, Any]:
        """Generic health check"""
        try:
            return await self.get("/health")
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            "service_name": self.config.service_name,
            "base_url": self.config.base_url,
            "timeout": self.config.timeout,
            "rate_limited": self.config.rate_limit_enabled
        }

# Context manager for multiple service clients
class ServiceClientManager:
    """Manager for multiple service clients"""
    
    def __init__(self):
        self.clients: Dict[str, BaseServiceClient] = {}
    
    def add_client(self, name: str, client: BaseServiceClient):
        """Add a service client"""
        self.clients[name] = client
    
    def get_client(self, name: str) -> Optional[BaseServiceClient]:
        """Get a service client by name"""
        return self.clients.get(name)
    
    async def connect_all(self):
        """Connect all clients"""
        for client in self.clients.values():
            await client.connect()
    
    async def disconnect_all(self):
        """Disconnect all clients"""
        for client in self.clients.values():
            await client.disconnect()
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Health check all services"""
        results = {}
        for name, client in self.clients.items():
            try:
                results[name] = await client.health_check()
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
        return results