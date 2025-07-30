"""
Custom exceptions for the instrument management system
"""


class InstrumentError(Exception):
    """Base exception for instrument-related errors"""
    pass


class InvalidInstrumentKeyError(InstrumentError):
    """Raised when an instrument key format is invalid"""
    pass


class InstrumentNotFoundError(InstrumentError):
    """Raised when an instrument is not found"""
    pass


class UnsupportedBrokerError(InstrumentError):
    """Raised when a broker is not supported"""
    pass


class ValidationError(InstrumentError):
    """Raised when instrument validation fails"""
    pass


class ConversionError(InstrumentError):
    """Raised when broker format conversion fails"""
    pass


class MoneynessCalculationError(InstrumentError):
    """Raised when moneyness calculation fails"""
    pass


# Commented out - table dropped
# class CorporateActionError(InstrumentError):
#     """Raised when corporate action processing fails"""
#     pass


class MarketDataError(InstrumentError):
    """Raised when market data is unavailable or invalid"""
    pass


class CacheError(InstrumentError):
    """Raised when cache operations fail"""
    pass


class ServiceUnavailableError(InstrumentError):
    """Raised when the instrument management service is unavailable"""
    pass