from io import BytesIO

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import inlineformset_factory
from PIL import Image as PILImage
from PIL import UnidentifiedImageError

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except Exception:
    pass

from .models import Category, Item, ItemImage, NSUKKA_ZONES

MOBILE_HEIC_TYPES = {"image/heic", "image/heif"}


class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ["image", "position"]
        widgets = {
            "image": forms.FileInput(attrs={"class": "photo-file-input", "accept": "image/*"}),
            "position": forms.HiddenInput(attrs={"class": "photo-position-input", "value": "0"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            return image

        extension = (image.name or "").rsplit(".", 1)[-1].lower() if "." in (image.name or "") else ""
        content_type = getattr(image, "content_type", "") or ""
        if content_type and not content_type.startswith("image/"):
            raise forms.ValidationError("Please upload a valid image file.")

        try:
            with PILImage.open(image) as img:
                img.verify()
        except (UnidentifiedImageError, OSError, ValueError):
            raise forms.ValidationError("Please upload a valid image file.")

        image.seek(0)
        try:
            with PILImage.open(image) as img:
                actual_format = (getattr(img, "format", None) or "").upper()
                is_heic_like = (
                    extension in {"heic", "heif"}
                    or content_type in MOBILE_HEIC_TYPES
                    or actual_format in {"HEIC", "HEIF"}
                )
                if is_heic_like:
                    rgb = img.convert("RGB")
                    buffer = BytesIO()
                    rgb.save(buffer, format="JPEG", quality=90)
                    image = SimpleUploadedFile(
                        f"{(image.name or 'photo').rsplit('.', 1)[0]}.jpg",
                        buffer.getvalue(),
                        content_type="image/jpeg",
                    )
        except Exception:
            pass

        return image


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            "category",
            "name",
            "description",
            "rental_price",
            "price_unit",
            "condition",
            "location",
            "quantity_available",
            "is_available",
        ]
        widgets = {
            "category":           forms.Select(attrs={"class": "field-input"}),
            "name":               forms.TextInput(attrs={"class": "field-input", "placeholder": "e.g. White plastic chairs (set of 50)"}),
            "description":        forms.Textarea(attrs={"class": "field-input", "rows": 5, "placeholder": "Describe the item, its condition, and what is included."}),
            "rental_price":       forms.NumberInput(attrs={"class": "field-input", "placeholder": "0.00", "step": "0.01"}),
            "price_unit":         forms.Select(attrs={"class": "field-input"}),
            "condition":          forms.Select(attrs={"class": "field-input"}),
            "location":           forms.Select(attrs={"class": "field-input"}),
            "quantity_available": forms.NumberInput(attrs={"class": "field-input", "min": 1}),
            "is_available":       forms.CheckboxInput(attrs={"class": "field-checkbox"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self.fields["category"].empty_label = "Select a category"
        # Build location choices from the canonical zone list; prepend blank prompt
        self.fields["location"].widget = forms.Select(
            attrs={"class": "field-input"},
            choices=[("", "Select your area…")] + NSUKKA_ZONES,
        )
        self.fields["location"].required = True


ItemImageFormSet = inlineformset_factory(
    Item,
    ItemImage,
    form=ItemImageForm,
    extra=1,
    max_num=8,
    can_delete=True,
)


class ItemSearchForm(forms.Form):
    q         = forms.CharField(required=False, label="Search")
    category  = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    location  = forms.CharField(required=False)
    max_price = forms.DecimalField(required=False, min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["q"].widget.attrs.update({
            "class": "field-input",
            "placeholder": "Search items, e.g. canopy, shop, gele",
        })
        self.fields["category"].widget.attrs.update({"class": "field-input"})
        self.fields["category"].empty_label = "All categories"
        # Combobox: plain text input enhanced by JS with a floating popover
        self.fields["location"].widget.attrs.update({
            "class": "field-input location-combobox-input",
            "placeholder": "Any location",
            "autocomplete": "off",
            "data-combobox": "location",
        })
        self.fields["max_price"].widget.attrs.update({
            "class": "field-input",
            "placeholder": "Max price",
        })
