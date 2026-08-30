from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import OwnerVerification, User


class SignUpForm(UserCreationForm):
    """
    One registration form used by both customers and item owners. The role
    is passed in from the two distinct entry points (sign up as customer /
    sign up as item owner) rather than left for the visitor to self-select
    on the form itself, which keeps the choice deliberate.
    """

    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "username",
            "password1",
            "password2",
        ]

    def __init__(self, *args, role=User.Role.CUSTOMER, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        placeholders = {
            "first_name": "Chidera",
            "last_name": "Okafor",
            "email": "you@example.com",
            "phone_number": "080 000 0000",
            "username": "Choose a username",
            "password1": "Create a password",
            "password2": "Repeat your password",
        }
        autocomplete_map = {
            "first_name": "given-name",
            "last_name": "family-name",
            "email": "email",
            "phone_number": "tel",
            "username": "username",
            "password1": "new-password",
            "password2": "new-password",
        }
        for field_name, field in self.fields.items():
            classes = ["field-input"]
            if field_name in {"password1", "password2"}:
                classes.append("password-toggle-input")
            field.widget.attrs.update(
                {
                    "class": " ".join(classes),
                    "placeholder": placeholders.get(field_name, ""),
                    "autocomplete": autocomplete_map.get(field_name, "off"),
                }
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.role
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "field-input",
                "placeholder": "Username",
                "autofocus": True,
                "autocomplete": "username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "field-input password-toggle-input",
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_number", "address"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "field-input"}),
            "last_name": forms.TextInput(attrs={"class": "field-input"}),
            "email": forms.EmailInput(attrs={"class": "field-input"}),
            "phone_number": forms.TextInput(attrs={"class": "field-input"}),
            "address": forms.TextInput(attrs={"class": "field-input"}),
        }


class OwnerVerificationForm(forms.ModelForm):
    selfie_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={"id": "id_selfie_image", "accept": "image/*", "tabindex": "-1"}
        ),
    )
    nin_front_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/*", "capture": "environment"}),
    )
    nin_back_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/*", "capture": "environment"}),
    )
    """Collects sensitive NIN details, a live selfie, and both sides of the
    physical NIN card. New submissions require all three images; rejected
    owners may resubmit while retaining existing images unless replacements
    are supplied."""

    class Meta:
        model = OwnerVerification
        fields = ["full_legal_name", "nin", "selfie_image", "nin_front_image", "nin_back_image"]
        widgets = {
            "full_legal_name": forms.TextInput(
                attrs={"class": "field-input", "placeholder": "Full name as shown on your National ID"}
            ),
            "nin": forms.TextInput(
                attrs={
                    "class": "field-input",
                    "placeholder": "11-digit NIN",
                    "inputmode": "numeric",
                    "maxlength": "11",
                    "autocomplete": "off",
                }
            ),
        }

    def clean_nin(self):
        nin = self.cleaned_data["nin"].strip()
        if not nin.isdigit() or len(nin) != 11:
            raise forms.ValidationError("Enter the 11-digit NIN exactly as issued, digits only.")
        return nin

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk:
            required = {
                "selfie_image": "A live selfie is required.",
                "nin_front_image": "A front photo of the NIN card is required.",
                "nin_back_image": "A back photo of the NIN card is required.",
            }
            for field_name, message in required.items():
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, message)
        return cleaned_data
    def clean_selfie_image(self):
        return self.cleaned_data.get("selfie_image")

    def clean_nin_front_image(self):
        return self.cleaned_data.get("nin_front_image")

    def clean_nin_back_image(self):
        return self.cleaned_data.get("nin_back_image")
