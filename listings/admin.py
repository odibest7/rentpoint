from django.contrib import admin

from .models import Category, Item, ItemImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "category", "rental_price", "price_unit", "is_available", "created_at")
    list_filter = ("category", "is_available", "condition")
    search_fields = ("name", "description", "owner__username")
    inlines = [ItemImageInline]
