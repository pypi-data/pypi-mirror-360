# shared_architecture/db/models/symbol.py
"""
Unified Symbol Database Models - Updated to use the new unified symbol structure
"""

# Re-export the unified models from the domain layer
from shared_architecture.domain.models.market.symbol import (
    UnifiedSymbol,
    # BrokerToken,  # Commented out - not needed for current implementation
    # CorporateAction,  # Commented out - table dropped
    SymbolMapping,
    AssetClass,
    ProductType,
    Exchange,
    OptionType,
    SymbolStatus,
    # CorporateActionType,  # Commented out - table dropped
    BrokerType,
    MarketDataSnapshot,
    # symbol_broker_tokens  # Commented out - not needed for current implementation
)

# Legacy Symbol model for backward compatibility
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from shared_architecture.db.base import Base


class Symbol(Base):
    """
    Legacy Symbol Model - Kept for backward compatibility
    
    DEPRECATED: Use UnifiedSymbol instead for new development
    """
    __tablename__ = "symbols_legacy"
    __table_args__ = {'schema': 'tradingdb'}
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Symbol identification
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(String(20), nullable=False, index=True)
    instrument_key = Column(String(100), nullable=False, unique=True, index=True)
    
    # Symbol details
    name = Column(String(200))
    description = Column(Text)
    symbol_type = Column(String(20))  # equity, option, future, etc.
    
    # Trading details
    lot_size = Column(Integer, default=1)
    tick_size = Column(Float, default=0.01)
    is_active = Column(Boolean, default=True)
    
    # Options specific (if applicable)
    expiry_date = Column(DateTime)
    strike_price = Column(Float)
    option_type = Column(String(10))  # call, put
    optiontype = Column(String(10))  # legacy column - duplicate of option_type
    underlying_symbol = Column(String(50))
    
    # Additional fields from database
    stock_token = Column(String(50))
    stock_code = Column(String(50))
    permittedtotrade = Column(Boolean, default=True)
    calevel = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Symbol(symbol='{self.symbol}', exchange='{self.exchange}', instrument_key='{self.instrument_key}')>"
    
    def to_dict(self):
        """Convert symbol to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'exchange': self.exchange,
            'instrument_key': self.instrument_key,
            'name': self.name,
            'description': self.description,
            'symbol_type': self.symbol_type,
            'lot_size': self.lot_size,
            'tick_size': self.tick_size,
            'is_active': self.is_active,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'strike_price': self.strike_price,
            'option_type': self.option_type,
            'optiontype': self.optiontype,  # legacy field
            'underlying_symbol': self.underlying_symbol,
            'stock_token': self.stock_token,
            'stock_code': self.stock_code,
            'permittedtotrade': self.permittedtotrade,
            'calevel': self.calevel,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Alias for the new unified model to maintain backward compatibility
# Use this import for new development: from shared_architecture.db.models.symbol import UnifiedSymbol
__all__ = [
    'UnifiedSymbol',  # Primary unified symbol model
    # 'BrokerToken',    # Broker-specific token mappings - Commented out - not needed for current implementation
    # 'CorporateAction', # Corporate actions - Commented out - table dropped
    'SymbolMapping',  # Legacy mappings
    'Symbol',         # Legacy model (deprecated)
    # Enums
    'AssetClass',
    'ProductType', 
    'Exchange',
    'OptionType',
    'SymbolStatus',
    # 'CorporateActionType',  # Commented out - table dropped
    'BrokerType',
    # Other
    'MarketDataSnapshot',
    # 'symbol_broker_tokens'  # Commented out - not needed for current implementation
]