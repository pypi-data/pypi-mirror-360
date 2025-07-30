"""
Unified Symbol Service for StocksBlitz Platform

This service provides centralized management of symbols across all services,
ensuring consistency and providing a single source of truth for symbol data.
"""

import logging
from typing import List, Dict, Optional, Any, Union, Tuple
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from sqlalchemy.exc import IntegrityError

from shared_architecture.domain.models.market.symbol import (
    UnifiedSymbol, BrokerToken, SymbolMapping,  # CorporateAction - table dropped
    AssetClass, ProductType, Exchange, OptionType, SymbolStatus, BrokerType
)
from shared_architecture.schemas.symbol import (
    UnifiedSymbolCreate, UnifiedSymbolUpdate, SymbolSearchFilters,
    SymbolSearchResult, BrokerTokenCreate  # CorporateActionCreate - table dropped
)
from shared_architecture.utils.unified_symbol_converter import (
    UnifiedSymbolConverter, BrokerSpecificConverter
)

logger = logging.getLogger(__name__)


class UnifiedSymbolService:
    """
    Centralized service for managing unified symbols across the platform
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the service with database session
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    # Symbol CRUD Operations
    
    def create_symbol(self, symbol_data: Union[UnifiedSymbolCreate, Dict]) -> UnifiedSymbol:
        """
        Create a new unified symbol
        
        Args:
            symbol_data: Symbol creation data
            
        Returns:
            Created UnifiedSymbol instance
            
        Raises:
            ValueError: If symbol data is invalid
            IntegrityError: If symbol already exists
        """
        if isinstance(symbol_data, dict):
            symbol_data = UnifiedSymbolCreate(**symbol_data)
        
        # Validate data
        if not symbol_data.instrument_key:
            raise ValueError("instrument_key is required")
        
        # Check if symbol already exists
        existing = self.get_symbol_by_instrument_key(symbol_data.instrument_key)
        if existing:
            raise IntegrityError(f"Symbol with instrument_key '{symbol_data.instrument_key}' already exists", None, None)
        
        # Create symbol
        symbol = UnifiedSymbol(**symbol_data.dict())
        
        # Validate consistency
        validation_errors = UnifiedSymbolConverter.validate_symbol_consistency(symbol)
        if validation_errors:
            raise ValueError(f"Symbol validation failed: {validation_errors}")
        
        self.db.add(symbol)
        self.db.commit()
        self.db.refresh(symbol)
        
        logger.info(f"Created symbol: {symbol.symbol} ({symbol.instrument_key})")
        return symbol
    
    def get_symbol_by_id(self, symbol_id: str) -> Optional[UnifiedSymbol]:
        """Get symbol by UUID"""
        return self.db.query(UnifiedSymbol).filter_by(id=symbol_id).first()
    
    def get_symbol_by_instrument_key(self, instrument_key: str) -> Optional[UnifiedSymbol]:
        """Get symbol by instrument key"""
        return self.db.query(UnifiedSymbol).filter_by(instrument_key=instrument_key).first()
    
    def get_symbol_by_isin(self, isin_code: str) -> Optional[UnifiedSymbol]:
        """Get symbol by ISIN code"""
        return self.db.query(UnifiedSymbol).filter_by(isin_code=isin_code).first()
    
    def update_symbol(self, symbol_id: str, update_data: Union[UnifiedSymbolUpdate, Dict]) -> UnifiedSymbol:
        """
        Update existing symbol
        
        Args:
            symbol_id: Symbol UUID
            update_data: Update data
            
        Returns:
            Updated UnifiedSymbol instance
            
        Raises:
            ValueError: If symbol not found or data invalid
        """
        symbol = self.get_symbol_by_id(symbol_id)
        if not symbol:
            raise ValueError(f"Symbol with ID {symbol_id} not found")
        
        if isinstance(update_data, dict):
            update_data = UnifiedSymbolUpdate(**update_data)
        
        # Apply updates
        for field, value in update_data.dict(exclude_unset=True).items():
            if hasattr(symbol, field):
                setattr(symbol, field, value)
        
        symbol.updated_at = datetime.utcnow()
        symbol.version += 1
        
        # Validate consistency
        validation_errors = UnifiedSymbolConverter.validate_symbol_consistency(symbol)
        if validation_errors:
            raise ValueError(f"Symbol validation failed: {validation_errors}")
        
        self.db.commit()
        self.db.refresh(symbol)
        
        logger.info(f"Updated symbol: {symbol.symbol} ({symbol.instrument_key})")
        return symbol
    
    def delete_symbol(self, symbol_id: str, soft_delete: bool = True) -> bool:
        """
        Delete symbol (soft delete by default)
        
        Args:
            symbol_id: Symbol UUID
            soft_delete: Whether to soft delete or permanently delete
            
        Returns:
            True if deleted successfully
        """
        symbol = self.get_symbol_by_id(symbol_id)
        if not symbol:
            return False
        
        if soft_delete:
            symbol.is_deleted = True
            symbol.deleted_at = datetime.utcnow()
            symbol.status = SymbolStatus.DELISTED
            self.db.commit()
        else:
            self.db.delete(symbol)
            self.db.commit()
        
        logger.info(f"Deleted symbol: {symbol.symbol} ({symbol.instrument_key})")
        return True
    
    # Symbol Search and Filtering
    
    def search_symbols(self, filters: Union[SymbolSearchFilters, Dict]) -> SymbolSearchResult:
        """
        Search symbols with advanced filtering
        
        Args:
            filters: Search filters
            
        Returns:
            SymbolSearchResult with paginated results
        """
        if isinstance(filters, dict):
            filters = SymbolSearchFilters(**filters)
        
        query = self.db.query(UnifiedSymbol).filter_by(is_deleted=False)
        
        # Apply filters
        if filters.symbol:
            query = query.filter(UnifiedSymbol.symbol.ilike(f"%{filters.symbol}%"))
        
        if filters.exchange:
            query = query.filter_by(exchange=filters.exchange)
        
        if filters.asset_class:
            query = query.filter_by(asset_class=filters.asset_class)
        
        if filters.product_type:
            query = query.filter_by(product_type=filters.product_type)
        
        if filters.status:
            query = query.filter_by(status=filters.status)
        
        if filters.search_text:
            search_term = f"%{filters.search_text}%"
            query = query.filter(
                or_(
                    UnifiedSymbol.symbol.ilike(search_term),
                    UnifiedSymbol.display_name.ilike(search_term),
                    UnifiedSymbol.company_name.ilike(search_term),
                    UnifiedSymbol.description.ilike(search_term)
                )
            )
        
        if filters.expiry_date_from:
            query = query.filter(UnifiedSymbol.expiry_date >= filters.expiry_date_from)
        
        if filters.expiry_date_to:
            query = query.filter(UnifiedSymbol.expiry_date <= filters.expiry_date_to)
        
        if filters.listing_date_from:
            query = query.filter(UnifiedSymbol.listing_date >= filters.listing_date_from)
        
        if filters.listing_date_to:
            query = query.filter(UnifiedSymbol.listing_date <= filters.listing_date_to)
        
        if filters.option_type:
            query = query.filter_by(option_type=filters.option_type)
        
        if filters.strike_price_min:
            query = query.filter(UnifiedSymbol.strike_price >= filters.strike_price_min)
        
        if filters.strike_price_max:
            query = query.filter(UnifiedSymbol.strike_price <= filters.strike_price_max)
        
        if filters.underlying_symbol:
            query = query.filter_by(underlying_symbol=filters.underlying_symbol)
        
        if filters.is_tradable is not None:
            query = query.filter_by(is_tradable=filters.is_tradable)
        
        if filters.is_active is not None:
            if filters.is_active:
                query = query.filter_by(status=SymbolStatus.ACTIVE)
            else:
                query = query.filter(UnifiedSymbol.status != SymbolStatus.ACTIVE)
        
        if filters.sector:
            query = query.filter_by(sector=filters.sector)
        
        if filters.industry:
            query = query.filter_by(industry=filters.industry)
        
        if filters.index_constituent:
            query = query.filter(UnifiedSymbol.index_constituents.contains([filters.index_constituent]))
        
        # Broker availability filter
        if filters.broker_type:
            query = query.join(UnifiedSymbol.broker_tokens).filter(
                BrokerToken.broker_type == filters.broker_type
            )
        
        if filters.has_broker_token is not None:
            if filters.has_broker_token:
                query = query.join(UnifiedSymbol.broker_tokens)
            else:
                query = query.filter(~UnifiedSymbol.broker_tokens.any())
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply sorting
        if filters.sort_by:
            sort_field = getattr(UnifiedSymbol, filters.sort_by, None)
            if sort_field:
                if filters.sort_order == 'desc':
                    query = query.order_by(sort_field.desc())
                else:
                    query = query.order_by(sort_field.asc())
        
        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        symbols = query.offset(offset).limit(filters.page_size).all()
        
        # Calculate pagination info
        total_pages = (total_count + filters.page_size - 1) // filters.page_size
        has_next = filters.page < total_pages
        has_previous = filters.page > 1
        
        return SymbolSearchResult(
            symbols=symbols,
            total_count=total_count,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
    
    def get_symbols_by_underlying(self, underlying_symbol: str, 
                                product_type: Optional[ProductType] = None) -> List[UnifiedSymbol]:
        """Get all derivatives for an underlying symbol"""
        query = self.db.query(UnifiedSymbol).filter_by(
            underlying_symbol=underlying_symbol,
            is_deleted=False
        )
        
        if product_type:
            query = query.filter_by(product_type=product_type)
        
        return query.all()
    
    def get_option_chain(self, underlying_symbol: str, expiry_date: date) -> List[UnifiedSymbol]:
        """Get option chain for underlying and expiry"""
        return self.db.query(UnifiedSymbol).filter_by(
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date,
            product_type=ProductType.OPTIONS,
            is_deleted=False
        ).order_by(UnifiedSymbol.strike_price).all()
    
    def get_expiry_dates(self, underlying_symbol: str, 
                        product_type: ProductType = ProductType.OPTIONS) -> List[date]:
        """Get available expiry dates for an underlying"""
        result = self.db.query(UnifiedSymbol.expiry_date).filter_by(
            underlying_symbol=underlying_symbol,
            product_type=product_type,
            is_deleted=False
        ).filter(
            UnifiedSymbol.expiry_date.isnot(None)
        ).distinct().order_by(UnifiedSymbol.expiry_date).all()
        
        return [row[0] for row in result]
    
    # Broker Token Management
    
    def add_broker_token(self, symbol_id: str, token_data: Union[BrokerTokenCreate, Dict]) -> BrokerToken:
        """
        Add broker token mapping to symbol
        
        Args:
            symbol_id: Symbol UUID
            token_data: Broker token data
            
        Returns:
            Created BrokerToken instance
        """
        symbol = self.get_symbol_by_id(symbol_id)
        if not symbol:
            raise ValueError(f"Symbol with ID {symbol_id} not found")
        
        if isinstance(token_data, dict):
            token_data = BrokerTokenCreate(**token_data)
        
        broker_token = BrokerToken(**token_data.dict())
        symbol.broker_tokens.append(broker_token)
        
        self.db.commit()
        self.db.refresh(broker_token)
        
        logger.info(f"Added broker token for {symbol.symbol}: {broker_token.broker_type}")
        return broker_token
    
    def get_broker_token(self, symbol_id: str, broker_type: BrokerType) -> Optional[BrokerToken]:
        """Get broker token for symbol and broker type"""
        symbol = self.get_symbol_by_id(symbol_id)
        if not symbol:
            return None
        
        return symbol.get_broker_token(broker_type)
    
    def update_broker_token(self, token_id: str, update_data: Dict) -> BrokerToken:
        """Update broker token"""
        token = self.db.query(BrokerToken).filter_by(id=token_id).first()
        if not token:
            raise ValueError(f"Broker token with ID {token_id} not found")
        
        for field, value in update_data.items():
            if hasattr(token, field):
                setattr(token, field, value)
        
        token.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(token)
        
        return token
    
    # Corporate Actions - Commented out - table dropped
    # 
    # def add_corporate_action(self, symbol_id: str, 
    #                        action_data: Union[CorporateActionCreate, Dict]) -> CorporateAction:
    #     """
    #     Add corporate action to symbol
    #     
    #     Args:
    #         symbol_id: Symbol UUID
    #         action_data: Corporate action data
    #         
    #     Returns:
    #         Created CorporateAction instance
    #     """
    #     symbol = self.get_symbol_by_id(symbol_id)
    #     if not symbol:
    #         raise ValueError(f"Symbol with ID {symbol_id} not found")
    #     
    #     if isinstance(action_data, dict):
    #         action_data = CorporateActionCreate(**action_data)
    #     
    #     corp_action = CorporateAction(symbol_id=symbol_id, **action_data.dict())
    #     
    #     self.db.add(corp_action)
    #     self.db.commit()
    #     self.db.refresh(corp_action)
    #     
    #     logger.info(f"Added corporate action for {symbol.symbol}: {corp_action.action_type}")
    #     return corp_action
    # 
    # def get_corporate_actions(self, symbol_id: str, 
    #                         action_type: Optional[str] = None) -> List[CorporateAction]:
    #     """Get corporate actions for symbol"""
    #     query = self.db.query(CorporateAction).filter_by(symbol_id=symbol_id)
    #     
    #     if action_type:
    #         query = query.filter_by(action_type=action_type)
    #     
    #     return query.order_by(CorporateAction.ex_date.desc()).all()
    
    # Symbol Conversion and Compatibility
    
    def convert_to_broker_format(self, symbol_id: str, broker_type: BrokerType) -> Dict:
        """Convert symbol to broker-specific format"""
        symbol = self.get_symbol_by_id(symbol_id)
        if not symbol:
            raise ValueError(f"Symbol with ID {symbol_id} not found")
        
        return UnifiedSymbolConverter.to_broker_format(symbol, broker_type)
    
    def import_from_broker(self, broker_data: Dict, broker_type: BrokerType) -> UnifiedSymbol:
        """
        Import symbol from broker-specific format
        
        Args:
            broker_data: Broker-specific symbol data
            broker_type: Source broker type
            
        Returns:
            Created or updated UnifiedSymbol instance
        """
        # Convert broker data to unified format
        if broker_type == BrokerType.ZERODHA_KITE:
            unified_data = BrokerSpecificConverter.zerodha_to_unified(broker_data)
        elif broker_type == BrokerType.ICICI_BREEZE:
            unified_data = BrokerSpecificConverter.icici_to_unified(broker_data)
        else:
            unified_data = BrokerSpecificConverter.autotrader_to_unified(broker_data)
        
        # Check if symbol already exists
        existing = self.get_symbol_by_instrument_key(unified_data['instrument_key'])
        
        if existing:
            # Update existing symbol
            return self.update_symbol(str(existing.id), unified_data)
        else:
            # Create new symbol
            return self.create_symbol(unified_data)
    
    # Bulk Operations
    
    def bulk_create_symbols(self, symbols_data: List[Dict]) -> Tuple[List[UnifiedSymbol], List[Dict]]:
        """
        Bulk create symbols
        
        Args:
            symbols_data: List of symbol dictionaries
            
        Returns:
            Tuple of (created_symbols, failed_items)
        """
        created_symbols = []
        failed_items = []
        
        for symbol_data in symbols_data:
            try:
                symbol = self.create_symbol(symbol_data)
                created_symbols.append(symbol)
            except Exception as e:
                failed_items.append({
                    'data': symbol_data,
                    'error': str(e)
                })
                logger.error(f"Failed to create symbol {symbol_data.get('symbol', 'unknown')}: {e}")
        
        return created_symbols, failed_items
    
    def bulk_update_symbols(self, updates: List[Dict]) -> Tuple[List[UnifiedSymbol], List[Dict]]:
        """
        Bulk update symbols
        
        Args:
            updates: List of update dictionaries with 'id' and update data
            
        Returns:
            Tuple of (updated_symbols, failed_items)
        """
        updated_symbols = []
        failed_items = []
        
        for update_item in updates:
            try:
                symbol_id = update_item['id']
                update_data = {k: v for k, v in update_item.items() if k != 'id'}
                symbol = self.update_symbol(symbol_id, update_data)
                updated_symbols.append(symbol)
            except Exception as e:
                failed_items.append({
                    'data': update_item,
                    'error': str(e)
                })
                logger.error(f"Failed to update symbol {update_item.get('id', 'unknown')}: {e}")
        
        return updated_symbols, failed_items
    
    # Statistics and Analytics
    
    def get_symbol_statistics(self) -> Dict[str, Any]:
        """Get comprehensive symbol statistics"""
        stats = {}
        
        # Total counts
        stats['total_symbols'] = self.db.query(UnifiedSymbol).filter_by(is_deleted=False).count()
        stats['active_symbols'] = self.db.query(UnifiedSymbol).filter_by(
            status=SymbolStatus.ACTIVE, is_deleted=False
        ).count()
        
        # Asset class distribution
        asset_class_stats = self.db.query(
            UnifiedSymbol.asset_class, func.count(UnifiedSymbol.id)
        ).filter_by(is_deleted=False).group_by(UnifiedSymbol.asset_class).all()
        stats['asset_class_distribution'] = {ac.value: count for ac, count in asset_class_stats}
        
        # Exchange distribution
        exchange_stats = self.db.query(
            UnifiedSymbol.exchange, func.count(UnifiedSymbol.id)
        ).filter_by(is_deleted=False).group_by(UnifiedSymbol.exchange).all()
        stats['exchange_distribution'] = {ex.value: count for ex, count in exchange_stats}
        
        # Product type distribution
        product_stats = self.db.query(
            UnifiedSymbol.product_type, func.count(UnifiedSymbol.id)
        ).filter_by(is_deleted=False).group_by(UnifiedSymbol.product_type).all()
        stats['product_type_distribution'] = {pt.value: count for pt, count in product_stats}
        
        # Broker token coverage
        total_broker_tokens = self.db.query(BrokerToken).count()
        stats['total_broker_tokens'] = total_broker_tokens
        stats['symbols_with_broker_tokens'] = self.db.query(UnifiedSymbol).join(
            UnifiedSymbol.broker_tokens
        ).distinct().count()
        
        return stats