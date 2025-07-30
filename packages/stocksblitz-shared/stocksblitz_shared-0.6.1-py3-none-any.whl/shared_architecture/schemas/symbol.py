"""
Unified Symbol Schemas for API Serialization and Validation

This module provides Pydantic schemas for the unified symbol model,
supporting serialization, validation, and API communication across services.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from shared_architecture.domain.models.market.symbol import (
    AssetClass, ProductType, Exchange, OptionType, SymbolStatus,
    # CorporateActionType,  # Commented out - table dropped
    BrokerType
)


# Base schemas for common fields
class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    class Config:
        from_attributes = True
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None,
            UUID: lambda v: str(v)
        }


# Broker Token Schemas
class BrokerTokenBase(BaseSchema):
    """Base schema for broker tokens"""
    broker_type: BrokerType
    broker_name: str
    broker_symbol: str
    broker_token: Optional[str] = None
    broker_instrument_id: Optional[str] = None
    broker_exchange_code: Optional[str] = None
    broker_segment: Optional[str] = None
    lot_size: Optional[int] = None
    tick_size: Optional[Decimal] = None
    price_precision: Optional[int] = 2
    is_active: bool = True
    is_tradable: bool = True
    broker_metadata: Optional[Dict[str, Any]] = None


class BrokerTokenCreate(BrokerTokenBase):
    """Schema for creating broker tokens"""
    pass


class BrokerTokenUpdate(BrokerTokenBase):
    """Schema for updating broker tokens"""
    broker_type: Optional[BrokerType] = None
    broker_name: Optional[str] = None
    broker_symbol: Optional[str] = None


class BrokerToken(BrokerTokenBase):
    """Complete broker token schema"""
    id: UUID
    last_verified: Optional[datetime] = None
    verification_status: str = "pending"
    created_at: datetime
    updated_at: datetime


# Corporate Action Schemas - Commented out - table dropped
# class CorporateActionBase(BaseSchema):
#     """Base schema for corporate actions"""
#     action_type: CorporateActionType
#     announcement_date: date
#     ex_date: date
#     record_date: Optional[date] = None
#     payment_date: Optional[date] = None
#     ratio: Optional[str] = None
#     amount: Optional[Decimal] = None
#     percentage: Optional[Decimal] = None
#     description: Optional[str] = None
#     remarks: Optional[str] = None
#     source: Optional[str] = None
#     metadata: Optional[Dict[str, Any]] = None
# 
# 
# class CorporateActionCreate(CorporateActionBase):
#     """Schema for creating corporate actions"""
#     symbol_id: UUID
# 
# 
# class CorporateActionUpdate(CorporateActionBase):
#     """Schema for updating corporate actions"""
#     action_type: Optional[CorporateActionType] = None
#     announcement_date: Optional[date] = None
#     ex_date: Optional[date] = None
#     status: Optional[str] = None
#     is_processed: Optional[bool] = None
# 
# 
# class CorporateAction(CorporateActionBase):
#     """Complete corporate action schema"""
#     id: UUID
#     symbol_id: UUID
#     status: str = "announced"
#     is_processed: bool = False
#     processed_date: Optional[datetime] = None
#     price_adjustment_factor: Decimal = Decimal('1.0')
#     quantity_adjustment_factor: Decimal = Decimal('1.0')
#     created_at: datetime
#     updated_at: datetime


# Market Data Schema
class MarketDataSnapshot(BaseSchema):
    """Real-time market data snapshot"""
    timestamp: datetime
    last_price: Optional[Decimal] = None
    bid_price: Optional[Decimal] = None
    ask_price: Optional[Decimal] = None
    bid_quantity: Optional[int] = None
    ask_quantity: Optional[int] = None
    open_price: Optional[Decimal] = None
    high_price: Optional[Decimal] = None
    low_price: Optional[Decimal] = None
    close_price: Optional[Decimal] = None
    volume: Optional[int] = None
    turnover: Optional[Decimal] = None
    open_interest: Optional[int] = None
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None


# Unified Symbol Schemas
class UnifiedSymbolBase(BaseSchema):
    """Base schema for unified symbols"""
    
    # Core identifiers
    instrument_key: str = Field(..., description="Universal instrument key")
    symbol: str = Field(..., max_length=100, description="Symbol code")
    exchange: Exchange = Field(..., description="Exchange")
    asset_class: AssetClass = Field(..., description="Asset class")
    product_type: ProductType = Field(..., description="Product type")
    
    # Names and descriptions
    display_name: Optional[str] = Field(None, max_length=300)
    company_name: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    short_name: Optional[str] = Field(None, max_length=100)
    
    # International identifiers
    isin_code: Optional[str] = Field(None, max_length=12, pattern=r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$')
    cusip: Optional[str] = Field(None, max_length=9)
    bloomberg_id: Optional[str] = Field(None, max_length=50)
    reuters_ric: Optional[str] = Field(None, max_length=50)
    figi: Optional[str] = Field(None, max_length=12)
    
    # Currency and regional
    currency: str = Field(default="INR", max_length=3)
    country_code: str = Field(default="IN", max_length=2)
    
    # Derivatives-specific
    expiry_date: Optional[date] = None
    option_type: Optional[OptionType] = None
    strike_price: Optional[Decimal] = None
    underlying_symbol: Optional[str] = Field(None, max_length=100)
    
    # Trading specifications
    lot_size: Optional[int] = None
    tick_size: Optional[Decimal] = None
    multiplier: int = Field(default=1, ge=1)
    board_lot_quantity: Optional[int] = None
    
    # Market and pricing
    face_value: Optional[Decimal] = None
    market_lot: Optional[int] = None
    price_band_lower: Optional[Decimal] = None
    price_band_upper: Optional[Decimal] = None
    base_price: Optional[Decimal] = None
    
    # Status and eligibility
    status: SymbolStatus = Field(default=SymbolStatus.ACTIVE)
    is_tradable: bool = True
    is_permitted_to_trade: bool = True
    
    # Market eligibility flags
    normal_market_allowed: bool = True
    odd_lot_market_allowed: bool = False
    spot_market_allowed: bool = True
    auction_market_allowed: bool = False
    
    # Risk and margin
    warning_quantity: Optional[int] = None
    freeze_quantity: Optional[int] = None
    freeze_percentage: Optional[Decimal] = None
    credit_rating: Optional[str] = Field(None, max_length=10)
    margin_percentage: Optional[Decimal] = None
    avm_buy_margin: Optional[Decimal] = None
    avm_sell_margin: Optional[Decimal] = None
    
    # Market data flags
    market_data_available: bool = True
    real_time_data_available: bool = True
    historical_data_available: bool = True
    
    # Important dates
    listing_date: Optional[date] = None
    delisting_date: Optional[date] = None
    first_trading_date: Optional[date] = None
    last_trading_date: Optional[date] = None
    
    # Options and derivatives specific
    exercise_start_date: Optional[date] = None
    exercise_end_date: Optional[date] = None
    exercise_style: Optional[str] = Field(None, max_length=20)
    
    # No delivery period
    no_delivery_start_date: Optional[date] = None
    no_delivery_end_date: Optional[date] = None
    
    # Book closure
    book_closure_start_date: Optional[date] = None
    book_closure_end_date: Optional[date] = None
    
    # Corporate events flags
    dividend_flag: bool = False
    bonus_flag: bool = False
    rights_flag: bool = False
    split_flag: bool = False
    merger_flag: bool = False
    
    # Surveillance
    surveillance_flag: bool = False
    suspension_flag: bool = False
    suspension_reason: Optional[str] = Field(None, max_length=500)
    suspension_date: Optional[date] = None
    
    # Options calculations
    intrinsic_value: Optional[Decimal] = None
    time_value: Optional[Decimal] = None
    moneyness: Optional[str] = Field(None, max_length=10)
    
    # Industry classification
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    sub_industry: Optional[str] = Field(None, max_length=100)
    
    # Index membership
    index_constituents: Optional[List[str]] = None
    
    # Market maker
    market_maker_flag: bool = False
    market_maker_names: Optional[List[str]] = None
    
    # Metadata
    symbol_metadata: Optional[Dict[str, Any]] = None
    
    # System fields
    data_source: str = "platform"
    data_quality_score: Decimal = Field(default=Decimal('100.00'), ge=0, le=100)
    
    @validator('instrument_key')
    def validate_instrument_key(cls, v):
        """Validate instrument key format"""
        if not v or len(v) < 10:
            raise ValueError('instrument_key must be at least 10 characters')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        """Validate currency code"""
        if v and len(v) != 3:
            raise ValueError('currency must be 3 characters')
        return v.upper() if v else v
    
    @validator('country_code')
    def validate_country_code(cls, v):
        """Validate country code"""
        if v and len(v) != 2:
            raise ValueError('country_code must be 2 characters')
        return v.upper() if v else v
    
    # Option validation removed due to Pydantic v2 compatibility issues
    # TODO: Re-implement with proper Pydantic v2 validators
    
    # Derivative validation removed due to Pydantic v2 compatibility issues
    # TODO: Re-implement with proper Pydantic v2 validators


class UnifiedSymbolCreate(UnifiedSymbolBase):
    """Schema for creating unified symbols"""
    
    @validator('instrument_key')
    def validate_unique_instrument_key(cls, v):
        """Additional validation can be added here for uniqueness check"""
        return v


class UnifiedSymbolUpdate(BaseSchema):
    """Schema for updating unified symbols"""
    
    # Allow partial updates - all fields optional
    symbol: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=300)
    company_name: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    short_name: Optional[str] = Field(None, max_length=100)
    
    # Status updates
    status: Optional[SymbolStatus] = None
    is_tradable: Optional[bool] = None
    is_permitted_to_trade: Optional[bool] = None
    
    # Market eligibility
    normal_market_allowed: Optional[bool] = None
    odd_lot_market_allowed: Optional[bool] = None
    spot_market_allowed: Optional[bool] = None
    auction_market_allowed: Optional[bool] = None
    
    # Trading specifications
    lot_size: Optional[int] = None
    tick_size: Optional[Decimal] = None
    multiplier: Optional[int] = Field(None, ge=1)
    
    # Market and pricing
    face_value: Optional[Decimal] = None
    base_price: Optional[Decimal] = None
    price_band_lower: Optional[Decimal] = None
    price_band_upper: Optional[Decimal] = None
    
    # Risk and margin
    warning_quantity: Optional[int] = None
    freeze_quantity: Optional[int] = None
    freeze_percentage: Optional[Decimal] = None
    margin_percentage: Optional[Decimal] = None
    
    # Flags
    dividend_flag: Optional[bool] = None
    bonus_flag: Optional[bool] = None
    rights_flag: Optional[bool] = None
    split_flag: Optional[bool] = None
    merger_flag: Optional[bool] = None
    surveillance_flag: Optional[bool] = None
    suspension_flag: Optional[bool] = None
    
    # Suspension details
    suspension_reason: Optional[str] = Field(None, max_length=500)
    suspension_date: Optional[date] = None
    
    # Classification
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    sub_industry: Optional[str] = Field(None, max_length=100)
    
    # Index membership
    index_constituents: Optional[List[str]] = None
    
    # Metadata
    symbol_metadata: Optional[Dict[str, Any]] = None
    
    # System fields
    data_quality_score: Optional[Decimal] = Field(None, ge=0, le=100)
    updated_by: Optional[str] = None


class UnifiedSymbol(UnifiedSymbolBase):
    """Complete unified symbol schema with all fields"""
    
    id: UUID
    
    # Corporate actions summary
    dividend_yield: Optional[Decimal] = None
    last_dividend_date: Optional[date] = None
    last_dividend_amount: Optional[Decimal] = None
    bonus_ratio: Optional[str] = None
    split_ratio: Optional[str] = None
    
    # System audit fields
    version: int = 1
    last_validated: Optional[datetime] = None
    validation_errors: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Soft delete
    deleted_at: Optional[datetime] = None
    is_deleted: bool = False
    
    # Related data
    broker_tokens: Optional[List[BrokerToken]] = []
    # corporate_actions: Optional[List[CorporateAction]] = []  # Commented out - table dropped
    
    # Computed fields
    broker_token_count: Optional[int] = Field(None, description="Number of broker tokens")
    # corporate_action_count: Optional[int] = Field(None, description="Number of corporate actions")  # Commented out - table dropped
    
    # Market data
    market_data: Optional[MarketDataSnapshot] = None


# Search and filtering schemas
class SymbolSearchFilters(BaseSchema):
    """Schema for symbol search filters"""
    
    # Basic filters
    symbol: Optional[str] = None
    exchange: Optional[Exchange] = None
    asset_class: Optional[AssetClass] = None
    product_type: Optional[ProductType] = None
    status: Optional[SymbolStatus] = None
    
    # Text search
    search_text: Optional[str] = Field(None, description="Search in symbol, name, description")
    
    # Date filters
    expiry_date_from: Optional[date] = None
    expiry_date_to: Optional[date] = None
    listing_date_from: Optional[date] = None
    listing_date_to: Optional[date] = None
    
    # Option filters
    option_type: Optional[OptionType] = None
    strike_price_min: Optional[Decimal] = None
    strike_price_max: Optional[Decimal] = None
    underlying_symbol: Optional[str] = None
    
    # Market filters
    is_tradable: Optional[bool] = None
    is_active: Optional[bool] = None
    
    # Industry filters
    sector: Optional[str] = None
    industry: Optional[str] = None
    
    # Index membership
    index_constituent: Optional[str] = None
    
    # Broker availability
    broker_type: Optional[BrokerType] = None
    has_broker_token: Optional[bool] = None
    
    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=1000)
    
    # Sorting
    sort_by: Optional[str] = Field(default="symbol", pattern=r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    sort_order: Optional[str] = Field(default="asc", pattern=r'^(asc|desc)$')


class SymbolSearchResult(BaseSchema):
    """Schema for symbol search results"""
    
    symbols: List[UnifiedSymbol]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


# Bulk operations schemas
class BulkSymbolOperation(BaseSchema):
    """Schema for bulk symbol operations"""
    
    operation: str = Field(..., pattern=r'^(create|update|delete|activate|deactivate)$')
    symbols: List[Union[UnifiedSymbolCreate, UnifiedSymbolUpdate, UUID]]
    
    # Options
    validate_only: bool = False
    ignore_errors: bool = False
    batch_size: int = Field(default=100, ge=1, le=1000)


class BulkOperationResult(BaseSchema):
    """Schema for bulk operation results"""
    
    operation: str
    total_requested: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = []
    warnings: List[str] = []
    execution_time_ms: float


# Legacy compatibility schemas (for backward compatibility)
class LegacySymbolBase(BaseSchema):
    """Legacy symbol schema for backward compatibility"""
    
    instrument_key: str
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    symbol_type: Optional[str] = None
    lot_size: Optional[int] = None
    tick_size: Optional[float] = None
    is_active: Optional[bool] = None
    expiry_date: Optional[datetime] = None
    strike_price: Optional[float] = None
    option_type: Optional[str] = None
    underlying_symbol: Optional[str] = None
    stock_token: Optional[str] = None
    stock_code: Optional[str] = None
    permittedtotrade: Optional[bool] = None
    calevel: Optional[int] = None


class LegacySymbolCreate(LegacySymbolBase):
    pass


class LegacySymbolUpdate(LegacySymbolBase):
    instrument_key: Optional[str] = None


class LegacySymbol(LegacySymbolBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Export all schemas
__all__ = [
    # Broker Token Schemas
    'BrokerTokenBase',
    'BrokerTokenCreate',
    'BrokerTokenUpdate',
    'BrokerToken',
    
    # Corporate Action Schemas - Commented out - table dropped
    # 'CorporateActionBase',
    # 'CorporateActionCreate', 
    # 'CorporateActionUpdate',
    # 'CorporateAction',
    
    # Market Data
    'MarketDataSnapshot',
    
    # Unified Symbol Schemas
    'UnifiedSymbolBase',
    'UnifiedSymbolCreate',
    'UnifiedSymbolUpdate',
    'UnifiedSymbol',
    
    # Search and Operations
    'SymbolSearchFilters',
    'SymbolSearchResult',
    'BulkSymbolOperation',
    'BulkOperationResult',
    
    # Legacy Compatibility
    'LegacySymbolBase',
    'LegacySymbolCreate',
    'LegacySymbolUpdate', 
    'LegacySymbol',
    
    # Base
    'BaseSchema'
]
