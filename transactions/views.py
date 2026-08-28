from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from listings.models import Item
from wallet.models import Wallet

from .forms import RentalRequestForm
from .models import Transaction
from .services import get_gateway


@login_required
def start_rental(request, slug):
    """Step one: the customer chooses how much of an item to rent. This
    creates a pending Transaction, which becomes the permanent record the
    report describes, regardless of what happens at the payment step."""
    item = get_object_or_404(Item, slug=slug, is_available=True)

    if not request.user.is_customer:
        messages.error(request, "Only customer accounts can rent items. Sign in with a customer account.")
        return redirect("listings:item_detail", slug=slug)

    if item.owner_id == request.user.id:
        messages.error(request, "You cannot rent your own listing.")
        return redirect("listings:item_detail", slug=slug)

    if request.method == "POST":
        form = RentalRequestForm(request.POST, item=item)
        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            duration = form.cleaned_data["duration"]
            amount = item.rental_price * quantity * duration

            transaction = Transaction.objects.create(
                customer=request.user,
                item=item,
                owner=item.owner,
                quantity=quantity,
                duration=duration,
                amount=amount,
            )
            return redirect("transactions:checkout", reference=transaction.reference)
    else:
        form = RentalRequestForm(item=item)

    return render(request, "transactions/start_rental.html", {"form": form, "item": item})


@login_required
def checkout(request, reference):
    transaction = get_object_or_404(Transaction, reference=reference, customer=request.user)

    if transaction.status == Transaction.Status.PAID:
        return redirect("transactions:receipt", reference=transaction.reference)

    if request.method == "POST":
        gateway = get_gateway()
        result = gateway.charge(
            amount=transaction.amount,
            email=request.user.email,
            reference=transaction.reference,
        )
        if result.success:
            _mark_transaction_paid(transaction, gateway.provider_name, result.provider_reference)
            messages.success(request, "Payment successful. Your receipt is ready below.")
            return redirect("transactions:receipt", reference=transaction.reference)

        transaction.status = Transaction.Status.FAILED
        transaction.save(update_fields=["status"])
        messages.error(request, "The payment could not be completed. Please try again.")

    return render(request, "transactions/checkout.html", {"transaction": transaction})


def _mark_transaction_paid(transaction, provider_name, provider_reference):
    """Confirms payment, records the platform commission, and credits the
    item owner's wallet, all inside one atomic block so the money and the
    transaction record never fall out of sync."""
    commission_rate = Decimal(str(settings.PLATFORM_COMMISSION_PERCENT)) / Decimal("100")

    with db_transaction.atomic():
        commission = (transaction.amount * commission_rate).quantize(Decimal("0.01"))
        owner_earning = transaction.amount - commission

        transaction.status = Transaction.Status.PAID
        transaction.payment_provider = provider_name
        transaction.provider_reference = provider_reference
        transaction.commission_amount = commission
        transaction.owner_earning = owner_earning
        transaction.paid_at = timezone.now()
        transaction.save()

        wallet, _created = Wallet.objects.get_or_create(owner=transaction.owner)
        wallet.credit(owner_earning)


@login_required
def receipt(request, reference):
    transaction = get_object_or_404(Transaction, reference=reference)
    if request.user not in (transaction.customer, transaction.owner) and not request.user.is_staff:
        messages.error(request, "You do not have access to that receipt.")
        return redirect("core:redirect_after_login")
    return render(request, "transactions/receipt.html", {"transaction": transaction})


@login_required
def my_transactions(request):
    if request.user.is_item_owner:
        transactions = (
            Transaction.objects.filter(owner=request.user)
            .select_related("item", "customer", "item__category")
            .prefetch_related("item__images")
        )
        total_earnings = sum(t.owner_earning for t in transactions if t.status == Transaction.Status.PAID)
        paid_count = sum(1 for t in transactions if t.status == Transaction.Status.PAID)
        pending_count = sum(1 for t in transactions if t.status == Transaction.Status.PENDING)
        context = {
            "transactions": transactions,
            "total_earnings": total_earnings,
            "paid_count": paid_count,
            "pending_count": pending_count,
            "total_count": len(transactions),
        }
    else:
        transactions = (
            Transaction.objects.filter(customer=request.user)
            .select_related("item", "owner", "item__category")
            .prefetch_related("item__images")
        )
        total_spent = sum(t.amount for t in transactions if t.status == Transaction.Status.PAID)
        paid_count = sum(1 for t in transactions if t.status == Transaction.Status.PAID)
        pending_count = sum(1 for t in transactions if t.status == Transaction.Status.PENDING)
        context = {
            "transactions": transactions,
            "total_spent": total_spent,
            "paid_count": paid_count,
            "pending_count": pending_count,
            "total_count": len(transactions),
        }
    return render(request, "transactions/transaction_list.html", context)
