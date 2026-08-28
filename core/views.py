from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from listings.models import Category, Item


def home(request):
    featured_items = (
        Item.objects.filter(is_available=True).select_related("category", "owner")[:8]
    )
    categories = Category.objects.all()[:8]
    context = {
        "featured_items": featured_items,
        "categories": categories,
        "item_count": Item.objects.filter(is_available=True).count(),
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html")


def how_it_works(request):
    return render(request, "core/how_it_works.html")


@login_required
def redirect_after_login(request):
    if request.user.is_item_owner:
        return redirect("listings:owner_item_list")
    return redirect("listings:item_list")


def custom_404(request, exception):
    return render(request, "core/404.html", status=404)


def custom_500(request):
    return render(request, "core/500.html", status=500)
