from django.conf import settings
from django.db import models


class Wallet(models.Model):
    """
    Holds each item owner's available rental earnings. A transaction
    credits the wallet when a customer's payment is confirmed; a
    withdrawal debits it once the request is approved. Keeping a running
    balance here (instead of summing transactions on every page load)
    keeps the earnings dashboard fast and gives a single source of truth
    for "available earnings," which the report treats as a distinct idea
    from the raw transaction history.
    """

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_withdrawn = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def credit(self, amount):
        self.balance += amount
        self.total_earned += amount
        self.save(update_fields=["balance", "total_earned", "updated_at"])

    def debit(self, amount):
        self.balance -= amount
        self.total_withdrawn += amount
        self.save(update_fields=["balance", "total_withdrawn", "updated_at"])

    def __str__(self):
        return f"Wallet of {self.owner}"


class WithdrawalRequest(models.Model):
    """An item owner's request to move available earnings out of the
    platform. Kept separate from Wallet so every request stays as an
    auditable record, matching the report's withdrawal-mechanism goal."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        APPROVED = "approved", "Approved and paid"
        REJECTED = "rejected", "Rejected"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="withdrawal_requests"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=150)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    admin_note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return f"Withdrawal of {self.amount} by {self.owner}"
