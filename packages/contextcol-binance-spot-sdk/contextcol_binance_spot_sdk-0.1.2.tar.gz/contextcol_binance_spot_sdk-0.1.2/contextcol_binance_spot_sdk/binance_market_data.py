"""
Binance Market Data API endpoints for ContextCol SDK
"""

import logging
import requests
from typing import Dict, Any, List, Optional, cast
from .exceptions import BinanceAPIError

logger = logging.getLogger(__name__)


class BinanceMarketData:
    """Binance Market Data API client"""

    def __init__(self, base_url: str):
        """Initialize market data client"""
        self.BASE_URL = base_url
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "contextcol-binance-spot-sdk/1.0"})

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Binance API"""
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.get(url, params=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise BinanceAPIError(f"Request failed: {str(e)}")
        except ValueError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise BinanceAPIError(f"JSON decode error: {str(e)}")

    def _make_request_with_list(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Make HTTP request to Binance API"""
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.get(url, params=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise BinanceAPIError(f"Request failed: {str(e)}")
        except ValueError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise BinanceAPIError(f"JSON decode error: {str(e)}")

    def get_order_book(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get order book for a symbol

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT')
            limit: Number of entries to return (default: 100, max: 5000)

        Returns:
            Order book data with bids and asks
        """
        params = {"symbol": symbol.upper(), "limit": limit}
        return cast(Dict[str, Any], self._make_request("/api/v3/depth", params))

    def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get recent trades for a symbol

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT')
            limit: Number of trades to return (default: 500, max: 1000)

        Returns:
            List of recent trades
        """
        params = {"symbol": symbol.upper(), "limit": limit}
        return cast(List[Dict[str, Any]], self._make_request("/api/v3/trades", params))

    def get_historical_trades(
        self, symbol: str, limit: int = 500, from_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical trades for a symbol

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT')
            limit: Number of trades to return (default: 500, max: 1000)
            from_id: Trade ID to fetch from (optional)

        Returns:
            List of historical trades
        """
        params = {"symbol": symbol.upper(), "limit": limit}
        if from_id is not None:
            params["fromId"] = from_id

        return cast(
            List[Dict[str, Any]], self._make_request("/api/v3/historicalTrades", params)
        )

    def get_aggregate_trades(
        self,
        symbol: str,
        from_id: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """
        Get compressed/aggregate trades for a symbol

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT')
            from_id: ID to get aggregate trades from (optional)
            start_time: Timestamp in ms to get aggregate trades from (optional)
            end_time: Timestamp in ms to get aggregate trades until (optional)
            limit: Number of trades to return (default: 500, max: 1000)

        Returns:
            List of aggregate trades
        """
        params = {"symbol": symbol.upper(), "limit": limit}
        if from_id is not None:
            params["fromId"] = from_id
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time

        return cast(
            List[Dict[str, Any]], self._make_request("/api/v3/aggTrades", params)
        )

    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        time_zone: Optional[str] = None,
        limit: int = 500,
    ) -> List[List[Any]]:
        """
        Get kline/candlestick data for a symbol

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT')
            interval: Kline interval (e.g. '1m', '5m', '1h', '1d')
            start_time: Start time timestamp in ms (optional)
            end_time: End time timestamp in ms (optional)
            time_zone: Timezone (optional, default: UTC)
            limit: Number of klines to return (default: 500, max: 1000)

        Returns:
            List of kline data
        """
        params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time
        if time_zone is not None:
            params["timeZone"] = time_zone

        return cast(List[List[Any]], self._make_request("/api/v3/klines", params))

    def get_ui_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        time_zone: Optional[str] = None,
        limit: int = 500,
    ) -> List[List[Any]]:
        """
        Get UI kline/candlestick data for a symbol (optimized for presentation)

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT')
            interval: Kline interval (e.g. '1m', '5m', '1h', '1d')
            start_time: Start time timestamp in ms (optional)
            end_time: End time timestamp in ms (optional)
            time_zone: Timezone (optional, default: UTC)
            limit: Number of klines to return (default: 500, max: 1000)

        Returns:
            List of UI kline data
        """
        params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time
        if time_zone is not None:
            params["timeZone"] = time_zone

        return cast(List[List[Any]], self._make_request("/api/v3/uiKlines", params))

    def get_avg_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current average price for a symbol

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT')

        Returns:
            Average price data
        """
        params = {"symbol": symbol.upper()}
        return cast(Dict[str, Any], self._make_request("/api/v3/avgPrice", params))

    def get_24hr_ticker(
        self,
        symbol: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        ticker_type: str = "FULL",
    ) -> Dict[str, Any]:
        """
        Get 24hr ticker price change statistics

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT') - optional
            symbols: List of trading symbols - optional
            ticker_type: Type of ticker data ('FULL' or 'MINI')

        Returns:
            Ticker data (single dict if symbol provided, list if symbols/all)
        """
        params = {"type": ticker_type}

        if symbol:
            params["symbol"] = symbol.upper()
        elif symbols:
            params["symbols"] = str(symbols).replace("'", '"')

        return self._make_request("/api/v3/ticker/24hr", params)

    def get_trading_day_ticker_with_symbol(
        self,
        symbol: str,
        time_zone: Optional[str] = None,
        ticker_type: str = "FULL",
    ) -> Dict[str, Any]:
        """
        Get trading day ticker price change statistics

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT') - optional
            symbols: List of trading symbols - optional
            time_zone: Timezone (optional, default: UTC)
            ticker_type: Type of ticker data ('FULL' or 'MINI')

        Returns:
            Trading day ticker data
        """
        params = {"type": ticker_type}
        params["symbol"] = symbol.upper()
        if time_zone:
            params["timeZone"] = time_zone

        return self._make_request("/api/v3/ticker/tradingDay", params)

    def get_trading_day_ticker_with_symbols(
        self,
        symbols: List[str],
        time_zone: Optional[str] = None,
        ticker_type: str = "FULL",
    ) -> List[Dict[str, Any]]:
        """
        Get trading day ticker price change statistics

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT') - optional
            symbols: List of trading symbols - optional
            time_zone: Timezone (optional, default: UTC)
            ticker_type: Type of ticker data ('FULL' or 'MINI')

        Returns:
            Trading day ticker data
        """
        params = {"type": ticker_type}

        params["symbols"] = str(symbols).replace("'", '"')
        if time_zone:
            params["timeZone"] = time_zone

        return self._make_request_with_list("/api/v3/ticker/tradingDay", params)

    def get_symbol_price_ticker(
        self, symbol: Optional[str] = None, symbols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get latest price for a symbol or symbols

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT') - optional
            symbols: List of trading symbols - optional

        Returns:
            Price ticker data
        """
        params = {}

        if symbol:
            params["symbol"] = symbol.upper()
        elif symbols:
            params["symbols"] = str(symbols).replace("'", '"')

        return cast(Dict[str, Any], self._make_request("/api/v3/ticker/price", params))

    def get_order_book_ticker_with_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        Get best price/qty on the order book for a symbol or symbols

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT') - optional
            symbols: List of trading symbols - optional

        Returns:
            Order book ticker data
        """
        params = {}

        params["symbol"] = symbol.upper()

        return cast(
            Dict[str, Any], self._make_request("/api/v3/ticker/bookTicker", params)
        )

    def get_order_book_ticker_with_symbols(
        self, symbols: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Get best price/qty on the order book for a symbol or symbols
        """
        params = {}
        params["symbols"] = str(symbols).replace("'", '"')
        return self._make_request_with_list("/api/v3/ticker/bookTicker", params)

    def get_rolling_window_ticker_with_symbol(
        self,
        symbol: str,
        window_size: str = "1d",
        ticker_type: str = "FULL",
    ) -> Dict[str, Any]:
        """
        Get rolling window price change statistics

        Args:
            symbol: Trading symbol (e.g. 'BTCUSDT') - optional
            symbols: List of trading symbols - optional
            window_size: Window size (e.g. '1m', '1h', '1d')
            ticker_type: Type of ticker data ('FULL' or 'MINI')

        Returns:
            Rolling window ticker data
        """
        params = {"windowSize": window_size, "type": ticker_type}
        params["symbol"] = symbol.upper()
        return cast(Dict[str, Any], self._make_request("/api/v3/ticker", params))

    def get_rolling_window_ticker_with_symbols(
        self, symbols: List[str], window_size: str = "1d", ticker_type: str = "FULL"
    ) -> List[Dict[str, Any]]:
        """
        Get rolling window price change statistics
        """
        params = {"windowSize": window_size, "type": ticker_type}
        params["symbols"] = str(symbols).replace("'", '"')
        return self._make_request_with_list("/api/v3/ticker", params)
