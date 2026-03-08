"""
Binance Futures Testnet client wrapper.

Handles authentication, API calls, and error handling for the
Binance Futures Testnet REST API using python-binance.

When MOCK_TRADING=true in .env, all API calls return realistic
simulated responses so the bot works fully offline for educational use.
"""

import logging
import random
import time

from django.conf import settings

logger = logging.getLogger(__name__)

# Check whether mock mode is enabled (for educational / offline use)
MOCK_MODE = getattr(settings, "MOCK_TRADING", False)


class BinanceClient:
    """Wrapper around python-binance Client for Futures Testnet."""

    def __init__(self):
        api_key = settings.BINANCE_API_KEY
        api_secret = settings.BINANCE_API_SECRET

        if MOCK_MODE:
            self.client = None
            logger.info(
                "BinanceClient initialised in MOCK mode  "
                "(no real API calls will be made)"
            )
            return

        # Real mode — requires python-binance
        from binance.client import Client  # noqa: E402

        if not api_key or not api_secret:
            raise ValueError(
                "API keys must be set. Copy .env.example to .env and "
                "add your Binance Futures Testnet credentials."
            )

        self.client = Client(api_key, api_secret, testnet=True)
        self.client.FUTURES_URL = settings.BINANCE_BASE_URL + "/fapi"

        logger.info(
            "BinanceClient initialised  |  base_url=%s",
            settings.BINANCE_BASE_URL,
        )

    # ── Order placement ────────────────────────────────────────────────

    def create_order(self, **params) -> dict:
        """
        Place a futures order on Binance Testnet.

        In MOCK mode this returns a realistic simulated response.
        """
        logger.info("ORDER REQUEST  |  params=%s", params)

        if MOCK_MODE:
            response = self._mock_order_response(params)
            logger.info("MOCK ORDER RESPONSE |  %s", response)
            return response

        # Real API call
        from binance.exceptions import (  # noqa: E402
            BinanceAPIException,
            BinanceRequestException,
        )

        try:
            response = self.client.futures_create_order(**params)
            logger.info("ORDER RESPONSE |  %s", response)
            return response

        except BinanceAPIException as exc:
            logger.error(
                "Binance API error  |  code=%s  msg=%s", exc.code, exc.message
            )
            raise
        except BinanceRequestException as exc:
            logger.error("Binance request error  |  %s", exc)
            raise
        except Exception as exc:
            logger.error("Unexpected error during order  |  %s", exc)
            raise

    # ── Exchange info ──────────────────────────────────────────────────

    def get_exchange_info(self) -> dict:
        """Fetch futures exchange info (for symbol validation)."""
        if MOCK_MODE:
            return self._mock_exchange_info()
        return self.client.futures_exchange_info()

    # ── Mock helpers (educational mode) ────────────────────────────────

    @staticmethod
    def _mock_order_response(params: dict) -> dict:
        """Generate a realistic Binance-style order response."""
        order_id = random.randint(100_000_000, 999_999_999)
        timestamp = int(time.time() * 1000)
        symbol = params.get("symbol", "BTCUSDT")
        side = params.get("side", "BUY")
        order_type = params.get("type", "MARKET")
        quantity = params.get("quantity", "0.001")

        # Simulate a realistic price for common pairs
        mock_prices = {
            "BTCUSDT": 87350.50,
            "ETHUSDT": 2150.75,
            "BNBUSDT": 610.20,
            "SOLUSDT": 135.40,
            "XRPUSDT": 2.35,
            "DOGEUSDT": 0.185,
            "ADAUSDT": 0.92,
        }
        price_val = params.get("price") or str(
            mock_prices.get(symbol, 100.00)
        )

        return {
            "orderId": order_id,
            "symbol": symbol,
            "status": "FILLED" if order_type == "MARKET" else "NEW",
            "clientOrderId": f"mock_{order_id}",
            "price": str(price_val),
            "avgPrice": str(price_val),
            "origQty": str(quantity),
            "executedQty": str(quantity) if order_type == "MARKET" else "0",
            "cumQuote": "0",
            "timeInForce": params.get("timeInForce", "GTC"),
            "type": order_type,
            "side": side,
            "updateTime": timestamp,
            "workingType": "CONTRACT_PRICE",
            "activatePrice": None,
            "priceRate": None,
        }

    @staticmethod
    def _mock_exchange_info() -> dict:
        """Return minimal mock exchange info with common symbols."""
        symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
            "XRPUSDT", "DOGEUSDT", "ADAUSDT",
        ]
        return {
            "timezone": "UTC",
            "serverTime": int(time.time() * 1000),
            "symbols": [
                {
                    "symbol": s,
                    "status": "TRADING",
                    "baseAsset": s.replace("USDT", ""),
                    "quoteAsset": "USDT",
                }
                for s in symbols
            ],
        }
