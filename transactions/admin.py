from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("reference", "item", "customer", "owner", "amount", "status", "created_at")
    list_filter = ("status", "payment_provider")
    search_fields = ("reference", "item__name", "customer__username", "owner__username")
    readonly_fields = [f.name for f in Transaction._meta.fields]

    def has_add_permission(self, request):
        return False
