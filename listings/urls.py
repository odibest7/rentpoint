from django.urls import path

from . import views

app_name = "listings"

urlpatterns = [
    path("", views.item_list, name="item_list"),
    path("locations/", views.location_options, name="location_options"),
    path("mine/", views.owner_item_list, name="owner_item_list"),
    path("new/", views.item_create, name="item_create"),
    path("<slug:slug>/", views.item_detail, name="item_detail"),
    path("<slug:slug>/edit/", views.item_update, name="item_update"),
    path("<slug:slug>/delete/", views.item_delete, name="item_delete"),
]
