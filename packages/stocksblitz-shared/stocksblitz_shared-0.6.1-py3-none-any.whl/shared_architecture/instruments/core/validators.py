"""
Validation utilities for the instrument management system
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date, datetime
import re

from .enums import AssetProductType, Exchange, OptionType, Moneyness
from .exceptions import ValidationError


class InstrumentValidator:
    """
    Comprehensive validation for instrument attributes
    """
    
    # Symbol validation patterns
    SYMBOL_PATTERNS = {
        'nse_equity': r'^[A-Z0-9&-]{1,25}$',
        'bse_equity': r'^[A-Z0-9&-]{1,25}$',
        'nse_index': r'^[A-Z0-9]{1,20}$',
        'mcx_commodity': r'^[A-Z0-9]{1,20}$',
        'us_equity': r'^[A-Z]{1,5}$',
        'crypto': r'^[A-Z0-9]{1,10}$',
        'default': r'^[A-Z0-9&-]{1,50}$'
    }
    
    # Strike price validation ranges
    STRIKE_RANGES = {
        'equity': (0.01, 100000),
        'index': (1, 50000),
        'commodity': (0.01, 100000),
        'currency': (0.0001, 1000),
        'crypto': (0.01, 1000000)
    }
    
    @classmethod
    def validate_symbol(cls, symbol: str, exchange: Exchange, 
                       asset_product_type: AssetProductType) -> bool:
        """
        Validate symbol format based on exchange and asset type
        """
        if not symbol or not isinstance(symbol, str):
            raise ValidationError("Symbol must be a non-empty string")
        
        # Get appropriate pattern
        pattern_key = cls._get_symbol_pattern_key(exchange, asset_product_type)
        pattern = cls.SYMBOL_PATTERNS.get(pattern_key, cls.SYMBOL_PATTERNS['default'])
        
        if not re.match(pattern, symbol):
            raise ValidationError(f"Invalid symbol format for {exchange.value}: {symbol}")
        
        return True
    
    @classmethod
    def _get_symbol_pattern_key(cls, exchange: Exchange, 
                              asset_product_type: AssetProductType) -> str:
        """
        Get the appropriate pattern key for symbol validation
        """
        asset_class = asset_product_type.asset_class
        
        if exchange == Exchange.NSE:
            if asset_class == 'equity':
                return 'nse_equity'
            elif asset_class == 'index':
                return 'nse_index'
        elif exchange == Exchange.BSE:
            if asset_class == 'equity':
                return 'bse_equity'
        elif exchange == Exchange.MCX:
            return 'mcx_commodity'
        elif exchange in [Exchange.NYSE, Exchange.NASDAQ]:
            return 'us_equity'
        elif exchange in [Exchange.BINANCE, Exchange.COINBASE]:
            return 'crypto'
        
        return 'default'
    
    @classmethod
    def validate_strike_price(cls, strike_price: Decimal, 
                            asset_product_type: AssetProductType) -> bool:
        """
        Validate strike price based on asset type
        """
        if strike_price is None:
            return True  # Optional field
        
        if not isinstance(strike_price, Decimal):
            raise ValidationError("Strike price must be a Decimal")
        
        if strike_price <= 0:
            raise ValidationError("Strike price must be positive")
        
        # Get range based on asset class
        asset_class = asset_product_type.asset_class
        min_val, max_val = cls.STRIKE_RANGES.get(asset_class, (0.01, 1000000))
        
        if not (min_val <= float(strike_price) <= max_val):
            raise ValidationError(
                f"Strike price {strike_price} outside valid range "
                f"[{min_val}, {max_val}] for {asset_class}"
            )
        
        return True
    
    @classmethod
    def validate_expiry_date(cls, expiry_date: date, 
                           asset_product_type: AssetProductType) -> bool:
        """
        Validate expiry date for derivatives
        """
        if expiry_date is None:
            if asset_product_type.requires_expiry():
                raise ValidationError(f"{asset_product_type.value} requires expiry date")
            return True
        
        if not isinstance(expiry_date, date):
            raise ValidationError("Expiry date must be a date object")
        
        # Check if date is in the future (for new instruments)
        if expiry_date <= date.today():
            # Allow historical dates for backtesting, but warn
            pass
        
        # Check if date is not too far in the future (10 years)
        max_future_date = date.today().replace(year=date.today().year + 10)
        if expiry_date > max_future_date:
            raise ValidationError(f"Expiry date {expiry_date} is too far in the future")
        
        return True
    
    @classmethod
    def validate_option_attributes(cls, option_type: Optional[OptionType],
                                 strike_price: Optional[Decimal],
                                 moneyness: Optional[Moneyness],
                                 asset_product_type: AssetProductType) -> bool:
        """
        Validate option-specific attributes
        """
        if not asset_product_type.supports_options():
            if option_type or strike_price or moneyness:
                raise ValidationError(
                    f"{asset_product_type.value} does not support option attributes"
                )
            return True
        
        # For options, we need either strike price or moneyness
        if not (strike_price or moneyness):
            raise ValidationError("Options require either strike_price or moneyness")
        
        # Option type is required for options
        if not option_type:
            raise ValidationError("Options require option_type")
        
        return True
    
    @classmethod
    def validate_lot_size(cls, lot_size: Optional[int],
                         asset_product_type: AssetProductType) -> bool:
        """
        Validate lot size
        """
        if lot_size is None:
            return True
        
        if not isinstance(lot_size, int) or lot_size <= 0:
            raise ValidationError("Lot size must be a positive integer")
        
        # Check reasonable bounds
        if lot_size > 1000000:
            raise ValidationError(f"Lot size {lot_size} seems unreasonably large")
        
        return True
    
    @classmethod
    def validate_tick_size(cls, tick_size: Optional[Decimal],
                          asset_product_type: AssetProductType) -> bool:
        """
        Validate tick size
        """
        if tick_size is None:
            return True
        
        if not isinstance(tick_size, Decimal) or tick_size <= 0:
            raise ValidationError("Tick size must be a positive Decimal")
        
        # Check reasonable bounds
        if tick_size > Decimal('1000'):
            raise ValidationError(f"Tick size {tick_size} seems unreasonably large")
        
        return True
    
    @classmethod
    def validate_instrument_combination(cls, exchange: Exchange,
                                      asset_product_type: AssetProductType) -> bool:
        """
        Validate that exchange supports the asset-product type
        """
        # Define supported combinations
        supported_combinations = {
            Exchange.NSE: [
                'equity_spot', 'equity_futures', 'equity_options',
                'index_spot', 'index_futures', 'index_options',
                'currency_futures', 'currency_options'
            ],
            Exchange.BSE: [
                'equity_spot', 'equity_futures', 'equity_options',
                'index_spot'
            ],
            Exchange.MCX: [
                'commodity_spot', 'commodity_futures', 'commodity_options'
            ],
            Exchange.NYSE: [
                'equity_spot', 'equity_options', 'equity_etf'
            ],
            Exchange.NASDAQ: [
                'equity_spot', 'equity_options', 'equity_etf'
            ],
            Exchange.BINANCE: [
                'crypto_spot', 'crypto_futures', 'crypto_options', 'crypto_perpetual'
            ],
            Exchange.COINBASE: [
                'crypto_spot'
            ]
        }
        
        exchange_supported = supported_combinations.get(exchange, [])
        
        if asset_product_type.value not in exchange_supported:
            raise ValidationError(
                f"Exchange {exchange.value} does not support {asset_product_type.value}"
            )
        
        return True
    
    @classmethod
    def validate_isin(cls, isin: str) -> bool:
        """
        Validate ISIN format
        """
        if not isin:
            return True  # ISIN is optional
        
        if not isinstance(isin, str):
            raise ValidationError("ISIN must be a string")
        
        # ISIN format: 2 letters + 9 alphanumeric + 1 check digit
        if len(isin) != 12:
            raise ValidationError("ISIN must be 12 characters long")
        
        if not re.match(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$', isin):
            raise ValidationError("Invalid ISIN format")
        
        # TODO: Implement ISIN check digit validation
        
        return True
    
    @classmethod
    def validate_custom_attributes(cls, custom_attributes: Optional[Dict[str, Any]]) -> bool:
        """
        Validate custom attributes
        """
        if custom_attributes is None:
            return True
        
        if not isinstance(custom_attributes, dict):
            raise ValidationError("Custom attributes must be a dictionary")
        
        # Check for reserved keys
        reserved_keys = {
            'id', 'instrument_key', 'created_at', 'updated_at',
            'asset_product_type', 'exchange', 'symbol'
        }
        
        for key in custom_attributes.keys():
            if key in reserved_keys:
                raise ValidationError(f"Custom attribute key '{key}' is reserved")
        
        # Check value types (should be JSON serializable)
        try:
            import json
            json.dumps(custom_attributes)
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Custom attributes must be JSON serializable: {e}")
        
        return True


class BusinessRuleValidator:
    """
    Business rule validation for instruments
    """
    
    @classmethod
    def validate_trading_hours(cls, exchange: Exchange, 
                             current_time: Optional[datetime] = None) -> bool:
        """
        Validate if the exchange is currently open for trading
        """
        if current_time is None:
            current_time = datetime.now()
        
        # This is a simplified implementation
        # In production, this would integrate with market calendar service
        
        # Define basic trading hours (in local time)
        trading_hours = {
            Exchange.NSE: ((9, 15), (15, 30)),  # 9:15 AM to 3:30 PM
            Exchange.BSE: ((9, 15), (15, 30)),
            Exchange.MCX: ((9, 0), (23, 30)),   # 9:00 AM to 11:30 PM
            Exchange.NYSE: ((9, 30), (16, 0)),  # 9:30 AM to 4:00 PM EST
            Exchange.NASDAQ: ((9, 30), (16, 0)),
            Exchange.BINANCE: ((0, 0), (23, 59)),  # 24/7
            Exchange.COINBASE: ((0, 0), (23, 59))
        }
        
        if exchange not in trading_hours:
            return True  # Unknown exchange, assume always open
        
        start_hour, start_min = trading_hours[exchange][0]
        end_hour, end_min = trading_hours[exchange][1]
        
        current_hour = current_time.hour
        current_min = current_time.minute
        
        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min
        current_minutes = current_hour * 60 + current_min
        
        return start_minutes <= current_minutes <= end_minutes
    
    @classmethod
    def validate_expiry_schedule(cls, expiry_date: date, 
                               asset_product_type: AssetProductType,
                               exchange: Exchange) -> bool:
        """
        Validate that expiry date follows exchange schedule
        """
        # This is a simplified implementation
        # In production, this would check against exchange calendars
        
        # Basic rule: expiry should be on Thursday for Indian options
        if exchange in [Exchange.NSE, Exchange.BSE]:
            if asset_product_type.supports_options():
                if expiry_date.weekday() != 3:  # Thursday = 3
                    raise ValidationError(
                        f"Indian options typically expire on Thursday, got {expiry_date.strftime('%A')}"
                    )
        
        return True