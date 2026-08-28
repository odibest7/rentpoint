from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ItemForm, ItemImageFormSet, ItemSearchForm
from .models import Category, Item


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
    return request.user.is_authenticated and request.user.is_item_owner


@login_required
def owner_item_list(request):
    if not _require_item_owner(request):
        messages.error(request, "Only item owner accounts can manage listings.")
        return redirect("core:redirect_after_login")

    items = request.user.items.select_related("category")
    return render(request, "listings/owner_item_list.html", {"items": items})


@login_required
def item_create(request):
    if not _require_item_owner(request):
        messages.error(request, "Only item owner accounts can create listings.")
        return redirect("core:redirect_after_login")

    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()
            formset = ItemImageFormSet(request.POST, request.FILES, instance=item)
            if formset.is_valid():
                formset.save()
            messages.success(request, f'"{item.name}" has been listed.')
            return redirect("listings:owner_item_list")
        formset = ItemImageFormSet(request.POST, request.FILES)
    else:
        form = ItemForm()
        formset = ItemImageFormSet()

    return render(request, "listings/item_form.html", {"form": form, "formset": formset, "is_new": True})


@login_required
def item_update(request, slug):
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
