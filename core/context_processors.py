from django.conf import settings
from accounts.models import User
from wallet.models import WithdrawalRequest

def site_settings(request):
    """Exposes a small set of branding values to every template so the
    platform name and service area are never hard-coded twice."""
    return {
        "PLATFORM_NAME": settings.PLATFORM_NAME,
        "PLATFORM_SERVICE_AREA": settings.PLATFORM_SERVICE_AREA,
        "PLATFORM_COMMISSION_PERCENT": settings.PLATFORM_COMMISSION_PERCENT,
        "PAYSTACK_PUBLIC_KEY": settings.PAYSTACK_PUBLIC_KEY,
        "pending_withdrawals_count": WithdrawalRequest.objects.filter(
            status=WithdrawalRequest.Status.PENDING
        ).count(),
        "pending_verifications_count": User.objects.filter(
            verification_status=User.VerificationStatus.PENDING
        ).count(),
    }
