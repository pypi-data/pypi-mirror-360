# fractrade-hl-simple

A simple Python wrapper for the Hyperliquid DEX API, focusing on perpetual futures trading. This library is yet in idea stage and not all features are available yet. We are using it for our own trading platform on fractrade.xyz and will add features as we need them.

⚠️ **Warning**: This is an early version of the library. Use with caution and test thoroughly before trading with real funds. Not all features are available yet. 

## Installation & Updates

Using pip:
```bash
# Install
pip install fractrade-hl-simple

# Update to latest version
pip install --upgrade fractrade-hl-simple
```

Using poetry:
```bash
# Install
poetry add fractrade-hl-simple

# Update to latest version
poetry update fractrade-hl-simple
```

⚠️ **Note**: This library is under active development. We recommend updating regularly to get the latest features and fixes.

## Logging Configuration

By default, the library uses Python's standard `logging` module. To see debug or info messages (for troubleshooting, order placement, API calls, etc.), configure logging in your script before using the client:

```python
import logging

# Show info-level logs from fractrade_hl_simple
logging.basicConfig(level=logging.INFO)

# For more detailed output (including debugging info), use:
# logging.basicConfig(level=logging.DEBUG)
```

You can place this at the top of your script or notebook.  
All logs from the library are under the `fractrade_hl_simple` logger.

## Setup

1. Create a `.env` file in your project root:
```env
HYPERLIQUID_ENV=testnet  # or mainnet
HYPERLIQUID_PUBLIC_ADDRESS=your_public_address
HYPERLIQUID_PRIVATE_KEY=your_private_key
```

We recommend creating a seperate API key wallet in the Hyperliquid UI for automated trading. This API wallets have not withdrawal permissions. 

2. Initialize the client:
```python
from fractrade_hl_simple import HyperliquidClient

client = HyperliquidClient()
```

## Authentication Modes

The client can operate in three modes:

### 1. Authenticated with Environment Variables (Default)
```python
from fractrade_hl_simple import HyperliquidClient

# Automatically loads credentials from .env
client = HyperliquidClient()
```

### 2. Authenticated with Explicit Account
```python
from fractrade_hl_simple import HyperliquidClient, HyperliquidAccount

account = HyperliquidAccount(
    private_key="your_private_key",
    env="mainnet",
    public_address="your_public_address"
)
client = HyperliquidClient(account=account)
```

### 3. Unauthenticated Mode
If no credentials are available, the client falls back to unauthenticated mode:
```python
# No .env file, no account provided
client = HyperliquidClient()  # Works for public endpoints only
```

### Public vs Private Endpoints

Some methods can be used without authentication:
```python
# These work without authentication
prices = client.get_price("BTC")
balance = client.get_perp_balance("0x123...")  # Requires address
state = client.get_user_state("0x123...")      # Requires address
market_info = client.get_market_info()
```

Methods that require authentication:
```python
# These require authentication
client.buy("BTC", 0.001)
client.sell("BTC", 0.001)
client.cancel_all()
client.get_positions()
balance = client.get_perp_balance()  # Without address requires auth
```

The client will automatically warn you when running in unauthenticated mode and help you understand which methods are available.

## Basic Usage

### Get Market Prices
```python
# Get single price
btc_price = client.get_price("BTC")
print(f"BTC price: ${btc_price:,.2f}")

# Get all prices
all_prices = client.get_price()
for symbol, price in all_prices.items():
    print(f"{symbol}: ${price:,.2f}")
```

### Get Market Info
```python
# Get info for all available markets
markets = client.get_market_info()
print(f"Available markets: {[m['name'] for m in markets]}")

# Get detailed info for a specific symbol
btc_info = client.get_market_info("BTC")
print("BTC market info:", btc_info)
```

### Get Funding Rates
```python
# Get all funding rates sorted from highest positive to lowest negative
funding_rates = client.get_funding_rates()
for rate_data in funding_rates:
    symbol = rate_data['symbol']
    rate = rate_data['funding_rate']
    print(f"{symbol}: {rate*100:.4f}%")

# Get funding rate for specific symbol
btc_rate = client.get_funding_rates("BTC")
print(f"BTC funding rate: {btc_rate*100:.4f}%")
```

### Get Order Book Data
```python
# Get complete order book for a symbol
order_book = client.get_order_book("BTC")
print(f"Best bid: ${order_book['best_bid']:,.2f}")
print(f"Best ask: ${order_book['best_ask']:,.2f}")
print(f"Spread: ${order_book['spread']:,.2f}")
print(f"Mid price: ${order_book['mid_price']:,.2f}")

# View top 5 bids and asks
print("\nTop 5 Bids:")
for i, bid in enumerate(order_book['bids'][:5]):
    print(f"  {i+1}. ${bid['price']:,.2f} - {bid['size']:.3f}")
    
print("\nTop 5 Asks:")
for i, ask in enumerate(order_book['asks'][:5]):
    print(f"  {i+1}. ${ask['price']:,.2f} - {ask['size']:.3f}")
```

### Get Optimal Limit Order Prices
```python
# Calculate optimal limit price based on urgency factor
# Urgency factor ranges from 0.0 (very patient) to 1.0 (very aggressive)

# Patient buy order (close to best bid)
patient_buy_price = client.get_optimal_limit_price("BTC", "buy", urgency_factor=0.1)
print(f"Patient buy price: ${patient_buy_price:,.2f}")

# Aggressive buy order (close to best ask)
aggressive_buy_price = client.get_optimal_limit_price("BTC", "buy", urgency_factor=0.9)
print(f"Aggressive buy price: ${aggressive_buy_price:,.2f}")

# Patient sell order (close to best ask)
patient_sell_price = client.get_optimal_limit_price("BTC", "sell", urgency_factor=0.1)
print(f"Patient sell price: ${patient_sell_price:,.2f}")

# Aggressive sell order (close to best bid)
aggressive_sell_price = client.get_optimal_limit_price("BTC", "sell", urgency_factor=0.9)
print(f"Aggressive sell price: ${aggressive_sell_price:,.2f}")
```

### Using the API Module (No Client Required)
You can also use the API module functions directly without creating a client:

```python
from fractrade_hl_simple import get_order_book, get_optimal_limit_price

# Get order book
order_book = get_order_book("BTC")
print(f"Spread: ${order_book['spread']:,.2f}")

# Get optimal price
optimal_price = get_optimal_limit_price("BTC", "buy", urgency_factor=0.5)
print(f"Optimal buy price: ${optimal_price:,.2f}")
```

### Check Account Balance
```python
balance = client.get_perp_balance()
print(f"Account balance: ${float(balance):,.2f}")
```

### View Positions
```python
positions = client.get_positions()
for pos in positions:
    print(f"Position: {pos.symbol} Size: {float(pos.size):+.3f}")
```

### Place Orders

Market Buy:
```python
order = client.buy("BTC", size=0.001)  # Market buy 0.001 BTC
print(f"Order placed: {order.order_id}")
```

Limit Buy:
```python
current_price = client.get_price("BTC")
limit_price = current_price * 0.99  # 1% below market
order = client.buy("BTC", size=0.001, limit_price=limit_price)
print(f"Limit order placed: {order.order_id}")
```

Market Sell:
```python
order = client.sell("BTC", size=0.001)  # Market sell 0.001 BTC
print(f"Order placed: {order.order_id}")
```

### Stop Loss and Take Profit

For Long Positions:
```python
# When you have a long position (bought BTC)
current_price = client.get_price("BTC")

# Place stop loss 5% below entry (sell when price drops)
stop_price = current_price * 0.95
sl_order = client.stop_loss("BTC", size=0.001, stop_price=stop_price)  # is_buy=False by default for long positions

# Place take profit 10% above entry (sell when price rises)
take_profit_price = current_price * 1.10
tp_order = client.take_profit("BTC", size=0.001, take_profit_price=take_profit_price)  # is_buy=False by default for long positions
```

For Short Positions:
```python
# When you have a short position (sold BTC)
current_price = client.get_price("BTC")

# Place stop loss 5% above entry (buy when price rises)
stop_price = current_price * 1.05
sl_order = client.stop_loss("BTC", size=0.001, stop_price=stop_price, is_buy=True)  # Must set is_buy=True for short positions

# Place take profit 10% below entry (buy when price drops)
take_profit_price = current_price * 0.90
tp_order = client.take_profit("BTC", size=0.001, take_profit_price=take_profit_price, is_buy=True)  # Must set is_buy=True for short positions
```

The `is_buy` parameter determines whether the TP/SL order will buy or sell when triggered:
- For long positions: use `is_buy=False` (default) to sell when triggered
- For short positions: use `is_buy=True` to buy when triggered

### Open Position with TP/SL

Alternatively, you can use the convenience methods that handle both entry and TP/SL orders:

Long Position:
```python
current_price = client.get_price("BTC")
position = client.open_long_position(
    symbol="BTC",
    size=0.001,
    stop_loss_price=current_price * 0.95,  # 5% below entry
    take_profit_price=current_price * 1.10  # 10% above entry
)
print(f"Entry order: {position['entry'].order_id}")
print(f"Stop loss: {position['stop_loss'].order_id}")
print(f"Take profit: {position['take_profit'].order_id}")
```

Short Position:
```python
current_price = client.get_price("BTC")
position = client.open_short_position(
    symbol="BTC",
    size=0.001,
    stop_loss_price=current_price * 1.05,  # 5% above entry
    take_profit_price=current_price * 0.90  # 10% below entry
)
```

These methods automatically set the correct `is_buy` parameter for TP/SL orders based on the position direction.

### Close Position
```python
close_order = client.close("BTC")
print(f"Position closed with order: {close_order.order_id}")
```

### Cancel Orders
```python
# Cancel orders for specific symbol
client.cancel_all_orders("BTC")

# Cancel all orders across all symbols
client.cancel_all()
```

## Complete Trading Example

Here's a full example showing a basic trading flow:

```python
from fractrade_hl_simple import HyperliquidClient
import time

def main():
    client = HyperliquidClient()
    SYMBOL = "BTC"
    POSITION_SIZE = 0.001
    
    try:
        # Check current price
        price = client.get_price(SYMBOL)
        print(f"Current {SYMBOL} price: ${price:,.2f}")
        
        # Place limit buy order
        limit_price = price * 0.99  # 1% below market
        order = client.buy(SYMBOL, POSITION_SIZE, limit_price=limit_price)
        print(f"Limit order placed: {order.order_id}")
        
        time.sleep(2)
        
        # Cancel limit order if not filled
        client.cancel_all_orders(SYMBOL)
        
        # Open market position
        order = client.buy(SYMBOL, POSITION_SIZE)
        print(f"Position opened with order: {order.order_id}")
        
        # Check position
        positions = client.get_positions()
        position = next((p for p in positions if p.symbol == SYMBOL), None)
        if position:
            print(f"Current position: {float(position.size):+.3f} {position.symbol}")
            print(f"Entry price: ${float(position.entry_price):,.2f}")
            print(f"Unrealized PnL: ${float(position.unrealized_pnl):,.2f}")
        
        # Close position
        close_order = client.close(SYMBOL)
        print(f"Position closed with order: {close_order.order_id}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        # Cleanup
        client.cancel_all_orders(SYMBOL)
        client.close(SYMBOL)

if __name__ == "__main__":
    main()
```


## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
MIT

## Disclaimer
This software is for educational purposes only. Use at your own risk. The authors take no responsibility for any financial losses incurred while using this software.
```
