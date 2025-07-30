"""
Core enumerations for the instrument management system
"""

from enum import Enum


class AssetProductType(Enum):
    """Combined asset class and product type for clarity"""
    
    # Equity
    EQUITY_SPOT = "equity_spot"
    EQUITY_FUTURES = "equity_futures" 
    EQUITY_OPTIONS = "equity_options"
    EQUITY_ETF = "equity_etf"
    
    # Index
    INDEX_SPOT = "index_spot"
    INDEX_FUTURES = "index_futures"
    INDEX_OPTIONS = "index_options"
    INDEX_ETF = "index_etf"
    
    # Commodity
    COMMODITY_SPOT = "commodity_spot"
    COMMODITY_FUTURES = "commodity_futures"
    COMMODITY_OPTIONS = "commodity_options"
    COMMODITY_ETF = "commodity_etf"
    
    # Currency/Forex
    CURRENCY_SPOT = "currency_spot"
    CURRENCY_FUTURES = "currency_futures"
    CURRENCY_OPTIONS = "currency_options"
    CURRENCY_FORWARD = "currency_forward"
    
    # Crypto
    CRYPTO_SPOT = "crypto_spot"
    CRYPTO_FUTURES = "crypto_futures"
    CRYPTO_OPTIONS = "crypto_options"
    CRYPTO_PERPETUAL = "crypto_perpetual"
    
    # Fixed Income
    BOND_GOVERNMENT = "bond_government"
    BOND_CORPORATE = "bond_corporate"
    BOND_TREASURY = "bond_treasury"
    BOND_MUNICIPAL = "bond_municipal"
    
    # Mutual Funds
    MF_EQUITY = "mf_equity"
    MF_DEBT = "mf_debt"
    MF_HYBRID = "mf_hybrid"
    MF_LIQUID = "mf_liquid"
    MF_SECTORAL = "mf_sectoral"
    
    @property
    def asset_class(self) -> str:
        """Extract asset class from asset-product type"""
        return self.value.split('_')[0]
    
    @property
    def product_type(self) -> str:
        """Extract product type from asset-product type"""
        return '_'.join(self.value.split('_')[1:])
    
    def is_derivative(self) -> bool:
        """Check if instrument is a derivative"""
        derivative_types = ['futures', 'options', 'forward', 'perpetual']
        return self.product_type in derivative_types
    
    def requires_expiry(self) -> bool:
        """Check if instrument requires expiry date"""
        return self.is_derivative() and self != AssetProductType.CRYPTO_PERPETUAL
    
    def supports_options(self) -> bool:
        """Check if asset class supports options"""
        return 'options' in self.value


class Exchange(Enum):
    """Supported exchanges"""
    
    # Indian Exchanges
    NSE = "NSE"
    BSE = "BSE"
    MCX = "MCX"
    NCDEX = "NCDEX"
    
    # International Exchanges
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    BINANCE = "BINANCE"
    COINBASE = "COINBASE"
    
    # Multi-exchange support
    ANY = "ANY"  # For instruments that can trade on multiple exchanges


class OptionType(Enum):
    """Option types"""
    CALL = "call"
    PUT = "put"


class Moneyness(Enum):
    """Option moneyness classifications"""
    DEEP_ITM = "DITM"    # Deep In The Money
    ITM5 = "ITM5"        # In The Money -5
    ITM4 = "ITM4"
    ITM3 = "ITM3"
    ITM2 = "ITM2"
    ITM1 = "ITM1"
    ATM = "ATM"          # At The Money
    OTM1 = "OTM1"        # Out of The Money +1
    OTM2 = "OTM2"
    OTM3 = "OTM3"
    OTM4 = "OTM4"
    OTM5 = "OTM5"
    DEEP_OTM = "DOTM"    # Deep Out of The Money
    
    def get_level(self) -> int:
        """Get numeric level for moneyness (-5 to +5, 0 for ATM)"""
        mapping = {
            self.DEEP_ITM: -6,
            self.ITM5: -5,
            self.ITM4: -4,
            self.ITM3: -3,
            self.ITM2: -2,
            self.ITM1: -1,
            self.ATM: 0,
            self.OTM1: 1,
            self.OTM2: 2,
            self.OTM3: 3,
            self.OTM4: 4,
            self.OTM5: 5,
            self.DEEP_OTM: 6,
        }
        return mapping.get(self, 0)
    
    @classmethod
    def from_level(cls, level: int, option_type: OptionType = OptionType.CALL):
        """Create moneyness from numeric level"""
        # For calls: positive level = OTM, negative = ITM
        # For puts: positive level = ITM, negative = OTM
        
        if option_type == OptionType.CALL:
            mapping = {
                0: cls.ATM,
                1: cls.OTM1, 2: cls.OTM2, 3: cls.OTM3, 4: cls.OTM4, 5: cls.OTM5,
                -1: cls.ITM1, -2: cls.ITM2, -3: cls.ITM3, -4: cls.ITM4, -5: cls.ITM5,
            }
            
            if level >= 6:
                return cls.DEEP_OTM
            elif level <= -6:
                return cls.DEEP_ITM
            else:
                return mapping.get(level, cls.ATM)
        
        else:  # PUT option - inverted logic
            mapping = {
                0: cls.ATM,
                1: cls.ITM1, 2: cls.ITM2, 3: cls.ITM3, 4: cls.ITM4, 5: cls.ITM5,
                -1: cls.OTM1, -2: cls.OTM2, -3: cls.OTM3, -4: cls.OTM4, -5: cls.OTM5,
            }
            
            if level >= 6:
                return cls.DEEP_ITM
            elif level <= -6:
                return cls.DEEP_OTM
            else:
                return mapping.get(level, cls.ATM)