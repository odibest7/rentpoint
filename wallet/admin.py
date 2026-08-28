from django.contrib import admin
from django.utils import timezone

from .models import Wallet, WithdrawalRequest


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("owner", "balance", "total_earned", "total_withdrawn", "updated_at")
    search_fields = ("owner__username", "owner__email")


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ("owner", "amount", "status", "requested_at", "resolved_at")
    list_filter = ("status",)
    actions = ["approve_and_pay", "reject_request"]

    @admin.action(description="Approve and pay selected withdrawal requests")
    def approve_and_pay(self, request, queryset):
        for withdrawal in queryset.filter(status=WithdrawalRequest.Status.PENDING):
            wallet = withdrawal.owner.wallet
            wallet.debit(withdrawal.amount)
            withdrawal.status = WithdrawalRequest.Status.APPROVED
            withdrawal.resolved_at = timezone.now()
            withdrawal.save(update_fields=["status", "resolved_at"])

    @admin.action(description="Reject selected withdrawal requests")
    def reject_request(self, request, queryset):
        queryset.filter(status=WithdrawalRequest.Status.PENDING).update(
            status=WithdrawalRequest.Status.REJECTED, resolved_at=timezone.now()
        )
