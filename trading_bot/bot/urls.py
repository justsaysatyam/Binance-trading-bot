"""Bot app URL configuration."""

from django.urls import path
from bot.views import PlaceOrderView

urlpatterns = [
    path("order/", PlaceOrderView.as_view(), name="place-order"),
]
