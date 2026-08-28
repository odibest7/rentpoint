from django import forms

from listings.models import Item


class RentalRequestForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)
    duration = forms.IntegerField(min_value=1, initial=1)

    def __init__(self, *args, item: Item, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item
        self.fields["quantity"].widget.attrs.update({"class": "field-input", "max": item.quantity_available})
        self.fields["duration"].widget.attrs.update({"class": "field-input"})
        self.fields["quantity"].help_text = f"{item.quantity_available} available"
        self.fields["duration"].help_text = f"Priced {item.get_price_unit_display()}"

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity > self.item.quantity_available:
            raise forms.ValidationError("That quantity is not available for this item.")
        return quantity
