import tempfile
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from accounts.models import User
from listings.models import Category, Item, ItemImage


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="rentpoint-media-"))
class ItemImageCleanupTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1",
            email="owner1@example.com",
            password="StrongPass123!",
            role=User.Role.ITEM_OWNER,
        )
        self.category = Category.objects.create(name="Furniture", slug="furniture")
        self.item = Item.objects.create(
            owner=self.owner,
            category=self.category,
            name="Test Item",
            description="Test description",
            rental_price="50.00",
            location="Nsukka",
            quantity_available=1,
        )

    def test_delete_removes_file_from_storage(self):
        image = ItemImage.objects.create(
            item=self.item,
            image=SimpleUploadedFile("first.png", b"first-image", content_type="image/png"),
            position=0,
        )

        file_path = Path(image.image.path)
        self.assertTrue(file_path.exists())

        image.delete()

        self.assertFalse(file_path.exists())

    def test_replacing_image_removes_old_file(self):
        image = ItemImage.objects.create(
            item=self.item,
            image=SimpleUploadedFile("old.png", b"old-image", content_type="image/png"),
            position=0,
        )
        old_path = Path(image.image.path)
        self.assertTrue(old_path.exists())

        image.image = SimpleUploadedFile("new.png", b"new-image", content_type="image/png")
        image.save()

        self.assertFalse(old_path.exists())
        self.assertTrue(Path(image.image.path).exists())
