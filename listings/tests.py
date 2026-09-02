import io
import tempfile
from pathlib import Path

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from accounts.models import User
from listings.models import Category, Item, ItemImage


def create_test_image_bytes():
    buf = io.BytesIO()
    image = Image.new("RGB", (100, 100), color="teal")
    image.save(buf, format="PNG")
    return buf.getvalue()


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
            image=SimpleUploadedFile("first.png", create_test_image_bytes(), content_type="image/png"),
            position=0,
        )

        file_path = Path(image.image.path)
        self.assertTrue(file_path.exists())

        image.delete()

        self.assertFalse(file_path.exists())

    def test_replacing_image_removes_old_file(self):
        image = ItemImage.objects.create(
            item=self.item,
            image=SimpleUploadedFile("old.png", create_test_image_bytes(), content_type="image/png"),
            position=0,
        )
        old_path = Path(image.image.path)
        self.assertTrue(old_path.exists())

        image.image = SimpleUploadedFile("new.png", create_test_image_bytes(), content_type="image/png")
        image.save()

        self.assertFalse(old_path.exists())
        self.assertTrue(Path(image.image.path).exists())


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="rentpoint-media-"))
class ItemCreationAndMediaServingTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="test_owner",
            email="owner@example.com",
            password="StrongPassword123!",
            role=User.Role.ITEM_OWNER,
        )
        self.category = Category.objects.create(name="Electronics", slug="electronics")

    def test_owner_create_item_with_image_upload(self):
        self.client.force_login(self.owner)
        fake_image = SimpleUploadedFile("camera.png", create_test_image_bytes(), content_type="image/png")

        post_data = {
            "name": "Sony Alpha 4K Camera",
            "category": self.category.pk,
            "description": "Professional 4K mirrorless camera with extra lenses.",
            "rental_price": "15000.00",
            "price_unit": "day",
            "condition": "good",
            "location": "Odenigbo, Nsukka",
            "quantity_available": 2,
            "is_available": "on",
            # Management form for 1 extra form
            "images-TOTAL_FORMS": "1",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "8",
            "images-0-id": "",
            "images-0-position": "0",
            "images-0-image": fake_image,
        }

        response = self.client.post("/listings/new/", post_data)
        self.assertEqual(response.status_code, 302)

        item = Item.objects.get(name="Sony Alpha 4K Camera")
        self.assertEqual(item.owner, self.owner)
        self.assertEqual(item.images.count(), 1)
        self.assertIsNotNone(item.primary_image)

        # Verify media file URL is accessible and served even in production (DEBUG=False)
        with self.settings(DEBUG=False):
            media_url = item.primary_image.image.url
            media_response = self.client.get(media_url)
            self.assertEqual(media_response.status_code, 200)

    def test_owner_item_list_renders_thumbnail(self):
        self.client.force_login(self.owner)
        item = Item.objects.create(
            owner=self.owner,
            category=self.category,
            name="Party Speakers",
            description="Loud speakers",
            rental_price="8000.00",
            location="University Market Road",
            quantity_available=1,
        )
        ItemImage.objects.create(
            item=item,
            image=SimpleUploadedFile("speaker.png", create_test_image_bytes(), content_type="image/png"),
            position=0,
        )

        response = self.client.get("/listings/mine/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "table-item-thumb")
        self.assertContains(response, item.primary_image.image.url)

    def test_catalogue_renders_image(self):
        item = Item.objects.create(
            owner=self.owner,
            category=self.category,
            name="Event Canopy",
            description="Large waterproof canopy",
            rental_price="12000.00",
            location="Hilltop, Nsukka",
            quantity_available=1,
            is_available=True,
        )
        ItemImage.objects.create(
            item=item,
            image=SimpleUploadedFile("canopy.png", create_test_image_bytes(), content_type="image/png"),
            position=0,
        )

        # Public catalogue
        response = self.client.get("/listings/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, item.primary_image.image.url)

        # Item detail
        response = self.client.get(item.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, item.primary_image.image.url)

