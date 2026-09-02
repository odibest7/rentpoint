from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction as db_transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import OwnerVerification, User
from listings.models import Category, Item
from transactions.models import Transaction
from wallet.models import Wallet, WithdrawalRequest


@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    customer_count = User.objects.filter(role=User.Role.CUSTOMER).count()
    owner_count = User.objects.filter(role=User.Role.ITEM_OWNER).count()

    total_items = Item.objects.count()
    available_items = Item.objects.filter(is_available=True).count()

    total_volume = Transaction.objects.filter(status=Transaction.Status.PAID).aggregate(
        total=Sum("amount")
    )["total"] or 0

    pending_withdrawals_count = WithdrawalRequest.objects.filter(
        status=WithdrawalRequest.Status.PENDING
    ).count()

    pending_withdrawals_sum = WithdrawalRequest.objects.filter(
        status=WithdrawalRequest.Status.PENDING
    ).aggregate(total=Sum("amount"))["total"] or 0

    pending_verifications_count = User.objects.filter(
        verification_status=User.VerificationStatus.PENDING
    ).count()
    verified_owner_count = User.objects.filter(
        verification_status=User.VerificationStatus.VERIFIED
    ).count()

    recent_transactions = Transaction.objects.select_related("item", "customer", "owner")[:6]
    recent_users = User.objects.order_by("-date_joined")[:5]

    context = {
        "total_users": total_users,
        "customer_count": customer_count,
        "owner_count": owner_count,
        "total_items": total_items,
        "available_items": available_items,
        "total_volume": total_volume,
        "pending_withdrawals_count": pending_withdrawals_count,
        "pending_withdrawals_sum": pending_withdrawals_sum,
        "pending_verifications_count": pending_verifications_count,
        "verified_owner_count": verified_owner_count,
        "recent_transactions": recent_transactions,
        "recent_users": recent_users,
    }
    return render(request, "site_admin/dashboard.html", context)


@staff_member_required
def admin_users(request):
    query = request.GET.get("q", "").strip()
    role_filter = request.GET.get("role", "").strip()

    users = User.objects.all().order_by("-date_joined")
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone_number__icontains=query)
        )
    if role_filter in [User.Role.CUSTOMER, User.Role.ITEM_OWNER]:
        users = users.filter(role=role_filter)

    context = {
        "users": users,
        "query": query,
        "role_filter": role_filter,
    }
    return render(request, "site_admin/users.html", context)


@staff_member_required
def admin_user_toggle_staff(request, user_id):
    if request.method != "POST":
        return redirect("core:admin_users")

    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot modify your own staff privileges.")
        return redirect("core:admin_users")

    target_user.is_staff = not target_user.is_staff
    target_user.save()
    status_str = "granted" if target_user.is_staff else "revoked"
    messages.success(request, f"Staff privileges {status_str} for {target_user.username}.")
    return redirect("core:admin_users")


@staff_member_required
def admin_listings(request):
    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    status_filter = request.GET.get("status", "").strip()

    items = Item.objects.select_related("category", "owner").order_by("-created_at")
    if query:
        items = items.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query))
    if category_id.isdigit():
        items = items.filter(category_id=category_id)
    if status_filter == "available":
        items = items.filter(is_available=True)
    elif status_filter == "unavailable":
        items = items.filter(is_available=False)

    categories = Category.objects.all()

    context = {
        "items": items,
        "categories": categories,
        "query": query,
        "category_id": category_id,
        "status_filter": status_filter,
    }
    return render(request, "site_admin/listings.html", context)


@staff_member_required
def admin_listing_toggle_available(request, slug):
    if request.method != "POST":
        return redirect("core:admin_listings")

    item = get_object_or_404(Item, slug=slug)
    item.is_available = not item.is_available
    item.save(update_fields=["is_available"])
    status_str = "available" if item.is_available else "unavailable"
    messages.success(request, f"Listing '{item.name}' marked as {status_str}.")
    return redirect("core:admin_listings")


@staff_member_required
def admin_transactions(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    transactions = Transaction.objects.select_related("item", "customer", "owner").order_by("-created_at")
    if query:
        transactions = transactions.filter(
            Q(reference__icontains=query)
            | Q(item__name__icontains=query)
            | Q(customer__username__icontains=query)
            | Q(owner__username__icontains=query)
        )
    if status_filter in [Transaction.Status.PAID, Transaction.Status.PENDING, Transaction.Status.FAILED]:
        transactions = transactions.filter(status=status_filter)

    context = {
        "transactions": transactions,
        "query": query,
        "status_filter": status_filter,
    }
    return render(request, "site_admin/transactions.html", context)


@staff_member_required
def admin_withdrawals(request):
    status_filter = request.GET.get("status", "").strip()

    withdrawals = WithdrawalRequest.objects.select_related("owner").order_by("-requested_at")
    if status_filter in [WithdrawalRequest.Status.PENDING, WithdrawalRequest.Status.APPROVED, WithdrawalRequest.Status.REJECTED]:
        withdrawals = withdrawals.filter(status=status_filter)

    context = {
        "withdrawals": withdrawals,
        "status_filter": status_filter,
    }
    return render(request, "site_admin/withdrawals.html", context)


@staff_member_required
def admin_withdrawal_action(request, withdrawal_id, action):
    if request.method != "POST":
        return redirect("core:admin_withdrawals")

    withdrawal = get_object_or_404(WithdrawalRequest, id=withdrawal_id)
    if withdrawal.status != WithdrawalRequest.Status.PENDING:
        messages.warning(request, "This withdrawal request has already been processed.")
        return redirect("core:admin_withdrawals")

    if action == "approve":
        with db_transaction.atomic():
            withdrawal = WithdrawalRequest.objects.select_for_update().get(pk=withdrawal.pk)
            wallet, _ = Wallet.objects.select_for_update().get_or_create(owner=withdrawal.owner)
            if withdrawal.status != WithdrawalRequest.Status.PENDING:
                messages.warning(request, "This withdrawal request has already been processed.")
                return redirect("core:admin_withdrawals")
            if wallet.balance < withdrawal.amount:
                messages.error(request, "This withdrawal cannot be approved because the owner's balance is insufficient.")
                return redirect("core:admin_withdrawals")
            withdrawal.status = WithdrawalRequest.Status.APPROVED
            withdrawal.resolved_at = timezone.now()
            withdrawal.save(update_fields=["status", "resolved_at"])
            wallet.debit(withdrawal.amount)
        messages.success(request, f"Approved payout of ₦{withdrawal.amount:,.2f} for {withdrawal.owner.username}.")
    elif action == "reject":
        wallet, _ = Wallet.objects.get_or_create(owner=withdrawal.owner)
        withdrawal.status = WithdrawalRequest.Status.REJECTED
        withdrawal.save()
        # Refund balance back to owner wallet
        wallet.balance += withdrawal.amount
        wallet.save()
        messages.info(request, f"Rejected payout of ₦{withdrawal.amount:,.2f}. Funds returned to owner wallet.")

    return redirect("core:admin_withdrawals")


@staff_member_required
def admin_categories(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        icon = request.POST.get("icon", "").strip()
        if not name:
            messages.error(request, "Category name cannot be empty.")
            return redirect("core:admin_categories")

        slug = slugify(name)
        if Category.objects.filter(slug=slug).exists():
            messages.error(request, f"A category with name '{name}' already exists.")
            return redirect("core:admin_categories")

        Category.objects.create(name=name, slug=slug, icon=icon)
        messages.success(request, f"Category '{name}' created successfully.")
        return redirect("core:admin_categories")

    categories = Category.objects.annotate(item_count=Count("items")).order_by("name")
    context = {"categories": categories}
    return render(request, "site_admin/categories.html", context)


@staff_member_required
def admin_category_delete(request, category_id):
    if request.method != "POST":
        return redirect("core:admin_categories")

    category = get_object_or_404(Category, id=category_id)
    if category.items.exists():
        messages.error(request, f"Cannot delete category '{category.name}' because it contains active listings.")
        return redirect("core:admin_categories")

    name = category.name
    category.delete()
    messages.success(request, f"Category '{name}' deleted.")
    return redirect("core:admin_categories")


@staff_member_required
def admin_verifications(request):
    """The identity verification review queue: every item owner who has
    submitted a NIN, filterable by where their submission currently
    stands. This is a manual review by design (see accounts/verification.py),
    ensuring every entry is verified by staff."""
    status_filter = request.GET.get("status", "").strip()

    submissions = OwnerVerification.objects.select_related("owner", "reviewed_by").order_by("-submitted_at")
    if status_filter in [
        User.VerificationStatus.PENDING,
        User.VerificationStatus.VERIFIED,
        User.VerificationStatus.REJECTED,
    ]:
        submissions = submissions.filter(owner__verification_status=status_filter)

    context = {
        "submissions": submissions,
        "status_filter": status_filter,
    }
    return render(request, "site_admin/verifications.html", context)


@staff_member_required
def admin_verification_action(request, submission_id, action):
    if request.method != "POST":
        return redirect("core:admin_verifications")

    submission = get_object_or_404(OwnerVerification, id=submission_id)
    owner = submission.owner

    if owner.verification_status != User.VerificationStatus.PENDING:
        messages.warning(request, "This submission has already been reviewed.")
        return redirect("core:admin_verifications")

    submission.reviewed_at = timezone.now()
    submission.reviewed_by = request.user

    if action == "approve":
        owner.verification_status = User.VerificationStatus.VERIFIED
        submission.rejection_reason = ""
        messages.success(request, f"{owner.get_full_name() or owner.username} is now a verified owner.")
    elif action == "reject":
        reason = request.POST.get("reason", "").strip()
        owner.verification_status = User.VerificationStatus.REJECTED
        submission.rejection_reason = reason or "The submitted details could not be confirmed."
        messages.info(request, f"Verification for {owner.username} was rejected.")
    else:
        messages.error(request, "Unknown verification action.")
        return redirect("core:admin_verifications")

    owner.save(update_fields=["verification_status"])
    submission.save(update_fields=["reviewed_at", "reviewed_by", "rejection_reason"])
    return redirect("core:admin_verifications")
