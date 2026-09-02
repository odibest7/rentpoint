import tempfile
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from accounts.models import OwnerVerification, User


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="rentpoint-verification-media-"))
class OwnerVerificationCleanupTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner2",
            email="owner2@example.com",
            password="StrongPass123!",
            role=User.Role.ITEM_OWNER,
        )

    def test_delete_removes_verification_files(self):
        verification = OwnerVerification.objects.create(
            owner=self.owner,
            full_legal_name="Jane Doe",
            nin="12345678901",
            selfie_image=SimpleUploadedFile("selfie.png", b"selfie-data", content_type="image/png"),
            nin_front_image=SimpleUploadedFile("front.png", b"front-data", content_type="image/png"),
            nin_back_image=SimpleUploadedFile("back.png", b"back-data", content_type="image/png"),
        )

        selfie_path = Path(verification.selfie_image.path)
        front_path = Path(verification.nin_front_image.path)
        back_path = Path(verification.nin_back_image.path)

        self.assertTrue(selfie_path.exists())
        self.assertTrue(front_path.exists())
        self.assertTrue(back_path.exists())

        verification.delete()

        self.assertFalse(selfie_path.exists())
        self.assertFalse(front_path.exists())
        self.assertFalse(back_path.exists())

    def test_replacing_verification_images_removes_old_files(self):
        verification = OwnerVerification.objects.create(
            owner=self.owner,
            full_legal_name="Jane Doe",
            nin="12345678901",
            selfie_image=SimpleUploadedFile("selfie-old.png", b"old-selfie", content_type="image/png"),
            nin_front_image=SimpleUploadedFile("front-old.png", b"old-front", content_type="image/png"),
            nin_back_image=SimpleUploadedFile("back-old.png", b"old-back", content_type="image/png"),
        )

        old_selfie = Path(verification.selfie_image.path)
        verification.selfie_image = SimpleUploadedFile("selfie-new.png", b"new-selfie", content_type="image/png")
        verification.save()

        self.assertFalse(old_selfie.exists())
        self.assertTrue(Path(verification.selfie_image.path).exists())
