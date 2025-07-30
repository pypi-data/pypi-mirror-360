"""
Minimal symbol model that only maps to existing database columns
"""

from datetime import datetime, date
from typing import Optional
from decimal import Decimal
import uuid

from sqlalchemy import (
    Column, String, Date, DateTime, Integer, Boolean, Text, 
    Numeric, MetaData
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

# Create a separate metadata instance to avoid conflicts
minimal_metadata = MetaData()
MinimalBase = declarative_base(metadata=minimal_metadata)


class SymbolMinimal(MinimalBase):
    """
    Minimal model that only uses columns that actually exist in the database
    Uses separate metadata to avoid conflicts
    """
    __tablename__ = "unified_symbols"
    __table_args__ = {'schema': 'tradingdb'}

    # Primary key
    instrument_key = Column(String, primary_key=True)
    
    # Core symbol information (verified to exist)
    symbol = Column(String)
    instrumentname = Column(String)
    companyname = Column(String)
    shortname = Column(String)
    
    # Exchange info
    exchangecode = Column(String)
    exchange_code = Column(String)
    
    # Type info
    instrumenttype = Column(String)
    product_type = Column(String)
    
    # Options/Derivatives
    expirydate = Column(Date)
    strikeprice = Column(Numeric)
    optiontype = Column(String)
    option_type = Column(String)
    
    # Trading specs
    lotsize = Column(Integer)
    ticksize = Column(Numeric)
    
    # Status
    permittedtotrade = Column(Boolean)
    deleteflag = Column(Boolean)
    
    # Tokens
    breeze_token = Column(String)
    kite_token = Column(String)
    
    # Dates
    localupdatedatetime = Column(DateTime)
    
    def to_dict(self):
        """Convert to dictionary"""
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
    
    def __repr__(self):
        return f"<SymbolMinimal(instrument_key='{self.instrument_key}', symbol='{self.symbol}')>"