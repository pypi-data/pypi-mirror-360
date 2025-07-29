"""
Binance Trading API integration for ContextCol SDK
"""

import logging
from typing import Dict, Any, Optional, List

from .exceptions import BinanceAPIError
from .contextcol_api import ContextcolAPI

logger = logging.getLogger(__name__)


class BinanceTrading:
    """Binance Trading API client wrapper"""

    def __init__(self, binance_client):
        """Initialize trading client with BinanceClient instance"""
        self.client = binance_client
        self.contextcol_api = ContextcolAPI(config=binance_client.config)
        self.config = binance_client.config
        self.base_url = binance_client.base_url
        self.session = binance_client.session
        self.binance_testnet = binance_client.binance_testnet
        logger.info(f"Binance Trading initialized with config: {self.config}")

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> Dict[str, Any]:
        """Make authenticated request using the main client"""
        return self.client._make_request(endpoint, params, method)

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

    # ========== SPOT TRADING ORDERS ==========

    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        timestamp: int,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        quote_order_qty: Optional[float] = None,
        time_in_force: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
        strategy_id: Optional[int] = None,
        strategy_type: Optional[int] = None,
        stop_price: Optional[float] = None,
        trailing_delta: Optional[int] = None,
        iceberg_qty: Optional[str] = None,
        new_order_resp_type: str = "FULL",
        self_trade_prevention_mode: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a new order (TRADE)
        POST /api/v3/order

        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            side: "BUY" or "SELL"
            order_type: Order type (LIMIT, MARKET, STOP_LOSS, etc.)
            quantity: Order quantity
            quote_order_qty: Quote order quantity (for MARKET orders)
            price: Order price (required for LIMIT orders)
            time_in_force: Time in force (GTC, IOC, FOK)
            new_client_order_id: Unique client order ID
            strategy_id: Strategy ID
            strategy_type: Strategy type (>= 1000000)
            stop_price: Stop price for stop orders
            trailing_delta: Trailing delta for trailing stop orders
            iceberg_qty: Iceberg quantity
            new_order_resp_type: Response type (ACK, RESULT, FULL)
            self_trade_prevention_mode: STP mode
            recv_window: Receive window

        Returns:
            Order response based on new_order_resp_type
        """

        print(f"Config: {self.config.binance_api_key}")
        print(f"Config: {self.config.binance_api_secret}")
        print(f"Testnet: {self.binance_testnet}")

        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "newOrderRespType": new_order_resp_type,
            "timestamp": timestamp,
        }

        if quantity is not None:
            params["quantity"] = quantity
        if quote_order_qty is not None:
            params["quoteOrderQty"] = quote_order_qty
        if price is not None:
            params["price"] = price
        if time_in_force is not None:
            params["timeInForce"] = time_in_force
        if new_client_order_id is not None:
            params["newClientOrderId"] = new_client_order_id
        if strategy_id is not None:
            params["strategyId"] = strategy_id
        if strategy_type is not None:
            params["strategyType"] = strategy_type
        if stop_price is not None:
            params["stopPrice"] = stop_price
        if trailing_delta is not None:
            params["trailingDelta"] = trailing_delta
        if iceberg_qty is not None:
            params["icebergQty"] = iceberg_qty
        if self_trade_prevention_mode is not None:
            params["selfTradePreventionMode"] = self_trade_prevention_mode
        if recv_window is not None:
            params["recvWindow"] = recv_window

        try:
            result = self._make_authenticated_request(
                "/api/v3/order", params, method="POST"
            )
            logger.info(f"Result: {result}")
            if isinstance(result, dict):
                if self.binance_testnet:
                    activity = self.contextcol_api.create_test_trading_bot_activity(
                        self.config.trading_bot_id,
                        {
                            "orderId": result["orderId"],
                            "name": "create_order",
                            "event": "create_order",
                            "data": params,
                            "type": "binance_spot_order",
                            "testTradingBotId": self.config.trading_bot_id,
                        },
                    )
                    self.contextcol_api.create_test_binance_spot_transaction(
                        {
                            "orderId": result["orderId"],
                            "symbol": symbol,
                            "side": side,
                            "type": order_type,
                            "quantity": quantity,
                            "price": price,
                            "timestamp": timestamp,
                            "request": params,
                            "response": result,
                            "tradingBotActivityId": activity["id"],
                            "tradingBotId": self.config.trading_bot_id,
                        },
                    )
                else:
                    activity = self.contextcol_api.create_trading_bot_activity(
                        {
                            "orderId": result["orderId"],
                            "name": "create_order",
                            "event": "create_order",
                            "data": params,
                            "type": "binance_spot_order",
                            "tradingBotId": self.config.trading_bot_id,
                        },
                    )
                    self.contextcol_api.create_binance_spot_transaction(
                        {
                            "orderId": result["orderId"],
                            "symbol": symbol,
                            "side": side,
                            "type": order_type,
                            "quantity": quantity,
                            "price": price,
                            "timestamp": timestamp,
                            "request": params,
                            "response": result,
                            "tradingBotActivityId": activity["id"],
                            "tradingBotId": self.config.trading_bot_id,
                        },
                    )
                return result
            else:
                raise BinanceAPIError("Unexpected response type")
        except Exception as e:
            raise BinanceAPIError(f"Failed to create order: {e}") from e

    def test_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Optional[str] = None,
        quote_order_qty: Optional[str] = None,
        price: Optional[str] = None,
        time_in_force: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
        strategy_id: Optional[int] = None,
        strategy_type: Optional[int] = None,
        stop_price: Optional[str] = None,
        trailing_delta: Optional[int] = None,
        iceberg_qty: Optional[str] = None,
        new_order_resp_type: str = "FULL",
        self_trade_prevention_mode: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Test new order creation (TRADE)
        POST /api/v3/order/test

        Args:
            Same as create_order, plus:
            compute_commission_rates: Whether to compute commission rates

        Returns:
            Empty dict or commission rates info
        """
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "newOrderRespType": new_order_resp_type,
        }

        # Add optional parameters (same as create_order)
        if quantity is not None:
            params["quantity"] = quantity
        if quote_order_qty is not None:
            params["quoteOrderQty"] = quote_order_qty
        if price is not None:
            params["price"] = price
        if time_in_force is not None:
            params["timeInForce"] = time_in_force
        if new_client_order_id is not None:
            params["newClientOrderId"] = new_client_order_id
        if strategy_id is not None:
            params["strategyId"] = strategy_id
        if strategy_type is not None:
            params["strategyType"] = strategy_type
        if stop_price is not None:
            params["stopPrice"] = stop_price
        if trailing_delta is not None:
            params["trailingDelta"] = trailing_delta
        if iceberg_qty is not None:
            params["icebergQty"] = iceberg_qty
        if self_trade_prevention_mode is not None:
            params["selfTradePreventionMode"] = self_trade_prevention_mode
        if recv_window is not None:
            params["recvWindow"] = recv_window

        return self._make_authenticated_request(
            "/api/v3/order/test", params, method="POST"
        )

    def cancel_order(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        orig_client_order_id: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
        cancel_restrictions: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Cancel an active order (TRADE)
        DELETE /api/v3/order

        Args:
            symbol: Trading symbol
            order_id: Order ID (either this or orig_client_order_id required)
            orig_client_order_id: Original client order ID
            new_client_order_id: New client order ID for cancellation
            cancel_restrictions: ONLY_NEW or ONLY_PARTIALLY_FILLED
            recv_window: Receive window

        Returns:
            Cancelled order information
        """
        params: Dict[str, Any] = {"symbol": symbol.upper()}

        if order_id is not None:
            params["orderId"] = order_id
        if orig_client_order_id is not None:
            params["origClientOrderId"] = orig_client_order_id
        if new_client_order_id is not None:
            params["newClientOrderId"] = new_client_order_id
        if cancel_restrictions is not None:
            params["cancelRestrictions"] = cancel_restrictions
        if recv_window is not None:
            params["recvWindow"] = recv_window

        if order_id is None and orig_client_order_id is None:
            raise ValueError("Either order_id or orig_client_order_id must be provided")

        result = self._make_authenticated_request(
            "/api/v3/order", params, method="DELETE"
        )
        if self.binance_testnet:
            self.contextcol_api.update_test_binance_spot_transaction(
                {
                    "orderId": result["orderId"],
                    "cancelRequest": params,
                    "cancelResponse": result,
                    "remark": "cancelOrder",
                },
            )
        else:
            self.contextcol_api.update_binance_spot_transaction(
                {
                    "orderId": result["orderId"],
                    "cancelRequest": params,
                    "cancelResponse": result,
                    "remark": "cancelOrder",
                },
            )
        return result

    def cancel_all_open_orders(
        self,
        symbol: str,
        recv_window: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Cancel all active orders on a symbol (TRADE)
        DELETE /api/v3/openOrders

        Args:
            symbol: Trading symbol
            recv_window: Receive window

        Returns:
            List of cancelled orders
        """
        params: Dict[str, Any] = {"symbol": symbol.upper()}

        if recv_window is not None:
            params["recvWindow"] = recv_window

        result = self._make_authenticated_request_with_list(
            "/api/v3/openOrders", params, method="DELETE"
        )
        for order in result:
            if self.binance_testnet:
                self.contextcol_api.update_test_binance_spot_transaction(
                    {
                        "orderId": order["orderId"],
                        "cancelRequest": params,
                        "cancelResponse": order,
                        "remark": "cancelAllOpenOrders",
                    },
                )
            else:
                self.contextcol_api.update_binance_spot_transaction(
                    {
                        "orderId": order["orderId"],
                        "cancelRequest": params,
                        "cancelResponse": order,
                        "remark": "cancelAllOpenOrders",
                    },
                )
        return result

    def cancel_replace_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        cancel_replace_mode: str,
        cancel_order_id: Optional[int] = None,
        cancel_orig_client_order_id: Optional[str] = None,
        cancel_new_client_order_id: Optional[str] = None,
        time_in_force: Optional[str] = None,
        quantity: Optional[str] = None,
        quote_order_qty: Optional[str] = None,
        price: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
        strategy_id: Optional[int] = None,
        strategy_type: Optional[int] = None,
        stop_price: Optional[str] = None,
        trailing_delta: Optional[int] = None,
        iceberg_qty: Optional[str] = None,
        new_order_resp_type: str = "FULL",
        self_trade_prevention_mode: Optional[str] = None,
        cancel_restrictions: Optional[str] = None,
        order_rate_limit_exceeded_mode: str = "DO_NOTHING",
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Cancel an existing order and send a new order (TRADE)
        POST /api/v3/order/cancelReplace

        Args:
            symbol: Trading symbol
            side: "BUY" or "SELL"
            order_type: Order type
            cancel_replace_mode: "STOP_ON_FAILURE" or "ALLOW_FAILURE"
            cancel_order_id: Order ID to cancel
            cancel_orig_client_order_id: Original client order ID to cancel
            cancel_new_client_order_id: New client order ID for cancellation
            ... (other parameters same as create_order)
            cancel_restrictions: ONLY_NEW or ONLY_PARTIALLY_FILLED
            order_rate_limit_exceeded_mode: "DO_NOTHING" or "CANCEL_ONLY"

        Returns:
            Cancel and replace operation result
        """
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "cancelReplaceMode": cancel_replace_mode,
            "orderRateLimitExceededMode": order_rate_limit_exceeded_mode,
        }

        # Cancel parameters
        if cancel_order_id is not None:
            params["cancelOrderId"] = cancel_order_id
        if cancel_orig_client_order_id is not None:
            params["cancelOrigClientOrderId"] = cancel_orig_client_order_id
        if cancel_new_client_order_id is not None:
            params["cancelNewClientOrderId"] = cancel_new_client_order_id
        if cancel_restrictions is not None:
            params["cancelRestrictions"] = cancel_restrictions

        # New order parameters
        if time_in_force is not None:
            params["timeInForce"] = time_in_force
        if quantity is not None:
            params["quantity"] = quantity
        if quote_order_qty is not None:
            params["quoteOrderQty"] = quote_order_qty
        if price is not None:
            params["price"] = price
        if new_client_order_id is not None:
            params["newClientOrderId"] = new_client_order_id
        if strategy_id is not None:
            params["strategyId"] = strategy_id
        if strategy_type is not None:
            params["strategyType"] = strategy_type
        if stop_price is not None:
            params["stopPrice"] = stop_price
        if trailing_delta is not None:
            params["trailingDelta"] = trailing_delta
        if iceberg_qty is not None:
            params["icebergQty"] = iceberg_qty
        if new_order_resp_type is not None:
            params["newOrderRespType"] = new_order_resp_type
        if self_trade_prevention_mode is not None:
            params["selfTradePreventionMode"] = self_trade_prevention_mode
        if recv_window is not None:
            params["recvWindow"] = recv_window

        if cancel_order_id is None and cancel_orig_client_order_id is None:
            raise ValueError(
                "Either cancel_order_id or cancel_orig_client_order_id must be provided"
            )

        result = self._make_authenticated_request(
            "/api/v3/order/cancelReplace", params, method="POST"
        )
        if self.binance_testnet:
            self.contextcol_api.update_test_binance_spot_transaction(
                {
                    "orderId": result["orderId"],
                    "cancelRequest": params,
                    "cancelResponse": result,
                    "remark": "cancelReplace",
                },
            )
        else:
            self.contextcol_api.update_binance_spot_transaction(
                {
                    "orderId": result["orderId"],
                    "cancelRequest": params,
                    "cancelResponse": result,
                    "remark": "cancelReplace",
                },
            )
        return result

    def amend_order_keep_priority(
        self,
        symbol: str,
        new_qty: str,
        order_id: Optional[int] = None,
        orig_client_order_id: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Reduce the quantity of an existing open order (TRADE)
        PUT /api/v3/order/amend/keepPriority

        Args:
            symbol: Trading symbol
            new_qty: New quantity (must be > 0 and < current quantity)
            order_id: Order ID (either this or orig_client_order_id required)
            orig_client_order_id: Original client order ID
            new_client_order_id: New client order ID after amendment
            recv_window: Receive window

        Returns:
            Amended order information
        """
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "newQty": new_qty,
        }

        if order_id is not None:
            params["orderId"] = order_id
        if orig_client_order_id is not None:
            params["origClientOrderId"] = orig_client_order_id
        if new_client_order_id is not None:
            params["newClientOrderId"] = new_client_order_id
        if recv_window is not None:
            params["recvWindow"] = recv_window

        if order_id is None and orig_client_order_id is None:
            raise ValueError("Either order_id or orig_client_order_id must be provided")

        return self._make_authenticated_request(
            "/api/v3/order/amend/keepPriority", params, method="PUT"
        )

    # ========== QUERY METHODS ==========

    def get_order_history(
        self,
        symbol: str,
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        recv_window: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get order history for a symbol
        GET /api/v3/allOrders

        Args:
            symbol: Trading symbol
            limit: Number of orders to return (max 1000)
            start_time: Start time filter
            end_time: End time filter
            recv_window: Receive window

        Returns:
            List of orders
        """
        params = {
            "symbol": symbol.upper(),
            "limit": limit,
        }

        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time
        if recv_window is not None:
            params["recvWindow"] = recv_window

        return self._make_authenticated_request_with_list("/api/v3/allOrders", params)

    def get_open_orders(
        self,
        symbol: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get open orders
        GET /api/v3/openOrders

        Args:
            symbol: Trading symbol (optional, if not provided returns all open orders)
            recv_window: Receive window

        Returns:
            List of open orders
        """
        params = {}

        if symbol is not None:
            params["symbol"] = symbol.upper()
        if recv_window is not None:
            params["recvWindow"] = recv_window

        return self._make_authenticated_request_with_list("/api/v3/openOrders", params)

    def get_order_status(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        orig_client_order_id: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get order status
        GET /api/v3/order

        Args:
            symbol: Trading symbol
            order_id: Order ID (either this or orig_client_order_id required)
            orig_client_order_id: Original client order ID
            recv_window: Receive window

        Returns:
            Order information
        """
        params: Dict[str, Any] = {"symbol": symbol.upper()}

        if order_id is not None:
            params["orderId"] = order_id
        if orig_client_order_id is not None:
            params["origClientOrderId"] = orig_client_order_id
        if recv_window is not None:
            params["recvWindow"] = recv_window

        if order_id is None and orig_client_order_id is None:
            raise ValueError("Either order_id or orig_client_order_id must be provided")

        return self._make_authenticated_request("/api/v3/order", params)

    # ========== CONVENIENCE METHODS ==========

    def buy_market(
        self,
        symbol: str,
        quantity: Optional[float] = None,
        quote_order_qty: Optional[float] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a market buy order

        Args:
            symbol: Trading symbol
            quantity: Quantity to buy
            quote_order_qty: Quote quantity to spend
            **kwargs: Additional parameters for create_order

        Returns:
            Order response
        """
        return self.create_order(
            symbol=symbol,
            side="BUY",
            order_type="MARKET",
            quantity=quantity,
            quote_order_qty=quote_order_qty,
            **kwargs,
        )

    def sell_market(self, symbol: str, quantity: float, **kwargs) -> Dict[str, Any]:
        """
        Create a market sell order

        Args:
            symbol: Trading symbol
            quantity: Quantity to sell
            **kwargs: Additional parameters for create_order

        Returns:
            Order response
        """
        return self.create_order(
            symbol=symbol, side="SELL", order_type="MARKET", quantity=quantity, **kwargs
        )

    def buy_limit(
        self,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a limit buy order

        Args:
            symbol: Trading symbol
            quantity: Quantity to buy
            price: Limit price
            time_in_force: Time in force
            **kwargs: Additional parameters for create_order

        Returns:
            Order response
        """
        return self.create_order(
            symbol=symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
            **kwargs,
        )

    def sell_limit(
        self,
        symbol: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a limit sell order

        Args:
            symbol: Trading symbol
            quantity: Quantity to sell
            price: Limit price
            time_in_force: Time in force
            **kwargs: Additional parameters for create_order

        Returns:
            Order response
        """
        return self.create_order(
            symbol=symbol,
            side="SELL",
            order_type="LIMIT",
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
            **kwargs,
        )

    def stop_loss(
        self, symbol: str, side: str, quantity: float, stop_price: float, **kwargs
    ) -> Dict[str, Any]:
        """
        Create a stop loss order

        Args:
            symbol: Trading symbol
            side: "BUY" or "SELL"
            quantity: Quantity
            stop_price: Stop price
            **kwargs: Additional parameters for create_order

        Returns:
            Order response
        """
        return self.create_order(
            symbol=symbol,
            side=side,
            order_type="STOP_LOSS",
            quantity=quantity,
            stop_price=stop_price,
            **kwargs,
        )

    def stop_loss_limit(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: str = "GTC",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a stop loss limit order

        Args:
            symbol: Trading symbol
            side: "BUY" or "SELL"
            quantity: Quantity
            price: Limit price
            stop_price: Stop price
            time_in_force: Time in force
            **kwargs: Additional parameters for create_order

        Returns:
            Order response
        """
        return self.create_order(
            symbol=symbol,
            side=side,
            order_type="STOP_LOSS_LIMIT",
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
            **kwargs,
        )

    def take_profit(
        self, symbol: str, side: str, quantity: float, stop_price: float, **kwargs
    ) -> Dict[str, Any]:
        """
        Create a take profit order

        Args:
            symbol: Trading symbol
            side: "BUY" or "SELL"
            quantity: Quantity
            stop_price: Stop price
            **kwargs: Additional parameters for create_order

        Returns:
            Order response
        """
        return self.create_order(
            symbol=symbol,
            side=side,
            order_type="TAKE_PROFIT",
            quantity=quantity,
            stop_price=stop_price,
            **kwargs,
        )

    def take_profit_limit(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: str = "GTC",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a take profit limit order

        Args:
            symbol: Trading symbol
            side: "BUY" or "SELL"
            quantity: Quantity
            price: Limit price
            stop_price: Stop price
            time_in_force: Time in force
            **kwargs: Additional parameters for create_order

        Returns:
            Order response
        """
        return self.create_order(
            symbol=symbol,
            side=side,
            order_type="TAKE_PROFIT_LIMIT",
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
            **kwargs,
        )

    # ========== SMART ORDER ROUTING (SOR) ==========

    def create_sor_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None,
        time_in_force: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
        strategy_id: Optional[int] = None,
        strategy_type: Optional[int] = None,
        iceberg_qty: Optional[str] = None,
        new_order_resp_type: str = "FULL",
        self_trade_prevention_mode: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a new order using Smart Order Routing (SOR) (TRADE)
        POST /api/v3/sor/order

        Args:
            symbol: Trading symbol
            side: "BUY" or "SELL"
            order_type: "LIMIT" or "MARKET"
            quantity: Order quantity
            price: Order price (for LIMIT orders)
            time_in_force: Time in force (for LIMIT orders)
            new_client_order_id: Unique client order ID
            strategy_id: Strategy ID
            strategy_type: Strategy type (>= 1000000)
            iceberg_qty: Iceberg quantity (for LIMIT orders)
            new_order_resp_type: Response type (ACK, RESULT, FULL)
            self_trade_prevention_mode: STP mode
            recv_window: Receive window

        Returns:
            SOR order response
        """
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity,
            "newOrderRespType": new_order_resp_type,
        }

        if price is not None:
            params["price"] = price
        if time_in_force is not None:
            params["timeInForce"] = time_in_force
        if new_client_order_id is not None:
            params["newClientOrderId"] = new_client_order_id
        if strategy_id is not None:
            params["strategyId"] = strategy_id
        if strategy_type is not None:
            params["strategyType"] = strategy_type
        if iceberg_qty is not None:
            params["icebergQty"] = iceberg_qty
        if self_trade_prevention_mode is not None:
            params["selfTradePreventionMode"] = self_trade_prevention_mode
        if recv_window is not None:
            params["recvWindow"] = recv_window

        result = self._make_authenticated_request(
            "/api/v3/sor/order", params, method="POST"
        )

        if self.binance_testnet:
            activity = self.contextcol_api.create_test_trading_bot_activity(
                self.config.trading_bot_id,
                {
                    "name": "create_sor_order",
                    "event": "create_sor_order",
                    "data": params,
                    "type": "binance_spot_order",
                    "testTradingBotId": self.config.trading_bot_id,
                },
            )
            self.contextcol_api.create_test_binance_spot_transaction(
                {
                    "symbol": symbol,
                    "side": side,
                    "type": order_type,
                    "quantity": quantity,
                    "price": price,
                    "timeInForce": time_in_force,
                    "newClientOrderId": new_client_order_id,
                    "strategyId": strategy_id,
                    "strategyType": strategy_type,
                    "icebergQty": iceberg_qty,
                    "selfTradePreventionMode": self_trade_prevention_mode,
                    "recvWindow": recv_window,
                    "request": params,
                    "response": result,
                    "tradingBotActivityId": activity["id"],
                    "tradingBotId": self.config.trading_bot_id,
                },
            )
        else:
            activity = self.contextcol_api.create_trading_bot_activity(
                {
                    "name": "create_sor_order",
                    "event": "create_sor_order",
                    "data": params,
                    "type": "binance_spot_order",
                    "tradingBotId": self.config.trading_bot_id,
                },
            )
            self.contextcol_api.create_binance_spot_transaction(
                {
                    "symbol": symbol,
                    "side": side,
                    "type": order_type,
                    "quantity": quantity,
                    "price": price,
                    "timeInForce": time_in_force,
                    "newClientOrderId": new_client_order_id,
                    "strategyId": strategy_id,
                    "strategyType": strategy_type,
                    "icebergQty": iceberg_qty,
                    "selfTradePreventionMode": self_trade_prevention_mode,
                    "recvWindow": recv_window,
                    "request": params,
                    "response": result,
                    "tradingBotActivityId": activity["id"],
                    "tradingBotId": self.config.trading_bot_id,
                },
            )
        return result

    def test_sor_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None,
        time_in_force: Optional[str] = None,
        new_client_order_id: Optional[str] = None,
        strategy_id: Optional[int] = None,
        strategy_type: Optional[int] = None,
        iceberg_qty: Optional[str] = None,
        new_order_resp_type: str = "FULL",
        self_trade_prevention_mode: Optional[str] = None,
        recv_window: Optional[int] = None,
        compute_commission_rates: bool = False,
    ) -> Dict[str, Any]:
        """
        Test new order creation using Smart Order Routing (SOR) (TRADE)
        POST /api/v3/sor/order/test

        Args:
            Same as create_sor_order, plus:
            compute_commission_rates: Whether to compute commission rates

        Returns:
            Empty dict or commission rates info
        """
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity,
            "newOrderRespType": new_order_resp_type,
            "computeCommissionRates": compute_commission_rates,
        }

        if price is not None:
            params["price"] = price
        if time_in_force is not None:
            params["timeInForce"] = time_in_force
        if new_client_order_id is not None:
            params["newClientOrderId"] = new_client_order_id
        if strategy_id is not None:
            params["strategyId"] = strategy_id
        if strategy_type is not None:
            params["strategyType"] = strategy_type
        if iceberg_qty is not None:
            params["icebergQty"] = iceberg_qty
        if self_trade_prevention_mode is not None:
            params["selfTradePreventionMode"] = self_trade_prevention_mode
        if recv_window is not None:
            params["recvWindow"] = recv_window

        return self._make_authenticated_request(
            "/api/v3/sor/order/test", params, method="POST"
        )

    # ========== CONVENIENCE METHODS FOR SOR ==========

    def sor_buy_market(self, symbol: str, quantity: str, **kwargs) -> Dict[str, Any]:
        """
        Create a market buy order using SOR

        Args:
            symbol: Trading symbol
            quantity: Quantity to buy
            **kwargs: Additional parameters

        Returns:
            SOR order response
        """
        return self.create_sor_order(
            symbol=symbol, side="BUY", order_type="MARKET", quantity=quantity, **kwargs
        )

    def sor_sell_market(self, symbol: str, quantity: str, **kwargs) -> Dict[str, Any]:
        """
        Create a market sell order using SOR

        Args:
            symbol: Trading symbol
            quantity: Quantity to sell
            **kwargs: Additional parameters

        Returns:
            SOR order response
        """
        return self.create_sor_order(
            symbol=symbol, side="SELL", order_type="MARKET", quantity=quantity, **kwargs
        )

    def sor_buy_limit(
        self,
        symbol: str,
        quantity: str,
        price: str,
        time_in_force: str = "GTC",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a limit buy order using SOR

        Args:
            symbol: Trading symbol
            quantity: Quantity to buy
            price: Limit price
            time_in_force: Time in force
            **kwargs: Additional parameters

        Returns:
            SOR order response
        """
        return self.create_sor_order(
            symbol=symbol,
            side="BUY",
            order_type="LIMIT",
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
            **kwargs,
        )

    def sor_sell_limit(
        self,
        symbol: str,
        quantity: str,
        price: str,
        time_in_force: str = "GTC",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a limit sell order using SOR

        Args:
            symbol: Trading symbol
            quantity: Quantity to sell
            price: Limit price
            time_in_force: Time in force
            **kwargs: Additional parameters

        Returns:
            SOR order response
        """
        return self.create_sor_order(
            symbol=symbol,
            side="SELL",
            order_type="LIMIT",
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
            **kwargs,
        )
