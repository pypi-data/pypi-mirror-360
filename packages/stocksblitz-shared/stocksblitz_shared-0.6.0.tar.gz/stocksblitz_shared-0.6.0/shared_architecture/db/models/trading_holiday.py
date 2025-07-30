"""
Trading Holiday Model for TimescaleDB
Stores exchange trading holidays for market timing calculations
"""

from sqlalchemy import Column, String, Date, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from shared_architecture.db.base import Base
from shared_architecture.utils.time_utils import utc_now

class TradingHoliday(Base):
    """
    Model to store trading holidays for different exchanges
    """
    __tablename__ = "trading_holidays"
    __table_args__ = {'schema': 'tradingdb'}

    # Primary key: combination of date and exchange
    date = Column(Date, primary_key=True, nullable=False, comment="Holiday date")
    exchange = Column(String(10), primary_key=True, nullable=False, comment="Exchange code (NSE, BSE, etc.)")
    
    # Holiday details
    holiday_name = Column(String(100), nullable=False, comment="Name of the holiday")
    holiday_type = Column(String(20), nullable=False, comment="Type: national, religious, state, etc.")
    description = Column(Text, nullable=True, comment="Detailed description of the holiday")
    
    # Metadata (store as naive datetime to avoid timezone issues)
    created_at = Column(DateTime(timezone=False), comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=False), comment="Record update timestamp")

    def __repr__(self):
        return f"<TradingHoliday(date='{self.date}', exchange='{self.exchange}', holiday='{self.holiday_name}')>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "date": self.date.isoformat() if self.date else None,
            "exchange": self.exchange,
            "holiday_name": self.holiday_name,
            "holiday_type": self.holiday_type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    async def is_trading_holiday(cls, session, date, exchange="NSE"):
        """
        Check if a given date is a trading holiday for the specified exchange
        
        Args:
            session: Async database session
            date: Date to check (datetime.date object)
            exchange: Exchange code (default: NSE)
            
        Returns:
            TradingHoliday object if it's a holiday, None otherwise
        """
        from sqlalchemy import select
        query = select(cls).where(cls.date == date, cls.exchange == exchange)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    def get_holidays_in_range(cls, session, start_date, end_date, exchange="NSE"):
        """
        Get all trading holidays in a date range for the specified exchange
        
        Args:
            session: Database session
            start_date: Start date (datetime.date object)
            end_date: End date (datetime.date object)
            exchange: Exchange code (default: NSE)
            
        Returns:
            List of TradingHoliday objects
        """
        return session.query(cls).filter(
            cls.date >= start_date,
            cls.date <= end_date,
            cls.exchange == exchange
        ).order_by(cls.date).all()

    @classmethod
    def get_next_holiday(cls, session, from_date, exchange="NSE"):
        """
        Get the next trading holiday after the given date
        
        Args:
            session: Database session
            from_date: Date to search from (datetime.date object)
            exchange: Exchange code (default: NSE)
            
        Returns:
            TradingHoliday object or None
        """
        return session.query(cls).filter(
            cls.date > from_date,
            cls.exchange == exchange
        ).order_by(cls.date).first()