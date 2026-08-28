from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    A single user table serves both operational roles described in the
    project scope: customers (who browse and pay for rentals) and item
    owners (who list items/properties and manage earnings). The role is
    stored on the user so authorization checks stay in one place instead
    of being scattered across views.

    Django's built-in is_staff / is_superuser flags continue to cover the
    administrator role, so a third "admin" role is not duplicated here.
    """

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        ITEM_OWNER = "item_owner", "Item owner"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_item_owner(self):
        return self.role == self.Role.ITEM_OWNER

    def __str__(self):
        return self.get_full_name() or self.username
