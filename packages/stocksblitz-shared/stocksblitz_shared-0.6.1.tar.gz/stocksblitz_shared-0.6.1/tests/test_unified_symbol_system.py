"""
Comprehensive Test Suite for Unified Symbol System

This module provides thorough testing of the unified symbol model,
conversion utilities, and service integrations.
"""

import pytest
import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared_architecture.domain.models.market.symbol import (
    UnifiedSymbol, BrokerToken, SymbolMapping,  # CorporateAction - table dropped
    AssetClass, ProductType, Exchange, OptionType, SymbolStatus, 
    BrokerType, Base  # CorporateActionType - table dropped
)
from shared_architecture.schemas.symbol import (
    UnifiedSymbolCreate, UnifiedSymbolUpdate, SymbolSearchFilters,
    BrokerTokenCreate  # CorporateActionCreate - table dropped
)
from shared_architecture.utils.unified_symbol_converter import (
    UnifiedSymbolConverter, BrokerSpecificConverter, SymbolMigrationUtility
)
from shared_architecture.services.unified_symbol_service import UnifiedSymbolService


@pytest.fixture
def db_session():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def symbol_service(db_session):
    """Create symbol service with test database"""
    return UnifiedSymbolService(db_session)


@pytest.fixture
def sample_equity_data():
    """Sample equity symbol data"""
    return {
        'instrument_key': 'NSE@RELIANCE@equities',
        'symbol': 'RELIANCE',
        'exchange': Exchange.NSE,
        'asset_class': AssetClass.EQUITY,
        'product_type': ProductType.SPOT,
        'display_name': 'Reliance Industries Limited',
        'company_name': 'Reliance Industries Limited',
        'isin_code': 'INE002A01018',
        'currency': 'INR',
        'country_code': 'IN',
        'lot_size': 1,
        'tick_size': Decimal('0.05'),
        'face_value': Decimal('10.00'),
        'listing_date': date(1980, 1, 1),
        'sector': 'Energy',
        'industry': 'Petroleum Products',
        'is_tradable': True,
        'status': SymbolStatus.ACTIVE
    }


@pytest.fixture
def sample_option_data():
    """Sample option symbol data"""
    return {
        'instrument_key': 'NSE@NIFTY@options@27-Jun-2024@call@23000',
        'symbol': 'NIFTY',
        'exchange': Exchange.NSE,
        'asset_class': AssetClass.DERIVATIVE,
        'product_type': ProductType.OPTIONS,
        'display_name': 'NIFTY 27JUN24 23000 CE',
        'expiry_date': date(2024, 6, 27),
        'option_type': OptionType.CALL,
        'strike_price': Decimal('23000.00'),
        'underlying_symbol': 'NIFTY',
        'lot_size': 50,
        'tick_size': Decimal('0.05'),
        'currency': 'INR',
        'country_code': 'IN',
        'is_tradable': True,
        'status': SymbolStatus.ACTIVE
    }


class TestUnifiedSymbolModel:
    """Test the UnifiedSymbol model"""
    
    def test_create_equity_symbol(self, sample_equity_data):
        """Test creating an equity symbol"""
        symbol = UnifiedSymbol(**sample_equity_data)
        
        assert symbol.symbol == 'RELIANCE'
        assert symbol.exchange == Exchange.NSE
        assert symbol.asset_class == AssetClass.EQUITY
        assert symbol.product_type == ProductType.SPOT
        assert symbol.is_equity()
        assert not symbol.is_option()
        assert not symbol.is_future()
        assert symbol.is_active()
    
    def test_create_option_symbol(self, sample_option_data):
        """Test creating an option symbol"""
        symbol = UnifiedSymbol(**sample_option_data)
        
        assert symbol.symbol == 'NIFTY'
        assert symbol.exchange == Exchange.NSE
        assert symbol.asset_class == AssetClass.DERIVATIVE
        assert symbol.product_type == ProductType.OPTIONS
        assert symbol.option_type == OptionType.CALL
        assert symbol.strike_price == Decimal('23000.00')
        assert not symbol.is_equity()
        assert symbol.is_option()
        assert symbol.is_derivative()
        assert symbol.is_active()
    
    def test_symbol_display_formatting(self, sample_option_data):
        """Test symbol display name generation"""
        symbol = UnifiedSymbol(**sample_option_data)
        display_symbol = symbol.get_display_symbol()
        
        # Should format as NIFTY27JUN2423000CALL
        assert 'NIFTY' in display_symbol
        assert '27JUN' in display_symbol
        assert '23000' in display_symbol
        assert 'CALL' in display_symbol.upper()
    
    def test_broker_token_mapping(self, sample_equity_data):
        """Test broker token relationships"""
        symbol = UnifiedSymbol(**sample_equity_data)
        
        # Create broker token
        kite_token = BrokerToken(
            broker_type=BrokerType.ZERODHA_KITE,
            broker_name='zerodha_kite',
            broker_symbol='RELIANCE',
            broker_token='738561'
        )
        
        symbol.broker_tokens.append(kite_token)
        
        # Test retrieval
        assert symbol.get_broker_token(BrokerType.ZERODHA_KITE) == '738561'
        assert symbol.get_broker_symbol(BrokerType.ZERODHA_KITE) == 'RELIANCE'
        assert symbol.get_broker_token(BrokerType.ICICI_BREEZE) is None


class TestUnifiedSymbolConverter:
    """Test the symbol converter utilities"""
    
    def test_legacy_to_unified_conversion(self):
        """Test converting legacy symbol data to unified format"""
        legacy_data = {
            'instrument_key': 'NSE@HDFC@equities',
            'symbol': 'HDFC',
            'exchange': 'NSE',
            'name': 'HDFC Bank Limited',
            'symbol_type': 'equity',
            'lot_size': 1,
            'tick_size': 0.05,
            'is_active': True,
            'listing_date': '2000-01-01',
            'isin': 'INE040A01034',
            'sector': 'Financial Services',
            'kite_token': '341249',
            'breeze_token': 'HDFC'
        }
        
        unified_data = UnifiedSymbolConverter.from_legacy_symbol(legacy_data)
        
        assert unified_data['instrument_key'] == 'NSE@HDFC@equities'
        assert unified_data['symbol'] == 'HDFC'
        assert unified_data['exchange'] == Exchange.NSE
        assert unified_data['asset_class'] == AssetClass.EQUITY
        assert unified_data['product_type'] == ProductType.SPOT
        assert unified_data['display_name'] == 'HDFC Bank Limited'
        assert unified_data['isin_code'] == 'INE040A01034'
        assert unified_data['sector'] == 'Financial Services'
        assert 'kite_token' in unified_data['metadata']
        assert 'breeze_token' in unified_data['metadata']
    
    def test_option_legacy_conversion(self):
        """Test converting legacy option data"""
        legacy_option = {
            'instrument_key': 'NSE@BANKNIFTY@options@29-Aug-2024@put@51000',
            'symbol': 'BANKNIFTY',
            'exchange': 'NSE',
            'product_type': 'options',
            'expiry_date': '2024-08-29',
            'option_type': 'put',
            'strike_price': 51000,
            'underlying_symbol': 'BANKNIFTY',
            'lot_size': 15,
            'tick_size': 0.05,
            'is_active': True
        }
        
        unified_data = UnifiedSymbolConverter.from_legacy_symbol(legacy_option)
        
        assert unified_data['asset_class'] == AssetClass.DERIVATIVE
        assert unified_data['product_type'] == ProductType.OPTIONS
        assert unified_data['option_type'] == OptionType.PUT
        assert unified_data['strike_price'] == Decimal('51000')
        assert unified_data['expiry_date'] == date(2024, 8, 29)
        assert unified_data['underlying_symbol'] == 'BANKNIFTY'
    
    def test_broker_format_conversion(self, sample_equity_data):
        """Test converting to broker-specific format"""
        symbol = UnifiedSymbol(**sample_equity_data)
        
        # Add broker token
        kite_token = BrokerToken(
            broker_type=BrokerType.ZERODHA_KITE,
            broker_name='zerodha_kite',
            broker_symbol='RELIANCE',
            broker_token='738561'
        )
        symbol.broker_tokens.append(kite_token)
        
        # Convert to broker format
        broker_data = UnifiedSymbolConverter.to_broker_format(symbol, BrokerType.ZERODHA_KITE)
        
        assert broker_data['symbol'] == 'RELIANCE'
        assert broker_data['exchange'] == 'NSE'
        assert broker_data['broker_token'] == '738561'
        assert broker_data['broker_symbol'] == 'RELIANCE'
        assert broker_data['lot_size'] == 1
        assert broker_data['is_tradable'] is True
    
    def test_symbol_validation(self, sample_equity_data):
        """Test symbol validation"""
        symbol = UnifiedSymbol(**sample_equity_data)
        
        # Valid symbol should have no errors
        errors = UnifiedSymbolConverter.validate_symbol_consistency(symbol)
        assert len(errors) == 0
        
        # Test invalid ISIN
        symbol.isin_code = 'INVALID_ISIN'
        errors = UnifiedSymbolConverter.validate_symbol_consistency(symbol)
        assert len(errors) > 0
        assert any('isin_code format is invalid' in error for error in errors)
    
    def test_option_validation(self, sample_option_data):
        """Test option-specific validation"""
        # Valid option
        symbol = UnifiedSymbol(**sample_option_data)
        errors = UnifiedSymbolConverter.validate_symbol_consistency(symbol)
        assert len(errors) == 0
        
        # Option without strike price
        symbol.strike_price = None
        errors = UnifiedSymbolConverter.validate_symbol_consistency(symbol)
        assert any('strike_price is required for options' in error for error in errors)
        
        # Option without expiry date
        symbol.strike_price = Decimal('23000')
        symbol.expiry_date = None
        errors = UnifiedSymbolConverter.validate_symbol_consistency(symbol)
        assert any('expiry_date is required for options' in error for error in errors)


class TestBrokerSpecificConverter:
    """Test broker-specific conversion utilities"""
    
    def test_zerodha_conversion(self):
        """Test Zerodha/Kite format conversion"""
        kite_data = {
            'instrument_token': '738561',
            'tradingsymbol': 'RELIANCE',
            'exchange': 'NSE',
            'name': 'RELIANCE INDUSTRIES LTD',
            'expiry': None,
            'strike': None,
            'instrument_type': 'EQ',
            'lot_size': 1,
            'tick_size': 0.05
        }
        
        unified_data = BrokerSpecificConverter.zerodha_to_unified(kite_data)
        
        assert unified_data['instrument_key'] == '738561'
        assert unified_data['symbol'] == 'RELIANCE'
        assert unified_data['exchange'] == Exchange.NSE
        assert unified_data['display_name'] == 'RELIANCE INDUSTRIES LTD'
        assert 'kite_token' in unified_data['metadata']
    
    def test_icici_conversion(self):
        """Test ICICI Breeze format conversion"""
        breeze_data = {
            'stock_code': 'HDFC',
            'exchange_code': 'NSE',
            'company_name': 'HDFC Bank Limited',
            'expiry_date': None,
            'strike_price': None,
            'right': None,
            'stock_token': 'HDFC_NSE'
        }
        
        unified_data = BrokerSpecificConverter.icici_to_unified(breeze_data)
        
        assert unified_data['symbol'] == 'HDFC'
        assert unified_data['exchange'] == Exchange.NSE
        assert unified_data['company_name'] == 'HDFC Bank Limited'
        assert 'breeze_token' in unified_data['metadata']


class TestUnifiedSymbolService:
    """Test the unified symbol service"""
    
    def test_create_symbol(self, symbol_service, sample_equity_data):
        """Test creating a symbol through the service"""
        symbol = symbol_service.create_symbol(sample_equity_data)
        
        assert symbol.id is not None
        assert symbol.symbol == 'RELIANCE'
        assert symbol.instrument_key == 'NSE@RELIANCE@equities'
    
    def test_get_symbol_by_instrument_key(self, symbol_service, sample_equity_data):
        """Test retrieving symbol by instrument key"""
        created_symbol = symbol_service.create_symbol(sample_equity_data)
        
        retrieved_symbol = symbol_service.get_symbol_by_instrument_key('NSE@RELIANCE@equities')
        
        assert retrieved_symbol is not None
        assert retrieved_symbol.id == created_symbol.id
        assert retrieved_symbol.symbol == 'RELIANCE'
    
    def test_update_symbol(self, symbol_service, sample_equity_data):
        """Test updating a symbol"""
        symbol = symbol_service.create_symbol(sample_equity_data)
        
        update_data = {
            'display_name': 'Reliance Industries Ltd.',
            'sector': 'Petrochemicals'
        }
        
        updated_symbol = symbol_service.update_symbol(str(symbol.id), update_data)
        
        assert updated_symbol.display_name == 'Reliance Industries Ltd.'
        assert updated_symbol.sector == 'Petrochemicals'
        assert updated_symbol.version == 2  # Version should increment
    
    def test_search_symbols(self, symbol_service, sample_equity_data, sample_option_data):
        """Test symbol search functionality"""
        # Create test symbols
        symbol_service.create_symbol(sample_equity_data)
        symbol_service.create_symbol(sample_option_data)
        
        # Search by exchange
        filters = SymbolSearchFilters(exchange=Exchange.NSE)
        result = symbol_service.search_symbols(filters)
        
        assert result.total_count == 2
        assert len(result.symbols) == 2
        
        # Search by asset class
        filters = SymbolSearchFilters(asset_class=AssetClass.EQUITY)
        result = symbol_service.search_symbols(filters)
        
        assert result.total_count == 1
        assert result.symbols[0].symbol == 'RELIANCE'
        
        # Text search
        filters = SymbolSearchFilters(search_text='Reliance')
        result = symbol_service.search_symbols(filters)
        
        assert result.total_count == 1
        assert result.symbols[0].symbol == 'RELIANCE'
    
    def test_option_chain_retrieval(self, symbol_service, sample_option_data):
        """Test option chain functionality"""
        # Create option symbol
        symbol_service.create_symbol(sample_option_data)
        
        # Create another option with different strike
        put_option_data = sample_option_data.copy()
        put_option_data['instrument_key'] = 'NSE@NIFTY@options@27-Jun-2024@put@23000'
        put_option_data['option_type'] = OptionType.PUT
        symbol_service.create_symbol(put_option_data)
        
        # Get option chain
        option_chain = symbol_service.get_option_chain('NIFTY', date(2024, 6, 27))
        
        assert len(option_chain) == 2
        strikes = [opt.strike_price for opt in option_chain]
        assert Decimal('23000') in strikes
    
    def test_broker_token_management(self, symbol_service, sample_equity_data):
        """Test broker token management"""
        symbol = symbol_service.create_symbol(sample_equity_data)
        
        # Add broker token
        token_data = BrokerTokenCreate(
            broker_type=BrokerType.ZERODHA_KITE,
            broker_name='zerodha_kite',
            broker_symbol='RELIANCE',
            broker_token='738561'
        )
        
        broker_token = symbol_service.add_broker_token(str(symbol.id), token_data)
        
        assert broker_token.broker_type == BrokerType.ZERODHA_KITE
        assert broker_token.broker_token == '738561'
        
        # Retrieve broker token
        retrieved_token = symbol_service.get_broker_token(str(symbol.id), BrokerType.ZERODHA_KITE)
        assert retrieved_token == '738561'
    
    def test_corporate_actions(self, symbol_service, sample_equity_data):
        """Test corporate action management"""
        symbol = symbol_service.create_symbol(sample_equity_data)
        
        # Add corporate action
        action_data = CorporateActionCreate(
            action_type=CorporateActionType.DIVIDEND,
            announcement_date=date(2024, 6, 1),
            ex_date=date(2024, 6, 15),
            amount=Decimal('15.00'),
            description='Interim dividend of Rs. 15 per share'
        )
        
        corp_action = symbol_service.add_corporate_action(str(symbol.id), action_data)
        
        assert corp_action.action_type == CorporateActionType.DIVIDEND
        assert corp_action.amount == Decimal('15.00')
        
        # Retrieve corporate actions
        actions = symbol_service.get_corporate_actions(str(symbol.id))
        assert len(actions) == 1
        assert actions[0].action_type == CorporateActionType.DIVIDEND
    
    def test_symbol_statistics(self, symbol_service, sample_equity_data, sample_option_data):
        """Test symbol statistics"""
        # Create test symbols
        symbol_service.create_symbol(sample_equity_data)
        symbol_service.create_symbol(sample_option_data)
        
        stats = symbol_service.get_symbol_statistics()
        
        assert stats['total_symbols'] == 2
        assert stats['active_symbols'] == 2
        assert 'EQUITY' in stats['asset_class_distribution']
        assert 'DERIVATIVE' in stats['asset_class_distribution']
        assert 'NSE' in stats['exchange_distribution']


class TestSymbolMigrationUtility:
    """Test symbol migration utilities"""
    
    def test_migration_report_generation(self):
        """Test migration report generation"""
        legacy_symbols = [
            {'symbol': 'RELIANCE', 'exchange': 'NSE'},
            {'symbol': 'HDFC', 'exchange': 'NSE'},
            {'symbol': 'TCS', 'exchange': 'NSE'}
        ]
        
        unified_symbols = [
            {'symbol': 'RELIANCE', 'asset_class': AssetClass.EQUITY, 'exchange': Exchange.NSE},
            {'symbol': 'HDFC', 'asset_class': AssetClass.EQUITY, 'exchange': Exchange.NSE}
        ]
        
        report = SymbolMigrationUtility.generate_migration_report(
            legacy_symbols, unified_symbols
        )
        
        assert report['total_legacy_symbols'] == 3
        assert report['total_unified_symbols'] == 2
        assert report['migration_success_rate'] == 66.67  # 2/3 * 100
        assert report['failed_migrations'] == 1
        assert AssetClass.EQUITY in report['asset_class_distribution']


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_duplicate_symbol_creation(self, symbol_service, sample_equity_data):
        """Test handling duplicate symbol creation"""
        symbol_service.create_symbol(sample_equity_data)
        
        # Attempt to create duplicate should raise error
        with pytest.raises(Exception):  # IntegrityError expected
            symbol_service.create_symbol(sample_equity_data)
    
    def test_invalid_symbol_data(self, symbol_service):
        """Test handling invalid symbol data"""
        invalid_data = {
            'symbol': 'TEST',
            # Missing required fields
        }
        
        with pytest.raises(ValueError):
            symbol_service.create_symbol(invalid_data)
    
    def test_nonexistent_symbol_operations(self, symbol_service):
        """Test operations on non-existent symbols"""
        fake_id = str(uuid.uuid4())
        
        # Update non-existent symbol
        with pytest.raises(ValueError):
            symbol_service.update_symbol(fake_id, {'display_name': 'Test'})
        
        # Add broker token to non-existent symbol
        with pytest.raises(ValueError):
            token_data = BrokerTokenCreate(
                broker_type=BrokerType.ZERODHA_KITE,
                broker_name='zerodha_kite',
                broker_symbol='TEST',
                broker_token='123456'
            )
            symbol_service.add_broker_token(fake_id, token_data)


class TestPerformance:
    """Test performance scenarios"""
    
    def test_bulk_symbol_creation(self, symbol_service):
        """Test bulk symbol creation performance"""
        symbols_data = []
        
        for i in range(100):
            symbols_data.append({
                'instrument_key': f'NSE@TEST{i}@equities',
                'symbol': f'TEST{i}',
                'exchange': Exchange.NSE,
                'asset_class': AssetClass.EQUITY,
                'product_type': ProductType.SPOT,
                'display_name': f'Test Company {i}',
                'lot_size': 1,
                'is_tradable': True,
                'status': SymbolStatus.ACTIVE
            })
        
        start_time = datetime.utcnow()
        created_symbols, failed_items = symbol_service.bulk_create_symbols(symbols_data)
        end_time = datetime.utcnow()
        
        duration = (end_time - start_time).total_seconds()
        
        assert len(created_symbols) == 100
        assert len(failed_items) == 0
        assert duration < 10.0  # Should complete within 10 seconds
    
    def test_large_search_performance(self, symbol_service):
        """Test search performance with large dataset"""
        # Create symbols for performance test
        symbols_data = []
        
        for i in range(1000):
            symbols_data.append({
                'instrument_key': f'NSE@PERF{i}@equities',
                'symbol': f'PERF{i}',
                'exchange': Exchange.NSE,
                'asset_class': AssetClass.EQUITY,
                'product_type': ProductType.SPOT,
                'display_name': f'Performance Test {i}',
                'sector': 'Technology' if i % 2 == 0 else 'Finance',
                'lot_size': 1,
                'is_tradable': True,
                'status': SymbolStatus.ACTIVE
            })
        
        symbol_service.bulk_create_symbols(symbols_data)
        
        # Test search performance
        start_time = datetime.utcnow()
        filters = SymbolSearchFilters(sector='Technology', page_size=50)
        result = symbol_service.search_symbols(filters)
        end_time = datetime.utcnow()
        
        duration = (end_time - start_time).total_seconds()
        
        assert result.total_count == 500  # Half should be Technology sector
        assert len(result.symbols) == 50  # Page size
        assert duration < 2.0  # Should complete within 2 seconds


if __name__ == '__main__':
    pytest.main([__file__])