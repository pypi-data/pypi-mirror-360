# shared_architecture/exceptions/base_exceptions.py

class ServiceUnavailableError(Exception):
    """Raised when a required service is unavailable"""
    pass

class UnauthorizedServiceError(Exception):
    """Raised when service access is unauthorized"""
    pass

class ServiceTimeoutError(Exception):
    """Raised when service request times out"""
    pass

class ServiceConnectionError(Exception):
    """Raised when service connection fails"""
    pass