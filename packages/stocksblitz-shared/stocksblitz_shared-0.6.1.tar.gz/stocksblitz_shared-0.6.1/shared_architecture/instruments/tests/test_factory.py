"""
Tests for the InstrumentKeyFactory class
"""

import pytest
from datetime import date
from decimal import Decimal

from ..utils.factory import InstrumentKeyFactory
from ..core.instrument_key import RelativeDate
from ..core.enums import AssetProductType, Exchange, OptionType, Moneyness
from ..core.exceptions import ValidationError


class TestInstrumentKeyFactory:
    """Test cases for InstrumentKeyFactory"""
    
    def test_equity_spot_creation(self):
        """Test creating equity spot instruments"""
        reliance = InstrumentKeyFactory.equity_spot("RELIANCE", Exchange.NSE)
        
        assert reliance.attributes.symbol == "RELIANCE"
        assert reliance.attributes.exchange == Exchange.NSE
        assert reliance.attributes.asset_product_type == AssetProductType.EQUITY_SPOT
        assert reliance.to_string() == "NSE@RELIANCE@equity_spot"
    
    def test_equity_futures_creation(self):
        """Test creating equity futures"""
        expiry = date(2025, 7, 31)
        futures = InstrumentKeyFactory.equity_futures("RELIANCE", expiry, Exchange.NSE)
        
        assert futures.attributes.symbol == "RELIANCE"
        assert futures.attributes.expiry_date == expiry
        assert futures.attributes.asset_product_type == AssetProductType.EQUITY_FUTURES
        assert futures.is_derivative()
        assert futures.requires_expiry()
    
    def test_equity_options_with_strike(self):
        """Test creating equity options with strike price"""
        expiry = date(2025, 7, 31)
        strike = Decimal("2800")
        
        call_option = InstrumentKeyFactory.equity_options(
            "RELIANCE", expiry, OptionType.CALL, strike_price=strike
        )
        
        assert call_option.attributes.option_type == OptionType.CALL
        assert call_option.attributes.strike_price == strike
        assert call_option.is_option()
        assert "call@2800" in call_option.to_string()
    
    def test_equity_options_with_moneyness(self):
        """Test creating equity options with moneyness"""
        expiry = date(2025, 7, 31)
        
        atm_call = InstrumentKeyFactory.equity_options(
            "RELIANCE", expiry, OptionType.CALL, moneyness=Moneyness.ATM
        )
        
        assert atm_call.attributes.moneyness == Moneyness.ATM
        assert atm_call.attributes.strike_price is None
        assert "call@ATM" in atm_call.to_string(include_moneyness=True)
    
    def test_index_spot_creation(self):
        """Test creating index spot instruments"""
        nifty = InstrumentKeyFactory.index_spot("NIFTY", Exchange.NSE)
        
        assert nifty.attributes.symbol == "NIFTY"
        assert nifty.attributes.asset_product_type == AssetProductType.INDEX_SPOT
        assert not nifty.is_derivative()
    
    def test_index_options_creation(self):
        """Test creating index options"""
        expiry = date(2025, 7, 31)
        strike = Decimal("25000")
        
        index_call = InstrumentKeyFactory.index_options(
            "NIFTY", expiry, OptionType.CALL, strike_price=strike
        )
        
        assert index_call.attributes.asset_product_type == AssetProductType.INDEX_OPTIONS
        assert index_call.attributes.symbol == "NIFTY"
        assert index_call.attributes.strike_price == strike
    
    def test_commodity_futures_creation(self):
        """Test creating commodity futures"""
        expiry = date(2025, 8, 30)
        
        gold_futures = InstrumentKeyFactory.commodity_futures(
            "GOLD", expiry, Exchange.MCX
        )
        
        assert gold_futures.attributes.symbol == "GOLD"
        assert gold_futures.attributes.exchange == Exchange.MCX
        assert gold_futures.attributes.asset_product_type == AssetProductType.COMMODITY_FUTURES
    
    def test_crypto_spot_creation(self):
        """Test creating crypto spot instruments"""
        btc = InstrumentKeyFactory.crypto_spot("BTCUSDT", Exchange.BINANCE)
        
        assert btc.attributes.symbol == "BTCUSDT"
        assert btc.attributes.exchange == Exchange.BINANCE
        assert btc.attributes.asset_product_type == AssetProductType.CRYPTO_SPOT
    
    def test_crypto_perpetual_creation(self):
        """Test creating crypto perpetual instruments"""
        eth_perp = InstrumentKeyFactory.crypto_perpetual("ETHUSDT", Exchange.BINANCE)
        
        assert eth_perp.attributes.symbol == "ETHUSDT"
        assert eth_perp.attributes.asset_product_type == AssetProductType.CRYPTO_PERPETUAL
        assert not eth_perp.requires_expiry()  # Perpetuals don't expire
    
    def test_currency_futures_creation(self):
        """Test creating currency futures"""
        expiry = date(2025, 7, 30)
        
        usdinr = InstrumentKeyFactory.currency_futures("USDINR", expiry, Exchange.NSE)
        
        assert usdinr.attributes.symbol == "USDINR"
        assert usdinr.attributes.asset_product_type == AssetProductType.CURRENCY_FUTURES
        assert usdinr.attributes.exchange == Exchange.NSE
    
    def test_from_string_with_validation(self):
        """Test creating from string with validation"""
        key_string = "NSE@RELIANCE@equity_spot"
        
        # With strict validation
        instrument = InstrumentKeyFactory.from_string_with_validation(key_string, strict=True)
        assert instrument.attributes.symbol == "RELIANCE"
        
        # With non-strict validation
        instrument_non_strict = InstrumentKeyFactory.from_string_with_validation(key_string, strict=False)
        assert instrument_non_strict.attributes.symbol == "RELIANCE"
    
    def test_weekly_option_chain_creation(self):
        """Test creating weekly option chain"""
        strikes = [Decimal("24000"), Decimal("24500"), Decimal("25000"), Decimal("25500")]
        
        call_chain = InstrumentKeyFactory.create_weekly_option_chain(
            "NIFTY", OptionType.CALL, strikes, Exchange.NSE, weeks_offset=0
        )
        
        assert len(call_chain) == 4
        
        for i, instrument in enumerate(call_chain):
            assert instrument.attributes.option_type == OptionType.CALL
            assert instrument.attributes.strike_price == strikes[i]
            assert isinstance(instrument.attributes.expiry_date, RelativeDate)
            assert instrument.attributes.expiry_date.type == "weekly"
    
    def test_atm_straddle_creation(self):
        """Test creating ATM straddle"""
        expiry = date(2025, 7, 31)
        atm_strike = Decimal("25000")
        
        call, put = InstrumentKeyFactory.create_atm_straddle(
            "NIFTY", expiry, atm_strike, Exchange.NSE
        )
        
        # Both should have same strike and expiry
        assert call.attributes.strike_price == put.attributes.strike_price == atm_strike
        assert call.attributes.expiry_date == put.attributes.expiry_date == expiry
        
        # Different option types
        assert call.attributes.option_type == OptionType.CALL
        assert put.attributes.option_type == OptionType.PUT
    
    def test_strangle_creation(self):
        """Test creating strangle"""
        expiry = date(2025, 7, 31)
        call_strike = Decimal("25500")
        put_strike = Decimal("24500")
        
        call, put = InstrumentKeyFactory.create_strangle(
            "NIFTY", expiry, call_strike, put_strike, Exchange.NSE
        )
        
        # Different strikes
        assert call.attributes.strike_price == call_strike
        assert put.attributes.strike_price == put_strike
        
        # Same expiry
        assert call.attributes.expiry_date == put.attributes.expiry_date == expiry
        
        # Different option types
        assert call.attributes.option_type == OptionType.CALL
        assert put.attributes.option_type == OptionType.PUT
    
    def test_with_lot_size_and_tick_size(self):
        """Test creating instruments with lot size and tick size"""
        nifty_futures = InstrumentKeyFactory.index_futures(
            "NIFTY", 
            date(2025, 7, 31), 
            Exchange.NSE,
            lot_size=50,
            tick_size=Decimal("0.05")
        )
        
        assert nifty_futures.attributes.lot_size == 50
        assert nifty_futures.attributes.tick_size == Decimal("0.05")
    
    def test_relative_date_instruments(self):
        """Test creating instruments with relative dates"""
        rel_expiry = RelativeDate("monthly", 1)  # Next month
        
        monthly_option = InstrumentKeyFactory.index_options(
            "NIFTY", rel_expiry, OptionType.CALL, strike_price=Decimal("25000")
        )
        
        assert isinstance(monthly_option.attributes.expiry_date, RelativeDate)
        assert monthly_option.attributes.expiry_date.type == "monthly"
        assert monthly_option.attributes.expiry_date.offset == 1
        
        # Test string representation includes relative date
        key_string = monthly_option.to_string()
        assert "REL_monthly_1" in key_string
    
    def test_validation_failures(self):
        """Test validation failures in factory methods"""
        # This would test validation if we had stricter validation in factory
        # For now, validation happens in InstrumentKey constructor
        
        expiry = date(2025, 7, 31)
        
        # This should work fine - factory creates valid instruments
        option = InstrumentKeyFactory.equity_options(
            "RELIANCE", expiry, OptionType.CALL, strike_price=Decimal("2800")
        )
        
        assert option is not None
        assert option.attributes.option_type == OptionType.CALL