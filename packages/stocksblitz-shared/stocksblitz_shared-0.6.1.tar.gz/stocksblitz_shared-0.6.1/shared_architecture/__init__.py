__version__ = "0.6.1"

from .services.base import BaseRedisServiceManager, BaseServiceEndpoints
from .core.config import BaseServiceConfig
from .core.dependencies import (
    get_async_db, get_sync_db, get_redis, get_service_config,
    DependencyFactory
)
from .core.auth.middleware import (
    BaseAuthMiddleware, MockAuthMiddleware, create_auth_middleware,
    UserContext, get_current_user, get_current_token, require_permission, require_role
)
from .domain.models.market import Symbol, HistoricalData, TickData
from .services.clients.base_client import (
    BaseServiceClient, ClientConfig, create_service_client,
    ServiceClientManager
)
from .utils.validation import (
    BaseValidator, TradingValidator, PaginationValidator,
    DateTimeValidator, validate_request, validate_pydantic_model
)

# Import instruments module
from . import instruments

__all__ = [
    # Base Services
    "BaseRedisServiceManager", 
    "BaseServiceEndpoints", 
    "BaseServiceConfig",
    
    # Database & Dependencies
    "get_async_db",
    "get_sync_db", 
    "get_redis",
    "get_service_config",
    "DependencyFactory",
    
    # Authentication
    "BaseAuthMiddleware",
    "MockAuthMiddleware", 
    "create_auth_middleware",
    "UserContext",
    "get_current_user",
    "get_current_token",
    "require_permission",
    "require_role",
    
    # Domain Models
    "Symbol", 
    "HistoricalData", 
    "TickData",
    
    # Service Clients
    "BaseServiceClient",
    "ClientConfig", 
    "create_service_client",
    "ServiceClientManager",
    
    # Validation
    "BaseValidator",
    "TradingValidator",
    "PaginationValidator", 
    "DateTimeValidator",
    "validate_request",
    "validate_pydantic_model",
    
    # Instruments
    "instruments"
]