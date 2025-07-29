"""
ContextCol Binance Spot SDK - Python SDK for Contextcol trading bot on Binance spot with Contextcol API integration
"""

__version__ = "0.1.0"
__author__ = "khemmapich"
__email__ = "khemmapich@contextcol.com"

from .client import ContextcolClient
from .config import Config
from .exceptions import ContextcolError, APIError, ConfigError
from .binance_client import BinanceClient
from .binance_market_data import BinanceMarketData
from .binance_account import BinanceAccount

__all__ = [
    "ContextcolClient",
    "Config",
    "ContextcolError",
    "APIError",
    "ConfigError",
    "BinanceClient",
    "BinanceMarketData",
    "BinanceAccount",
]
