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


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="emeka_renter",
            email="emeka@example.com",
            password="OldPassword123!",
            first_name="Emeka",
            last_name="Nnamdi",
            role=User.Role.CUSTOMER,
        )

    def test_password_reset_request_view_renders(self):
        response = self.client.get("/accounts/password-reset/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_form.html")
        self.assertContains(response, "Forgot Password?")

    def test_password_reset_sends_email_for_registered_user(self):
        from django.core import mail

        response = self.client.post(
            "/accounts/password-reset/",
            {"email": "emeka@example.com"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_done.html")

        # Verify email was dispatched
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertIn("Reset your", sent_email.subject)
        self.assertEqual(sent_email.to, ["emeka@example.com"])
        self.assertIn("accounts/password-reset/", sent_email.body)

    def test_password_reset_enumeration_protection(self):
        from django.core import mail

        response = self.client.post(
            "/accounts/password-reset/",
            {"email": "nonexistent@example.com"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_done.html")
        # No email sent for non-existent user, but UI confirms gracefully
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_confirm_and_complete_flow(self):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        # GET confirm page with valid token (Django stores token in session and redirects to set-password form for security)
        confirm_url = f"/accounts/password-reset/{uid}/{token}/"
        response = self.client.get(confirm_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_confirm.html")
        self.assertTrue(response.context["validlink"])

        # POST new password to the active redirected form URL
        post_url = response.redirect_chain[0][0] if response.redirect_chain else confirm_url
        post_response = self.client.post(
            post_url,
            {
                "new_password1": "NewSecurePassword999!",
                "new_password2": "NewSecurePassword999!",
            },
            follow=True,
        )
        self.assertEqual(post_response.status_code, 200)
        self.assertTemplateUsed(post_response, "accounts/password_reset_complete.html")

        # Verify user can log in with new password and not old password
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecurePassword999!"))
        self.assertFalse(self.user.check_password("OldPassword123!"))

        # Verify old token cannot be reused
        reuse_response = self.client.get(confirm_url, follow=True)
        self.assertEqual(reuse_response.status_code, 200)
        self.assertFalse(reuse_response.context["validlink"])


    def test_password_reset_confirm_invalid_token(self):
        invalid_url = "/accounts/password-reset/invalid-uid/invalid-token/"
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_confirm.html")
        self.assertFalse(response.context["validlink"])
        self.assertContains(response, "Reset Link Expired or Invalid")

