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

    list_display = ("owner", "full_legal_name", "nin", "selfie_thumbnail", "nin_front_thumbnail", "nin_back_thumbnail", "owner_status", "submitted_at", "reviewed_by")
    list_filter = ("owner__verification_status",)
    search_fields = ("owner__username", "full_legal_name", "nin")
    readonly_fields = ("submitted_at", "updated_at", "selfie_thumbnail", "nin_front_thumbnail", "nin_back_thumbnail")

    @admin.display(description="Status")
    def owner_status(self, obj):
        return obj.owner.get_verification_status_display()

    def _image_thumbnail(self, image, alt):
        if not image:
            return "—"
        return format_html(
            '<a href="{0}" target="_blank" rel="noopener"><img src="{0}" alt="{1}" style="width:64px;height:48px;object-fit:cover;border-radius:4px;"></a>',
            image.url,
            alt,
        )

    @admin.display(description="Selfie")
    def selfie_thumbnail(self, obj):
        return self._image_thumbnail(obj.selfie_image, "Live selfie")

    @admin.display(description="NIN front")
    def nin_front_thumbnail(self, obj):
        return self._image_thumbnail(obj.nin_front_image, "Front of NIN card")

    @admin.display(description="NIN back")
    def nin_back_thumbnail(self, obj):
        return self._image_thumbnail(obj.nin_back_image, "Back of NIN card")
