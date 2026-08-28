from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class RentPointUserAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "email", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("RentPoint profile", {"fields": ("role", "phone_number", "address")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("RentPoint profile", {"fields": ("role", "phone_number", "address")}),
    )
