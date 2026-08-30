import logging
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from listings.models import Item
from wallet.models import Wallet

from .forms import RentalRequestForm
from .models import Transaction
from .services import get_gateway

logger = logging.getLogger(__name__)


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
        form = RentalRequestForm(request.POST, item=item, user=request.user)
        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            duration = form.cleaned_data["duration"]
            amount = item.rental_price * quantity * duration
            contact_phone = form.cleaned_data["contact_phone"]
            delivery_address = form.cleaned_data.get("delivery_address", "")
            delivery_option = form.cleaned_data["delivery_option"]
            pickup_notes = form.cleaned_data.get("pickup_notes", "")

            # Automatically persist contact details to user profile if empty
            if not request.user.phone_number and contact_phone:
                request.user.phone_number = contact_phone
                request.user.save(update_fields=["phone_number"])
            if not request.user.address and delivery_address:
                request.user.address = delivery_address
                request.user.save(update_fields=["address"])

            transaction = Transaction.objects.create(
                customer=request.user,
                item=item,
                owner=item.owner,
                quantity=quantity,
                duration=duration,
                amount=amount,
                delivery_option=delivery_option,
                delivery_address=delivery_address,
                contact_phone=contact_phone,
                pickup_notes=pickup_notes,
            )
            return redirect("transactions:checkout", reference=transaction.reference)
    else:
        form = RentalRequestForm(item=item, user=request.user)

    return render(request, "transactions/start_rental.html", {"form": form, "item": item})


@login_required
def checkout(request, reference):
    transaction = get_object_or_404(Transaction, reference=reference, customer=request.user)

    if transaction.status == Transaction.Status.PAID:
        return redirect("transactions:receipt", reference=transaction.reference)

    return render(request, "transactions/checkout.html", {"transaction": transaction})


@require_POST
@login_required
def paystack_verify(request):
    reference = request.POST.get("reference") or request.GET.get("reference")
    if not reference:
        return JsonResponse({"success": False, "message": "Missing payment reference."}, status=400)

    transaction = get_object_or_404(Transaction, reference=reference, customer=request.user)
    if transaction.status == Transaction.Status.PAID:
        return JsonResponse({"success": True, "redirect_url": reverse("transactions:receipt", args=[transaction.reference])})

    gateway = get_gateway()
    result = gateway.verify(reference)
    if result.success:
        _mark_transaction_paid(transaction, gateway.provider_name, result.provider_reference)
        return JsonResponse({"success": True, "redirect_url": reverse("transactions:receipt", args=[transaction.reference])})

    logger.error(
        "Paystack verification failed via AJAX for transaction=%s gateway=%s provider_reference=%s message=%s",
        transaction.reference,
        gateway.provider_name,
        result.provider_reference,
        result.message,
    )
    # A failed verification can be a transient provider or network error.
    # Keep the order pending so the customer can retry instead of turning a
    # successfully paid Paystack transaction into a terminal failed state.
    return JsonResponse({"success": False, "message": result.message}, status=400)


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


@require_GET
def paystack_callback(request):
    reference = request.GET.get("reference") or request.GET.get("trxref")
    transaction = get_object_or_404(Transaction, reference=reference)
    if transaction.status == Transaction.Status.PAID:
        return redirect("transactions:receipt", reference=transaction.reference)

    gateway = get_gateway()
    if gateway.provider_name != "paystack":
        messages.error(request, "Paystack callback received while Paystack is not the active gateway.")
        return redirect("transactions:checkout", reference=transaction.reference)

    result = gateway.verify(reference)
    if result.success:
        _mark_transaction_paid(transaction, gateway.provider_name, result.provider_reference)
        messages.success(request, "Payment verified successfully. Your receipt is ready below.")
        return redirect("transactions:receipt", reference=transaction.reference)

    logger.error(
        "Paystack verification failed for transaction=%s gateway=%s provider_reference=%s message=%s",
        transaction.reference,
        gateway.provider_name,
        result.provider_reference,
        result.message,
    )
    messages.error(request, f"Paystack could not verify this payment: {result.message}")
    return redirect("transactions:checkout", reference=transaction.reference)

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
        transactions = list(
            Transaction.objects.filter(owner=request.user)
            .select_related("item", "customer", "item__category")
            .prefetch_related("item__images")
        )
        paid_transactions = [t for t in transactions if t.status == Transaction.Status.PAID]
        context = {
            "transactions": transactions,
            "total_earnings": sum(t.owner_earning for t in paid_transactions),
            "paid_count": len(paid_transactions),
            "pending_count": sum(1 for t in transactions if t.status == Transaction.Status.PENDING),
            "total_count": len(transactions),
        }
    else:
        transactions = list(
            Transaction.objects.filter(customer=request.user)
            .select_related("item", "owner", "item__category")
            .prefetch_related("item__images")
        )
        paid_transactions = [t for t in transactions if t.status == Transaction.Status.PAID]
        context = {
            "transactions": transactions,
            "total_spent": sum(t.amount for t in paid_transactions),
            "paid_count": len(paid_transactions),
            "pending_count": sum(1 for t in transactions if t.status == Transaction.Status.PENDING),
            "total_count": len(transactions),
        }
    return render(request, "transactions/transaction_list.html", context)
