# Binance Futures Testnet Trading Bot

A Django-based Python application for placing **Market** and **Limit** orders on [Binance Futures Testnet](https://testnet.binancefuture.com) (USDT-M).

## Features

- **CLI interface** via Django management command (`python manage.py trade`)
- **REST API** endpoint (`POST /api/order/`)
- **Input validation** with Pydantic (symbol, side, type, quantity, price)
- **Structured logging** to `logs/trading_bot.log`
- **Order persistence** via Django ORM (`OrderRecord` model)
- **Django Admin** for browsing order history
- **Error handling** for invalid input, API errors, and network failures

## Project Structure

```
trading_bot/
├── manage.py                  # Django entry point
├── cli.py                     # Convenience CLI wrapper
├── requirements.txt
├── .env.example
├── trading_bot/               # Django settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── bot/                       # Trading logic app
│   ├── client.py              # Binance API wrapper
│   ├── orders.py              # Order placement logic
│   ├── validators.py          # Pydantic validation
│   ├── models.py              # OrderRecord model
│   ├── views.py               # REST API endpoint
│   ├── urls.py                # API routing
│   ├── admin.py               # Admin registration
│   └── management/commands/
│       └── trade.py           # CLI management command
└── logs/
    └── trading_bot.log
```

## Setup

### 1. Clone and install dependencies

```bash
cd trading_bot
pip install -r requirements.txt
```

### 2. Configure API credentials

```bash
cp .env.example .env
```

Edit `.env` and add your **Binance Futures Testnet** API keys.  
Get them at: https://testnet.binancefuture.com

### 3. Run database migrations

```bash
python manage.py migrate
```

## Usage

### CLI — Management Command

**Place a MARKET order:**
```bash
python manage.py trade --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Place a LIMIT order:**
```bash
python manage.py trade --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000
```

**Using the convenience wrapper:**
```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### REST API

Start the Django dev server:
```bash
python manage.py runserver
```

Place an order via HTTP:
```bash
curl -X POST http://127.0.0.1:8000/api/order/ \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "side": "BUY", "order_type": "MARKET", "quantity": 0.001}'
```

### Django Admin

```bash
python manage.py createsuperuser
python manage.py runserver
# Visit http://127.0.0.1:8000/admin/
```

## Example Output

### CLI — Successful MARKET Order

```
=======================================================
  ORDER REQUEST SUMMARY
=======================================================
  Symbol   : BTCUSDT
  Side     : BUY
  Type     : MARKET
  Quantity : 0.001
-------------------------------------------------------

=======================================================
  ORDER RESPONSE
=======================================================
  Order ID     : 123456789
  Status       : FILLED
  Type         : MARKET
  Side         : BUY
  Orig Qty     : 0.001
  Executed Qty : 0.001
  Avg Price    : 89500.00
-------------------------------------------------------
  ✓ Order placed successfully!
```

### CLI — Validation Error

```
  ✗ Validation error: Value error, Price is required for LIMIT orders. Use --price to specify.
```

## Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log` with the format:

```
2026-03-07 12:00:00,000 | INFO     | bot.client | ORDER REQUEST  |  params={...}
2026-03-07 12:00:01,000 | INFO     | bot.client | ORDER RESPONSE |  {...}
```

## Assumptions

- This bot targets **Binance Futures Testnet** only (not production)
- Uses `python-binance` library for API interaction with HMAC SHA256 authentication
- SQLite is used for order persistence (suitable for development/testing)
- The bot supports **MARKET** and **LIMIT** order types
- All orders are placed with `timeInForce=GTC` for LIMIT orders
- API credentials are loaded from `.env` file using `python-dotenv`

## Tech Stack

- Python 3.x
- Django 4.2
- Django REST Framework
- python-binance
- Pydantic 2.x
- python-dotenv
