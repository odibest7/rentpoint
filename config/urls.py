"""
Root URL configuration for RentPoint.

Each domain of the system (accounts, listings, transactions, wallet, core
pages) owns its own urls.py and is included here under a clear prefix.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

def serve_media(request, path):
    return serve(request, path, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("listings/", include("listings.urls")),
    path("transactions/", include("transactions.urls")),
    path("wallet/", include("wallet.urls")),
    # Serve media files (item images, uploads) in both dev and production
    re_path(r"^media/(?P<path>.*)$", serve_media),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.custom_404"
handler500 = "core.views.custom_500"
