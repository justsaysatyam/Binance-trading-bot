"""
Django management command — CLI entry point for placing orders.

Usage:
    python manage.py trade --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
    python manage.py trade --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from pydantic import ValidationError

from bot.client import BinanceClient
from bot.orders import place_market_order, place_limit_order
from bot.validators import OrderParams
from bot.models import OrderRecord

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Place an order on Binance Futures Testnet"

    def add_arguments(self, parser):
        parser.add_argument(
            "--symbol",
            type=str,
            required=True,
            help="Trading pair symbol (e.g. BTCUSDT)",
        )
        parser.add_argument(
            "--side",
            type=str,
            required=True,
            help="Order side: BUY or SELL",
        )
        parser.add_argument(
            "--type",
            type=str,
            required=True,
            dest="order_type",
            help="Order type: MARKET or LIMIT",
        )
        parser.add_argument(
            "--quantity",
            type=float,
            required=True,
            help="Order quantity",
        )
        parser.add_argument(
            "--price",
            type=float,
            default=None,
            help="Order price (required for LIMIT orders)",
        )

    def handle(self, *args, **options):
        symbol = options["symbol"]
        side = options["side"]
        order_type = options["order_type"]
        quantity = options["quantity"]
        price = options["price"]

        # ── Step 1: Validate inputs FIRST ──────────────────────────────
        try:
            params = OrderParams(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
            )
        except ValidationError as exc:
            self.stderr.write("")
            for error in exc.errors():
                msg = error["msg"]
                self.stderr.write(self.style.ERROR(f"  ✗ Validation error: {msg}"))
            self.stderr.write("")
            logger.error("Validation failed  |  %s", exc)
            return

        # ── Step 2: Print request summary ──────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("=" * 55))
        self.stdout.write(self.style.HTTP_INFO("  ORDER REQUEST SUMMARY"))
        self.stdout.write(self.style.HTTP_INFO("=" * 55))
        self.stdout.write(f"  Symbol   : {params.symbol}")
        self.stdout.write(f"  Side     : {params.side}")
        self.stdout.write(f"  Type     : {params.order_type}")
        self.stdout.write(f"  Quantity : {params.quantity}")
        if params.price is not None:
            self.stdout.write(f"  Price    : {params.price}")
        self.stdout.write(self.style.HTTP_INFO("-" * 55))
        self.stdout.write("")

        # ── Step 3: Create client and place order ──────────────────────
        try:
            client = BinanceClient()

            if params.order_type == "MARKET":
                result = place_market_order(
                    client, params.symbol, params.side, params.quantity
                )
            else:
                result = place_limit_order(
                    client, params.symbol, params.side,
                    params.quantity, params.price,
                )

        except ValueError as exc:
            self.stderr.write(self.style.ERROR(f"  ✗ {exc}"))
            logger.error("Value error  |  %s", exc)
            return

        except Exception as exc:
            self.stderr.write(
                self.style.ERROR(f"  ✗ Order failed: {exc}")
            )
            logger.error("Order failed  |  %s", exc)
            return

        # ── Step 4: Save to database ──────────────────────────────────
        try:
            resp = result["response"]
            OrderRecord.objects.create(
                symbol=params.symbol,
                side=params.side,
                order_type=params.order_type,
                quantity=params.quantity,
                price=params.price,
                order_id=resp.get("orderId"),
                status=resp.get("status", "UNKNOWN"),
                executed_qty=resp.get("executedQty", ""),
                avg_price=resp.get("avgPrice", ""),
                raw_response=resp,
            )
        except Exception as exc:
            logger.warning("Could not persist order record  |  %s", exc)

        # ── Step 5: Print response details ────────────────────────────
        resp = result["response"]
        self.stdout.write(self.style.SUCCESS("=" * 55))
        self.stdout.write(self.style.SUCCESS("  ORDER RESPONSE"))
        self.stdout.write(self.style.SUCCESS("=" * 55))
        self.stdout.write(f"  Order ID     : {resp.get('orderId')}")
        self.stdout.write(f"  Status       : {resp.get('status')}")
        self.stdout.write(f"  Type         : {resp.get('type')}")
        self.stdout.write(f"  Side         : {resp.get('side')}")
        self.stdout.write(f"  Orig Qty     : {resp.get('origQty')}")
        self.stdout.write(f"  Executed Qty : {resp.get('executedQty')}")
        self.stdout.write(f"  Avg Price    : {resp.get('avgPrice', 'N/A')}")
        self.stdout.write(self.style.SUCCESS("-" * 55))
        self.stdout.write(
            self.style.SUCCESS("  [OK] Order placed successfully!")
        )
        self.stdout.write("")
