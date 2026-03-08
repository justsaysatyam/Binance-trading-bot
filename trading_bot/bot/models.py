"""
OrderRecord model — persists every order attempt for audit / history.
"""

from django.db import models
from django.utils import timezone


class OrderRecord(models.Model):
    """Stores submitted order details and API responses."""

    symbol = models.CharField(max_length=20)
    side = models.CharField(max_length=4)  # BUY / SELL
    order_type = models.CharField(max_length=10)  # MARKET / LIMIT
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    price = models.DecimalField(
        max_digits=20, decimal_places=8, null=True, blank=True
    )

    # Fields populated from API response
    order_id = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=30, default="PENDING")
    executed_qty = models.CharField(max_length=30, blank=True, default="")
    avg_price = models.CharField(max_length=30, blank=True, default="")
    raw_response = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order Record"
        verbose_name_plural = "Order Records"

    def __str__(self):
        return (
            f"{self.side} {self.order_type} {self.symbol} "
            f"qty={self.quantity} — {self.status}"
        )
