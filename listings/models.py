from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


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
    location = models.CharField(max_length=150, help_text="Area within Nsukka Urban, e.g. Odenigbo.")
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
                previous.image.storage.delete(previous.image.name)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image and self.image.name:
            self.image.storage.delete(self.image.name)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.item.name}"
