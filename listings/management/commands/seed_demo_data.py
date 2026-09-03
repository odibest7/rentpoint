"""
Populates the database with realistic categories and demo listings so the
platform is not an empty shell the first time someone opens it.

Usage: python manage.py seed_demo_data
Safe to re-run: existing records are matched by name and left untouched.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from listings.models import Category, Item

User = get_user_model()

CATEGORIES = [
    ("Household & kitchen items", "kitchen"),
    ("Event & party equipment", "event"),
    ("Furniture", "furniture"),
    ("Clothing & fashion", "fashion"),
    ("Jewellery", "jewellery"),
    ("Hair-related items", "hair"),
    ("Footwear", "footwear"),
    ("Commercial properties", "shop"),
    ("Other rentable items", "other"),
]

DEMO_ITEMS = [
    {
        "owner_username": "demo_owner",
        "category": "Event & party equipment",
        "name": "White canopy & chairs (set of 100)",
        "description": "A full event setup: one large white canopy plus 100 matching plastic chairs. Ideal for weddings, burials, and birthday parties. Delivery and setup within Nsukka Urban can be arranged.",
        "rental_price": 15000,
        "price_unit": Item.PriceUnit.PER_DAY,
        "location": "Odenigbo, Nsukka",
        "quantity_available": 3,
    },
    {
        "owner_username": "demo_owner",
        "category": "Furniture",
        "name": "Plastic tables (set of 10)",
        "description": "Sturdy plastic tables, seats 6 people each comfortably. Good condition, cleaned after every rental.",
        "rental_price": 5000,
        "price_unit": Item.PriceUnit.PER_DAY,
        "location": "Ihe Achara, Nsukka",
        "quantity_available": 5,
    },
    {
        "owner_username": "demo_owner",
        "category": "Commercial properties",
        "name": "Small lock-up shop, Ogige Market road",
        "description": "A 3x4 metre lock-up shop close to Ogige Market, suitable for a short-term retail pop-up or storage.",
        "rental_price": 25000,
        "price_unit": Item.PriceUnit.PER_MONTH,
        "location": "Ogige Market, Nsukka",
        "quantity_available": 1,
    },
    {
        "owner_username": "demo_owner",
        "category": "Clothing & fashion",
        "name": "Ankara Agbada set (size L)",
        "description": "A well-kept Ankara agbada set, size large, suitable for weddings and traditional events. Dry cleaned after every rental.",
        "rental_price": 3500,
        "price_unit": Item.PriceUnit.PER_DAY,
        "location": "Nsukka Urban",
        "quantity_available": 2,
    },
    {
        "owner_username": "demo_owner",
        "category": "Household & kitchen items",
        "name": "Large cooking pots (set of 4)",
        "description": "Four large aluminium pots suitable for cooking for events of 100 guests or more.",
        "rental_price": 4000,
        "price_unit": Item.PriceUnit.PER_DAY,
        "location": "Hilltop, Nsukka",
        "quantity_available": 4,
    },
]


class Command(BaseCommand):
    help = "Seed RentPoint with demo categories, a demo item owner, sample listings, and a superuser from environment variables."

    def handle(self, *args, **options):
        username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "admin").strip() or "admin"
        email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "admin@example.com").strip() or "admin@example.com"
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD") or "Admin@1234"

        admin_user, admin_created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        needs_admin_update = (
            admin_created
            or admin_user.email != email
            or not admin_user.is_staff
            or not admin_user.is_superuser
            or not admin_user.check_password(password)
        )

        if needs_admin_update:
            admin_user.email = email
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password(password)
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    "Ensured seeded superuser exists "
                    f"(username: {username}, email: {email})."
                )
            )

        for name, icon in CATEGORIES:
            Category.objects.get_or_create(name=name, defaults={"icon": icon})
        self.stdout.write(self.style.SUCCESS(f"Ensured {len(CATEGORIES)} categories exist."))

        owner, created = User.objects.get_or_create(
            username="demo_owner",
            defaults={
                "first_name": "Chika",
                "last_name": "Eze",
                "email": "demo_owner@example.com",
                "role": User.Role.ITEM_OWNER,
                "phone_number": "08030000000",
            },
        )
        if created:
            owner.set_password("DemoOwner!2026")
            owner.save()
            self.stdout.write(self.style.SUCCESS("Created demo item owner (username: demo_owner / password: DemoOwner!2026)."))

        for entry in DEMO_ITEMS:
            category = Category.objects.get(name=entry["category"])
            Item.objects.get_or_create(
                name=entry["name"],
                defaults={
                    "owner": owner,
                    "category": category,
                    "description": entry["description"],
                    "rental_price": entry["rental_price"],
                    "price_unit": entry["price_unit"],
                    "location": entry["location"],
                    "quantity_available": entry["quantity_available"],
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Ensured {len(DEMO_ITEMS)} demo listings exist."))
        self.stdout.write(self.style.SUCCESS("Seeding complete."))
