"""
Payment gateway abstraction.

The report calls for "a secure electronic payment mechanism" without
tying the system to one specific provider. This module keeps that
decision out of the views: a view calls ``get_gateway()`` and works
against a small, provider-independent interface.

Providers
---------
mock     — simulates a successful payment with no real money. Default for
           local development and coursework evaluation.
paystack — live Paystack payments (Nigerian NGN). Set
           PAYMENT_GATEWAY_PROVIDER=paystack and supply real API keys.
           The Paystack flow is redirect-based (initialize -> redirect to
           Paystack checkout page -> callback URL -> verify).
"""

import uuid
from dataclasses import dataclass

import urllib.request
import urllib.error
import json

from django.conf import settings


@dataclass
class PaymentResult:
    success: bool
    provider_reference: str
    message: str
    # For redirect-based gateways: the URL the browser should visit to pay
    redirect_url: str = ""


class BasePaymentGateway:
    provider_name = "base"

    def charge(self, *, amount, email, reference) -> PaymentResult:
        """
        Initiate payment.
        For inline gateways: performs the charge immediately.
        For redirect gateways: returns a redirect_url for the user.
        """
        raise NotImplementedError

    def verify(self, provider_reference) -> PaymentResult:
        """Verify a payment reference with the provider."""
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


class PaystackGateway(BasePaymentGateway):
    """
    Live Paystack integration (https://paystack.com).

    How the flow works:
    1. call charge() — this calls Paystack's Initialize Transaction API
       and returns a redirect_url pointing to Paystack's hosted checkout.
    2. The view redirects the customer to redirect_url.
    3. After the customer pays (or cancels), Paystack redirects back to
       the callback URL you set in your Paystack dashboard, or to the
       PAYSTACK_CALLBACK_URL env variable.
    4. The callback view calls verify() with the Paystack reference to
       confirm the payment was actually successful.

    Required environment variables:
        PAYSTACK_SECRET_KEY   — starts with sk_live_... (production)
                                or sk_test_... (testing mode)
        PAYSTACK_PUBLIC_KEY   — starts with pk_live_... or pk_test_...
        PAYSTACK_CALLBACK_URL — full URL where Paystack should redirect after
                                payment, e.g. https://yourdomain.com/transactions/paystack/callback/
    """

    provider_name = "paystack"
    _BASE = "https://api.paystack.co"

    def _secret_key(self):
        key = getattr(settings, "PAYSTACK_SECRET_KEY", "")
        if not key:
            raise ValueError(
                "PAYSTACK_SECRET_KEY is not set. Add it to your .env file."
            )
        return key

    def _request(self, method, path, body=None):
        """Minimal HTTP helper — avoids adding requests as a dependency."""
        url = f"{self._BASE}{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self._secret_key()}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            return json.loads(exc.read())

    def charge(self, *, amount, email, reference):
        """
        Initialize a Paystack transaction.
        amount must be in Naira; this converts to kobo before sending.
        """
        callback_url = getattr(settings, "PAYSTACK_CALLBACK_URL", "")
        payload = {
            "email": email,
            "amount": int(amount * 100),   # Paystack expects kobo (1 NGN = 100 kobo)
            "reference": str(reference),
            "currency": "NGN",
        }
        if callback_url:
            payload["callback_url"] = callback_url

        data = self._request("POST", "/transaction/initialize", payload)

        if data.get("status"):
            auth_data = data.get("data", {})
            return PaymentResult(
                success=True,
                provider_reference=auth_data.get("reference", str(reference)),
                message="Paystack checkout initialized.",
                redirect_url=auth_data.get("authorization_url", ""),
            )

        return PaymentResult(
            success=False,
            provider_reference=str(reference),
            message=data.get("message", "Paystack initialization failed."),
        )

    def verify(self, provider_reference):
        """Confirm a completed payment with Paystack's verify endpoint."""
        data = self._request("GET", f"/transaction/verify/{provider_reference}")

        if data.get("status") and data.get("data", {}).get("status") == "success":
            return PaymentResult(
                success=True,
                provider_reference=provider_reference,
                message="Payment confirmed by Paystack.",
            )

        return PaymentResult(
            success=False,
            provider_reference=provider_reference,
            message=data.get("data", {}).get("gateway_response", "Payment not confirmed."),
        )


def get_gateway() -> BasePaymentGateway:
    provider = getattr(settings, "PAYMENT_GATEWAY_PROVIDER", "mock")
    if provider == "mock":
        return MockPaymentGateway()
    if provider == "paystack":
        return PaystackGateway()
    raise NotImplementedError(
        f"Payment provider '{provider}' is not wired up yet. "
        "Implement it in transactions/services.py and register it in get_gateway()."
    )
