"""
Unified Symbol Converter for StocksBlitz Platform

This module provides comprehensive conversion utilities for the unified symbol model,
supporting multi-asset types, broker-specific mappings, and legacy format migrations.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from datetime import datetime, date
import re

from shared_architecture.domain.models.market.symbol import (
    UnifiedSymbol, BrokerToken, BrokerType, AssetClass, 
    ProductType, Exchange, OptionType, SymbolStatus
)

logger = logging.getLogger(__name__)


class UnifiedSymbolConverter:
    """
    Enhanced Symbol Converter for Unified Symbol Model
    
    Provides comprehensive conversion between different symbol formats,
    supporting multi-asset types and broker-specific mappings.
    """
    
    @staticmethod
    def from_legacy_symbol(legacy_data: Dict) -> Dict:
        """
        Convert legacy symbol data to unified symbol format
        
        Args:
            legacy_data: Dictionary containing legacy symbol data
            
        Returns:
            Dictionary suitable for UnifiedSymbol creation
        """
        unified_data = {}
        
        # Core identifiers
        unified_data['instrument_key'] = legacy_data.get('instrument_key', '')
        unified_data['symbol'] = legacy_data.get('symbol', '')
        
        # Exchange mapping
        exchange_str = legacy_data.get('exchange', '').upper()
        try:
            unified_data['exchange'] = Exchange(exchange_str)
        except ValueError:
            unified_data['exchange'] = Exchange.NSE  # Default
            
        # Asset classification
        product_type = legacy_data.get('product_type', '').lower()
        symbol_type = legacy_data.get('symbol_type', '').lower()
        asset_product_type = legacy_data.get('asset_product_type', '').lower()
        
        if product_type in ['equity', 'equities'] or symbol_type in ['equity', 'equities']:
            unified_data['asset_class'] = AssetClass.EQUITY
            unified_data['product_type'] = ProductType.SPOT
        elif product_type in ['futures', 'future'] or 'future' in asset_product_type:
            unified_data['asset_class'] = AssetClass.DERIVATIVE
            unified_data['product_type'] = ProductType.FUTURES
        elif product_type in ['options', 'option'] or 'option' in asset_product_type:
            unified_data['asset_class'] = AssetClass.DERIVATIVE
            unified_data['product_type'] = ProductType.OPTIONS
        elif product_type in ['bonds', 'bond'] or 'bond' in asset_product_type:
            unified_data['asset_class'] = AssetClass.FIXED_INCOME
            unified_data['product_type'] = ProductType.GOVERNMENT_BOND
        elif product_type in ['commodity'] or 'commodity' in asset_product_type:
            unified_data['asset_class'] = AssetClass.COMMODITY
            unified_data['product_type'] = ProductType.SPOT
        elif product_type in ['crypto', 'cryptocurrency']:
            unified_data['asset_class'] = AssetClass.CRYPTO
            unified_data['product_type'] = ProductType.SPOT
        elif product_type in ['etf']:
            unified_data['asset_class'] = AssetClass.ETF
            unified_data['product_type'] = ProductType.SPOT
        else:
            unified_data['asset_class'] = AssetClass.EQUITY
            unified_data['product_type'] = ProductType.SPOT
            
        # Names and descriptions
        unified_data['display_name'] = (
            legacy_data.get('name') or 
            legacy_data.get('instrument_name') or 
            legacy_data.get('Instrument_Name') or
            legacy_data.get('display_name')
        )
        unified_data['company_name'] = legacy_data.get('company_name')
        unified_data['description'] = legacy_data.get('description')
        unified_data['short_name'] = legacy_data.get('short_name')
        
        # International identifiers
        unified_data['isin_code'] = legacy_data.get('isin', legacy_data.get('isin_code'))
        unified_data['cusip'] = legacy_data.get('cusip')
        unified_data['bloomberg_id'] = legacy_data.get('bloomberg_id')
        unified_data['reuters_ric'] = legacy_data.get('reuters_ric')
        unified_data['figi'] = legacy_data.get('figi')
        
        # Currency and regional
        unified_data['currency'] = legacy_data.get('currency', 'INR')
        unified_data['country_code'] = legacy_data.get('country', legacy_data.get('country_code', 'IN'))
        
        # Derivatives-specific
        if legacy_data.get('expiry_date'):
            unified_data['expiry_date'] = UnifiedSymbolConverter._parse_date(legacy_data['expiry_date'])
                
        if legacy_data.get('option_type'):
            opt_type = legacy_data['option_type'].lower()
            if opt_type in ['call', 'ce']:
                unified_data['option_type'] = OptionType.CALL
            elif opt_type in ['put', 'pe']:
                unified_data['option_type'] = OptionType.PUT
                
        if legacy_data.get('strike_price'):
            unified_data['strike_price'] = Decimal(str(legacy_data['strike_price']))
            
        unified_data['underlying_symbol'] = legacy_data.get('underlying_symbol')
        
        # Trading specifications
        unified_data['lot_size'] = (
            legacy_data.get('lot_size') or 
            legacy_data.get('minimum_lot_qty') or
            legacy_data.get('board_lot_qty')
        )
        unified_data['tick_size'] = legacy_data.get('tick_size')
        if unified_data['tick_size']:
            unified_data['tick_size'] = Decimal(str(unified_data['tick_size']))
        
        unified_data['multiplier'] = legacy_data.get('multiplier', 1)
        unified_data['board_lot_quantity'] = legacy_data.get('board_lot_quantity')
            
        # Market and pricing
        unified_data['face_value'] = legacy_data.get('face_value')
        if unified_data['face_value']:
            unified_data['face_value'] = Decimal(str(unified_data['face_value']))
            
        unified_data['market_lot'] = legacy_data.get('market_lot')
        unified_data['base_price'] = legacy_data.get('base_price')
        if unified_data['base_price']:
            unified_data['base_price'] = Decimal(str(unified_data['base_price']))
            
        # Price bands
        unified_data['price_band_lower'] = legacy_data.get('low_price_range')
        unified_data['price_band_upper'] = legacy_data.get('high_price_range')
        
        # Status mapping
        if legacy_data.get('is_active', True) and not legacy_data.get('suspension_flag', False):
            unified_data['status'] = SymbolStatus.ACTIVE
        elif legacy_data.get('suspension_flag', False):
            unified_data['status'] = SymbolStatus.SUSPENDED
        else:
            unified_data['status'] = SymbolStatus.SUSPENDED
            
        unified_data['is_tradable'] = legacy_data.get('is_tradable', True)
        unified_data['is_permitted_to_trade'] = (
            legacy_data.get('permittedtotrade', True) or
            legacy_data.get('permitted_to_trade', True)
        )
        
        # Market eligibility
        unified_data['normal_market_allowed'] = (
            legacy_data.get('normal_market_status') != 'N' and
            legacy_data.get('normal_market_eligibility') != 'N'
        )
        unified_data['odd_lot_market_allowed'] = (
            legacy_data.get('odd_lot_market_status') != 'N' and
            legacy_data.get('odd_lot_market_eligibility') != 'N'
        )
        unified_data['spot_market_allowed'] = (
            legacy_data.get('spot_market_status') != 'N' and
            legacy_data.get('spot_market_eligibility') != 'N'
        )
        unified_data['auction_market_allowed'] = (
            legacy_data.get('auction_market_status') != 'N' and
            legacy_data.get('auction_market_eligibility') != 'N'
        )
        
        # Risk and margin
        unified_data['warning_quantity'] = legacy_data.get('warning_qty')
        unified_data['freeze_quantity'] = legacy_data.get('freeze_qty')
        unified_data['freeze_percentage'] = legacy_data.get('freeze_percent')
        unified_data['credit_rating'] = legacy_data.get('credit_rating')
        unified_data['margin_percentage'] = legacy_data.get('margin_percentage')
        unified_data['avm_buy_margin'] = legacy_data.get('avm_buy_margin')
        unified_data['avm_sell_margin'] = legacy_data.get('avm_sell_margin')
        
        # Important dates
        unified_data['listing_date'] = UnifiedSymbolConverter._parse_date(
            legacy_data.get('listing_date') or legacy_data.get('date_of_listing')
        )
        unified_data['delisting_date'] = UnifiedSymbolConverter._parse_date(
            legacy_data.get('delisting_date') or legacy_data.get('date_of_delisting')
        )
        unified_data['first_trading_date'] = UnifiedSymbolConverter._parse_date(
            legacy_data.get('first_trading_date')
        )
        unified_data['last_trading_date'] = UnifiedSymbolConverter._parse_date(
            legacy_data.get('last_trading_date')
        )
        
        # Exercise dates for options
        unified_data['exercise_start_date'] = UnifiedSymbolConverter._parse_date(
            legacy_data.get('excercise_start_date') or legacy_data.get('exercise_start_date')
        )
        unified_data['exercise_end_date'] = UnifiedSymbolConverter._parse_date(
            legacy_data.get('excercise_end_date') or legacy_data.get('exercise_end_date')
        )
        unified_data['exercise_style'] = legacy_data.get('excercise_style') or legacy_data.get('exercise_style')
        
        # No delivery period
        unified_data['no_delivery_start_date'] = UnifiedSymbolConverter._parse_date(
            legacy_data.get('no_delivery_start_date') or legacy_data.get('nds_date')
        )
        unified_data['no_delivery_end_date'] = UnifiedSymbolConverter._parse_date(
            legacy_data.get('no_delivery_end_date') or legacy_data.get('nde_date')
        )
        
        # Book closure
        unified_data['book_closure_start_date'] = UnifiedSymbolConverter._parse_date(
            legacy_data.get('book_cls_start_date')
        )
        unified_data['book_closure_end_date'] = UnifiedSymbolConverter._parse_date(
            legacy_data.get('book_cls_end_date')
        )
        
        # Corporate actions flags
        unified_data['dividend_flag'] = legacy_data.get('dividends') == 'Y' or legacy_data.get('dividend_flag', False)
        unified_data['bonus_flag'] = legacy_data.get('bonus') == 'Y' or legacy_data.get('bonus_flag', False)
        unified_data['rights_flag'] = legacy_data.get('rights') == 'Y' or legacy_data.get('rights_flag', False)
        unified_data['split_flag'] = legacy_data.get('split_flag', False)
        unified_data['merger_flag'] = legacy_data.get('merger_flag', False)
        
        # Surveillance
        unified_data['surveillance_flag'] = legacy_data.get('surveillance_flag', False)
        unified_data['suspension_flag'] = legacy_data.get('susp_status') != 'N' or legacy_data.get('suspension_flag', False)
        unified_data['suspension_reason'] = legacy_data.get('suspension_reason')
        unified_data['suspension_date'] = UnifiedSymbolConverter._parse_date(legacy_data.get('suspension_date'))
        
        # Options calculations
        unified_data['intrinsic_value'] = legacy_data.get('intrinsic_value')
        unified_data['time_value'] = legacy_data.get('extrinsic_value')  # extrinsic = time value
        if legacy_data.get('intrinsic_value') and unified_data['time_value']:
            unified_data['time_value'] = Decimal(str(unified_data['time_value']))
        if unified_data['intrinsic_value']:
            unified_data['intrinsic_value'] = Decimal(str(unified_data['intrinsic_value']))
            
        # Industry classification
        unified_data['sector'] = legacy_data.get('sector') or legacy_data.get('group_name')
        unified_data['industry'] = legacy_data.get('industry')
        unified_data['sub_industry'] = legacy_data.get('sub_industry')
        
        # Additional metadata
        metadata = {}
        broker_fields = [
            'stock_token', 'stock_code', 'calevel', 'ca_level', 'breeze_token', 
            'kite_token', 'scrip_id', 'scrip_code', 'scrip_name', 'old_token',
            'asset_token', 'asset_instrument', 'asset_name'
        ]
        
        for key in broker_fields:
            if legacy_data.get(key):
                metadata[key] = legacy_data[key]
        
        # Market data related
        if legacy_data.get('weeks_52_high'):
            metadata['52_week_high'] = legacy_data['weeks_52_high']
        if legacy_data.get('weeks_52_low'):
            metadata['52_week_low'] = legacy_data['weeks_52_low']
        if legacy_data.get('lifetime_high'):
            metadata['lifetime_high'] = legacy_data['lifetime_high']
        if legacy_data.get('lifetime_low'):
            metadata['lifetime_low'] = legacy_data['lifetime_low']
            
        if metadata:
            unified_data['metadata'] = metadata
            
        return unified_data
    
    @staticmethod
    def to_broker_format(unified_symbol: UnifiedSymbol, broker_type: BrokerType) -> Dict:
        """
        Convert unified symbol to broker-specific format
        
        Args:
            unified_symbol: UnifiedSymbol instance
            broker_type: Target broker type
            
        Returns:
            Dictionary with broker-specific symbol format
        """
        broker_data = {
            'symbol': unified_symbol.symbol,
            'exchange': unified_symbol.exchange.value,
            'instrument_key': unified_symbol.instrument_key,
        }
        
        # Get broker-specific token if available
        broker_token = unified_symbol.get_broker_token(broker_type)
        broker_symbol = unified_symbol.get_broker_symbol(broker_type)
        
        if broker_token:
            broker_data['broker_token'] = broker_token
        if broker_symbol:
            broker_data['broker_symbol'] = broker_symbol
            
        # Add derivatives-specific data
        if unified_symbol.is_option():
            broker_data.update({
                'option_type': unified_symbol.option_type.value if unified_symbol.option_type else None,
                'strike_price': float(unified_symbol.strike_price) if unified_symbol.strike_price else None,
                'expiry_date': unified_symbol.expiry_date.isoformat() if unified_symbol.expiry_date else None,
                'underlying_symbol': unified_symbol.underlying_symbol
            })
        elif unified_symbol.is_future():
            broker_data.update({
                'expiry_date': unified_symbol.expiry_date.isoformat() if unified_symbol.expiry_date else None,
                'underlying_symbol': unified_symbol.underlying_symbol
            })
            
        # Trading specifications
        broker_data.update({
            'lot_size': unified_symbol.lot_size,
            'tick_size': float(unified_symbol.tick_size) if unified_symbol.tick_size else None,
            'is_tradable': unified_symbol.is_tradable,
            'product_type': unified_symbol.product_type.value,
            'asset_class': unified_symbol.asset_class.value
        })
        
        return broker_data
    
    @staticmethod
    def create_broker_token_mapping(
        unified_symbol: UnifiedSymbol,
        broker_type: BrokerType,
        broker_symbol: str,
        broker_token: Optional[str] = None,
        **kwargs
    ) -> BrokerToken:
        """
        Create broker token mapping for unified symbol
        
        Args:
            unified_symbol: UnifiedSymbol instance
            broker_type: Broker type
            broker_symbol: Broker-specific symbol
            broker_token: Broker-specific token
            **kwargs: Additional broker-specific data
            
        Returns:
            BrokerToken instance
        """
        broker_mapping = BrokerToken(
            broker_type=broker_type,
            broker_name=broker_type.value,
            broker_symbol=broker_symbol,
            broker_token=broker_token,
            broker_instrument_id=kwargs.get('broker_instrument_id'),
            broker_exchange_code=kwargs.get('broker_exchange_code'),
            broker_segment=kwargs.get('broker_segment'),
            lot_size=kwargs.get('lot_size', unified_symbol.lot_size),
            tick_size=kwargs.get('tick_size', unified_symbol.tick_size),
            is_active=kwargs.get('is_active', True),
            is_tradable=kwargs.get('is_tradable', unified_symbol.is_tradable),
            broker_metadata=kwargs.get('broker_metadata')
        )
        
        return broker_mapping
    
    @staticmethod
    def validate_symbol_consistency(unified_symbol: UnifiedSymbol) -> List[str]:
        """
        Validate symbol data consistency
        
        Args:
            unified_symbol: UnifiedSymbol instance to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not unified_symbol.instrument_key:
            errors.append("instrument_key is required")
        if not unified_symbol.symbol:
            errors.append("symbol is required")
            
        # Validate instrument key format
        key_parts = unified_symbol.instrument_key.split('@')
        if len(key_parts) < 3:
            errors.append("instrument_key format invalid - minimum 3 parts required")
        else:
            exchange_part, symbol_part, product_part = key_parts[:3]
            
            if exchange_part != unified_symbol.exchange.value:
                errors.append(f"instrument_key exchange ({exchange_part}) doesn't match exchange field ({unified_symbol.exchange.value})")
                
        # Validate options-specific fields
        if unified_symbol.product_type == ProductType.OPTIONS:
            if not unified_symbol.expiry_date:
                errors.append("expiry_date is required for options")
            if not unified_symbol.option_type:
                errors.append("option_type is required for options")
            if not unified_symbol.strike_price:
                errors.append("strike_price is required for options")
                
        # Validate futures-specific fields
        if unified_symbol.product_type == ProductType.FUTURES:
            if not unified_symbol.expiry_date:
                errors.append("expiry_date is required for futures")
                
        # Validate expiry date for derivatives
        if unified_symbol.expiry_date and unified_symbol.expiry_date < date.today():
            if unified_symbol.status not in [SymbolStatus.EXPIRED, SymbolStatus.DELISTED]:
                errors.append("expired instruments should have status EXPIRED or DELISTED")
                
        # Validate ISIN format
        if unified_symbol.isin_code:
            if not re.match(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$', unified_symbol.isin_code):
                errors.append("isin_code format is invalid")
                
        # Validate currency format
        if unified_symbol.currency and len(unified_symbol.currency) != 3:
            errors.append("currency must be 3 characters")
            
        # Validate country code format
        if unified_symbol.country_code and len(unified_symbol.country_code) != 2:
            errors.append("country_code must be 2 characters")
            
        return errors
    
    @staticmethod
    def merge_symbol_updates(
        existing_symbol: UnifiedSymbol,
        update_data: Dict
    ) -> UnifiedSymbol:
        """
        Merge update data into existing symbol
        
        Args:
            existing_symbol: Current UnifiedSymbol instance
            update_data: Dictionary of updates to apply
            
        Returns:
            Updated UnifiedSymbol instance
        """
        # Create a copy to avoid modifying the original
        for field, value in update_data.items():
            if hasattr(existing_symbol, field) and value is not None:
                setattr(existing_symbol, field, value)
                
        # Update version and timestamp
        existing_symbol.version += 1
        existing_symbol.updated_at = datetime.utcnow()
        
        return existing_symbol
    
    @staticmethod
    def _parse_date(date_value: Any) -> Optional[date]:
        """
        Parse various date formats to date object
        
        Args:
            date_value: Date value in various formats
            
        Returns:
            Parsed date or None
        """
        if not date_value:
            return None
            
        if isinstance(date_value, date):
            return date_value
        elif isinstance(date_value, datetime):
            return date_value.date()
        elif isinstance(date_value, str):
            # Try common date formats
            formats = [
                '%Y-%m-%d',      # 2024-06-20
                '%d-%m-%Y',      # 20-06-2024
                '%d/%m/%Y',      # 20/06/2024
                '%d-%b-%Y',      # 20-Jun-2024
                '%Y-%m-%d %H:%M:%S',  # With time
                '%Y-%m-%dT%H:%M:%S',  # ISO format
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
                    
        return None


class BrokerSpecificConverter:
    """
    Broker-specific conversion utilities
    """
    
    @staticmethod
    def zerodha_to_unified(kite_data: Dict) -> Dict:
        """Convert Zerodha/Kite format to unified format"""
        return UnifiedSymbolConverter.from_legacy_symbol({
            'instrument_key': kite_data.get('instrument_token'),
            'symbol': kite_data.get('tradingsymbol'),
            'exchange': kite_data.get('exchange'),
            'name': kite_data.get('name'),
            'expiry_date': kite_data.get('expiry'),
            'strike_price': kite_data.get('strike'),
            'option_type': kite_data.get('instrument_type'),
            'lot_size': kite_data.get('lot_size'),
            'tick_size': kite_data.get('tick_size'),
            'kite_token': kite_data.get('instrument_token')
        })
    
    @staticmethod
    def icici_to_unified(breeze_data: Dict) -> Dict:
        """Convert ICICI Breeze format to unified format"""
        return UnifiedSymbolConverter.from_legacy_symbol({
            'instrument_key': breeze_data.get('stock_code'),
            'symbol': breeze_data.get('stock_code'),
            'exchange': breeze_data.get('exchange_code'),
            'name': breeze_data.get('company_name'),
            'expiry_date': breeze_data.get('expiry_date'),
            'strike_price': breeze_data.get('strike_price'),
            'option_type': breeze_data.get('right'),
            'breeze_token': breeze_data.get('stock_token')
        })
    
    @staticmethod
    def autotrader_to_unified(autotrader_data: Dict) -> Dict:
        """Convert AutoTrader format to unified format"""
        return UnifiedSymbolConverter.from_legacy_symbol(autotrader_data)


class SymbolMigrationUtility:
    """
    Utilities for migrating legacy symbol data to unified format
    """
    
    @staticmethod
    def migrate_ticker_service_symbols(ticker_symbols: List[Dict]) -> List[Dict]:
        """
        Migrate ticker service symbols to unified format
        
        Args:
            ticker_symbols: List of ticker service symbol dictionaries
            
        Returns:
            List of unified symbol dictionaries
        """
        unified_symbols = []
        
        for symbol_data in ticker_symbols:
            try:
                unified_data = UnifiedSymbolConverter.from_legacy_symbol(symbol_data)
                unified_symbols.append(unified_data)
            except Exception as e:
                logger.error(f"Failed to migrate symbol {symbol_data.get('symbol', 'unknown')}: {e}")
                
        return unified_symbols
    
    @staticmethod
    def migrate_instrument_service_symbols(instrument_symbols: List[Dict]) -> List[Dict]:
        """
        Migrate instrument service symbols to unified format
        
        Args:
            instrument_symbols: List of instrument service symbol dictionaries
            
        Returns:
            List of unified symbol dictionaries
        """
        unified_symbols = []
        
        for symbol_data in instrument_symbols:
            try:
                unified_data = UnifiedSymbolConverter.from_legacy_symbol(symbol_data)
                unified_symbols.append(unified_data)
            except Exception as e:
                logger.error(f"Failed to migrate instrument {symbol_data.get('instrument_key', 'unknown')}: {e}")
                
        return unified_symbols
    
    @staticmethod
    def generate_migration_report(
        legacy_symbols: List[Dict], 
        unified_symbols: List[Dict]
    ) -> Dict:
        """
        Generate migration report comparing legacy and unified symbols
        
        Args:
            legacy_symbols: List of legacy symbol dictionaries
            unified_symbols: List of unified symbol dictionaries
            
        Returns:
            Migration report dictionary
        """
        report = {
            'total_legacy_symbols': len(legacy_symbols),
            'total_unified_symbols': len(unified_symbols),
            'migration_success_rate': len(unified_symbols) / len(legacy_symbols) * 100 if legacy_symbols else 0,
            'failed_migrations': len(legacy_symbols) - len(unified_symbols),
            'asset_class_distribution': {},
            'exchange_distribution': {},
            'product_type_distribution': {}
        }
        
        # Analyze unified symbols distribution
        for symbol in unified_symbols:
            asset_class = symbol.get('asset_class', 'unknown')
            exchange = symbol.get('exchange', 'unknown')
            product_type = symbol.get('product_type', 'unknown')
            
            report['asset_class_distribution'][asset_class] = report['asset_class_distribution'].get(asset_class, 0) + 1
            report['exchange_distribution'][exchange] = report['exchange_distribution'].get(exchange, 0) + 1
            report['product_type_distribution'][product_type] = report['product_type_distribution'].get(product_type, 0) + 1
            
        return report