from django.urls import path

from . import admin_views, views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("how-it-works/", views.how_it_works, name="how_it_works"),
    path("dashboard/", views.redirect_after_login, name="redirect_after_login"),
    
    # Custom Site Admin Dashboard routes
    path("site-admin/", admin_views.admin_dashboard, name="admin_dashboard"),
    path("site-admin/users/", admin_views.admin_users, name="admin_users"),
    path("site-admin/users/<int:user_id>/toggle-staff/", admin_views.admin_user_toggle_staff, name="admin_user_toggle_staff"),
    path("site-admin/listings/", admin_views.admin_listings, name="admin_listings"),
    path("site-admin/listings/<slug:slug>/toggle-available/", admin_views.admin_listing_toggle_available, name="admin_listing_toggle_available"),
    path("site-admin/transactions/", admin_views.admin_transactions, name="admin_transactions"),
    path("site-admin/withdrawals/", admin_views.admin_withdrawals, name="admin_withdrawals"),
    path("site-admin/withdrawals/<int:withdrawal_id>/<str:action>/", admin_views.admin_withdrawal_action, name="admin_withdrawal_action"),
    path("site-admin/categories/", admin_views.admin_categories, name="admin_categories"),
    path("site-admin/categories/<int:category_id>/delete/", admin_views.admin_category_delete, name="admin_category_delete"),
    path("site-admin/verifications/", admin_views.admin_verifications, name="admin_verifications"),
    path("site-admin/verifications/<int:submission_id>/<str:action>/", admin_views.admin_verification_action, name="admin_verification_action"),
]
