from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import LoginForm, OwnerVerificationForm, ProfileForm, SignUpForm
from .models import OwnerVerification, User
from .verification import get_verification_provider


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


@login_required
def verification(request):
    """Lets an item owner submit their NIN for identity verification, and
    shows them the current status of that submission. A customer account
    has no verification of its own because verification exists to answer the
    question a customer asks before paying a stranger: "can I trust this
    item owner?", so this page is item-owner only."""
    if not request.user.is_item_owner:
        messages.error(request, "Identity verification is only for item owner accounts.")
        return redirect("core:redirect_after_login")

    existing = OwnerVerification.objects.filter(owner=request.user).first()
    can_submit = request.user.verification_status in (
        User.VerificationStatus.UNVERIFIED,
        User.VerificationStatus.REJECTED,
    )

    if request.method == "POST" and can_submit:
        form = OwnerVerificationForm(request.POST, request.FILES, instance=existing)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.owner = request.user
            submission.reviewed_at = None
            submission.reviewed_by = None
            submission.rejection_reason = ""
            submission.save()

            result = get_verification_provider().check(
                full_legal_name=submission.full_legal_name, nin=submission.nin
            )
            request.user.verification_status = User.VerificationStatus.PENDING
            request.user.save(update_fields=["verification_status"])

            messages.success(request, result.message)
            return redirect("accounts:verification")
    else:
        form = OwnerVerificationForm(instance=existing if can_submit else None)

    context = {
        "form": form,
        "existing": existing,
        "can_submit": can_submit,
    }
    return render(request, "accounts/verification.html", context)
