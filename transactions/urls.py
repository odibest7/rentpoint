from django.urls import path

from . import views

app_name = "transactions"

urlpatterns = [
    path("mine/", views.my_transactions, name="my_transactions"),
    path("rent/<slug:slug>/", views.start_rental, name="start_rental"),
    path("checkout/<str:reference>/", views.checkout, name="checkout"),
    path("paystack/verify/", views.paystack_verify, name="paystack_verify"),
    path("paystack/callback/", views.paystack_callback, name="paystack_callback"),
    path("receipt/<str:reference>/", views.receipt, name="receipt"),
]
