from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


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
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "field-input",
                    "placeholder": placeholders.get(field_name, ""),
                    "autocomplete": "off",
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
            {"class": "field-input", "placeholder": "Username", "autofocus": True}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "field-input", "placeholder": "Password"}
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
