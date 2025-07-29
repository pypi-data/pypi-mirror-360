"""
Binance API integration for ContextCol SDK
"""

import logging
import time
import hmac
import hashlib
import requests
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlencode
from .config import Config
from .exceptions import BinanceAPIError, AuthenticationError
from .binance_market_data import BinanceMarketData
from .binance_trading import BinanceTrading
from .binance_account import BinanceAccount

logger = logging.getLogger(__name__)


class BinanceClient:
    """Binance API client wrapper"""

    def __init__(self, config: Config):
        """Initialize Binance client"""
        self.config = config
        self.base_url = config.binance_base_url
        self.binance_testnet = config.binance_testnet

        self.session = requests.Session()
        headers = {"User-Agent": "contextcol-binance-spot-sdk/1.0"}
        headers = {}
        if config.binance_api_key:
            headers["X-MBX-APIKEY"] = config.binance_api_key
        headers["Content-Type"] = "application/json"
        self.session.headers.update(headers)

        print(f"Base URL: {self.base_url}")
        print(f"Binance testnet: {self.binance_testnet}")
        print(f"Binance API key: {config.binance_api_key}")
        print(f"Binance API secret: {config.binance_api_secret}")

        # Initialize market data client
        self.market_data = BinanceMarketData(base_url=config.binance_base_url)

        self.trading = BinanceTrading(self)
        self.account = BinanceAccount(self)

        # Test connection
        self._test_connection()

    def _test_connection(self):
        """Test connection to Binance API"""
        try:
            self.config.validate_required_for_binance()

            # Test connection with ping
            response = self.session.get(f"{self.base_url}/api/v3/ping")
            response.raise_for_status()

            logger.info("Binance client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {str(e)}")
            raise AuthenticationError(f"Failed to initialize Binance client: {str(e)}")

    def _generate_signature(self, query_string: str) -> str:
        """Generate HMAC SHA256 signature"""
        if not self.config.binance_api_secret:
            raise AuthenticationError(
                "Binance API secret is required for authenticated requests"
            )
        print(f"API secret: {self.config.binance_api_secret}")
        m = hmac.new(
            self.config.binance_api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        )
        print(f"Signature: {m.hexdigest()}")
        return m.hexdigest()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Binance API requests."""
        return {
            "X-MBX-APIKEY": self.config.binance_api_key or "",
            "Content-Type": "application/json",
        }

    def _make_authenticated_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> Dict[str, Any]:
        """Make authenticated request to Binance API"""
        if params is None:
            params = {}

        # Add timestamp
        params["timestamp"] = int(time.time() * 1000)

        # Create query string
        query_string = urlencode(params)
        print(f"Query string: {query_string}")

        # Generate signature
        signature = self._generate_signature(query_string)
        params["signature"] = signature

        print(f"Endpoint: {endpoint}")
        print(f"Params: {params}")
        print(f"Method: {method}")
        headers = self._get_headers()
        self.session.headers.update(headers)
        print(f"Headers: {headers}")

        url = f"{self.base_url}{endpoint}"
        print(f"URL: {url}")

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, params=params)
                logger.info(f"Response: {response.json()}")
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            logger.error(f"Error: {e.response}")
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    raise BinanceAPIError(
                        f"Binance API error: {error_data.get('msg', str(e))}",
                        error_data.get("code", -1),
                    )
                except ValueError:
                    pass
            raise BinanceAPIError(f"Request failed: {str(e)}")

    def _make_authenticated_request_with_list(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> List[Dict[str, Any]]:
        """Make authenticated request to Binance API"""
        if params is None:
            params = {}

        # Add timestamp
        params["timestamp"] = int(time.time() * 1000)

        # Create query string
        query_string = urlencode(params)

        # Generate signature
        signature = self._generate_signature(query_string)
        params["signature"] = signature

        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, data=params)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    raise BinanceAPIError(
                        f"Binance API error: {error_data.get('msg', str(e))}",
                        error_data.get("code", -1),
                    )
                except ValueError:
                    pass
            raise BinanceAPIError(f"Request failed: {str(e)}")

    def ping(self) -> Dict[str, Any]:
        """Test connectivity to the Rest API"""
        try:
            response = self.session.get(f"{self.base_url}/api/v3/ping")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ping request failed: {str(e)}")
            raise BinanceAPIError(f"Ping failed: {str(e)}")

    def get_server_time(self) -> Dict[str, Any]:
        """Test connectivity to the Rest API and get the current server time"""
        try:
            response = self.session.get(f"{self.base_url}/api/v3/time")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Server time request failed: {str(e)}")
            raise BinanceAPIError(f"Server time request failed: {str(e)}")

    def get_exchange_info(
        self,
        symbol: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        permissions: Optional[Union[str, List[str]]] = None,
        show_permission_sets: Optional[bool] = None,
        symbol_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get current exchange trading rules and symbol information

        Args:
            symbol: Optional[str] = None (default: None)
            symbols: Optional[List[str]] = None (default: None)
            permissions: Optional[Union[str, List[str]]] = None (default: None)
            show_permission_sets: Optional[bool] = None (default: None)
            symbol_status: Optional[str] = None (default: None)
        """
        params = {}

        if symbol:
            params["symbol"] = symbol.upper()
        elif symbols:
            params["symbols"] = [s.upper() for s in symbols]

        if permissions:
            if isinstance(permissions, str):
                params["permissions"] = permissions
            else:
                params["permissions"] = permissions

        if show_permission_sets is not None:
            params["showPermissionSets"] = str(show_permission_sets).lower()

        if symbol_status:
            params["symbolStatus"] = symbol_status

        try:
            response = self.session.get(
                f"{self.base_url}/api/v3/exchangeInfo", params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Exchange info request failed: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    raise BinanceAPIError(
                        f"Binance API error: {error_data.get('msg', str(e))}",
                        error_data.get("code", -1),
                    )
                except ValueError:
                    pass
            raise BinanceAPIError(f"Exchange info request failed: {str(e)}")

    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get symbol information"""
        exchange_info = self.get_exchange_info(symbol=symbol)

        if "symbols" in exchange_info and exchange_info["symbols"]:
            return exchange_info["symbols"][0]

        raise BinanceAPIError(f"Symbol {symbol} not found")
