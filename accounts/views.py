from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import LoginForm, ProfileForm, SignUpForm
from .models import User


def signup_customer(request):
    return _signup(request, role=User.Role.CUSTOMER)


def signup_item_owner(request):
    return _signup(request, role=User.Role.ITEM_OWNER)


def _signup(request, role):
    """Shared registration handler for both account types."""
    if request.user.is_authenticated:
        return redirect("core:redirect_after_login")

    if request.method == "POST":
        form = SignUpForm(request.POST, role=role)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to RentPoint, {user.first_name}.")
            return redirect("core:redirect_after_login")
    else:
        form = SignUpForm(role=role)

    context = {
        "form": form,
        "role": role,
        "is_item_owner_signup": role == User.Role.ITEM_OWNER,
    }
    return render(request, "accounts/signup.html", context)


class RentPointLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class RentPointLogoutView(LogoutView):
    next_page = "core:home"


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})
