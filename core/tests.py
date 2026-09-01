from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from listings.models import Category, Item


class CustomAdminDashboardTests(TestCase):
    def setUp(self):
        admin_pass = "adminpassword123"  # nosec B106
        cust_pass = "custpassword123"   # nosec B106
        self.staff_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password=admin_pass,
            role=User.Role.ITEM_OWNER,
        )
        self.customer = User.objects.create_user(
            username="customer1",
            email="cust@example.com",
            password=cust_pass,
            role=User.Role.CUSTOMER,
        )
        self.category = Category.objects.create(name="Tools", slug="tools")

    def test_non_staff_user_access_denied(self):
        self.client.login(username="customer1", password="custpassword123")  # nosec B106
        response = self.client.get(reverse("core:admin_dashboard"))
        # Standard staff_member_required redirects non-staff to admin login
        self.assertEqual(response.status_code, 302)

    def test_staff_user_dashboard_access(self):
        self.client.login(username="adminuser", password="adminpassword123")  # nosec B106
        response = self.client.get(reverse("core:admin_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Control Dashboard")

    def test_staff_user_can_view_users(self):
        self.client.login(username="adminuser", password="adminpassword123")  # nosec B106
        response = self.client.get(reverse("core:admin_users"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "customer1")

    def test_staff_user_can_create_category(self):
        self.client.login(username="adminuser", password="adminpassword123")  # nosec B106
        response = self.client.post(
            reverse("core:admin_categories"),
            {"name": "Electronics", "icon": "laptop"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name="Electronics").exists())


class HomePageRoleExperienceTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="renter",
            email="renter@example.com",
            password="customerpass123",
            role=User.Role.CUSTOMER,
        )
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="ownerpass123",
            role=User.Role.ITEM_OWNER,
        )

    def test_guest_homepage_shows_default_onboarding_cards(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Two Ways to Use RentPoint")
        self.assertContains(response, "Looking to Rent?")
        self.assertContains(response, "Own Items to Rent Out?")
        self.assertContains(response, "Sign Up as Customer")
        self.assertContains(response, "List Items as Owner")

    def test_customer_homepage_uses_browse_action_and_hides_owner_pitch(self):
        self.client.login(username="renter", password="customerpass123")
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ready to rent something?")
        self.assertContains(response, "Browse Items")
        self.assertNotContains(response, "Own Items to Rent Out?")
        self.assertNotContains(response, "List Items as Owner")
        self.assertContains(response, "Owner accounts are separate")

    def test_owner_homepage_uses_listing_and_wallet_actions(self):
        self.client.login(username="owner", password="ownerpass123")
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manage your listings")
        self.assertContains(response, "Go to Listings")
        self.assertContains(response, "Earnings & withdrawals")
        self.assertContains(response, "View Wallet")
        self.assertNotContains(response, "Looking to Rent?")
        self.assertNotContains(response, "Sign Up as Customer")
