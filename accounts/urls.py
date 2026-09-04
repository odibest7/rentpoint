from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/customer/", views.signup_customer, name="signup_customer"),
    path("signup/item-owner/", views.signup_item_owner, name="signup_item_owner"),
    path("login/", views.RentPointLoginView.as_view(), name="login"),
    path("logout/", views.RentPointLogoutView.as_view(), name="logout"),
    path("password-reset/", views.RentPointPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", views.RentPointPasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "password-reset/<uidb64>/<token>/",
        views.RentPointPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        views.RentPointPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("profile/", views.profile, name="profile"),
    path("verification/", views.verification, name="verification"),
]

