"""
Item owner identity verification.

Trust between customers and item owners is one of the concerns the
project report raises directly. Letting an item owner submit their NIN
(National Identification Number) and having it checked against NIMC's
records is the standard way Nigerian platforms build that trust, but
NIMC does not expose a free public verification endpoint — real
verification requires a paid third-party provider such as Prembly,
VerifyMe, or Youverify.

This module keeps that decision out of the views, the same way
transactions/services.py keeps the payment provider out of the checkout
view: a view calls get_verification_provider() and works against a
small, provider-independent interface.

Unlike payments, there is no safe "auto-approve" default here. Wrongly
telling a customer an owner is verified is worse than not verifying
anyone at all, so the default provider (ManualReviewProvider) never
auto-approves anything — it only records the submission and leaves the
owner's status at "pending" for a member of staff to review by hand,
via the site-admin verification queue. Swapping in a real provider is a
matter of implementing the same interface and changing
NIN_VERIFICATION_PROVIDER in settings.
"""

from dataclasses import dataclass

from django.conf import settings


@dataclass
class VerificationCheckResult:
    """What a provider reports back after looking at a submission.

    auto_decision is intentionally not a plain boolean: "pending" (the
    manual-review default) is a distinct outcome from "verified" or
    "rejected", and views should not have to guess what an absent
    decision means.
    """

    auto_decision: str  # "pending", "verified", or "rejected"
    message: str


class BaseVerificationProvider:
    provider_name = "base"

    def check(self, *, full_legal_name: str, nin: str) -> VerificationCheckResult:
        raise NotImplementedError


class ManualReviewProvider(BaseVerificationProvider):
    """
    Records the submission and defers the decision entirely to a staff
    member. This is the only provider implemented today, and it is the
    safe default: no automated system here is allowed to claim someone's
    identity has been confirmed.
    """

    provider_name = "manual"

    def check(self, *, full_legal_name: str, nin: str) -> VerificationCheckResult:
        return VerificationCheckResult(
            auto_decision="pending",
            message="Submitted for manual review by RentPoint staff.",
        )


def get_verification_provider() -> BaseVerificationProvider:
    provider = getattr(settings, "NIN_VERIFICATION_PROVIDER", "manual")
    if provider == "manual":
        return ManualReviewProvider()
    raise NotImplementedError(
        f"NIN verification provider '{provider}' is not wired up yet. "
        "Implement it in accounts/verification.py and register it here, "
        "the same way a real payment gateway would be added in "
        "transactions/services.py."
    )
