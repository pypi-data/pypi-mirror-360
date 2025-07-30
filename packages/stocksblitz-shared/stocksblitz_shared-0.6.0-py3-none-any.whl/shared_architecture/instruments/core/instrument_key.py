"""
Universal Instrument Key System for StocksBlitz Platform

This module provides a standardized way to identify trading instruments across
all microservices and third-party broker integrations.
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List, Union, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
import re
import json

from .enums import AssetProductType, Exchange, OptionType, Moneyness
from .exceptions import InvalidInstrumentKeyError, ValidationError


@dataclass
class RelativeDate:
    """Represents relative date specifications for expiry dates"""
    type: str  # 'weekly', 'monthly', 'quarterly'
    offset: int = 0  # 0 = current, 1 = next, -1 = previous
    day_condition: Optional[str] = None  # 'if_wed_thu_fri_current_else_next'
    
    def resolve(self, reference_date: Optional[date] = None) -> date:
        """Resolve relative date to absolute date"""
        if reference_date is None:
            reference_date = date.today()
            
        # This is a simplified implementation
        # In production, this would integrate with market calendar service
        if self.type == "weekly":
            # Find next Thursday (typical Indian weekly expiry)
            days_ahead = 3 - reference_date.weekday()  # Thursday = 3
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            
            target_date = reference_date + timedelta(days=days_ahead)
            return target_date + timedelta(weeks=self.offset)
            
        elif self.type == "monthly":
            # Find last Thursday of current/next month
            # Simplified logic - in production would use market calendar
            if self.offset == 0:
                # Current month
                year, month = reference_date.year, reference_date.month
            else:
                # Calculate target month
                total_months = reference_date.month + self.offset
                year = reference_date.year + (total_months - 1) // 12
                month = ((total_months - 1) % 12) + 1
            
            # Find last Thursday of the month (simplified)
            # Last day of month
            if month == 12:
                last_day = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(year, month + 1, 1) - timedelta(days=1)
            
            # Find last Thursday
            days_back = (last_day.weekday() - 3) % 7
            last_thursday = last_day - timedelta(days=days_back)
            
            return last_thursday
            
        elif self.type == "quarterly":
            # Quarterly expiries (March, June, September, December)
            current_quarter = (reference_date.month - 1) // 3
            target_quarter = (current_quarter + self.offset) % 4
            target_year = reference_date.year + (current_quarter + self.offset) // 4
            
            # Quarterly months
            quarterly_months = [3, 6, 9, 12]
            target_month = quarterly_months[target_quarter]
            
            # Last Thursday of target month
            if target_month == 12:
                last_day = date(target_year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(target_year, target_month + 1, 1) - timedelta(days=1)
            
            days_back = (last_day.weekday() - 3) % 7
            return last_day - timedelta(days=days_back)
        
        # Default fallback
        return reference_date + timedelta(days=self.offset * 7)
    
    def __str__(self) -> str:
        base = f"REL_{self.type}_{self.offset}"
        if self.day_condition:
            base += f"_{self.day_condition}"
        return base


@dataclass
class InstrumentAttributes:
    """Container for instrument-specific attributes"""
    asset_product_type: AssetProductType
    symbol: str
    exchange: Exchange
    expiry_date: Optional[Union[date, RelativeDate]] = None
    option_type: Optional[OptionType] = None
    strike_price: Optional[Decimal] = None
    moneyness: Optional[Moneyness] = None
    lot_size: Optional[int] = None
    tick_size: Optional[Decimal] = None
    multiplier: Optional[int] = None
    custom_attributes: Dict[str, Any] = field(default_factory=dict)


class InstrumentKey:
    """
    Universal Instrument Key System
    
    Provides a standardized way to identify trading instruments with:
    - Support for all asset types and product types
    - Flexible date handling (absolute and relative)
    - Multiple representation formats
    - Third-party broker integration
    - Database integration capabilities
    """
    
    DELIMITER = "@"
    VERSION = "1.0"
    
    def __init__(self, attributes: InstrumentAttributes):
        self.attributes = attributes
        self._validate()
    
    def _validate(self):
        """Validate instrument attributes"""
        # Check required combinations
        if self.attributes.asset_product_type.supports_options():
            if not self.attributes.option_type:
                raise ValidationError("Options require option_type")
            if not (self.attributes.strike_price or self.attributes.moneyness):
                raise ValidationError("Options require either strike_price or moneyness")
        
        if self.attributes.asset_product_type.requires_expiry():
            if not self.attributes.expiry_date:
                raise ValidationError("Derivatives require expiry_date")
        
        # Validate symbol format
        if not self.attributes.symbol or len(self.attributes.symbol) > 50:
            raise ValidationError("Symbol must be 1-50 characters")
        
        # Validate strike price
        if self.attributes.strike_price is not None and self.attributes.strike_price <= 0:
            raise ValidationError("Strike price must be positive")
    
    @classmethod
    def from_string(cls, key_string: str) -> 'InstrumentKey':
        """
        Parse instrument key from string format
        
        Format: exchange@symbol@asset_product_type[@expiry_date][@option_type][@strike_price|moneyness]
        """
        if not key_string or not isinstance(key_string, str):
            raise InvalidInstrumentKeyError("Instrument key cannot be empty")
        
        parts = key_string.split(cls.DELIMITER)
        
        if len(parts) < 3:
            raise InvalidInstrumentKeyError(f"Invalid instrument key format: {key_string}")
        
        try:
            exchange = Exchange(parts[0])
            symbol = parts[1]
            asset_product_type = AssetProductType(parts[2])
        except ValueError as e:
            raise InvalidInstrumentKeyError(f"Invalid enum value in instrument key: {e}")
        
        attributes = InstrumentAttributes(
            asset_product_type=asset_product_type,
            symbol=symbol,
            exchange=exchange
        )
        
        # Parse optional components
        if len(parts) > 3 and parts[3]:
            attributes.expiry_date = cls._parse_date(parts[3])
        
        if len(parts) > 4 and parts[4]:
            try:
                attributes.option_type = OptionType(parts[4])
            except ValueError:
                raise InvalidInstrumentKeyError(f"Invalid option type: {parts[4]}")
        
        if len(parts) > 5 and parts[5]:
            # Could be strike price or moneyness
            try:
                # Try parsing as decimal first
                attributes.strike_price = Decimal(parts[5])
            except:
                try:
                    # Try parsing as moneyness
                    attributes.moneyness = Moneyness(parts[5])
                except ValueError:
                    raise InvalidInstrumentKeyError(f"Invalid strike price or moneyness: {parts[5]}")
        
        return cls(attributes)
    
    @staticmethod
    def _parse_date(date_str: str) -> Union[date, RelativeDate]:
        """Parse date string to date or RelativeDate object"""
        # Check if it's a relative date specification
        if date_str.startswith("REL_"):
            # Parse relative date format: REL_weekly_1 or REL_monthly_0_if_wed_thu_fri
            parts = date_str.split("_")
            if len(parts) < 3:
                raise InvalidInstrumentKeyError(f"Invalid relative date format: {date_str}")
            
            rel_type = parts[1]
            try:
                offset = int(parts[2])
            except ValueError:
                raise InvalidInstrumentKeyError(f"Invalid offset in relative date: {date_str}")
            
            condition = "_".join(parts[3:]) if len(parts) > 3 else None
            
            return RelativeDate(
                type=rel_type,
                offset=offset,
                day_condition=condition
            )
        
        # Parse absolute date
        # Support multiple date formats
        date_formats = ["%d-%b-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise InvalidInstrumentKeyError(f"Invalid date format: {date_str}")
    
    def to_string(self, include_moneyness: bool = False) -> str:
        """
        Convert to string representation
        
        Args:
            include_moneyness: If True and moneyness is available, use moneyness instead of strike_price
        """
        parts = [
            self.attributes.exchange.value,
            self.attributes.symbol,
            self.attributes.asset_product_type.value
        ]
        
        # Add expiry date if present
        if self.attributes.expiry_date:
            if isinstance(self.attributes.expiry_date, RelativeDate):
                parts.append(str(self.attributes.expiry_date))
            else:
                parts.append(self.attributes.expiry_date.strftime("%d-%b-%Y"))
        
        # Add option type if present
        if self.attributes.option_type:
            parts.append(self.attributes.option_type.value)
        
        # Add strike price or moneyness
        if include_moneyness and self.attributes.moneyness:
            parts.append(self.attributes.moneyness.value)
        elif self.attributes.strike_price:
            parts.append(str(self.attributes.strike_price))
        elif self.attributes.moneyness:
            parts.append(self.attributes.moneyness.value)
        
        return self.DELIMITER.join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = {
            'asset_product_type': self.attributes.asset_product_type.value,
            'symbol': self.attributes.symbol,
            'exchange': self.attributes.exchange.value,
            'version': self.VERSION
        }
        
        if self.attributes.expiry_date:
            if isinstance(self.attributes.expiry_date, RelativeDate):
                result['expiry_date'] = {
                    'type': 'relative',
                    'rel_type': self.attributes.expiry_date.type,
                    'offset': self.attributes.expiry_date.offset,
                    'condition': self.attributes.expiry_date.day_condition
                }
            else:
                result['expiry_date'] = {
                    'type': 'absolute',
                    'date': self.attributes.expiry_date.isoformat()
                }
        
        if self.attributes.option_type:
            result['option_type'] = self.attributes.option_type.value
        
        if self.attributes.strike_price:
            result['strike_price'] = float(self.attributes.strike_price)
        
        if self.attributes.moneyness:
            result['moneyness'] = self.attributes.moneyness.value
        
        if self.attributes.lot_size:
            result['lot_size'] = self.attributes.lot_size
        
        if self.attributes.tick_size:
            result['tick_size'] = float(self.attributes.tick_size)
        
        if self.attributes.multiplier:
            result['multiplier'] = self.attributes.multiplier
        
        if self.attributes.custom_attributes:
            result['custom_attributes'] = self.attributes.custom_attributes
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InstrumentKey':
        """Create from dictionary representation"""
        try:
            attributes = InstrumentAttributes(
                asset_product_type=AssetProductType(data['asset_product_type']),
                symbol=data['symbol'],
                exchange=Exchange(data['exchange'])
            )
        except KeyError as e:
            raise InvalidInstrumentKeyError(f"Missing required field: {e}")
        except ValueError as e:
            raise InvalidInstrumentKeyError(f"Invalid enum value: {e}")
        
        # Parse expiry date
        if 'expiry_date' in data:
            exp_data = data['expiry_date']
            if exp_data['type'] == 'relative':
                attributes.expiry_date = RelativeDate(
                    type=exp_data['rel_type'],
                    offset=exp_data['offset'],
                    day_condition=exp_data.get('condition')
                )
            else:
                attributes.expiry_date = datetime.fromisoformat(exp_data['date']).date()
        
        if 'option_type' in data:
            attributes.option_type = OptionType(data['option_type'])
        
        if 'strike_price' in data:
            attributes.strike_price = Decimal(str(data['strike_price']))
        
        if 'moneyness' in data:
            attributes.moneyness = Moneyness(data['moneyness'])
        
        if 'lot_size' in data:
            attributes.lot_size = data['lot_size']
        
        if 'tick_size' in data:
            attributes.tick_size = Decimal(str(data['tick_size']))
        
        if 'multiplier' in data:
            attributes.multiplier = data['multiplier']
        
        if 'custom_attributes' in data:
            attributes.custom_attributes = data['custom_attributes']
        
        return cls(attributes)
    
    def get_variants(self) -> List['InstrumentKey']:
        """
        Get all valid variants of this instrument key
        
        For example, an option can have both strike_price and moneyness variants
        """
        variants = [self]
        
        # For options with strike price, we could add moneyness variant if calculable
        # This would require current market data, so we'll keep it simple for now
        
        return variants
    
    def resolve_relative_dates(self, reference_date: Optional[date] = None) -> 'InstrumentKey':
        """Resolve any relative dates to absolute dates"""
        if isinstance(self.attributes.expiry_date, RelativeDate):
            resolved_date = self.attributes.expiry_date.resolve(reference_date)
            
            # Create new attributes with resolved date
            new_attributes = InstrumentAttributes(
                asset_product_type=self.attributes.asset_product_type,
                symbol=self.attributes.symbol,
                exchange=self.attributes.exchange,
                expiry_date=resolved_date,
                option_type=self.attributes.option_type,
                strike_price=self.attributes.strike_price,
                moneyness=self.attributes.moneyness,
                lot_size=self.attributes.lot_size,
                tick_size=self.attributes.tick_size,
                multiplier=self.attributes.multiplier,
                custom_attributes=self.attributes.custom_attributes.copy()
            )
            
            return InstrumentKey(new_attributes)
        
        return self
    
    def is_option(self) -> bool:
        """Check if this instrument is an option"""
        return self.attributes.asset_product_type.supports_options()
    
    def is_derivative(self) -> bool:
        """Check if this instrument is a derivative"""
        return self.attributes.asset_product_type.is_derivative()
    
    def requires_expiry(self) -> bool:
        """Check if this instrument requires an expiry date"""
        return self.attributes.asset_product_type.requires_expiry()
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        return f"InstrumentKey({self.to_string()})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, InstrumentKey):
            return False
        return self.to_string() == other.to_string()
    
    def __hash__(self) -> int:
        return hash(self.to_string())
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, InstrumentKey):
            return NotImplemented
        return self.to_string() < other.to_string()