from django.urls import path

from . import views

app_name = "wallet"

urlpatterns = [
    path("", views.earnings, name="earnings"),
    path("withdraw/", views.request_withdrawal, name="withdraw"),
]
