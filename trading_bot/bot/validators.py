"""
Input validation for order parameters.

Uses Pydantic for strict type checking and custom validation rules.
"""

from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class OrderParams(BaseModel):
    """Validated order parameters."""

    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        v = v.strip().upper()
        if not v:
            raise ValueError("Symbol must not be empty")
        if not v.isalnum():
            raise ValueError(
                f"Invalid symbol '{v}'. Symbol must be alphanumeric (e.g. BTCUSDT)"
            )
        return v

    @field_validator("side")
    @classmethod
    def validate_side(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in ("BUY", "SELL"):
            raise ValueError(
                f"Invalid side '{v}'. Must be 'BUY' or 'SELL'"
            )
        return v

    @field_validator("order_type")
    @classmethod
    def validate_order_type(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in ("MARKET", "LIMIT"):
            raise ValueError(
                f"Invalid order type '{v}'. Must be 'MARKET' or 'LIMIT'"
            )
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(
                f"Invalid quantity '{v}'. Quantity must be greater than 0"
            )
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError(
                f"Invalid price '{v}'. Price must be greater than 0"
            )
        return v

    @model_validator(mode="after")
    def check_limit_price(self):
        """Ensure price is provided for LIMIT orders."""
        if self.order_type == "LIMIT" and self.price is None:
            raise ValueError(
                "Price is required for LIMIT orders. Use --price to specify."
            )
        return self
