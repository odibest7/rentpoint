from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction as db_transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from core.utils import is_item_owner_request
from .forms import ItemForm, ItemImageFormSet, ItemSearchForm
from .models import Category, Item, NSUKKA_ZONES


def item_list(request):
    """Public catalogue of available items. Anyone can browse without an
    account, matching the report's aim of giving customers easy access to
    rental information before they commit to paying for anything."""
    items = Item.objects.filter(is_available=True).select_related("category", "owner")
    form = ItemSearchForm(request.GET or None)

    if form.is_valid():
        query = form.cleaned_data.get("q")
        category = form.cleaned_data.get("category")
        location = form.cleaned_data.get("location")
        max_price = form.cleaned_data.get("max_price")

        if query:
            items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))
        if category:
            items = items.filter(category=category)
        if location:
            items = items.filter(location__icontains=location)
        if max_price is not None:
            items = items.filter(rental_price__lte=max_price)

    paginator = Paginator(items, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "form": form,
        "page_obj": page_obj,
        "categories": Category.objects.all(),
    }
    return render(request, "listings/item_list.html", context)


def item_detail(request, slug):
    item = get_object_or_404(Item.objects.select_related("category", "owner"), slug=slug)
    related_items = (
        Item.objects.filter(category=item.category, is_available=True)
        .exclude(pk=item.pk)
        .select_related("category")[:4]
    )
    return render(request, "listings/item_detail.html", {"item": item, "related_items": related_items})


def _require_item_owner(request):
    return is_item_owner_request(request)


@login_required
def owner_item_list(request):
    if not _require_item_owner(request):
        messages.error(request, "Only item owner accounts can manage listings.")
        return redirect("core:redirect_after_login")

    items = request.user.items.select_related("category").prefetch_related("images")
    return render(request, "listings/owner_item_list.html", {"items": items})


@login_required
def item_create(request):
    if not _require_item_owner(request):
        messages.error(request, "Only item owner accounts can create listings.")
        return redirect("core:redirect_after_login")

    if request.method == "POST":
        form = ItemForm(request.POST)
        formset = ItemImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            with db_transaction.atomic():
                item = form.save(commit=False)
                item.owner = request.user
                item.save()
                formset.instance = item
                formset.save()
            messages.success(request, f'"{item.name}" has been listed.')
            return redirect("listings:owner_item_list")
    else:
        form = ItemForm()
        formset = ItemImageFormSet()

    return render(request, "listings/item_form.html", {"form": form, "formset": formset, "is_new": True})


@login_required
def item_update(request, slug):
    if not _require_item_owner(request):
        messages.error(request, "Only item owner accounts can manage listings.")
        return redirect("core:redirect_after_login")

    item = get_object_or_404(Item, slug=slug, owner=request.user)

    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        formset = ItemImageFormSet(request.POST, request.FILES, instance=item)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'"{item.name}" has been updated.')
            return redirect("listings:owner_item_list")
    else:
        form = ItemForm(instance=item)
        formset = ItemImageFormSet(instance=item)

    return render(request, "listings/item_form.html", {"form": form, "formset": formset, "item": item, "is_new": False})


@login_required
def item_delete(request, slug):
    item = get_object_or_404(Item, slug=slug, owner=request.user)
    if request.method == "POST":
        item_name = item.name
        item.delete()
        messages.success(request, f'"{item_name}" has been removed.')
        return redirect("listings:owner_item_list")
    return render(request, "listings/item_confirm_delete.html", {"item": item})



def location_options(request):
    """
    JSON endpoint for the catalogue location combobox.
    Returns canonical Nsukka zones with the count of available items that
    contain the zone name anywhere in their location field (icontains),
    so free-text values like 'Hilltop, Nsukka' are correctly matched to
    the 'Hilltop' zone.

    Query params:
      q  – optional search term to filter zone names (case-insensitive)
    """
    q = (request.GET.get("q") or "").strip()

    results = []
    for value, label in NSUKKA_ZONES:
        # Skip zones that don't match the search term
        if q and q.lower() not in label.lower():
            continue

        # Count items whose location field contains this zone name (icontains)
        # This handles stored values like "Hilltop, Nsukka" -> zone "Hilltop"
        item_count = (
            Item.objects
            .filter(is_available=True, location__icontains=value)
            .count()
        )

        # When the user is actively searching, include all matching zones
        # (even with 0 items) so they can see what exists.
        # When no search term, only show zones that actually have items.
        if not q and item_count == 0:
            continue

        results.append({"value": value, "label": label, "count": item_count})

    return JsonResponse({"results": results})
