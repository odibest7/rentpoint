"""
Payment gateway abstraction.

The report calls for "a secure electronic payment mechanism" without
tying the system to one specific provider. This module keeps that
decision out of the views: a view calls ``get_gateway()`` and works
against a small, provider-independent interface. Today only a mock
provider is implemented, which simulates a successful payment so the
full rental-to-earnings flow can be reviewed end to end without live
payment credentials. A real provider (Paystack, Flutterwave, or any
other gateway used in Nigeria) can be dropped in by implementing the
same two methods and switching PAYMENT_GATEWAY_PROVIDER in settings.
"""

import uuid
from dataclasses import dataclass

from django.conf import settings


@dataclass
class PaymentResult:
    success: bool
    provider_reference: str
    message: str


class BasePaymentGateway:
    provider_name = "base"

    def charge(self, *, amount, email, reference) -> PaymentResult:
        raise NotImplementedError

    def verify(self, provider_reference) -> PaymentResult:
        raise NotImplementedError


class MockPaymentGateway(BasePaymentGateway):
    """
    Simulates an electronic payment channel. Every charge succeeds
    immediately, which is appropriate for demonstrations, coursework
    evaluation, and local development. Nothing here touches real money.
    """

    provider_name = "mock"

    def charge(self, *, amount, email, reference):
        provider_reference = f"MOCK-{uuid.uuid4().hex[:12].upper()}"
        return PaymentResult(
            success=True,
            provider_reference=provider_reference,
            message="Payment approved by simulated gateway.",
        )

    def verify(self, provider_reference):
        return PaymentResult(
            success=True,
            provider_reference=provider_reference,
            message="Payment verified.",
        )


def get_gateway() -> BasePaymentGateway:
    provider = getattr(settings, "PAYMENT_GATEWAY_PROVIDER", "mock")
    if provider == "mock":
        return MockPaymentGateway()
    raise NotImplementedError(
        f"Payment provider '{provider}' is not wired up yet. "
        "Implement it in transactions/services.py and register it here."
    )
