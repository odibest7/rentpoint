from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/customer/", views.signup_customer, name="signup_customer"),
    path("signup/item-owner/", views.signup_item_owner, name="signup_item_owner"),
    path("login/", views.RentPointLoginView.as_view(), name="login"),
    path("logout/", views.RentPointLogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
]
