"""
Compatibility version of UnifiedSymbol model that works with VARCHAR columns
This is a temporary solution until we can properly migrate the database
"""

from datetime import datetime, date
from typing import Optional
from decimal import Decimal
import uuid

from sqlalchemy import (
    Column, String, Date, DateTime, Integer, Boolean, Text, 
    Numeric, JSON, Index, UniqueConstraint, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from shared_architecture.db.base import Base
from .symbol import (
    AssetClass, ProductType, Exchange, OptionType, SymbolStatus,
    BrokerType, SymbolMapping
)


class UnifiedSymbolCompat(Base):
    """
    Compatibility version of UnifiedSymbol that uses VARCHAR instead of ENUM
    """
    __tablename__ = "unified_symbols"
    __table_args__ = {'schema': 'tradingdb', 'extend_existing': True}

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core identifiers
    instrument_key = Column(String(300), unique=True, nullable=False, index=True)
    
    # Basic symbol information - Using String instead of ENUM
    symbol = Column(String(100), nullable=False, index=True)
    exchange = Column(String(50), nullable=False, index=True)  # VARCHAR instead of ENUM
    asset_class = Column(String(50), nullable=False, index=True)  # VARCHAR instead of ENUM
    product_type = Column(String(50), nullable=False, index=True)  # VARCHAR instead of ENUM
    
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
    option_type = Column(String(10), nullable=True)  # VARCHAR instead of ENUM
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
    status = Column(String(20), default="active", nullable=False, index=True)  # VARCHAR instead of ENUM
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
    exercise_style = Column(String(20), nullable=True)
    
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
    
    # Options-specific calculations
    intrinsic_value = Column(Numeric(15, 4), nullable=True)
    time_value = Column(Numeric(15, 4), nullable=True)
    moneyness = Column(String(10), nullable=True)
    
    # Industry and sector classification
    sector = Column(String(100), nullable=True, index=True)
    industry = Column(String(100), nullable=True)
    sub_industry = Column(String(100), nullable=True)
    
    # Index membership
    index_constituents = Column(ARRAY(String), nullable=True)
    
    # Market maker information
    market_maker_flag = Column(Boolean, default=False, nullable=False)
    market_maker_names = Column(ARRAY(String), nullable=True)
    
    # Additional metadata
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
    
    # Version control
    version = Column(Integer, default=1, nullable=False)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = uuid.uuid4()
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, (datetime, date)):
                result[column.name] = value.isoformat() if value else None
            elif isinstance(value, Decimal):
                result[column.name] = float(value) if value is not None else None
            elif isinstance(value, uuid.UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
        return result
    
    def is_option(self):
        """Check if symbol is an option"""
        return self.product_type == 'options'
    
    def is_future(self):
        """Check if symbol is a future"""
        return self.product_type == 'futures'
    
    def is_derivative(self):
        """Check if symbol is a derivative"""
        return self.product_type in ['options', 'futures']
    
    def is_equity(self):
        """Check if symbol is equity"""
        return self.asset_class == 'equity'
    
    def is_active(self):
        """Check if symbol is active for trading"""
        return (
            self.status == 'active' and
            self.is_tradable and
            not self.is_deleted and
            (self.expiry_date is None or self.expiry_date >= date.today())
        )
    
    def __repr__(self):
        return f"<UnifiedSymbolCompat(id='{self.id}', instrument_key='{self.instrument_key}', symbol='{self.symbol}', exchange='{self.exchange}')>"