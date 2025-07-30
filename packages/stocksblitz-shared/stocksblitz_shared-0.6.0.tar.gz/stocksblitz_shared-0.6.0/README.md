# StocksBlitz Shared Architecture

A comprehensive Python library providing the foundational components for the StocksBlitz algorithmic trading platform microservices ecosystem.

## Overview

The StocksBlitz Shared Architecture is a centralized library that eliminates code duplication across microservices by providing common infrastructure, business logic, and utilities. It enables the platform's microservices to focus on their specific business functions rather than reimplementing common technical patterns.

## Architecture Philosophy

### Functional over Technical
- **Business Domain Separation**: Trading, market data, user management components are organized by business function
- **Service-Agnostic**: Components can be used by any microservice without tight coupling
- **Pattern Standardization**: Common patterns (Redis management, API endpoints, configuration) are standardized

### Current Microservices Ecosystem
- **User Service** (8002): Authentication, permissions, multi-tenant organizations
- **Ticker Service** (8001): Market data streaming, symbol management  
- **Signal Service** (8003): Technical indicators, Options Greeks, threshold monitoring
- **Subscription Service** (8005): Strategy subscriptions, tiering, quota management
- **Trade Service** (8004): Order execution, position management, risk validation

## Package Structure

```
shared_architecture/
├── core/                    # Core infrastructure components
├── domain/                  # Business domain logic
├── infrastructure/          # Cross-cutting infrastructure
├── services/               # Service integration patterns
├── utils/                  # Focused utility modules
├── testing/                # Test utilities and mocks
└── deployment/             # Deployment and operations
```

## Core Components

### 🔧 Core Infrastructure (`core/`)

#### Authentication & Authorization (`auth/`)
```python
from shared_architecture.core.auth import JWTManager, PermissionChecker

jwt_manager = JWTManager()
token = await jwt_manager.create_access_token(user_id="123", permissions=["trade:read"])

permission_checker = PermissionChecker()
await permission_checker.check_permission(user_id, "trade:execute", resource_id)
```

**Features:**
- JWT token management with 15-minute access tokens
- Multi-tenant permission system with hierarchical roles
- API key management with encryption and rotation
- Keycloak integration for enterprise authentication

#### Configuration Management (`config/`)
```python
from shared_architecture.core.config import BaseServiceConfig

class UserServiceConfig(BaseServiceConfig):
    MAX_LOGIN_ATTEMPTS: int = 5
    SESSION_TIMEOUT: int = 3600

config = UserServiceConfig.create_for_service("user_service")
```

**Features:**
- Environment-based configuration loading
- Service-specific configuration inheritance
- Validation and type checking with Pydantic
- Secrets management integration

#### Database Connections (`connections/`)
```python
from shared_architecture.core.connections import get_async_db, RedisClusterManager

# Database sessions
async with get_async_db() as db:
    users = await db.execute(select(User))

# Redis cluster management
redis = RedisClusterManager()
await redis.store_json_with_expiry("user:123", user_data, ttl=3600)
```

**Features:**
- Async PostgreSQL/TimescaleDB connections
- Redis cluster management with 6-node setup
- Connection pooling and health monitoring
- Service discovery for dynamic environments

### 🏢 Business Domain (`domain/`)

#### Models (`models/`)
Comprehensive SQLAlchemy models for the trading platform:

```python
from shared_architecture.domain.models import User, Order, Position, Symbol

# User management
user = User(email="trader@example.com", organization_id="org_123")

# Trading operations
order = Order(
    user_id=user.id,
    symbol="AAPL",
    quantity=100,
    order_type="MARKET",
    side="BUY"
)

# Market data
symbol = Symbol(
    symbol="AAPL",
    exchange="NASDAQ",
    sector="Technology"
)
```

**Available Models:**
- **User Management**: User, Organization, Permission, APIKey
- **Trading**: Order, Position, Holding, Margin, Trade
- **Market Data**: Symbol, HistoricalData, TickData, MarketSession
- **Broker Integration**: Broker, BrokerConfig, Session

#### Schemas (`schemas/`)
Pydantic schemas for API validation and serialization:

```python
from shared_architecture.domain.schemas import OrderCreateSchema, UserResponseSchema

# Request validation
order_data = OrderCreateSchema(
    symbol="AAPL",
    quantity=100,
    order_type="MARKET",
    side="BUY"
)

# Response serialization  
user_response = UserResponseSchema.from_orm(user)
```

**Schema Categories:**
- **Trading**: Order, Position, Trade requests/responses
- **Market**: Symbol, historical data, real-time quotes
- **User**: Authentication, profile, organization schemas
- **Common**: Pagination, filtering, error responses

### 🏗️ Infrastructure (`infrastructure/`)

#### Observability (`observability/`)
```python
from shared_architecture.infrastructure.observability import HealthChecker, MetricsCollector

# Health monitoring
health_checker = HealthChecker("user_service")
health_status = await health_checker.check_health()

# Metrics collection
metrics = MetricsCollector()
metrics.increment_counter("api_requests", tags={"endpoint": "/users"})
metrics.record_histogram("response_time", 0.150)
```

**Features:**
- Health checks (liveness, readiness, dependency checks)
- Prometheus metrics integration
- Structured logging with correlation IDs
- Distributed tracing support

#### Resilience (`resilience/`)
```python
from shared_architecture.infrastructure.resilience import CircuitBreaker, RateLimiter

# Circuit breaker for external services
@CircuitBreaker(failure_threshold=5, timeout=30)
async def call_external_api():
    return await external_service.get_data()

# Rate limiting
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
await rate_limiter.check_rate_limit(user_id="123")
```

**Features:**
- Circuit breakers with exponential backoff
- Configurable retry policies
- Advanced rate limiting (per-user, per-endpoint)
- Timeout and deadline management

### 🔗 Service Integration (`services/`)

#### Base Service Patterns (`base/`)
```python
from shared_architecture.services.base import BaseRedisServiceManager, BaseServiceConfig

class UserRedisManager(BaseRedisServiceManager):
    def __init__(self):
        super().__init__("user_service")
    
    async def store_user_session(self, user_id: str, session_data: dict):
        await self.store_user_data(user_id, "session", session_data, ttl=3600)
    
    async def get_user_preferences(self, user_id: str):
        return await self.get_user_data(user_id, "preferences")
```

**Features:**
- Base Redis manager with common patterns
- Standard service configuration
- Common API endpoint patterns
- Dependency injection utilities

#### Service Clients (`clients/`)
```python
from shared_architecture.services.clients import ServiceClient

user_client = ServiceClient("user_service")
user_data = await user_client.get("/users/123")

# With circuit breaker and retry
trade_client = ServiceClient("trade_service", 
                           enable_circuit_breaker=True,
                           max_retries=3)
```

**Features:**
- Service discovery integration
- Load balancing across instances
- Circuit breaker integration
- Request/response logging

### 🛠️ Utilities (`utils/`)

#### Data Processing (`data/`)
```python
from shared_architecture.utils.data import DataConverter, DataValidator

# Data conversion
converter = DataConverter()
price_data = converter.convert_price_format(raw_price, from_format="cents", to_format="dollars")

# Data validation
validator = DataValidator()
is_valid = validator.validate_trading_hours(timestamp, exchange="NYSE")
```

#### Trading Utilities (`trading/`)
```python
from shared_architecture.utils.trading import RiskCalculator, InstrumentHelper

# Risk calculations
risk_calc = RiskCalculator()
position_risk = risk_calc.calculate_position_risk(
    quantity=100,
    entry_price=150.00,
    current_price=155.00,
    volatility=0.25
)

# Instrument utilities
instrument = InstrumentHelper()
symbol_info = instrument.parse_symbol("AAPL_CALL_170_20240315")
```

### 🧪 Testing (`testing/`)

```python
from shared_architecture.testing import MockServiceClient, DatabaseFixtures

# Mock external services
mock_client = MockServiceClient("broker_service")
mock_client.setup_response("/orders", {"status": "filled"})

# Test database setup
fixtures = DatabaseFixtures()
test_user = await fixtures.create_test_user()
test_order = await fixtures.create_test_order(user_id=test_user.id)
```

## Installation

### Development (Mount Mode)
For active development, mount the local shared_architecture:

```yaml
# docker-compose.yml
services:
  user-service:
    volumes:
      - ./shared_architecture/shared_architecture:/app/shared_architecture
    environment:
      - ENVIRONMENT=development
```

### Production (PyPI)
Install from PyPI:

```bash
pip install shared_architecture==1.0.0
```

```python
# requirements.txt
shared_architecture>=1.0.0
```

## Usage Patterns

### 1. Creating a New Service

```python
# config.py
from shared_architecture.core.config import BaseServiceConfig

class MyServiceConfig(BaseServiceConfig):
    MY_SERVICE_SETTING: str = "default_value"

config = MyServiceConfig.create_for_service("my_service")
```

```python
# redis_manager.py
from shared_architecture.services.base import BaseRedisServiceManager

class MyServiceRedisManager(BaseRedisServiceManager):
    def __init__(self):
        super().__init__("my_service")
    
    async def initialize_service_data(self):
        # Service-specific Redis setup
        pass
```

```python
# main.py
from shared_architecture.services.base import BaseServiceEndpoints

app = FastAPI()
app.include_router(BaseServiceEndpoints.create_health_router("my_service"))
```

### 2. Database Operations

```python
from shared_architecture.core.connections import get_async_db
from shared_architecture.domain.models import User
from sqlalchemy import select

async def get_user(user_id: str):
    async with get_async_db() as db:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
```

### 3. Service Communication

```python
from shared_architecture.services.clients import ServiceClient

async def get_user_portfolio(user_id: str):
    trade_client = ServiceClient("trade_service")
    positions = await trade_client.get(f"/users/{user_id}/positions")
    return positions
```

### 4. Authentication & Authorization

```python
from shared_architecture.core.auth import JWTManager, PermissionChecker

async def protected_endpoint(token: str = Depends(get_jwt_token)):
    jwt_manager = JWTManager()
    payload = await jwt_manager.verify_token(token)
    
    permission_checker = PermissionChecker()
    await permission_checker.require_permission(
        user_id=payload["user_id"],
        permission="trade:execute"
    )
```

## Configuration

### Environment Variables

The shared architecture uses environment variables for configuration:

```bash
# Database
TIMESCALEDB_HOST=localhost
TIMESCALEDB_PORT=5432
TIMESCALEDB_USER=tradmin
TIMESCALEDB_PASSWORD=secure_password
TIMESCALEDB_DB=tradingdb

# Redis
REDIS_HOST=redis-cluster-proxy
REDIS_PORT=6379
REDIS_PASSWORD=secure_redis_password
REDIS_CLUSTER_NODES=redis1:7001,redis2:7002,redis3:7003

# Authentication
JWT_SECRET_KEY=your_secure_jwt_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15

# Service Configuration
SERVICE_NAME=your_service_name
ENVIRONMENT=development  # or production
DEBUG=false
```

### Service-Specific Configuration

Each service can extend the base configuration:

```python
from shared_architecture.core.config import BaseServiceConfig

class TradeServiceConfig(BaseServiceConfig):
    MAX_ORDER_SIZE: int = 10000
    RISK_CHECK_ENABLED: bool = True
    BROKER_TIMEOUT: int = 30
    
    class Config:
        env_prefix = "TRADE_SERVICE_"
```

## Performance Characteristics

### Benchmarks
- **Database Connections**: 10ms average query time
- **Redis Operations**: 2ms average response time
- **Service Communication**: 50ms average inter-service call
- **JWT Validation**: 1ms average validation time

### Scalability
- **Concurrent Requests**: Supports 1000+ concurrent requests per service
- **Database Pool**: 20 connections per service
- **Redis Cluster**: 6-node cluster supporting 100K+ operations/second
- **Memory Usage**: ~50MB base memory footprint per service

## Development

### Local Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd stocksblitz-platform

# Install shared_architecture in development mode
cd shared_architecture
pip install -e .

# Run tests
python -m pytest tests/

# Code formatting
black shared_architecture/
isort shared_architecture/
```

### Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=shared_architecture

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
```

### Contributing

1. Follow the established patterns in shared_architecture
2. Add comprehensive tests for new components
3. Update documentation for new features
4. Ensure backward compatibility or provide migration guide

## Migration from Previous Versions

### From 0.x to 1.0

The 1.0 release includes significant reorganization. See `ARCHITECTURE_REORGANIZATION_PLAN.md` for detailed migration instructions.

**Key Changes:**
- New directory structure with functional organization
- Base service classes for common patterns
- Enhanced infrastructure components
- Consolidated monitoring and observability

**Breaking Changes:**
- Import paths have changed
- Some utility functions have been moved
- Configuration patterns standardized

## Security

### Authentication
- JWT tokens with 15-minute expiry
- Refresh tokens with 7-day expiry
- API key management with encryption
- Multi-tenant permission system

### Database Security
- Connection encryption with TLS
- Parameterized queries preventing SQL injection
- Role-based database access
- Connection pooling with secure credentials

### Network Security
- Service-to-service authentication
- Request signing for inter-service communication
- Rate limiting and DDoS protection
- Circuit breakers preventing cascade failures

## Monitoring & Observability

### Health Checks
```python
# Standard health endpoints available for all services
GET /health      # Overall service health
GET /health/live # Liveness probe
GET /health/ready # Readiness probe
```

### Metrics
- Request/response metrics
- Database connection metrics
- Redis performance metrics
- Business metrics (orders, trades, users)

### Logging
- Structured JSON logging
- Correlation IDs for request tracing
- Configurable log levels
- Centralized log aggregation

## License

This shared architecture is part of the StocksBlitz trading platform and is proprietary software.

## Support

For questions or issues with shared_architecture:

1. Check the documentation in `/docs`
2. Review the reorganization plan for architectural guidance
3. Consult the microservice examples in `/services`
4. Contact the platform development team

---

**Version**: 1.0.0  
**Last Updated**: July 2025  
**Compatibility**: Python 3.11+, PostgreSQL 15+, Redis 7.0+