"""
Tests for the InstrumentKey class
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from ..core.instrument_key import InstrumentKey, InstrumentAttributes, RelativeDate
from ..core.enums import AssetProductType, Exchange, OptionType, Moneyness
from ..core.exceptions import InvalidInstrumentKeyError, ValidationError


class TestInstrumentKey:
    """Test cases for InstrumentKey class"""
    
    def test_equity_spot_creation(self):
        """Test creating equity spot instrument"""
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.EQUITY_SPOT,
            symbol="RELIANCE",
            exchange=Exchange.NSE
        )
        
        instrument = InstrumentKey(attributes)
        
        assert instrument.attributes.symbol == "RELIANCE"
        assert instrument.attributes.exchange == Exchange.NSE
        assert instrument.attributes.asset_product_type == AssetProductType.EQUITY_SPOT
        assert instrument.to_string() == "NSE@RELIANCE@equity_spot"
    
    def test_option_creation_with_strike(self):
        """Test creating option with strike price"""
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.INDEX_OPTIONS,
            symbol="NIFTY",
            exchange=Exchange.NSE,
            expiry_date=date(2025, 7, 31),
            option_type=OptionType.CALL,
            strike_price=Decimal("25000")
        )
        
        instrument = InstrumentKey(attributes)
        
        assert instrument.is_option()
        assert instrument.is_derivative()
        assert instrument.requires_expiry()
        assert instrument.to_string() == "NSE@NIFTY@index_options@31-Jul-2025@call@25000"
    
    def test_option_creation_with_moneyness(self):
        """Test creating option with moneyness"""
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.INDEX_OPTIONS,
            symbol="NIFTY",
            exchange=Exchange.NSE,
            expiry_date=date(2025, 7, 31),
            option_type=OptionType.PUT,
            moneyness=Moneyness.ATM
        )
        
        instrument = InstrumentKey(attributes)
        
        assert instrument.to_string(include_moneyness=True) == "NSE@NIFTY@index_options@31-Jul-2025@put@ATM"
    
    def test_relative_date_creation(self):
        """Test creating instrument with relative date"""
        rel_date = RelativeDate("weekly", 1)
        
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.INDEX_OPTIONS,
            symbol="NIFTY",
            exchange=Exchange.NSE,
            expiry_date=rel_date,
            option_type=OptionType.CALL,
            strike_price=Decimal("25000")
        )
        
        instrument = InstrumentKey(attributes)
        
        assert str(rel_date) == "REL_weekly_1"
        assert "REL_weekly_1" in instrument.to_string()
    
    def test_from_string_parsing(self):
        """Test parsing from string format"""
        key_string = "NSE@RELIANCE@equity_spot"
        instrument = InstrumentKey.from_string(key_string)
        
        assert instrument.attributes.symbol == "RELIANCE"
        assert instrument.attributes.exchange == Exchange.NSE
        assert instrument.attributes.asset_product_type == AssetProductType.EQUITY_SPOT
    
    def test_from_string_with_option(self):
        """Test parsing option from string"""
        key_string = "NSE@NIFTY@index_options@31-Jul-2025@call@25000"
        instrument = InstrumentKey.from_string(key_string)
        
        assert instrument.attributes.symbol == "NIFTY"
        assert instrument.attributes.option_type == OptionType.CALL
        assert instrument.attributes.strike_price == Decimal("25000")
        assert instrument.attributes.expiry_date == date(2025, 7, 31)
    
    def test_from_string_with_moneyness(self):
        """Test parsing option with moneyness from string"""
        key_string = "NSE@NIFTY@index_options@31-Jul-2025@call@ATM"
        instrument = InstrumentKey.from_string(key_string)
        
        assert instrument.attributes.moneyness == Moneyness.ATM
        assert instrument.attributes.strike_price is None
    
    def test_from_string_with_relative_date(self):
        """Test parsing with relative date"""
        key_string = "NSE@NIFTY@index_options@REL_weekly_1@call@25000"
        instrument = InstrumentKey.from_string(key_string)
        
        assert isinstance(instrument.attributes.expiry_date, RelativeDate)
        assert instrument.attributes.expiry_date.type == "weekly"
        assert instrument.attributes.expiry_date.offset == 1
    
    def test_invalid_key_format(self):
        """Test invalid key format raises exception"""
        with pytest.raises(InvalidInstrumentKeyError):
            InstrumentKey.from_string("INVALID")
        
        with pytest.raises(InvalidInstrumentKeyError):
            InstrumentKey.from_string("NSE@RELIANCE")  # Missing asset_product_type
        
        with pytest.raises(InvalidInstrumentKeyError):
            InstrumentKey.from_string("")
    
    def test_validation_errors(self):
        """Test validation errors"""
        # Option without option type
        with pytest.raises(ValidationError):
            attributes = InstrumentAttributes(
                asset_product_type=AssetProductType.INDEX_OPTIONS,
                symbol="NIFTY",
                exchange=Exchange.NSE,
                expiry_date=date(2025, 7, 31),
                strike_price=Decimal("25000")
                # Missing option_type
            )
            InstrumentKey(attributes)
        
        # Option without strike or moneyness
        with pytest.raises(ValidationError):
            attributes = InstrumentAttributes(
                asset_product_type=AssetProductType.INDEX_OPTIONS,
                symbol="NIFTY",
                exchange=Exchange.NSE,
                expiry_date=date(2025, 7, 31),
                option_type=OptionType.CALL
                # Missing strike_price or moneyness
            )
            InstrumentKey(attributes)
        
        # Derivative without expiry
        with pytest.raises(ValidationError):
            attributes = InstrumentAttributes(
                asset_product_type=AssetProductType.INDEX_FUTURES,
                symbol="NIFTY",
                exchange=Exchange.NSE
                # Missing expiry_date
            )
            InstrumentKey(attributes)
    
    def test_to_dict_conversion(self):
        """Test converting to dictionary"""
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.INDEX_OPTIONS,
            symbol="NIFTY",
            exchange=Exchange.NSE,
            expiry_date=date(2025, 7, 31),
            option_type=OptionType.CALL,
            strike_price=Decimal("25000")
        )
        
        instrument = InstrumentKey(attributes)
        data = instrument.to_dict()
        
        assert data["symbol"] == "NIFTY"
        assert data["asset_product_type"] == "index_options"
        assert data["exchange"] == "NSE"
        assert data["option_type"] == "call"
        assert data["strike_price"] == 25000.0
        assert data["expiry_date"]["type"] == "absolute"
    
    def test_from_dict_conversion(self):
        """Test creating from dictionary"""
        data = {
            "asset_product_type": "index_options",
            "symbol": "NIFTY",
            "exchange": "NSE",
            "expiry_date": {
                "type": "absolute",
                "date": "2025-07-31"
            },
            "option_type": "call",
            "strike_price": 25000.0
        }
        
        instrument = InstrumentKey.from_dict(data)
        
        assert instrument.attributes.symbol == "NIFTY"
        assert instrument.attributes.strike_price == Decimal("25000.0")
        assert instrument.attributes.expiry_date == date(2025, 7, 31)
    
    def test_relative_date_resolution(self):
        """Test relative date resolution"""
        rel_date = RelativeDate("weekly", 1)
        resolved = rel_date.resolve(date(2025, 7, 1))  # Tuesday
        
        # Should resolve to next week's Thursday
        assert resolved.weekday() == 3  # Thursday
        assert resolved > date(2025, 7, 1)
    
    def test_resolve_relative_dates(self):
        """Test resolving relative dates in instrument"""
        rel_date = RelativeDate("weekly", 0)
        
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.INDEX_OPTIONS,
            symbol="NIFTY",
            exchange=Exchange.NSE,
            expiry_date=rel_date,
            option_type=OptionType.CALL,
            strike_price=Decimal("25000")
        )
        
        instrument = InstrumentKey(attributes)
        resolved_instrument = instrument.resolve_relative_dates(date(2025, 7, 1))
        
        assert isinstance(resolved_instrument.attributes.expiry_date, date)
        assert resolved_instrument.attributes.expiry_date.weekday() == 3  # Thursday
    
    def test_equality_and_hashing(self):
        """Test equality and hashing"""
        attributes1 = InstrumentAttributes(
            asset_product_type=AssetProductType.EQUITY_SPOT,
            symbol="RELIANCE",
            exchange=Exchange.NSE
        )
        
        attributes2 = InstrumentAttributes(
            asset_product_type=AssetProductType.EQUITY_SPOT,
            symbol="RELIANCE",
            exchange=Exchange.NSE
        )
        
        instrument1 = InstrumentKey(attributes1)
        instrument2 = InstrumentKey(attributes2)
        
        assert instrument1 == instrument2
        assert hash(instrument1) == hash(instrument2)
        
        # Test in set
        instrument_set = {instrument1, instrument2}
        assert len(instrument_set) == 1
    
    def test_comparison(self):
        """Test comparison operators"""
        reliance = InstrumentKey.from_string("NSE@RELIANCE@equity_spot")
        tcs = InstrumentKey.from_string("NSE@TCS@equity_spot")
        
        # Should sort alphabetically by string representation
        assert reliance > tcs  # R comes after T in the alphabet when comparing full strings
    
    def test_string_representations(self):
        """Test string representations"""
        instrument = InstrumentKey.from_string("NSE@RELIANCE@equity_spot")
        
        assert str(instrument) == "NSE@RELIANCE@equity_spot"
        assert repr(instrument) == "InstrumentKey(NSE@RELIANCE@equity_spot)"


class TestRelativeDate:
    """Test cases for RelativeDate class"""
    
    def test_weekly_expiry_current(self):
        """Test weekly expiry for current week"""
        rel_date = RelativeDate("weekly", 0)
        resolved = rel_date.resolve(date(2025, 7, 1))  # Tuesday
        
        # Should be Thursday of current week (July 3, 2025)
        assert resolved == date(2025, 7, 3)
        assert resolved.weekday() == 3
    
    def test_weekly_expiry_next(self):
        """Test weekly expiry for next week"""
        rel_date = RelativeDate("weekly", 1)
        resolved = rel_date.resolve(date(2025, 7, 1))  # Tuesday
        
        # Should be Thursday of next week (July 10, 2025)
        assert resolved == date(2025, 7, 10)
        assert resolved.weekday() == 3
    
    def test_monthly_expiry(self):
        """Test monthly expiry"""
        rel_date = RelativeDate("monthly", 0)
        resolved = rel_date.resolve(date(2025, 7, 1))
        
        # Should be last Thursday of July 2025
        assert resolved.month == 7
        assert resolved.year == 2025
        assert resolved.weekday() == 3
        
        # Check it's actually the last Thursday
        next_week = resolved + datetime.timedelta(days=7)
        assert next_week.month == 8  # Next Thursday is in August
    
    def test_quarterly_expiry(self):
        """Test quarterly expiry"""
        rel_date = RelativeDate("quarterly", 0)
        resolved = rel_date.resolve(date(2025, 7, 1))
        
        # Should be last Thursday of September 2025 (Q3)
        assert resolved.month == 9
        assert resolved.year == 2025
        assert resolved.weekday() == 3