"""
Factory methods for creating common instrument types
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Union

from ..core.instrument_key import InstrumentKey, InstrumentAttributes, RelativeDate
from ..core.enums import AssetProductType, Exchange, OptionType, Moneyness
from ..core.validators import InstrumentValidator


class InstrumentKeyFactory:
    """
    Factory class for creating common instrument types with validation
    """
    
    @classmethod
    def equity_spot(cls, symbol: str, exchange: Exchange = Exchange.NSE,
                   lot_size: Optional[int] = None,
                   tick_size: Optional[Decimal] = None) -> InstrumentKey:
        """
        Create equity spot instrument
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE", "TCS")
            exchange: Exchange (defaults to NSE)
            lot_size: Lot size for trading
            tick_size: Minimum price movement
        """
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.EQUITY_SPOT,
            symbol=symbol,
            exchange=exchange,
            lot_size=lot_size,
            tick_size=tick_size
        )
        
        return InstrumentKey(attributes)
    
    @classmethod
    def equity_futures(cls, symbol: str, expiry_date: Union[date, RelativeDate],
                      exchange: Exchange = Exchange.NSE,
                      lot_size: Optional[int] = None,
                      tick_size: Optional[Decimal] = None) -> InstrumentKey:
        """
        Create equity futures instrument
        
        Args:
            symbol: Stock symbol
            expiry_date: Expiry date (absolute or relative)
            exchange: Exchange (defaults to NSE)
            lot_size: Lot size for trading
            tick_size: Minimum price movement
        """
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.EQUITY_FUTURES,
            symbol=symbol,
            exchange=exchange,
            expiry_date=expiry_date,
            lot_size=lot_size,
            tick_size=tick_size
        )
        
        return InstrumentKey(attributes)
    
    @classmethod
    def equity_options(cls, symbol: str, expiry_date: Union[date, RelativeDate],
                      option_type: OptionType,
                      strike_price: Optional[Decimal] = None,
                      moneyness: Optional[Moneyness] = None,
                      exchange: Exchange = Exchange.NSE,
                      lot_size: Optional[int] = None,
                      tick_size: Optional[Decimal] = None) -> InstrumentKey:
        """
        Create equity options instrument
        
        Args:
            symbol: Stock symbol
            expiry_date: Expiry date (absolute or relative)
            option_type: CALL or PUT
            strike_price: Strike price (provide either this or moneyness)
            moneyness: Moneyness level (provide either this or strike_price)
            exchange: Exchange (defaults to NSE)
            lot_size: Lot size for trading
            tick_size: Minimum price movement
        """
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.EQUITY_OPTIONS,
            symbol=symbol,
            exchange=exchange,
            expiry_date=expiry_date,
            option_type=option_type,
            strike_price=strike_price,
            moneyness=moneyness,
            lot_size=lot_size,
            tick_size=tick_size
        )
        
        return InstrumentKey(attributes)
    
    @classmethod
    def index_spot(cls, symbol: str, exchange: Exchange = Exchange.NSE,
                  tick_size: Optional[Decimal] = None) -> InstrumentKey:
        """
        Create index spot instrument
        
        Args:
            symbol: Index symbol (e.g., "NIFTY", "SENSEX")
            exchange: Exchange (defaults to NSE)
            tick_size: Minimum price movement
        """
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.INDEX_SPOT,
            symbol=symbol,
            exchange=exchange,
            tick_size=tick_size
        )
        
        return InstrumentKey(attributes)
    
    @classmethod
    def index_futures(cls, symbol: str, expiry_date: Union[date, RelativeDate],
                     exchange: Exchange = Exchange.NSE,
                     lot_size: Optional[int] = None,
                     tick_size: Optional[Decimal] = None) -> InstrumentKey:
        """
        Create index futures instrument
        
        Args:
            symbol: Index symbol
            expiry_date: Expiry date (absolute or relative)
            exchange: Exchange (defaults to NSE)
            lot_size: Lot size for trading
            tick_size: Minimum price movement
        """
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.INDEX_FUTURES,
            symbol=symbol,
            exchange=exchange,
            expiry_date=expiry_date,
            lot_size=lot_size,
            tick_size=tick_size
        )
        
        return InstrumentKey(attributes)
    
    @classmethod
    def index_options(cls, symbol: str, expiry_date: Union[date, RelativeDate],
                     option_type: OptionType,
                     strike_price: Optional[Decimal] = None,
                     moneyness: Optional[Moneyness] = None,
                     exchange: Exchange = Exchange.NSE,
                     lot_size: Optional[int] = None,
                     tick_size: Optional[Decimal] = None) -> InstrumentKey:
        """
        Create index options instrument
        
        Args:
            symbol: Index symbol
            expiry_date: Expiry date (absolute or relative)
            option_type: CALL or PUT
            strike_price: Strike price (provide either this or moneyness)
            moneyness: Moneyness level (provide either this or strike_price)
            exchange: Exchange (defaults to NSE)
            lot_size: Lot size for trading
            tick_size: Minimum price movement
        """
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.INDEX_OPTIONS,
            symbol=symbol,
            exchange=exchange,
            expiry_date=expiry_date,
            option_type=option_type,
            strike_price=strike_price,
            moneyness=moneyness,
            lot_size=lot_size,
            tick_size=tick_size
        )
        
        return InstrumentKey(attributes)
    
    @classmethod
    def commodity_futures(cls, symbol: str, expiry_date: Union[date, RelativeDate],
                         exchange: Exchange = Exchange.MCX,
                         lot_size: Optional[int] = None,
                         tick_size: Optional[Decimal] = None) -> InstrumentKey:
        """
        Create commodity futures instrument
        
        Args:
            symbol: Commodity symbol (e.g., "GOLD", "CRUDE")
            expiry_date: Expiry date (absolute or relative)
            exchange: Exchange (defaults to MCX)
            lot_size: Lot size for trading
            tick_size: Minimum price movement
        """
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.COMMODITY_FUTURES,
            symbol=symbol,
            exchange=exchange,
            expiry_date=expiry_date,
            lot_size=lot_size,
            tick_size=tick_size
        )
        
        return InstrumentKey(attributes)
    
    @classmethod
    def commodity_options(cls, symbol: str, expiry_date: Union[date, RelativeDate],
                         option_type: OptionType,
                         strike_price: Optional[Decimal] = None,
                         moneyness: Optional[Moneyness] = None,
                         exchange: Exchange = Exchange.MCX,
                         lot_size: Optional[int] = None,
                         tick_size: Optional[Decimal] = None) -> InstrumentKey:
        """
        Create commodity options instrument
        
        Args:
            symbol: Commodity symbol
            expiry_date: Expiry date (absolute or relative)
            option_type: CALL or PUT
            strike_price: Strike price (provide either this or moneyness)
            moneyness: Moneyness level (provide either this or strike_price)
            exchange: Exchange (defaults to MCX)
            lot_size: Lot size for trading
            tick_size: Minimum price movement
        """
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.COMMODITY_OPTIONS,
            symbol=symbol,
            exchange=exchange,
            expiry_date=expiry_date,
            option_type=option_type,
            strike_price=strike_price,
            moneyness=moneyness,
            lot_size=lot_size,
            tick_size=tick_size
        )
        
        return InstrumentKey(attributes)
    
    @classmethod
    def currency_futures(cls, symbol: str, expiry_date: Union[date, RelativeDate],
                        exchange: Exchange = Exchange.NSE,
                        lot_size: Optional[int] = None,
                        tick_size: Optional[Decimal] = None) -> InstrumentKey:
        """
        Create currency futures instrument
        
        Args:
            symbol: Currency pair (e.g., "USDINR", "EURINR")
            expiry_date: Expiry date (absolute or relative)
            exchange: Exchange (defaults to NSE)
            lot_size: Lot size for trading
            tick_size: Minimum price movement
        """
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.CURRENCY_FUTURES,
            symbol=symbol,
            exchange=exchange,
            expiry_date=expiry_date,
            lot_size=lot_size,
            tick_size=tick_size
        )
        
        return InstrumentKey(attributes)
    
    @classmethod
    def crypto_spot(cls, symbol: str, exchange: Exchange = Exchange.BINANCE,
                   tick_size: Optional[Decimal] = None) -> InstrumentKey:
        """
        Create crypto spot instrument
        
        Args:
            symbol: Crypto pair (e.g., "BTCUSDT", "ETHUSDT")
            exchange: Exchange (defaults to BINANCE)
            tick_size: Minimum price movement
        """
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.CRYPTO_SPOT,
            symbol=symbol,
            exchange=exchange,
            tick_size=tick_size
        )
        
        return InstrumentKey(attributes)
    
    @classmethod
    def crypto_futures(cls, symbol: str, expiry_date: Union[date, RelativeDate],
                      exchange: Exchange = Exchange.BINANCE,
                      lot_size: Optional[int] = None,
                      tick_size: Optional[Decimal] = None) -> InstrumentKey:
        """
        Create crypto futures instrument
        
        Args:
            symbol: Crypto pair
            expiry_date: Expiry date (absolute or relative)
            exchange: Exchange (defaults to BINANCE)
            lot_size: Lot size for trading
            tick_size: Minimum price movement
        """
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.CRYPTO_FUTURES,
            symbol=symbol,
            exchange=exchange,
            expiry_date=expiry_date,
            lot_size=lot_size,
            tick_size=tick_size
        )
        
        return InstrumentKey(attributes)
    
    @classmethod
    def crypto_perpetual(cls, symbol: str, exchange: Exchange = Exchange.BINANCE,
                        tick_size: Optional[Decimal] = None) -> InstrumentKey:
        """
        Create crypto perpetual instrument
        
        Args:
            symbol: Crypto pair
            exchange: Exchange (defaults to BINANCE)
            tick_size: Minimum price movement
        """
        attributes = InstrumentAttributes(
            asset_product_type=AssetProductType.CRYPTO_PERPETUAL,
            symbol=symbol,
            exchange=exchange,
            tick_size=tick_size
        )
        
        return InstrumentKey(attributes)
    
    @classmethod
    def from_string_with_validation(cls, key_string: str, 
                                   strict: bool = True) -> InstrumentKey:
        """
        Create instrument from string with comprehensive validation
        
        Args:
            key_string: Instrument key string
            strict: If True, apply strict validation rules
        """
        instrument = InstrumentKey.from_string(key_string)
        
        if strict:
            # Apply comprehensive validation
            validator = InstrumentValidator()
            
            # Validate symbol format
            validator.validate_symbol(
                instrument.attributes.symbol,
                instrument.attributes.exchange,
                instrument.attributes.asset_product_type
            )
            
            # Validate exchange-asset combination
            validator.validate_instrument_combination(
                instrument.attributes.exchange,
                instrument.attributes.asset_product_type
            )
            
            # Validate option attributes
            validator.validate_option_attributes(
                instrument.attributes.option_type,
                instrument.attributes.strike_price,
                instrument.attributes.moneyness,
                instrument.attributes.asset_product_type
            )
            
            # Validate expiry date
            if isinstance(instrument.attributes.expiry_date, date):
                validator.validate_expiry_date(
                    instrument.attributes.expiry_date,
                    instrument.attributes.asset_product_type
                )
        
        return instrument
    
    @classmethod
    def create_weekly_option_chain(cls, symbol: str, option_type: OptionType,
                                  strikes: list[Decimal],
                                  exchange: Exchange = Exchange.NSE,
                                  weeks_offset: int = 0) -> list[InstrumentKey]:
        """
        Create a chain of weekly options for different strikes
        
        Args:
            symbol: Underlying symbol
            option_type: CALL or PUT
            strikes: List of strike prices
            exchange: Exchange
            weeks_offset: Number of weeks from current week (0 = current week)
        """
        expiry = RelativeDate("weekly", weeks_offset)
        
        instruments = []
        for strike in strikes:
            instrument = cls.equity_options(
                symbol=symbol,
                expiry_date=expiry,
                option_type=option_type,
                strike_price=strike,
                exchange=exchange
            )
            instruments.append(instrument)
        
        return instruments
    
    @classmethod
    def create_atm_straddle(cls, symbol: str, expiry_date: Union[date, RelativeDate],
                           atm_strike: Decimal,
                           exchange: Exchange = Exchange.NSE) -> tuple[InstrumentKey, InstrumentKey]:
        """
        Create ATM straddle (CALL + PUT at same strike)
        
        Args:
            symbol: Underlying symbol
            expiry_date: Expiry date
            atm_strike: ATM strike price
            exchange: Exchange
        """
        call = cls.equity_options(
            symbol=symbol,
            expiry_date=expiry_date,
            option_type=OptionType.CALL,
            strike_price=atm_strike,
            exchange=exchange
        )
        
        put = cls.equity_options(
            symbol=symbol,
            expiry_date=expiry_date,
            option_type=OptionType.PUT,
            strike_price=atm_strike,
            exchange=exchange
        )
        
        return call, put
    
    @classmethod
    def create_strangle(cls, symbol: str, expiry_date: Union[date, RelativeDate],
                       call_strike: Decimal, put_strike: Decimal,
                       exchange: Exchange = Exchange.NSE) -> tuple[InstrumentKey, InstrumentKey]:
        """
        Create strangle (CALL + PUT at different strikes)
        
        Args:
            symbol: Underlying symbol
            expiry_date: Expiry date
            call_strike: Call strike price
            put_strike: Put strike price
            exchange: Exchange
        """
        call = cls.equity_options(
            symbol=symbol,
            expiry_date=expiry_date,
            option_type=OptionType.CALL,
            strike_price=call_strike,
            exchange=exchange
        )
        
        put = cls.equity_options(
            symbol=symbol,
            expiry_date=expiry_date,
            option_type=OptionType.PUT,
            strike_price=put_strike,
            exchange=exchange
        )
        
        return call, put