"""
Order placement logic.

Provides high-level functions to place MARKET and LIMIT orders
through the BinanceClient, with validation and structured output.
"""

import logging
from bot.client import BinanceClient
from bot.validators import OrderParams

logger = logging.getLogger(__name__)


def _format_result(order_params: OrderParams, response: dict) -> dict:
    """Build a unified result dict from order params + API response."""
    return {
        "request": {
            "symbol": order_params.symbol,
            "side": order_params.side,
            "type": order_params.order_type,
            "quantity": order_params.quantity,
            "price": order_params.price,
        },
        "response": {
            "orderId": response.get("orderId"),
            "status": response.get("status"),
            "executedQty": response.get("executedQty"),
            "avgPrice": response.get("avgPrice", "N/A"),
            "origQty": response.get("origQty"),
            "type": response.get("type"),
            "side": response.get("side"),
        },
        "success": True,
    }


def place_market_order(
    client: BinanceClient, symbol: str, side: str, quantity: float
) -> dict:
    """
    Place a MARKET order on Binance Futures Testnet.

    Returns a structured result dict with request summary and response details.
    """
    params = OrderParams(
        symbol=symbol, side=side, order_type="MARKET", quantity=quantity
    )

    logger.info(
        "Placing MARKET order  |  symbol=%s  side=%s  qty=%s",
        params.symbol,
        params.side,
        params.quantity,
    )

    response = client.create_order(
        symbol=params.symbol,
        side=params.side,
        type="MARKET",
        quantity=str(params.quantity),
    )

    return _format_result(params, response)


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
) -> dict:
    """
    Place a LIMIT order on Binance Futures Testnet.

    Returns a structured result dict with request summary and response details.
    """
    params = OrderParams(
        symbol=symbol,
        side=side,
        order_type="LIMIT",
        quantity=quantity,
        price=price,
    )

    logger.info(
        "Placing LIMIT order  |  symbol=%s  side=%s  qty=%s  price=%s",
        params.symbol,
        params.side,
        params.quantity,
        params.price,
    )

    response = client.create_order(
        symbol=params.symbol,
        side=params.side,
        type="LIMIT",
        timeInForce="GTC",
        quantity=str(params.quantity),
        price=str(params.price),
    )

    return _format_result(params, response)
