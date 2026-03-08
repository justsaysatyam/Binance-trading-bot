"""trading_bot URL Configuration."""

from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include

from bot.models import OrderRecord


def home(request):
    orders = OrderRecord.objects.all()[:20]
    return render(request, "bot/home.html", {"orders": orders})


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("bot.urls")),
]


