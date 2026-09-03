from decimal import Decimal
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from listings.models import Category, Item
from transactions.models import Transaction


class DynamicRentalCalculationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner_user",
            email="owner@rentpoint.test",
            password="StrongPassword123!",
            role=User.Role.ITEM_OWNER,
        )
        self.customer = User.objects.create_user(
            username="customer_user",
            email="customer@rentpoint.test",
            password="StrongPassword123!",
            role=User.Role.CUSTOMER,
            phone_number="08012345678",
            address="12 Campus Gate, Nsukka",
        )
        self.category = Category.objects.create(name="Events", slug="events")
        self.item = Item.objects.create(
            owner=self.owner,
            category=self.category,
            name="Deluxe Canopy 20x20",
            description="High quality event canopy",
            rental_price=Decimal("15000.00"),
            price_unit="day",
            condition="new",
            location="University Road, Nsukka",
            quantity_available=10,
            is_available=True,
        )

    def test_start_rental_initializes_with_query_params(self):
        self.client.force_login(self.customer)
        url = reverse("transactions:start_rental", kwargs={"slug": self.item.slug})
        response = self.client.get(f"{url}?quantity=4&duration=3")

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.initial.get("quantity"), 4)
        self.assertEqual(form.initial.get("duration"), 3)

    def test_start_rental_clamps_invalid_query_params(self):
        self.client.force_login(self.customer)
        url = reverse("transactions:start_rental", kwargs={"slug": self.item.slug})
        # quantity 999 exceeds available stock 10
        response = self.client.get(f"{url}?quantity=999&duration=-5")

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        # Out-of-bounds params are omitted from initial so form falls back to clean default 1
        self.assertNotIn("quantity", form.initial)
        self.assertNotIn("duration", form.initial)

    def test_start_rental_post_calculates_total_amount_correctly(self):
        self.client.force_login(self.customer)
        url = reverse("transactions:start_rental", kwargs={"slug": self.item.slug})
        post_data = {
            "quantity": 3,
            "duration": 4,
            "delivery_option": "pickup",
            "contact_phone": "08012345678",
            "delivery_address": "",
            "pickup_notes": "Will pick up early morning",
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        transaction = Transaction.objects.filter(customer=self.customer, item=self.item).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.quantity, 3)
        self.assertEqual(transaction.duration, 4)
        expected_total = Decimal("15000.00") * 3 * 4  # 180,000.00
        self.assertEqual(transaction.amount, expected_total)
