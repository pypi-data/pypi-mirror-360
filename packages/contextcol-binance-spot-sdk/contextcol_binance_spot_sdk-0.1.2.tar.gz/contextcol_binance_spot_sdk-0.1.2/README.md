# ContextCol SDK

A comprehensive Python SDK for Binance trading with ContextCol API integration. This SDK provides seamless integration between Binance spot trading and ContextCol's trading bot analytics platform.

## Features

- **Binance Integration**: Complete Binance API wrapper with spot trading capabilities
- **Market Data API**: Comprehensive market data endpoints using requests directly
- **ContextCol API**: Full integration with ContextCol's trading bot activity tracking
- **Secure Configuration**: Environment-based configuration with validation
- **Comprehensive Error Handling**: Custom exceptions for different error scenarios
- **Type Hints**: Full type annotation support for better IDE experience
- **No External Dependencies**: Uses requests directly instead of outdated binance library

## Installation

```bash
pip install contextcol
```

## Quick Start

### Basic Setup

```python
from contextcol import ContextColClient

# Initialize with environment variables
client = ContextColClient()

# Or initialize with direct configuration
client = ContextColClient(
    binance_api_key="your_binance_api_key",
    binance_api_secret="your_binance_api_secret",
    contextcol_api_key="your_contextcol_api_key"
)
```

### Environment Variables

Create a `.env` file in your project root:

```env
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
BINANCE_TESTNET=false
CONTEXTCOL_API_KEY=your_contextcol_api_key
CONTEXTCOL_BASE_URL=https://api.contextcol.com
```

### Simple Trading Example

```python
from contextcol import ContextColClient

# Initialize client
client = ContextColClient()

# Execute a spot trade and log to ContextCol
result = client.execute_spot_trade(
    symbol="BTCUSDT",
    side="BUY",
    quantity="0.001",
    order_type="MARKET",
    test=True  # Use test mode first
)

print(f"Order result: {result['binance_order']}")
print(f"ContextCol log: {result['contextcol_log']}")
```

## API Reference

### ContextColClient

The main client class that provides access to all SDK functionality.

#### Trading Methods

```python
# Execute spot trade with ContextCol logging
client.execute_spot_trade(symbol, side, quantity, order_type="MARKET", price=None, test=False)

# Create trading bot activity
client.create_trading_bot_activity(activity_data)

# Test trading bot activity
client.test_trading_bot_activity(activity_id, test_data)
```

#### Binance Methods

```python
# Get account information
account_info = client.binance.get_account_info()

# Get account balance
balance = client.binance.get_balance("BTC")

# Create spot order
order = client.binance.create_spot_order("BTCUSDT", "BUY", "0.001")

# Get ticker price
price = client.binance.get_ticker_price("BTCUSDT")
```

#### Market Data Methods

```python
# Access market data client
market_data = client.binance.market_data

# Get order book
order_book = market_data.get_order_book("BTCUSDT", limit=100)

# Get recent trades
trades = market_data.get_recent_trades("BTCUSDT", limit=500)

# Get historical trades
historical_trades = market_data.get_historical_trades("BTCUSDT", limit=500)

# Get aggregate trades
agg_trades = market_data.get_aggregate_trades("BTCUSDT", limit=500)

# Get klines (candlestick data)
klines = market_data.get_klines("BTCUSDT", "1h", limit=100)

# Get UI klines (optimized for charts)
ui_klines = market_data.get_ui_klines("BTCUSDT", "1h", limit=100)

# Get average price
avg_price = market_data.get_avg_price("BTCUSDT")

# Get 24hr ticker statistics
ticker_24hr = market_data.get_24hr_ticker("BTCUSDT")

# Get trading day ticker
trading_day_ticker = market_data.get_trading_day_ticker("BTCUSDT")

# Get symbol price ticker
price_ticker = market_data.get_symbol_price_ticker("BTCUSDT")

# Get order book ticker
book_ticker = market_data.get_order_book_ticker("BTCUSDT")

# Get rolling window ticker
rolling_ticker = market_data.get_rolling_window_ticker("BTCUSDT", window_size="1d")
```

#### ContextCol API Methods

```python
# Create Binance spot transaction log
client.create_binance_spot_transaction(transaction_data)

# Test Binance spot transaction
client.test_binance_spot_transaction(transaction_data)

# Get trading analytics
analytics = client.get_trading_analytics(start_date="2024-01-01", end_date="2024-01-31")
```

## Configuration

### Config Class

```python
from contextcol import Config

# Create configuration
config = Config(
    binance_api_key="your_key",
    binance_api_secret="your_secret",
    contextcol_api_key="your_contextcol_key",
    binance_testnet=True,  # Use testnet
    timeout=30,
    max_retries=3
)

# Initialize client with config
client = ContextColClient(config=config)
```

### Configuration Options

| Parameter             | Type | Default                    | Description                |
| --------------------- | ---- | -------------------------- | -------------------------- |
| `binance_api_key`     | str  | None                       | Binance API key            |
| `binance_api_secret`  | str  | None                       | Binance API secret         |
| `binance_testnet`     | bool | False                      | Use Binance testnet        |
| `contextcol_api_key`  | str  | None                       | ContextCol API key         |
| `contextcol_base_url` | str  | https://api.contextcol.com | ContextCol API base URL    |
| `timeout`             | int  | 30                         | Request timeout in seconds |
| `max_retries`         | int  | 3                          | Maximum retry attempts     |

## Error Handling

The SDK provides comprehensive error handling with custom exceptions:

```python
from contextcol_binance_spot_sdk.exceptions import (
    ContextColError,
    APIError,
    ConfigError,
    BinanceAPIError,
    AuthenticationError,
    ValidationError
)

try:
    result = client.execute_spot_trade("BTCUSDT", "BUY", "0.001")
except BinanceAPIError as e:
    print(f"Binance API error: {e.message} (Code: {e.code})")
except APIError as e:
    print(f"ContextCol API error: {e} (Status: {e.status_code})")
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Advanced Usage

### Context Manager

```python
with ContextColClient() as client:
    # Your trading logic here
    result = client.execute_spot_trade("BTCUSDT", "BUY", "0.001")
    print(result)
# Client connections are automatically closed
```

### Validate Configuration

```python
client = ContextColClient()
validation_result = client.validate_configuration()

if validation_result['binance_connection']:
    print("Binance connection successful")
if validation_result['contextcol_connection']:
    print("ContextCol connection successful")

for error in validation_result['errors']:
    print(f"Error: {error}")
```

### Get Account Summary

```python
summary = client.get_account_summary()
print(f"Binance Account: {summary['binance_account']}")
print(f"ContextCol User: {summary['contextcol_user']}")
print(f"Recent Activities: {summary['recent_activities']}")
```

## ContextCol API Endpoints

The SDK supports all major ContextCol API endpoints:

- `POST /trading-bot-activity` - Create trading bot activity
- `POST /trading-bot-activity/:id/test` - Test trading bot activity
- `POST /binance/spot/transaction` - Create Binance spot transaction
- `POST /binance/spot/transaction/test` - Test Binance spot transaction

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact [khemmapich@gmail.com](mailto:khemmapich@gmail.com) or create an issue on GitHub.

## Changelog

### 0.1.0

- Initial release
- Binance API integration
- ContextCol API integration
- Comprehensive error handling
- Type hints support
- Configuration management
