"""
Compatibility schema for existing unified_symbols table structure
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


class ExistingSymbolBase(BaseModel):
    """Base schema matching existing database structure"""
    
    class Config:
        from_attributes = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None,
            UUID: lambda v: str(v)
        }


class ExistingUnifiedSymbol(ExistingSymbolBase):
    """Schema for existing unified_symbols table structure"""
    
    # Primary key
    instrument_key: str
    
    # Core symbol information
    symbol: Optional[str] = None
    instrumentname: Optional[str] = None
    companyname: Optional[str] = None
    shortname: Optional[str] = None
    
    # Exchange and classification
    exchangecode: Optional[str] = None
    exchange_code: Optional[str] = None
    instrumenttype: Optional[str] = None
    product_type: Optional[str] = None
    
    # Options/Derivatives
    expirydate: Optional[date] = None
    strikeprice: Optional[Decimal] = None
    optiontype: Optional[str] = None
    option_type: Optional[str] = None
    
    # Trading specifications  
    lotsize: Optional[int] = None
    ticksize: Optional[Decimal] = None
    minimumlotqty: Optional[int] = None
    boardlotqty: Optional[int] = None
    
    # Market data
    baseprice: Optional[Decimal] = None
    facevalue: Optional[Decimal] = None
    marketlot: Optional[int] = None
    
    # Price ranges
    lowpricerange: Optional[Decimal] = None
    highpricerange: Optional[Decimal] = None
    lifetimehigh: Optional[Decimal] = None
    lifetimelow: Optional[Decimal] = None
    
    # Margin information
    marginpercentage: Optional[Decimal] = None
    avmbuymargin: Optional[Decimal] = None
    avmsellmargin: Optional[Decimal] = None
    
    # Risk management
    warningqty: Optional[int] = None
    freezeqty: Optional[int] = None
    freezepercent: Optional[Decimal] = None
    creditrating: Optional[str] = None
    
    # Status and permissions
    permittedtotrade: Optional[bool] = None
    deleteflag: Optional[bool] = None
    refresh_flag: Optional[bool] = None
    suspstatus: Optional[str] = None
    suspensionreason: Optional[str] = None
    suspensiondate: Optional[date] = None
    
    # Market eligibility
    normalmarketstatus: Optional[str] = None
    oddlotmarketstatus: Optional[str] = None
    spotmarketstatus: Optional[str] = None
    auctionmarketstatus: Optional[str] = None
    
    # Identifiers
    isincode: Optional[str] = None
    stock_token: Optional[str] = None
    breeze_token: Optional[str] = None
    kite_token: Optional[str] = None
    
    # Dates
    listingdate: Optional[date] = None
    dateofdelisting: Optional[date] = None
    dateoflisting: Optional[date] = None
    first_added_datetime: Optional[date] = None
    localupdatedatetime: Optional[datetime] = None
    
    # Corporate actions
    bonus: Optional[str] = None
    rights: Optional[str] = None
    dividends: Optional[str] = None
    interest: Optional[str] = None
    
    # Additional fields
    remarks: Optional[str] = None
    groupname: Optional[str] = None
    scripcode: Optional[str] = None
    scripname: Optional[str] = None
    
    # Computed/display fields
    @property
    def display_name(self) -> Optional[str]:
        """Get display name from available fields"""
        return self.instrumentname or self.companyname or self.symbol or self.scripname
    
    @property
    def exchange(self) -> Optional[str]:
        """Get exchange from available fields"""
        return self.exchange_code or self.exchangecode or "NSE"
    
    @property
    def option_type_normalized(self) -> Optional[str]:
        """Get normalized option type"""
        opt_type = self.option_type or self.optiontype
        if opt_type:
            return opt_type.lower()
        return None
    
    @property
    def is_active(self) -> bool:
        """Check if symbol is active"""
        return (
            not self.deleteflag and
            self.permittedtotrade and
            (self.expirydate is None or self.expirydate >= date.today())
        )
    
    @property
    def asset_class(self) -> str:
        """Derive asset class from instrument type"""
        if self.instrumenttype:
            instrument_type = self.instrumenttype.lower()
            if instrument_type == 'equity':
                return 'equity'
            elif instrument_type in ['option', 'future']:
                return 'derivative'
            elif instrument_type == 'commodity':
                return 'commodity'
        return 'equity'  # default
    
    @property
    def product_type_normalized(self) -> str:
        """Derive product type"""
        if self.product_type:
            return self.product_type.lower()
        elif self.instrumenttype:
            instrument_type = self.instrumenttype.lower()
            if instrument_type == 'equity':
                return 'spot'
            elif instrument_type == 'option':
                return 'options'
            elif instrument_type == 'future':
                return 'futures'
        return 'spot'  # default


class ExistingSymbolResponse(ExistingUnifiedSymbol):
    """Response schema with computed fields"""
    
    # Include computed properties in response
    display_name: Optional[str] = None
    exchange: Optional[str] = None
    asset_class: Optional[str] = None
    product_type_normalized: Optional[str] = None
    option_type_normalized: Optional[str] = None
    is_active: Optional[bool] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Populate computed fields
        self.display_name = self.display_name
        self.exchange = self.exchange  
        self.asset_class = self.asset_class
        self.product_type_normalized = self.product_type_normalized
        self.option_type_normalized = self.option_type_normalized
        self.is_active = self.is_active


class ExistingSymbolCreate(ExistingSymbolBase):
    """Schema for creating symbols with existing structure"""
    instrument_key: str
    symbol: Optional[str] = None
    instrumentname: Optional[str] = None
    exchange_code: Optional[str] = None
    instrumenttype: Optional[str] = None


class ExistingSymbolUpdate(ExistingSymbolBase):
    """Schema for updating symbols with existing structure"""
    symbol: Optional[str] = None
    instrumentname: Optional[str] = None
    companyname: Optional[str] = None
    lotsize: Optional[int] = None
    ticksize: Optional[Decimal] = None
    permittedtotrade: Optional[bool] = None