from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
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

    class VerificationStatus(models.TextChoices):
        UNVERIFIED = "unverified", "Not verified"
        PENDING = "pending", "Pending review"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Denormalized onto the user (rather than only living on
    # OwnerVerification) so item cards, listing pages, and receipts can
    # show a verified badge without an extra query on every render.
    # OwnerVerification remains the source of truth for why this status
    # was reached (the submitted NIN, the reviewer, and the reasoning).
    verification_status = models.CharField(
        max_length=12,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED,
    )

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_item_owner(self):
        return self.role == self.Role.ITEM_OWNER

    @property
    def is_verified(self):
        return self.verification_status == self.VerificationStatus.VERIFIED

    def __str__(self):
        return self.get_full_name() or self.username


def validate_verification_image_size(image):
    "Keep sensitive identity images reasonably small for secure storage."
    if image.size > 5 * 1024 * 1024:
        raise ValidationError("Verification images must be 5 MB or smaller.")

class OwnerVerification(models.Model):
    """
    An item owner's identity verification submission: the NIN (National
    Identification Number) and legal name they provided, plus an audit
    trail of who reviewed it and why. One row per owner: resubmitting
    after a rejection updates this row rather than creating a new one, so
    there is always exactly one current submission to review.

    The NIN is genuinely sensitive personal data (comparable to a
    national ID or SSN elsewhere), so nothing outside this model or the
    Django admin should ever read the `nin` field directly. Use
    `masked_nin` everywhere else: item cards, dashboards, and the
    verification status page shown back to the owner themselves. The selfie photo and both physical NIN-card photographs are treated with
    the same care: they are only ever shown on the staff review queue and in
    the Django admin, never to customers or on any public page.
    """

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification",
        limit_choices_to={"role": "item_owner"},
    )
    full_legal_name = models.CharField(
        max_length=150,
        help_text="Full name exactly as it appears on the National ID.",
    )
    nin = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^\d{11}$", "Enter the 11-digit NIN exactly as issued.")],
        help_text="11-digit National Identification Number.",
    )
    selfie_image = models.ImageField(
        upload_to="verifications/selfies/",
        validators=[validate_verification_image_size],
        blank=True,
        help_text="A live selfie taken during submission, for a reviewer to compare against the NIN.",
    )
    nin_front_image = models.ImageField(
        upload_to="verifications/nin-cards/front/",
        validators=[validate_verification_image_size],
        blank=True,
        help_text="Front photograph of the owner's physical NIN card.",
    )
    nin_back_image = models.ImageField(
        upload_to="verifications/nin-cards/back/",
        validators=[validate_verification_image_size],
        blank=True,
        help_text="Back photograph of the owner's physical NIN card.",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verifications_reviewed",
        limit_choices_to={"is_staff": True},
    )
    rejection_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Shown to the item owner if the submission is rejected.",
    )

    class Meta:
        verbose_name = "Owner verification"
        verbose_name_plural = "Owner verifications"

    @property
    def masked_nin(self):
        """The only form of the NIN that should ever appear outside the
        review queue or the Django admin: everything but the last four
        digits replaced with bullets, e.g. '•••••••1234'."""
        if len(self.nin) < 4:
            return "•" * len(self.nin)
        return "•" * (len(self.nin) - 4) + self.nin[-4:]

    def __str__(self):
        return f"Verification for {self.owner} ({self.owner.get_verification_status_display()})"
