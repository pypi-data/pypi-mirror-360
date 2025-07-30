"""
Shared validation utilities for all microservices
Provides common validation patterns, decorators, and error handling
"""

import re
import json
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError, validator
from functools import wraps
import logging

from shared_architecture.utils.logging_utils import log_warning, log_exception

# Common validation patterns
class ValidationPatterns:
    """Common regex patterns for validation"""
    
    EMAIL = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE = re.compile(r'^\+?1?-?\.?\s?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
    
    # Trading-specific patterns
    INSTRUMENT_KEY = re.compile(r'^[A-Z]+:[A-Z0-9]+:[A-Z0-9-]+$')  # Format: EXCHANGE:SYMBOL:EXPIRY-STRIKE-TYPE
    SYMBOL_CODE = re.compile(r'^[A-Z0-9]{1,20}$')
    ORDER_ID = re.compile(r'^[A-Z0-9]{8,50}$')
    
    # Financial patterns
    PRICE = re.compile(r'^\d+(\.\d{1,4})?$')  # Up to 4 decimal places
    QUANTITY = re.compile(r'^\d+$')  # Whole numbers only
    
    # Security patterns
    JWT_TOKEN = re.compile(r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$')
    API_KEY = re.compile(r'^[A-Za-z0-9]{32,128}$')

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)

class BaseValidator:
    """Base validator class with common validation methods"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        return bool(ValidationPatterns.EMAIL.match(email.strip().lower()))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone or not isinstance(phone, str):
            return False
        return bool(ValidationPatterns.PHONE.match(phone.strip()))
    
    @staticmethod
    def validate_instrument_key(instrument_key: str) -> bool:
        """Validate trading instrument key format"""
        if not instrument_key or not isinstance(instrument_key, str):
            return False
        return bool(ValidationPatterns.INSTRUMENT_KEY.match(instrument_key.strip().upper()))
    
    @staticmethod
    def validate_symbol_code(symbol: str) -> bool:
        """Validate symbol code format"""
        if not symbol or not isinstance(symbol, str):
            return False
        return bool(ValidationPatterns.SYMBOL_CODE.match(symbol.strip().upper()))
    
    @staticmethod
    def validate_price(price: Union[str, float, Decimal]) -> bool:
        """Validate price format and range"""
        try:
            if isinstance(price, str):
                if not ValidationPatterns.PRICE.match(price):
                    return False
                price = float(price)
            
            if isinstance(price, (int, float)):
                return 0 <= price <= 1000000  # Reasonable price range
            
            if isinstance(price, Decimal):
                return Decimal('0') <= price <= Decimal('1000000')
            
            return False
        except (ValueError, InvalidOperation):
            return False
    
    @staticmethod
    def validate_quantity(quantity: Union[str, int]) -> bool:
        """Validate quantity format and range"""
        try:
            if isinstance(quantity, str):
                if not ValidationPatterns.QUANTITY.match(quantity):
                    return False
                quantity = int(quantity)
            
            return isinstance(quantity, int) and 0 < quantity <= 10000000
        except ValueError:
            return False
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date, max_days: int = 365) -> bool:
        """Validate date range"""
        if not isinstance(start_date, date) or not isinstance(end_date, date):
            return False
        
        if start_date > end_date:
            return False
        
        if (end_date - start_date).days > max_days:
            return False
        
        return True
    
    @staticmethod
    def validate_json_structure(data: str, required_fields: List[str] = None) -> bool:
        """Validate JSON structure and required fields"""
        try:
            parsed_data = json.loads(data) if isinstance(data, str) else data
            
            if not isinstance(parsed_data, dict):
                return False
            
            if required_fields:
                return all(field in parsed_data for field in required_fields)
            
            return True
        except (json.JSONDecodeError, TypeError):
            return False

class TradingValidator(BaseValidator):
    """Validator for trading-specific data"""
    
    VALID_EXCHANGES = {"NSE", "BSE", "NFO", "BFO", "MCX"}
    VALID_ORDER_TYPES = {"MARKET", "LIMIT", "SL", "SL-M"}
    VALID_PRODUCT_TYPES = {"CNC", "MIS", "NRML"}
    VALID_TRANSACTION_TYPES = {"BUY", "SELL"}
    
    @classmethod
    def validate_exchange(cls, exchange: str) -> bool:
        """Validate exchange code"""
        if not exchange or not isinstance(exchange, str):
            return False
        return exchange.strip().upper() in cls.VALID_EXCHANGES
    
    @classmethod
    def validate_order_type(cls, order_type: str) -> bool:
        """Validate order type"""
        if not order_type or not isinstance(order_type, str):
            return False
        return order_type.strip().upper() in cls.VALID_ORDER_TYPES
    
    @classmethod
    def validate_product_type(cls, product_type: str) -> bool:
        """Validate product type"""
        if not product_type or not isinstance(product_type, str):
            return False
        return product_type.strip().upper() in cls.VALID_PRODUCT_TYPES
    
    @classmethod
    def validate_transaction_type(cls, transaction_type: str) -> bool:
        """Validate transaction type (BUY/SELL)"""
        if not transaction_type or not isinstance(transaction_type, str):
            return False
        return transaction_type.strip().upper() in cls.VALID_TRANSACTION_TYPES
    
    @classmethod
    def validate_order_data(cls, order_data: Dict[str, Any]) -> List[str]:
        """Validate complete order data and return list of errors"""
        errors = []
        
        # Required fields
        required_fields = ["instrument_key", "quantity", "price", "order_type", "transaction_type"]
        for field in required_fields:
            if field not in order_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate individual fields
        if "instrument_key" in order_data and not cls.validate_instrument_key(order_data["instrument_key"]):
            errors.append("Invalid instrument_key format")
        
        if "quantity" in order_data and not cls.validate_quantity(order_data["quantity"]):
            errors.append("Invalid quantity")
        
        if "price" in order_data and not cls.validate_price(order_data["price"]):
            errors.append("Invalid price")
        
        if "order_type" in order_data and not cls.validate_order_type(order_data["order_type"]):
            errors.append("Invalid order_type")
        
        if "transaction_type" in order_data and not cls.validate_transaction_type(order_data["transaction_type"]):
            errors.append("Invalid transaction_type")
        
        if "exchange" in order_data and not cls.validate_exchange(order_data["exchange"]):
            errors.append("Invalid exchange")
        
        return errors

def validate_request(validator_class: type = BaseValidator):
    """
    Decorator for validating request data using specified validator class
    
    Usage:
        @validate_request(TradingValidator)
        async def create_order(order_data: dict):
            # order_data is automatically validated
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request data from kwargs
            request_data = None
            for arg in args:
                if isinstance(arg, dict):
                    request_data = arg
                    break
            
            if not request_data:
                for value in kwargs.values():
                    if isinstance(value, dict):
                        request_data = value
                        break
            
            # Validate if we found request data
            if request_data and hasattr(validator_class, 'validate_order_data'):
                errors = validator_class.validate_order_data(request_data)
                if errors:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"validation_errors": errors}
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def validate_pydantic_model(model_class: BaseModel):
    """
    Decorator for automatic Pydantic model validation
    
    Usage:
        @validate_pydantic_model(OrderSchema)
        async def create_order(order_data: dict):
            # order_data is validated against OrderSchema
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Find dict argument to validate
                for i, arg in enumerate(args):
                    if isinstance(arg, dict):
                        validated_data = model_class(**arg)
                        args = list(args)
                        args[i] = validated_data.dict()
                        args = tuple(args)
                        break
                
                return await func(*args, **kwargs)
            except ValidationError as e:
                log_warning(f"Pydantic validation failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"validation_errors": e.errors()}
                )
        return wrapper
    return decorator

class PaginationValidator:
    """Validator for pagination parameters"""
    
    MAX_PAGE_SIZE = 1000
    DEFAULT_PAGE_SIZE = 50
    
    @classmethod
    def validate_pagination(cls, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> tuple:
        """Validate and normalize pagination parameters"""
        try:
            page = max(1, int(page))
            page_size = max(1, min(cls.MAX_PAGE_SIZE, int(page_size)))
            offset = (page - 1) * page_size
            return page, page_size, offset
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid pagination parameters"
            )

class DateTimeValidator:
    """Validator for date and time parameters"""
    
    @staticmethod
    def validate_datetime_string(datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """Validate and parse datetime string"""
        try:
            return datetime.strptime(datetime_str, format_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid datetime format. Expected: {format_str}"
            )
    
    @staticmethod
    def validate_date_string(date_str: str, format_str: str = "%Y-%m-%d") -> date:
        """Validate and parse date string"""
        try:
            return datetime.strptime(date_str, format_str).date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date format. Expected: {format_str}"
            )

# Utility functions for common validation scenarios
def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that all required fields are present"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )

def sanitize_string(value: str, max_length: int = 255, allow_special_chars: bool = True) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # Check length
    if len(value) > max_length:
        raise ValidationError(f"Value exceeds maximum length of {max_length}")
    
    # Remove potentially dangerous characters if not allowed
    if not allow_special_chars:
        value = re.sub(r'[<>"\']', '', value)
    
    return value

def validate_numeric_range(value: Union[int, float], min_val: float = None, max_val: float = None) -> None:
    """Validate numeric value is within specified range"""
    if min_val is not None and value < min_val:
        raise ValidationError(f"Value {value} is below minimum {min_val}")
    
    if max_val is not None and value > max_val:
        raise ValidationError(f"Value {value} is above maximum {max_val}")

# Export commonly used validators
__all__ = [
    'ValidationPatterns',
    'ValidationError', 
    'BaseValidator',
    'TradingValidator',
    'PaginationValidator',
    'DateTimeValidator',
    'validate_request',
    'validate_pydantic_model',
    'validate_required_fields',
    'sanitize_string',
    'validate_numeric_range'
]