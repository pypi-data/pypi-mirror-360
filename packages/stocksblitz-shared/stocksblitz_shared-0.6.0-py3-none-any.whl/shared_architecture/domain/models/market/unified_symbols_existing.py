"""
Compatibility model that maps to the existing unified_symbols table structure
This model works with the actual column names in the database
"""

from datetime import datetime, date
from typing import Optional
from decimal import Decimal
import uuid

from sqlalchemy import (
    Column, String, Date, DateTime, Integer, Boolean, Text, 
    Numeric, UUID as SqlUUID
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from shared_architecture.db.base import Base


class UnifiedSymbolsExisting(Base):
    """
    Model that maps to existing unified_symbols table structure
    """
    __tablename__ = "unified_symbols"
    __table_args__ = {'schema': 'tradingdb', 'extend_existing': True}

    # Primary key (matches actual table structure)
    instrument_key = Column(Text, primary_key=True)
    
    # Existing columns from the actual table
    stock_token = Column(Text)
    instrumentname = Column(Text)
    stock_code = Column(Text)
    series = Column(Text)
    expirydate = Column(Date)
    strikeprice = Column(Numeric)
    optiontype = Column(Text)
    calevel = Column(Text)
    permittedtotrade = Column(Boolean)
    issuecapital = Column(Numeric)
    warningqty = Column(Integer)
    freezeqty = Column(Integer)
    creditrating = Column(Text)
    normalmarketstatus = Column(Text)
    oddlotmarketstatus = Column(Text)
    spotmarketstatus = Column(Text)
    auctionmarketstatus = Column(Text)
    normalmarketeligibility = Column(Text)
    oddlotmarketeligibility = Column(Text)
    spotmarketeligibility = Column(Text)
    auctionmarketeligibility = Column(Text)
    scripid = Column(Text)
    issuerate = Column(Numeric)
    issuestartdate = Column(Date)
    interestpaymentdate = Column(Date)
    issuematuritydate = Column(Date)
    marginpercentage = Column(Numeric)
    minimumlotqty = Column(Integer)
    lotsize = Column(Integer)
    ticksize = Column(Numeric)
    companyname = Column(Text)
    listingdate = Column(Date)
    expulsiondate = Column(Date)
    readmissiondate = Column(Date)
    recorddate = Column(Date)
    lowpricerange = Column(Numeric)
    highpricerange = Column(Numeric)
    securityexpirydate = Column(Date)
    nodeliverystartdate = Column(Date)
    nodeliveryenddate = Column(Date)
    aon = Column(Text)
    participantinmarketindex = Column(Text)
    bookclsstartdate = Column(Date)
    bookclsenddate = Column(Date)
    excercisestartdate = Column(Date)
    excerciseenddate = Column(Date)
    oldtoken = Column(Text)
    assetinstrument = Column(Text)
    assetname = Column(Text)
    assettoken = Column(Integer)
    intrinsicvalue = Column(Numeric)
    extrinsicvalue = Column(Numeric)
    excercisestyle = Column(Text)
    egm = Column(Text)
    agm = Column(Text)
    interest = Column(Text)
    bonus = Column(Text)
    rights = Column(Text)
    dividends = Column(Text)
    exallowed = Column(Text)
    exrejectionallowed = Column(Boolean)
    plallowed = Column(Boolean)
    isthisasset = Column(Boolean)
    iscorpadjusted = Column(Boolean)
    localupdatedatetime = Column(DateTime)
    deleteflag = Column(Boolean)
    remarks = Column(Text)
    baseprice = Column(Numeric)
    exchangecode = Column(Text)
    exchange_code = Column(Text)
    product_type = Column(Text)
    option_type = Column(Text)
    breeze_token = Column(Text)
    kite_token = Column(Text)
    boardlotqty = Column(Integer)
    dateofdelisting = Column(Date)
    dateoflisting = Column(Date)
    facevalue = Column(Numeric)
    freezepercent = Column(Numeric)
    highdate = Column(Date)
    isincode = Column(Text)
    instrumenttype = Column(Text)
    issueprice = Column(Numeric)
    lifetimehigh = Column(Numeric)
    lifetimelow = Column(Numeric)
    lowdate = Column(Date)
    avmbuymargin = Column(Numeric)
    avmsellmargin = Column(Numeric)
    bcastflag = Column(Boolean)
    groupname = Column(Text)
    marketlot = Column(Integer)
    ndedate = Column(Date)
    ndsdate = Column(Date)
    ndflag = Column(Boolean)
    scripcode = Column(Text)
    scripname = Column(Text)
    suspstatus = Column(Text)
    suspensionreason = Column(Text)
    suspensiondate = Column(Date)
    refresh_flag = Column(Boolean)
    first_added_datetime = Column(Date)
    symbol = Column(Text)
    shortname = Column(Text)
    mfill = Column(Text)
    # Note: 'id' column exists in DB but will be auto-mapped by SQLAlchemy
    
    # Additional columns that might be dynamically named
    _52WeeksHigh = Column("52WeeksHigh", Numeric)
    _52WeeksLow = Column("52WeeksLow", Numeric)

    def to_dict(self):
        """Convert to dictionary for serialization"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, (datetime, date)):
                result[column.name] = value.isoformat() if value else None
            elif isinstance(value, Decimal):
                result[column.name] = float(value) if value is not None else None
            elif isinstance(value, uuid.UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
        return result

    def get_exchange(self):
        """Get exchange from exchange_code or exchangecode"""
        return self.exchange_code or self.exchangecode or "NSE"
    
    def get_display_name(self):
        """Get display name from available fields"""
        return self.instrumentname or self.companyname or self.symbol or self.scripname
    
    def get_option_type(self):
        """Get option type in standardized format"""
        if self.option_type:
            return self.option_type.lower()
        elif self.optiontype:
            return self.optiontype.lower()
        return None
    
    def is_option(self):
        """Check if symbol is an option"""
        return self.get_option_type() in ['call', 'put', 'ce', 'pe']
    
    def is_future(self):
        """Check if symbol is a future"""
        return self.product_type == 'futures' or self.instrumenttype == 'future'
    
    def is_equity(self):
        """Check if symbol is equity"""
        return self.product_type == 'spot' or self.instrumenttype == 'equity'
    
    def is_active(self):
        """Check if symbol is active for trading"""
        return (
            not self.deleteflag and
            self.permittedtotrade and
            (self.expirydate is None or self.expirydate >= date.today())
        )

    def __repr__(self):
        return f"<UnifiedSymbolsExisting(instrument_key='{self.instrument_key}', symbol='{self.symbol}', exchange='{self.get_exchange()}')>"