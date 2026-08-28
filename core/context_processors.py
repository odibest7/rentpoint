from django.conf import settings


def site_settings(request):
    """Exposes a small set of branding values to every template so the
    platform name and service area are never hard-coded twice."""
    return {
        "PLATFORM_NAME": settings.PLATFORM_NAME,
        "PLATFORM_SERVICE_AREA": settings.PLATFORM_SERVICE_AREA,
    }
