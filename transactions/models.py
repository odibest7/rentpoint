import uuid

from django.conf import settings
from django.db import models

from listings.models import Item


class Transaction(models.Model):
    """
    Records the full lifecycle of one rental payment, from a customer's
    request through to a confirmed electronic payment. This is the
    "transaction record" the project report identifies as central to
    transparency between customers and item owners.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending payment"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    class DeliveryOption(models.TextChoices):
        PICKUP = "pickup", "Self-Pickup at Owner Location"
        DELIVERY = "delivery", "Direct Delivery to Customer Address"

    reference = models.CharField(max_length=40, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchases"
    )
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="transactions")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sales"
    )
    quantity = models.PositiveIntegerField(default=1)
    duration = models.PositiveIntegerField(default=1, help_text="Number of price units rented, e.g. 3 days.")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount paid by the customer.")
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    owner_earning = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_option = models.CharField(
        max_length=20, choices=DeliveryOption.choices, default=DeliveryOption.PICKUP
    )
    delivery_address = models.CharField(
        max_length=255, blank=True, help_text="Customer delivery address or area."
    )
    contact_phone = models.CharField(
        max_length=30, blank=True, help_text="Direct phone number for pickup/delivery coordination."
    )
    pickup_notes = models.TextField(
        blank=True, help_text="Special instructions, pickup time, or handover details."
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    payment_provider = models.CharField(max_length=30, blank=True)
    provider_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"RP-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} ({self.get_status_display()})"
