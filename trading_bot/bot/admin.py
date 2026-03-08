"""
Django admin registration for the bot app.
"""

from django.contrib import admin
from bot.models import OrderRecord


@admin.register(OrderRecord)
class OrderRecordAdmin(admin.ModelAdmin):
    list_display = [
        "order_id",
        "symbol",
        "side",
        "order_type",
        "quantity",
        "price",
        "status",
        "created_at",
    ]
    list_filter = ["side", "order_type", "status", "symbol"]
    search_fields = ["symbol", "order_id"]
    readonly_fields = ["raw_response", "created_at"]
