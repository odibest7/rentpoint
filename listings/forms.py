from django import forms
from django.forms import inlineformset_factory

from .models import Category, Item, ItemImage


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
            "category": forms.Select(attrs={"class": "field-input"}),
            "name": forms.TextInput(attrs={"class": "field-input", "placeholder": "e.g. White plastic chairs (set of 50)"}),
            "description": forms.Textarea(attrs={"class": "field-input", "rows": 5, "placeholder": "Describe the item, its condition, and what is included."}),
            "rental_price": forms.NumberInput(attrs={"class": "field-input", "placeholder": "0.00", "step": "0.01"}),
            "price_unit": forms.Select(attrs={"class": "field-input"}),
            "condition": forms.Select(attrs={"class": "field-input"}),
            "location": forms.TextInput(attrs={"class": "field-input", "placeholder": "e.g. Odenigbo, Nsukka"}),
            "quantity_available": forms.NumberInput(attrs={"class": "field-input", "min": 1}),
            "is_available": forms.CheckboxInput(attrs={"class": "field-checkbox"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self.fields["category"].empty_label = "Select a category"


ItemImageFormSet = inlineformset_factory(
    Item,
    ItemImage,
    fields=["image", "position"],
    extra=1,
    max_num=8,
    can_delete=True,
    widgets={
        "image": forms.FileInput(attrs={"class": "photo-file-input", "accept": "image/*"}),
        "position": forms.HiddenInput(attrs={"class": "photo-position-input", "value": "0"}),
    },
)


class ItemSearchForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    location = forms.CharField(required=False)
    max_price = forms.DecimalField(required=False, min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["q"].widget.attrs.update({"class": "field-input", "placeholder": "Search items, e.g. canopy, shop, gele"})
        self.fields["category"].widget.attrs.update({"class": "field-input"})
        self.fields["category"].empty_label = "All categories"
        self.fields["location"].widget.attrs.update({"class": "field-input", "placeholder": "Location"})
        self.fields["max_price"].widget.attrs.update({"class": "field-input", "placeholder": "Max price"})
