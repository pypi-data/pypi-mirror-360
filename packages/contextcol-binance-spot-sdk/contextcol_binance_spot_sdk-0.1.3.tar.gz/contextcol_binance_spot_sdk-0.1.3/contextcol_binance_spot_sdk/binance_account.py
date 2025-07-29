"""
Binance Account API integration for ContextCol SDK
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class BinanceAccount:
    """Binance Account API client wrapper"""

    def __init__(self, binance_client):
        """Initialize account client with BinanceClient instance"""
        self.client = binance_client
        self.config = binance_client.config
        self.base_url = binance_client.base_url
        self.session = binance_client.session

    def _make_authenticated_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> Dict[str, Any]:
        """Make authenticated request using the main client"""
        return self.client._make_authenticated_request(endpoint, params, method)

    def _make_authenticated_request_with_list(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> List[Dict[str, Any]]:
        """Make authenticated request using the main client"""
        return self.client._make_authenticated_request_with_list(
            endpoint, params, method
        )

    # ========== ACCOUNT INFORMATION ==========

    def get_account_info(
        self,
        omit_zero_balances: bool = False,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get current account information (USER_DATA)
        GET /api/v3/account

        Args:
            omit_zero_balances: When set to true, emits only the non-zero balances
            recv_window: The value cannot be greater than 60000

        Returns:
            Account information including balances, permissions, and commission rates
        """
        params: Dict[str, Any] = {}
        if omit_zero_balances:
            params["omitZeroBalances"] = "true"
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request("/api/v3/account", params)
        logger.info(f"Binance Account Info: {result}")
        return result if isinstance(result, dict) else {}

    # ========== ORDER QUERIES ==========

    def get_order(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        orig_client_order_id: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Query order (USER_DATA)
        GET /api/v3/order

        Args:
            symbol: Trading symbol
            order_id: Order ID (either this or orig_client_order_id must be sent)
            orig_client_order_id: Original client order ID
            recv_window: The value cannot be greater than 60000

        Returns:
            Order information
        """
        if order_id is None and orig_client_order_id is None:
            raise ValueError("Either order_id or orig_client_order_id must be provided")

        params: Dict[str, Any] = {"symbol": symbol.upper()}
        if order_id is not None:
            params["orderId"] = str(order_id)
        if orig_client_order_id is not None:
            params["origClientOrderId"] = orig_client_order_id
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request("/api/v3/order", params)
        return result if isinstance(result, dict) else {}

    def get_open_orders(
        self,
        symbol: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all open orders on a symbol (USER_DATA)
        GET /api/v3/openOrders

        Args:
            symbol: Trading symbol (optional, if not sent returns all symbols)
            recv_window: The value cannot be greater than 60000

        Returns:
            List of open orders
        """
        params: Dict[str, Any] = {}
        if symbol is not None:
            params["symbol"] = symbol.upper()
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request_with_list(
            "/api/v3/openOrders", params
        )
        return result

    def get_all_orders(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500,
        recv_window: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all account orders; active, canceled, or filled (USER_DATA)
        GET /api/v3/allOrders

        Args:
            symbol: Trading symbol
            order_id: Order ID (if set, gets orders >= that orderId)
            start_time: Start time timestamp in ms
            end_time: End time timestamp in ms
            limit: Number of orders to return (default: 500, max: 1000)
            recv_window: The value cannot be greater than 60000

        Returns:
            List of all orders
        """
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "limit": str(limit),
        }
        if order_id is not None:
            params["orderId"] = str(order_id)
        if start_time is not None:
            params["startTime"] = str(start_time)
        if end_time is not None:
            params["endTime"] = str(end_time)
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request_with_list("/api/v3/allOrders", params)
        return result

    # ========== ORDER LIST QUERIES ==========

    def get_order_list(
        self,
        order_list_id: Optional[int] = None,
        orig_client_order_id: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Query Order list (USER_DATA)
        GET /api/v3/orderList

        Args:
            order_list_id: Order list ID (either this or orig_client_order_id must be provided)
            orig_client_order_id: Original client order ID
            recv_window: The value cannot be greater than 60000

        Returns:
            Order list information
        """
        if order_list_id is None and orig_client_order_id is None:
            raise ValueError(
                "Either order_list_id or orig_client_order_id must be provided"
            )

        params: Dict[str, Any] = {}
        if order_list_id is not None:
            params["orderListId"] = str(order_list_id)
        if orig_client_order_id is not None:
            params["origClientOrderId"] = orig_client_order_id
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request("/api/v3/orderList", params)
        return result if isinstance(result, dict) else {}

    def get_all_order_lists(
        self,
        from_id: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500,
        recv_window: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query all Order lists (USER_DATA)
        GET /api/v3/allOrderList

        Args:
            from_id: From ID (if supplied, neither startTime or endTime can be provided)
            start_time: Start time timestamp in ms
            end_time: End time timestamp in ms
            limit: Number of order lists to return (default: 500, max: 1000)
            recv_window: The value cannot be greater than 60000

        Returns:
            List of all order lists
        """
        params: Dict[str, Any] = {"limit": str(limit)}
        if from_id is not None:
            params["fromId"] = str(from_id)
        if start_time is not None:
            params["startTime"] = str(start_time)
        if end_time is not None:
            params["endTime"] = str(end_time)
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request_with_list(
            "/api/v3/allOrderList", params
        )
        return result

    def get_open_order_lists(
        self,
        recv_window: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query Open Order lists (USER_DATA)
        GET /api/v3/openOrderList

        Args:
            recv_window: The value cannot be greater than 60000

        Returns:
            List of open order lists
        """
        params: Dict[str, Any] = {}
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request_with_list(
            "/api/v3/openOrderList", params
        )
        return result

    # ========== TRADE HISTORY ==========

    def get_my_trades(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        from_id: Optional[int] = None,
        limit: int = 500,
        recv_window: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get trades for a specific account and symbol (USER_DATA)
        GET /api/v3/myTrades

        Args:
            symbol: Trading symbol
            order_id: Order ID (can only be used in combination with symbol)
            start_time: Start time timestamp in ms
            end_time: End time timestamp in ms
            from_id: Trade ID to fetch from (gets most recent trades if not set)
            limit: Number of trades to return (default: 500, max: 1000)
            recv_window: The value cannot be greater than 60000

        Returns:
            List of trades
        """
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "limit": str(limit),
        }
        if order_id is not None:
            params["orderId"] = str(order_id)
        if start_time is not None:
            params["startTime"] = str(start_time)
        if end_time is not None:
            params["endTime"] = str(end_time)
        if from_id is not None:
            params["fromId"] = str(from_id)
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request_with_list("/api/v3/myTrades", params)
        return result

    # ========== RATE LIMITS AND MONITORING ==========

    def get_unfilled_order_count(
        self,
        recv_window: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query Unfilled Order Count (USER_DATA)
        GET /api/v3/rateLimit/order

        Args:
            recv_window: The value cannot be greater than 60000

        Returns:
            List of unfilled order counts for all intervals
        """
        params: Dict[str, Any] = {}
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request_with_list(
            "/api/v3/rateLimit/order", params
        )
        return result

    def get_prevented_matches(
        self,
        symbol: str,
        prevented_match_id: Optional[int] = None,
        order_id: Optional[int] = None,
        from_prevented_match_id: Optional[int] = None,
        limit: int = 500,
        recv_window: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query Prevented Matches (USER_DATA)
        GET /api/v3/myPreventedMatches

        Args:
            symbol: Trading symbol
            prevented_match_id: Prevented match ID
            order_id: Order ID
            from_prevented_match_id: From prevented match ID
            limit: Number of matches to return (default: 500, max: 1000)
            recv_window: The value cannot be greater than 60000

        Returns:
            List of prevented matches
        """
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "limit": str(limit),
        }
        if prevented_match_id is not None:
            params["preventedMatchId"] = str(prevented_match_id)
        if order_id is not None:
            params["orderId"] = str(order_id)
        if from_prevented_match_id is not None:
            params["fromPreventedMatchId"] = str(from_prevented_match_id)
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request_with_list(
            "/api/v3/myPreventedMatches", params
        )
        return result

    def get_allocations(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        from_allocation_id: Optional[int] = None,
        limit: int = 500,
        order_id: Optional[int] = None,
        recv_window: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query Allocations (USER_DATA)
        GET /api/v3/myAllocations

        Args:
            symbol: Trading symbol
            start_time: Start time timestamp in ms
            end_time: End time timestamp in ms
            from_allocation_id: From allocation ID
            limit: Number of allocations to return (default: 500, max: 1000)
            order_id: Order ID
            recv_window: The value cannot be greater than 60000

        Returns:
            List of allocations
        """
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "limit": str(limit),
        }
        if start_time is not None:
            params["startTime"] = str(start_time)
        if end_time is not None:
            params["endTime"] = str(end_time)
        if from_allocation_id is not None:
            params["fromAllocationId"] = str(from_allocation_id)
        if order_id is not None:
            params["orderId"] = str(order_id)
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request_with_list(
            "/api/v3/myAllocations", params
        )
        return result

    def get_commission_rates(
        self,
        symbol: str,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Query Commission Rates (USER_DATA)
        GET /api/v3/account/commission

        Args:
            symbol: Trading symbol
            recv_window: The value cannot be greater than 60000

        Returns:
            Commission rates information
        """
        params: Dict[str, Any] = {"symbol": symbol.upper()}
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request("/api/v3/account/commission", params)
        return result if isinstance(result, dict) else {}

    def get_order_amendments(
        self,
        symbol: str,
        order_id: int,
        from_execution_id: Optional[int] = None,
        limit: int = 500,
        recv_window: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query Order Amendments (USER_DATA)
        GET /api/v3/order/amendments

        Args:
            symbol: Trading symbol
            order_id: Order ID7y6hgn bgm
            from_execution_id: From execution ID
            limit: Number of amendments to return (default: 500, max: 1000)
            recv_window: The value cannot be greater than 60000

        Returns:
            List of order amendments
        """
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "orderId": str(order_id),
            "limit": str(limit),
        }
        if from_execution_id is not None:
            params["fromExecutionId"] = str(from_execution_id)
        if recv_window is not None:
            params["recvWindow"] = str(recv_window)

        result = self._make_authenticated_request_with_list(
            "/api/v3/order/amendments", params
        )
        return result

    # ========== CONVENIENCE METHODS ==========

    def get_balance(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """
        Get account balance for specific asset or all assets

        Args:
            asset: Asset symbol (optional, if not provided returns all non-zero balances)

        Returns:
            Balance information
        """
        account_info = self.get_account_info(omit_zero_balances=True)
        balances = account_info.get("balances", [])

        if asset:
            for balance in balances:
                if balance["asset"] == asset.upper():
                    return balance
            return {
                "asset": asset.upper(),
                "free": "0.00000000",
                "locked": "0.00000000",
            }

        return {
            balance["asset"]: balance
            for balance in balances
            if float(balance["free"]) > 0 or float(balance["locked"]) > 0
        }

    def get_total_balance_in_btc(self) -> float:
        """
        Get total account balance converted to BTC

        Returns:
            Total balance in BTC
        """
        account_info = self.get_account_info()
        # This would need additional price conversion logic
        # For now, return 0 as placeholder
        logger.warning(
            "get_total_balance_in_btc not fully implemented - requires price conversion"
        )
        return 0.0

    def has_sufficient_balance(self, asset: str, amount: float) -> bool:
        """
        Check if account has sufficient balance for a given asset and amount

        Args:
            asset: Asset symbol
            amount: Required amount

        Returns:
            True if sufficient balance exists
        """
        balance = self.get_balance(asset)
        if isinstance(balance, dict) and "free" in balance:
            return float(balance["free"]) >= amount
        return False
