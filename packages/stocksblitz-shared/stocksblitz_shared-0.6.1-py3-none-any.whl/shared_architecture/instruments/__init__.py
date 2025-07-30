"""
Universal Instrument Management for StocksBlitz Platform

This module provides a standardized way to identify trading instruments across
all microservices and third-party broker integrations.

Core Classes:
    InstrumentKey: Universal instrument identification
    InstrumentKeyFactory: Factory methods for creating instruments
    LocalInstrumentManager: High-performance local operations
    BrokerConverter: Third-party format conversions

Example Usage:
    # Create equity instrument
    nifty = InstrumentKeyFactory.equity_spot("NIFTY", Exchange.NSE)
    
    # Create option with moneyness
    option = InstrumentKeyFactory.index_options(
        "NIFTY", RelativeDate("weekly", 0), OptionType.CALL, moneyness=Moneyness.ATM
    )
    
    # Parse from string
    parsed = InstrumentKey.from_string("NSE@NIFTY@index_options@31-JUL-2025@call@25000")
    
    # Convert to broker format
    breeze_symbol = option.to_broker_format("breeze")
"""

# Import submodules to make them accessible
from . import core
from . import managers  
from . import utils

from .core.instrument_key import InstrumentKey, InstrumentAttributes, RelativeDate
from .core.enums import AssetProductType, Exchange, OptionType, Moneyness
from .core.exceptions import (
    InstrumentError, InvalidInstrumentKeyError, InstrumentNotFoundError,
    UnsupportedBrokerError, ValidationError
)
from .managers.local_manager import LocalInstrumentManager
from .managers.service_client import InstrumentServiceClient
from .utils.factory import InstrumentKeyFactory

__version__ = "1.0.0"
__all__ = [
    # Submodules
    "core",
    "managers",
    "utils",
    
    # Core classes
    "InstrumentKey",
    "InstrumentAttributes", 
    "RelativeDate",
    
    # Enums
    "AssetProductType",
    "Exchange",
    "OptionType", 
    "Moneyness",
    
    # Exceptions
    "InstrumentError",
    "InvalidInstrumentKeyError",
    "InstrumentNotFoundError",
    "UnsupportedBrokerError",
    "ValidationError",
    
    # Managers
    "LocalInstrumentManager",
    "InstrumentServiceClient",
    
    # Utilities
    "InstrumentKeyFactory",
]