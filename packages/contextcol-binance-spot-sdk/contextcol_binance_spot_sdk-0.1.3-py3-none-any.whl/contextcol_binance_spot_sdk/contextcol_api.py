"""
ContextCol API integration for ContextCol SDK
"""

import logging
import time
from typing import Dict, Any, Optional
import requests
from .config import Config
from .exceptions import APIError, AuthenticationError

logger = logging.getLogger(__name__)


class ContextcolAPI:
    """Contextcol API client"""

    def __init__(self, config: Config):
        """Initialize Contextcol API client"""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "contextcol-binance-spot-sdk/0.1.0",
            }
        )
        self._setup_session()

    def _setup_session(self):
        """Setup HTTP session with authentication"""
        self.config.validate_required_for_contextcol()

        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.config.contextcol_api_key}",
                "Content-Type": "application/json",
                "User-Agent": "contextcol-binance-spot-sdk/0.1.0",
            }
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = f"{self.config.contextcol_base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        headers = self.session.headers
        headers["Authorization"] = f"Bearer a23538a1-7624-4604-8ebf-f84ced2b6532"
        self.session.headers.update(headers)
        logger.info(f"Headers: {headers}")

        for attempt in range(self.config.max_retries + 1):
            try:
                logger.info(f"ContextCol API Request: {method} {url} {data} {params}")
                response = self.session.request(
                    method=method, url=url, json=data, params=params
                )
                logger.info(f"ContextCol API Response: {response.json()}")

                if response.status_code == 401:
                    raise AuthenticationError("Invalid or expired API key")

                if response.status_code >= 400:
                    error_data = (
                        response.json()
                        if response.headers.get("content-type", "").startswith(
                            "application/json"
                        )
                        else {"error": response.text}
                    )
                    raise APIError(
                        f"API request failed: {error_data.get('error', 'Unknown error')}",
                        status_code=response.status_code,
                        response=error_data,
                    )

                return (
                    response.json()
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else {"status": "success", "data": response.text}
                )

            except requests.RequestException as e:
                logger.error(f"Request failed from ContextCol API {url}: {e}")
                if attempt == self.config.max_retries:
                    raise APIError(
                        f"Request failed after {self.config.max_retries} retries: {str(e)}"
                    )

                # Wait before retry (exponential backoff)
                wait_time = (2**attempt) * 1
                logger.warning(
                    f"Request failed, retrying in {wait_time} seconds... (attempt {attempt + 1})"
                )
                time.sleep(wait_time)

        raise APIError("Max retries exceeded")

    def create_trading_bot_activity(
        self, activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create trading bot activity

        Args:
            activity_data: Dict[str, Any]
                - name: string
                - event: string
                - data: dict
                - type: string
                - tradingBotId: string

        Returns:
            Dict[str, Any]
        """
        return self._make_request("POST", "/trading-bot-activity", data=activity_data)

    def create_test_trading_bot_activity(
        self, test_trading_bot_id: str, activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Test trading bot activity

        Args:
            test_trading_bot_id: string
            activity_data: Dict[str, Any]
                - name: string
                - event: string
                - data: dict
                - type: string
                - testTradingBotId: string

        Returns:
            Dict[str, Any]
        """
        return self._make_request(
            "POST",
            f"/trading-bot-activity/{test_trading_bot_id}/test",
            data=activity_data,
        )

    def create_binance_spot_transaction(
        self, transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create Binance spot transaction

        Args:
            transaction_data: Dict[str, Any]
                    - orderId: string (optional)
                    - symbol: string
                    - side: string
                    - type: string
                    - quantity: number
                    - price: number (optional)
                    - timestamp: number
                    - request: object (optional)
                    - response: object (optional)
                    - cancelRequest: object (optional)
                    - cancelResponse: object (optional)
                    - signalId: string (optional)
                    - tradingBotActivityId: string (optional)
                    - tradingBotId: string (optional)
                    - remark: string (optional)
        """
        return self._make_request(
            "POST", "/binance/spot/transaction", data=transaction_data
        )

    def create_test_binance_spot_transaction(
        self, transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Test Binance spot transaction

        Args:
            transaction_data: Dict[str, Any]
                - orderId: string (optional)
                - symbol: string
                - side: string
                - type: string
                - quantity: number
                - price: number (optional)
                - timestamp: number
                - request: object (optional)
                - response: object (optional)
                - cancelRequest: object (optional)
                - cancelResponse: object (optional)
                - testSignalId: string (optional)
                - testTradingBotActivityId: string (optional)
                - testTradingBotId: string (optional)
                - remark: string (optional)
        """
        return self._make_request(
            "POST", "/binance/spot/transaction/test", data=transaction_data
        )

    # def get_health(self) -> Dict[str, Any]:
    #     """Get API health status"""
    #     return self._make_request("GET", "/health")

    def update_trading_bot_activity(
        self, activity_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update trading bot activity

        Args:
            activity_id: string
            update_data: Dict[str, Any]
                - name: string
                - event: string
                - data: dict
                - type: string
                - tradingBotId: string
        """
        return self._make_request(
            "PUT", f"/trading-bot-activity/{activity_id}", data=update_data
        )

    def update_test_trading_bot_activity(
        self, activity_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update trading bot activity

        Args:
            activity_id: string
            update_data: Dict[str, Any]
                - name: string
                - event: string
                - data: dict
                - type: string
                - testTradingBotId: string
        """
        return self._make_request(
            "PUT", f"/trading-bot-activity/{activity_id}/test", data=update_data
        )

    def update_binance_spot_transaction(
        self, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update Binance spot transaction

        Args:
            update_data: Dict[str, Any]
                - orderId: string (optional)
                - symbol: string
                - side: string
                - type: string
                - quantity: number
                - price: number (optional)
                - timestamp: number
                - request: object (optional)
                - response: object (optional)
                - cancelRequest: object (optional)
                - cancelResponse: object (optional)
                - signalId: string (optional)
                - tradingBotActivityId: string (optional)
                - tradingBotId: string (optional)
                - remark: string (optional)
        """
        return self._make_request("PUT", f"/binance/spot/transaction", data=update_data)

    def update_test_binance_spot_transaction(
        self, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update Binance spot transaction

        Args:
            update_data: Dict[str, Any]
                - orderId: string (optional)
                - symbol: string
                - side: string
                - type: string
                - quantity: number
                - price: number (optional)
                - timestamp: number
                - request: object (optional)
                - response: object (optional)
                - cancelRequest: object (optional)
                - cancelResponse: object (optional)
                - testSignalId: string (optional)
                - testTradingBotActivityId: string (optional)
                - testTradingBotId: string (optional)
                - remark: string (optional)
        """
        return self._make_request(
            "PUT", f"/binance/spot/transaction/test", data=update_data
        )

    def validate_api_key(self) -> Dict[str, Any]:
        """Validate API key"""
        return self._make_request("GET", "/validate")

    def close(self):
        """Close the HTTP session"""
        self.session.close()
