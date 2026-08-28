from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import WithdrawalRequestForm
from .models import Wallet, WithdrawalRequest


def _require_item_owner(request):
    return request.user.is_authenticated and request.user.is_item_owner


@login_required
def earnings(request):
    if not _require_item_owner(request):
        messages.error(request, "Only item owner accounts have an earnings wallet.")
        return redirect("core:redirect_after_login")

    wallet, _created = Wallet.objects.get_or_create(owner=request.user)
    withdrawals = request.user.withdrawal_requests.all()[:20]
    return render(request, "wallet/earnings.html", {"wallet": wallet, "withdrawals": withdrawals})


@login_required
def request_withdrawal(request):
    if not _require_item_owner(request):
        messages.error(request, "Only item owner accounts can request withdrawals.")
        return redirect("core:redirect_after_login")

    wallet, _created = Wallet.objects.get_or_create(owner=request.user)

    if request.method == "POST":
        form = WithdrawalRequestForm(request.POST, wallet=wallet)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.owner = request.user
            withdrawal.save()
            messages.success(
                request,
                f"Withdrawal request for ₦{withdrawal.amount:,.2f} has been submitted for review.",
            )
            return redirect("wallet:earnings")
    else:
        form = WithdrawalRequestForm(wallet=wallet)

    return render(request, "wallet/withdraw.html", {"form": form, "wallet": wallet})
