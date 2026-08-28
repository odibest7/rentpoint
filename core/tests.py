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
        self.assertContains(response, "Site Control Dashboard")

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
