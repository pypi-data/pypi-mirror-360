"""
Unified Symbol Domain Model for StocksBlitz Platform

This module provides a comprehensive, standardized representation of trading symbols
that serves as the single source of truth across all services in the platform.

Key Features:
- Multi-asset type support (equity, options, futures, crypto, forex, bonds)
- Broker-agnostic unified identifiers
- Comprehensive broker token mapping
- Asset classification and validation
- Corporate actions tracking
- Market data integration
- Flexible metadata storage
"""

from datetime import datetime, date, time
from typing import Optional, Dict, Any, List, Union, Set
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

from sqlalchemy import (
    Column, String, Date, DateTime, Integer, Boolean, Text, 
    Numeric, JSON, Index, UniqueConstraint, ForeignKey, Table
)
from sqlalchemy.dialects.postgresql import UUID, ENUM, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from shared_architecture.db.base import Base


class AssetClass(Enum):
    """Asset classes supported by the platform"""
    EQUITY = "equity"
    DERIVATIVE = "derivative"
    COMMODITY = "commodity"
    CURRENCY = "currency"
    CRYPTO = "crypto"
    FIXED_INCOME = "fixed_income"
    MUTUAL_FUND = "mutual_fund"
    ETF = "etf"
    INDEX = "index"


class ProductType(Enum):
    """Product types within asset classes"""
    # Equity products
    SPOT = "spot"
    FUTURES = "futures"
    OPTIONS = "options"
    
    # Fixed income products
    GOVERNMENT_BOND = "government_bond"
    CORPORATE_BOND = "corporate_bond"
    TREASURY_BILL = "treasury_bill"
    
    # Mutual fund products
    EQUITY_FUND = "equity_fund"
    DEBT_FUND = "debt_fund"
    HYBRID_FUND = "hybrid_fund"
    LIQUID_FUND = "liquid_fund"
    
    # Crypto products
    PERPETUAL = "perpetual"
    
    # Currency products
    FORWARD = "forward"
    SWAP = "swap"


class Exchange(Enum):
    """Supported exchanges"""
    # Indian Exchanges
    NSE = "NSE"
    BSE = "BSE"
    MCX = "MCX"
    NCDEX = "NCDEX"
    ICEX = "ICEX"
    
    # International Exchanges
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    LSE = "LSE"
    TSE = "TSE"
    HKEX = "HKEX"
    
    # Crypto Exchanges
    BINANCE = "BINANCE"
    COINBASE = "COINBASE"
    KRAKEN = "KRAKEN"
    BITFINEX = "BITFINEX"
    
    # Multi-exchange
    ANY = "ANY"


class OptionType(Enum):
    """Option types"""
    CALL = "call"
    PUT = "put"


class SymbolStatus(Enum):
    """Symbol status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELISTED = "delisted"
    EXPIRED = "expired"
    UPCOMING = "upcoming"


# Commented out - table dropped
# class CorporateActionType(Enum):
#     """Types of corporate actions"""
#     DIVIDEND = "dividend"
#     BONUS = "bonus"
#     SPLIT = "split"
#     MERGER = "merger"
#     SPIN_OFF = "spin_off"
#     RIGHTS = "rights"
#     BUYBACK = "buyback"


class BrokerType(Enum):
    """Supported broker types"""
    ZERODHA_KITE = "zerodha_kite"
    ICICI_BREEZE = "icici_breeze"
    UPSTOX = "upstox"
    FYERS = "fyers"
    ANGEL_ONE = "angel_one"
    ALICE_BLUE = "alice_blue"
    AUTOTRADER = "autotrader"
    INTERACTIVE_BROKERS = "interactive_brokers"


# Association table for symbol broker tokens
# Commented out - table not needed for current implementation
# symbol_broker_tokens = Table(
#     'symbol_broker_tokens',
#     Base.metadata,
#     Column('symbol_id', UUID(as_uuid=True), ForeignKey('unified_symbols.id'), primary_key=True),
#     Column('broker_token_id', UUID(as_uuid=True), ForeignKey('broker_tokens.id'), primary_key=True),
#     schema='tradingdb'
# )


@dataclass
class MarketDataSnapshot:
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


# Commented out - BrokerToken class not needed for current implementation
# class BrokerToken(Base):
#     """
#     Broker-specific tokens and identifiers for symbols
#     """
#     __tablename__ = "broker_tokens"
#     __table_args__ = {'schema': 'tradingdb'}
#
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
#     # Broker identification
#     broker_type = Column(ENUM(BrokerType), nullable=False, index=True)
#     broker_name = Column(String(100), nullable=False)
#     
#     # Broker-specific identifiers
#     broker_symbol = Column(String(200), nullable=False, index=True)
#     broker_token = Column(String(200), nullable=True, index=True)
#     broker_instrument_id = Column(String(200), nullable=True)
#     broker_exchange_code = Column(String(50), nullable=True)
#     broker_segment = Column(String(50), nullable=True)
#     
#     # Trading specifications from broker
#     lot_size = Column(Integer, nullable=True)
#     tick_size = Column(Numeric(10, 6), nullable=True)
#     price_precision = Column(Integer, default=2)
#     
#     # Status and validation
#     is_active = Column(Boolean, default=True, nullable=False)
#     is_tradable = Column(Boolean, default=True, nullable=False)
#     last_verified = Column(DateTime(timezone=True), nullable=True)
#     verification_status = Column(String(50), default="pending")
#     
#     # Metadata
#     broker_metadata = Column(JSON, nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
#     # Constraints
#     __table_args__ = (
#         UniqueConstraint('broker_type', 'broker_symbol', name='uq_broker_symbol'),
#         UniqueConstraint('broker_type', 'broker_token', name='uq_broker_token'),
#         Index('idx_broker_tokens_lookup', 'broker_type', 'broker_symbol'),
#         {'schema': 'tradingdb'}
#     )


class UnifiedSymbol(Base):
    """
    Unified Symbol Model - Single source of truth for all trading instruments
    
    This model provides:
    - Standardized symbol identification across all services
    - Multi-asset type support with proper classification
    - Comprehensive broker token mapping
    - Corporate actions tracking
    - Market data integration
    - Flexible metadata storage
    """
    __tablename__ = "unified_symbols"
    __table_args__ = {'schema': 'tradingdb'}

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core identifiers - The universal instrument key
    instrument_key = Column(String(300), unique=True, nullable=False, index=True)
    
    # Basic symbol information
    symbol = Column(String(100), nullable=False, index=True)
    exchange = Column(ENUM(Exchange), nullable=False, index=True)
    asset_class = Column(ENUM(AssetClass), nullable=False, index=True)
    product_type = Column(ENUM(ProductType), nullable=False, index=True)
    
    # Symbol names and descriptions
    display_name = Column(String(300), nullable=True)
    company_name = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)
    short_name = Column(String(100), nullable=True)
    
    # International identifiers
    isin_code = Column(String(12), nullable=True, index=True)
    cusip = Column(String(9), nullable=True)
    bloomberg_id = Column(String(50), nullable=True)
    reuters_ric = Column(String(50), nullable=True)
    figi = Column(String(12), nullable=True)
    
    # Currency and regional information
    currency = Column(String(3), default="INR", nullable=False)
    country_code = Column(String(2), default="IN", nullable=False)
    
    # Derivatives-specific fields
    expiry_date = Column(Date, nullable=True, index=True)
    option_type = Column(ENUM(OptionType), nullable=True)
    strike_price = Column(Numeric(15, 4), nullable=True)
    underlying_symbol = Column(String(100), nullable=True, index=True)
    
    # Trading specifications
    lot_size = Column(Integer, nullable=True)
    tick_size = Column(Numeric(10, 6), nullable=True)
    multiplier = Column(Integer, default=1, nullable=False)
    board_lot_quantity = Column(Integer, nullable=True)
    
    # Market and pricing information
    face_value = Column(Numeric(15, 4), nullable=True)
    market_lot = Column(Integer, nullable=True)
    price_band_lower = Column(Numeric(15, 4), nullable=True)
    price_band_upper = Column(Numeric(15, 4), nullable=True)
    base_price = Column(Numeric(15, 4), nullable=True)
    
    # Corporate actions
    dividend_yield = Column(Numeric(8, 4), nullable=True)
    last_dividend_date = Column(Date, nullable=True)
    last_dividend_amount = Column(Numeric(15, 4), nullable=True)
    bonus_ratio = Column(String(20), nullable=True)
    split_ratio = Column(String(20), nullable=True)
    
    # Market status and eligibility
    status = Column(ENUM(SymbolStatus), default=SymbolStatus.ACTIVE, nullable=False, index=True)
    is_tradable = Column(Boolean, default=True, nullable=False)
    is_permitted_to_trade = Column(Boolean, default=True, nullable=False)
    
    # Market eligibility flags
    normal_market_allowed = Column(Boolean, default=True, nullable=False)
    odd_lot_market_allowed = Column(Boolean, default=False, nullable=False)
    spot_market_allowed = Column(Boolean, default=True, nullable=False)
    auction_market_allowed = Column(Boolean, default=False, nullable=False)
    
    # Risk and margin information
    warning_quantity = Column(Integer, nullable=True)
    freeze_quantity = Column(Integer, nullable=True)
    freeze_percentage = Column(Numeric(8, 4), nullable=True)
    credit_rating = Column(String(10), nullable=True)
    
    # Margin requirements
    margin_percentage = Column(Numeric(8, 4), nullable=True)
    avm_buy_margin = Column(Numeric(8, 4), nullable=True)
    avm_sell_margin = Column(Numeric(8, 4), nullable=True)
    
    # Market data flags
    market_data_available = Column(Boolean, default=True, nullable=False)
    real_time_data_available = Column(Boolean, default=True, nullable=False)
    historical_data_available = Column(Boolean, default=True, nullable=False)
    
    # Date information
    listing_date = Column(Date, nullable=True, index=True)
    delisting_date = Column(Date, nullable=True)
    first_trading_date = Column(Date, nullable=True)
    last_trading_date = Column(Date, nullable=True)
    
    # For options and derivatives
    exercise_start_date = Column(Date, nullable=True)
    exercise_end_date = Column(Date, nullable=True)
    exercise_style = Column(String(20), nullable=True)  # american, european
    
    # No delivery period
    no_delivery_start_date = Column(Date, nullable=True)
    no_delivery_end_date = Column(Date, nullable=True)
    
    # Book closure dates
    book_closure_start_date = Column(Date, nullable=True)
    book_closure_end_date = Column(Date, nullable=True)
    
    # Corporate events flags
    dividend_flag = Column(Boolean, default=False, nullable=False)
    bonus_flag = Column(Boolean, default=False, nullable=False)
    rights_flag = Column(Boolean, default=False, nullable=False)
    split_flag = Column(Boolean, default=False, nullable=False)
    merger_flag = Column(Boolean, default=False, nullable=False)
    
    # Surveillance and compliance
    surveillance_flag = Column(Boolean, default=False, nullable=False)
    suspension_flag = Column(Boolean, default=False, nullable=False)
    suspension_reason = Column(String(500), nullable=True)
    suspension_date = Column(Date, nullable=True)
    
    # Options-specific calculations (can be computed)
    intrinsic_value = Column(Numeric(15, 4), nullable=True)
    time_value = Column(Numeric(15, 4), nullable=True)
    moneyness = Column(String(10), nullable=True)  # ITM, OTM, ATM
    
    # Industry and sector classification
    sector = Column(String(100), nullable=True, index=True)
    industry = Column(String(100), nullable=True)
    sub_industry = Column(String(100), nullable=True)
    
    # Index membership
    index_constituents = Column(ARRAY(String), nullable=True)  # List of indexes
    
    # Market maker information
    market_maker_flag = Column(Boolean, default=False, nullable=False)
    market_maker_names = Column(ARRAY(String), nullable=True)
    
    # Additional metadata (flexible JSON storage)
    symbol_metadata = Column(JSON, nullable=True)
    
    # System fields
    data_source = Column(String(100), default="platform", nullable=False)
    data_quality_score = Column(Numeric(5, 2), default=100.00, nullable=False)
    last_validated = Column(DateTime(timezone=True), nullable=True)
    validation_errors = Column(JSON, nullable=True)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    
    # Version control for data synchronization
    version = Column(Integer, default=1, nullable=False)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    # Commented out - broker_tokens relationship not needed for current implementation
    # broker_tokens = relationship(
    #     "BrokerToken",
    #     secondary=symbol_broker_tokens,
    #     back_populates="symbols",
    #     cascade="all, delete"
    # )
    
    # Commented out - table dropped
    # corporate_actions = relationship(
    #     "CorporateAction",
    #     back_populates="symbol",
    #     cascade="all, delete-orphan"
    # )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_unified_symbol_exchange', 'symbol', 'exchange'),
        Index('idx_unified_asset_product', 'asset_class', 'product_type'),
        Index('idx_unified_expiry_status', 'expiry_date', 'status'),
        Index('idx_unified_underlying', 'underlying_symbol'),
        Index('idx_unified_isin_active', 'isin_code', 'status'),
        Index('idx_unified_sector', 'sector'),
        Index('idx_unified_listing_date', 'listing_date'),
        Index('idx_unified_search', 'symbol', 'company_name', 'display_name'),
        UniqueConstraint('instrument_key', name='uq_unified_instrument_key'),
        {'schema': 'tradingdb'}
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = uuid.uuid4()

    def to_dict(self) -> Dict[str, Any]:
        """Convert symbol to dictionary representation"""
        result = {}
        
        # Basic fields
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Handle special types
            if isinstance(value, (datetime, date)):
                result[column.name] = value.isoformat() if value else None
            elif isinstance(value, Decimal):
                result[column.name] = float(value) if value is not None else None
            elif isinstance(value, Enum):
                result[column.name] = value.value if value else None
            elif isinstance(value, uuid.UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
        
        # Add computed fields
        # Commented out - broker_tokens not available
        # result['broker_token_count'] = len(self.broker_tokens) if self.broker_tokens else 0
        result['broker_token_count'] = 0
        # result['corporate_action_count'] = len(self.corporate_actions) if self.corporate_actions else 0
        result['corporate_action_count'] = 0  # Commented out - table dropped
        
        return result

    def get_broker_token(self, broker_type: BrokerType) -> Optional[str]:
        """Get broker token for specific broker"""
        # Commented out - broker_tokens not available
        # if not self.broker_tokens:
        #     return None
        #     
        # for token_mapping in self.broker_tokens:
        #     if token_mapping.broker_type == broker_type:
        #         return token_mapping.broker_token
        #         
        # return None
        return None

    def get_broker_symbol(self, broker_type: BrokerType) -> Optional[str]:
        """Get broker symbol for specific broker"""
        # Commented out - broker_tokens not available
        # if not self.broker_tokens:
        #     return None
        #     
        # for token_mapping in self.broker_tokens:
        #     if token_mapping.broker_type == broker_type:
        #         return token_mapping.broker_symbol
        #         
        # return None
        return None

    def is_option(self) -> bool:
        """Check if symbol is an option"""
        return self.product_type == ProductType.OPTIONS

    def is_future(self) -> bool:
        """Check if symbol is a future"""
        return self.product_type == ProductType.FUTURES

    def is_derivative(self) -> bool:
        """Check if symbol is a derivative"""
        return self.product_type in [ProductType.OPTIONS, ProductType.FUTURES]

    def is_equity(self) -> bool:
        """Check if symbol is equity"""
        return self.asset_class == AssetClass.EQUITY

    def is_active(self) -> bool:
        """Check if symbol is active for trading"""
        return (
            self.status == SymbolStatus.ACTIVE and
            self.is_tradable and
            not self.is_deleted and
            (self.expiry_date is None or self.expiry_date >= date.today())
        )

    def is_expired(self) -> bool:
        """Check if symbol is expired"""
        return (
            self.expiry_date is not None and 
            self.expiry_date < date.today()
        ) or self.status == SymbolStatus.EXPIRED

    def get_display_symbol(self) -> str:
        """Get formatted display symbol"""
        if self.display_name:
            return self.display_name
        
        base = f"{self.symbol}"
        
        if self.is_option():
            if self.expiry_date and self.strike_price and self.option_type:
                exp_str = self.expiry_date.strftime("%d%b%y").upper()
                return f"{base}{exp_str}{self.strike_price}{self.option_type.value.upper()}"
        elif self.is_future():
            if self.expiry_date:
                exp_str = self.expiry_date.strftime("%d%b%y").upper()
                return f"{base}{exp_str}FUT"
        
        return base

    def __repr__(self):
        return f"<UnifiedSymbol(id='{self.id}', instrument_key='{self.instrument_key}', symbol='{self.symbol}', exchange='{self.exchange}')>"


# Add relationship back to BrokerToken
# Commented out - BrokerToken not used in current implementation
# BrokerToken.symbols = relationship(
#     "UnifiedSymbol",
#     secondary=symbol_broker_tokens,
#     back_populates="broker_tokens"
# )


# Commented out - table dropped
# class CorporateAction(Base):
#     """
#     Corporate actions affecting symbols
#     """
#     __tablename__ = "corporate_actions"
#     __table_args__ = {'schema': 'tradingdb'}
# 
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     symbol_id = Column(UUID(as_uuid=True), ForeignKey('unified_symbols.id'), nullable=False)
#     
#     # Action details
#     action_type = Column(ENUM(CorporateActionType), nullable=False, index=True)
#     announcement_date = Column(Date, nullable=False)
#     ex_date = Column(Date, nullable=False, index=True)
#     record_date = Column(Date, nullable=True)
#     payment_date = Column(Date, nullable=True)
#     
#     # Action parameters
#     ratio = Column(String(50), nullable=True)  # e.g., "1:2" for split
#     amount = Column(Numeric(15, 4), nullable=True)  # dividend amount
#     percentage = Column(Numeric(8, 4), nullable=True)  # bonus percentage
#     
#     # Status and processing
#     status = Column(String(20), default="announced", nullable=False)  # announced, processed, cancelled
#     is_processed = Column(Boolean, default=False, nullable=False)
#     processed_date = Column(DateTime(timezone=True), nullable=True)
#     
#     # Impact on pricing and quantity
#     price_adjustment_factor = Column(Numeric(10, 6), default=1.0, nullable=False)
#     quantity_adjustment_factor = Column(Numeric(10, 6), default=1.0, nullable=False)
#     
#     # Additional information
#     description = Column(Text, nullable=True)
#     remarks = Column(Text, nullable=True)
#     source = Column(String(100), nullable=True)
#     
#     # Metadata
#     action_metadata = Column(JSON, nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
#     
#     # Relationship
#     symbol = relationship("UnifiedSymbol", back_populates="corporate_actions")
#     
#     __table_args__ = (
#         Index('idx_corp_action_symbol_date', 'symbol_id', 'ex_date'),
#         Index('idx_corp_action_type_date', 'action_type', 'ex_date'),
#         {'schema': 'tradingdb'}
#     )


class SymbolMapping(Base):
    """
    Legacy symbol mappings for backward compatibility
    """
    __tablename__ = "symbol_mappings"
    __table_args__ = {'schema': 'tradingdb'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unified_symbol_id = Column(UUID(as_uuid=True), ForeignKey('tradingdb.unified_symbols.id'), nullable=False)
    
    # Legacy mapping information
    legacy_table = Column(String(100), nullable=False)  # table name
    legacy_id = Column(String(200), nullable=False)     # legacy primary key
    legacy_symbol = Column(String(200), nullable=False) # legacy symbol
    
    # Mapping metadata
    mapping_confidence = Column(Numeric(5, 2), default=100.00, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100), nullable=True)
    
    # Relationship
    unified_symbol = relationship("UnifiedSymbol")
    
    __table_args__ = (
        UniqueConstraint('legacy_table', 'legacy_id', name='uq_legacy_mapping'),
        Index('idx_symbol_mapping_legacy', 'legacy_table', 'legacy_symbol'),
        {'schema': 'tradingdb'}
    )