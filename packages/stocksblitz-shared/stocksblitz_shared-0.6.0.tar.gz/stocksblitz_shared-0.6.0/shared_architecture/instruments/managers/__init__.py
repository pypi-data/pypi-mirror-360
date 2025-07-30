"""
Manager modules for instrument operations
"""

from .local_manager import LocalInstrumentManager
from .service_client import InstrumentServiceClient

__all__ = ["LocalInstrumentManager", "InstrumentServiceClient"]