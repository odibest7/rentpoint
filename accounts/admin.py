from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import OwnerVerification, User


@admin.register(User)
class RentPointUserAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "email", "role", "verification_status", "is_active", "date_joined")
    list_filter = ("role", "verification_status", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("RentPoint profile", {"fields": ("role", "phone_number", "address", "verification_status")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("RentPoint profile", {"fields": ("role", "phone_number", "address")}),
    )


@admin.register(OwnerVerification)
class OwnerVerificationAdmin(admin.ModelAdmin):
    """
    Full NIN visibility here is intentional and limited to Django admin
    staff: reviewing a submission requires seeing what was submitted.
    Every other surface in the app (the site-admin review queue included)
    uses masked_nin instead. See accounts/verification.py for why
    approval is never automated.
    """

    list_display = ("owner", "full_legal_name", "nin", "selfie_thumbnail", "owner_status", "submitted_at", "reviewed_by")
    list_filter = ("owner__verification_status",)
    search_fields = ("owner__username", "full_legal_name", "nin")
    readonly_fields = ("submitted_at", "updated_at", "selfie_thumbnail")

    @admin.display(description="Status")
    def owner_status(self, obj):
        return obj.owner.get_verification_status_display()

    @admin.display(description="Selfie")
    def selfie_thumbnail(self, obj):
        if not obj.selfie_image:
            return "—"
        return format_html(
            '<img src="{}" style="width:44px;height:44px;object-fit:cover;border-radius:50%;">',
            obj.selfie_image.url,
        )
