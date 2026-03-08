"""
REST API views for placing orders via HTTP.
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pydantic import ValidationError

from bot.client import BinanceClient
from bot.orders import place_market_order, place_limit_order
from bot.models import OrderRecord

logger = logging.getLogger(__name__)


class PlaceOrderView(APIView):
    """
    POST /api/order/

    JSON body:
    {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "order_type": "MARKET",
        "quantity": 0.001,
        "price": 50000        // required for LIMIT
    }
    """

    def post(self, request):
        data = request.data
        symbol = data.get("symbol", "")
        side = data.get("side", "")
        order_type = data.get("order_type", "")
        quantity = data.get("quantity")
        price = data.get("price")

        try:
            quantity = float(quantity) if quantity is not None else 0
            price = float(price) if price is not None else None
        except (ValueError, TypeError):
            return Response(
                {"success": False, "error": "Invalid numeric value for quantity or price"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            client = BinanceClient()

            if order_type.upper() == "MARKET":
                result = place_market_order(client, symbol, side, quantity)
            elif order_type.upper() == "LIMIT":
                result = place_limit_order(client, symbol, side, quantity, price)
            else:
                return Response(
                    {
                        "success": False,
                        "error": f"Invalid order type '{order_type}'. Must be MARKET or LIMIT.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except ValidationError as exc:
            errors = [e["msg"] for e in exc.errors()]
            return Response(
                {"success": False, "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValueError as exc:
            return Response(
                {"success": False, "error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as exc:
            logger.error("API order failed  |  %s", exc)
            return Response(
                {"success": False, "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Persist to database
        try:
            resp = result["response"]
            OrderRecord.objects.create(
                symbol=symbol.upper(),
                side=side.upper(),
                order_type=order_type.upper(),
                quantity=quantity,
                price=price,
                order_id=resp.get("orderId"),
                status=resp.get("status", "UNKNOWN"),
                executed_qty=resp.get("executedQty", ""),
                avg_price=resp.get("avgPrice", ""),
                raw_response=resp,
            )
        except Exception as exc:
            logger.warning("Could not persist order record  |  %s", exc)

        return Response(result, status=status.HTTP_200_OK)
