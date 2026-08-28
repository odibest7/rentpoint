from django import forms

from listings.models import Item


class RentalRequestForm(forms.Form):
    DELIVERY_CHOICES = [
        ("pickup", "Self-Pickup at Owner's Location"),
        ("delivery", "Request Delivery to My Address"),
    ]

    quantity = forms.IntegerField(min_value=1, initial=1, label="Quantity")
    duration = forms.IntegerField(min_value=1, initial=1, label="Duration")
    delivery_option = forms.ChoiceField(
        choices=DELIVERY_CHOICES,
        initial="pickup",
        label="Fulfillment / Pickup Method",
        widget=forms.Select(attrs={"class": "field-input"}),
    )
    contact_phone = forms.CharField(
        max_length=30,
        required=True,
        label="Your Contact Phone Number",
        widget=forms.TextInput(attrs={"class": "field-input", "placeholder": "e.g. 08012345678"}),
        help_text="Item owner will reach you on this number to coordinate pickup or delivery.",
    )
    delivery_address = forms.CharField(
        max_length=255,
        required=False,
        label="Delivery Address / Specific Area",
        widget=forms.TextInput(attrs={"class": "field-input", "placeholder": "e.g. 14 University Road, Odenigbo, Nsukka"}),
        help_text="Required if requesting delivery. If picking up, you can leave this blank.",
    )
    pickup_notes = forms.CharField(
        required=False,
        label="Special Instructions or Preferred Pickup Time",
        widget=forms.Textarea(attrs={"class": "field-input", "rows": 2, "placeholder": "e.g. Will pick up on Saturday by 10:00 AM"}),
    )

    def __init__(self, *args, item: Item, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item
        self.fields["quantity"].widget.attrs.update({"class": "field-input", "max": item.quantity_available})
        self.fields["duration"].widget.attrs.update({"class": "field-input"})
        self.fields["quantity"].help_text = f"{item.quantity_available} available in stock"
        self.fields["duration"].help_text = f"Priced per {item.get_price_unit_display()}"

        if user and not self.is_bound:
            if getattr(user, "phone_number", None):
                self.fields["contact_phone"].initial = user.phone_number
            if getattr(user, "address", None):
                self.fields["delivery_address"].initial = user.address

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity > self.item.quantity_available:
            raise forms.ValidationError("That quantity is not available for this item.")
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        delivery_option = cleaned_data.get("delivery_option")
        delivery_address = cleaned_data.get("delivery_address")

        if delivery_option == "delivery" and not delivery_address:
            self.add_error("delivery_address", "Please provide a delivery address when requesting direct delivery.")

        return cleaned_data
