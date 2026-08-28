from django import forms
from django.conf import settings

from .models import WithdrawalRequest


class WithdrawalRequestForm(forms.ModelForm):
    class Meta:
        model = WithdrawalRequest
        fields = ["amount", "bank_name", "account_number", "account_name"]
        widgets = {
            "amount": forms.NumberInput(attrs={"class": "field-input", "step": "0.01", "placeholder": "0.00"}),
            "bank_name": forms.TextInput(attrs={"class": "field-input", "placeholder": "e.g. GTBank"}),
            "account_number": forms.TextInput(attrs={"class": "field-input", "placeholder": "10-digit account number"}),
            "account_name": forms.TextInput(attrs={"class": "field-input", "placeholder": "Name on the account"}),
        }

    def __init__(self, *args, wallet=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.wallet = wallet

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        minimum = settings.MINIMUM_WITHDRAWAL_AMOUNT
        if amount < minimum:
            raise forms.ValidationError(f"The minimum withdrawal amount is ₦{minimum:,.2f}.")
        if self.wallet and amount > self.wallet.balance:
            raise forms.ValidationError("You cannot withdraw more than your available balance.")
        return amount
