from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
import time
import logging


# Recognised Nsukka Urban zones used as standardised location choices.
# Stored as plain CharField so existing free-text data is preserved.
NSUKKA_ZONES = [
    ("Hilltop",         "Hilltop"),
    ("UNN Campus",      "UNN Campus"),
    ("Onuiyi",          "Onuiyi"),
    ("Odenigbo",        "Odenigbo"),
    ("Ede-Oballa",      "Ede-Oballa"),
    ("Urban Area",      "Urban Area"),
    ("Enugwu-Ezike",    "Enugwu-Ezike"),
    ("Orba",            "Orba"),
    ("Ibagwa-Ani",      "Ibagwa-Ani"),
    ("Opi",             "Opi"),
    ("Eha-Amufu",       "Eha-Amufu"),
    ("Ogurugu",         "Ogurugu"),
    ("Ede-Uturu",       "Ede-Uturu"),
    ("Other / Not Listed", "Other / Not Listed"),
]


class Category(models.Model):
    """
    Groups rentable items so customers can browse and filter instead of
    scanning every listing on the platform, matching the categorisation
    described in the project scope (household items, event equipment,
    furniture, fashion, commercial properties, and so on).
    """

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    icon = models.CharField(
        max_length=40,
        blank=True,
        help_text="Name of an icon from static/img/icons, e.g. 'sofa'.",
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Item(models.Model):
    """
    A single rentable item or property. This model intentionally covers
    both movable items (chairs, canopies, clothes) and fixed properties
    (shops), since the report defines "rentable item or property" as one
    concept rather than two separate structures.
    """

    class Condition(models.TextChoices):
        NEW = "new", "New"
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"

    class PriceUnit(models.TextChoices):
        PER_DAY = "day", "per day"
        PER_WEEK = "week", "per week"
        PER_MONTH = "month", "per month"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="items",
        limit_choices_to={"role": "item_owner"},
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="items")
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField()
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_unit = models.CharField(max_length=10, choices=PriceUnit.choices, default=PriceUnit.PER_DAY)
    condition = models.CharField(max_length=10, choices=Condition.choices, default=Condition.GOOD)
    location = models.CharField(
        max_length=150,
        help_text="Recognised Nsukka Urban zone where the item is located.",
    )
    quantity_available = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)[:120]
            slug = base_slug
            counter = 1
            while Item.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("listings:item_detail", kwargs={"slug": self.slug})

    @property
    def primary_image(self):
        return self.images.first()

    def __str__(self):
        return self.name


class ItemImage(models.Model):
    """Items may carry more than one photograph; the first one uploaded
    (by ``position``) is treated as the primary listing image."""

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="listings/")
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                previous = ItemImage.objects.get(pk=self.pk)
            except ItemImage.DoesNotExist:
                previous = None

            if previous and previous.image and previous.image.name and previous.image.name != self.image.name:
                # On Windows the file may be locked by another process or by a still-open
                # file handle. Try to close any open file handles and retry deletion a
                # few times before giving up to avoid race conditions that raise
                # PermissionError ([WinError 32]). This makes replace operations
                # robust in local dev on Windows.
                try:
                    previous.image.storage.delete(previous.image.name)
                except PermissionError:
                    logger = logging.getLogger(__name__)
                    for attempt in range(5):
                        try:
                            try:
                                previous.image.close()
                            except Exception:
                                pass
                            # Close underlying file if present
                            f = getattr(previous.image, 'file', None)
                            if f:
                                try:
                                    f.close()
                                except Exception:
                                    pass
                            previous.image.storage.delete(previous.image.name)
                            break
                        except PermissionError:
                            time.sleep(0.08)
                    else:
                        logger.warning("Could not delete previous image '%s' after several attempts (PermissionError).", previous.image.name)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image and self.image.name:
            try:
                self.image.storage.delete(self.image.name)
            except PermissionError:
                # Try a few times to close and delete on Windows where file locks may occur
                logger = logging.getLogger(__name__)
                for attempt in range(5):
                    try:
                        try:
                            self.image.close()
                        except Exception:
                            pass
                        f = getattr(self.image, 'file', None)
                        if f:
                            try:
                                f.close()
                            except Exception:
                                pass
                        self.image.storage.delete(self.image.name)
                        break
                    except PermissionError:
                        time.sleep(0.08)
                else:
                    logger.warning("Could not delete image '%s' after several attempts (PermissionError).", self.image.name)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.item.name}"
