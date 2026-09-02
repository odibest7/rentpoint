"""
Payment gateway abstraction.

The report calls for "a secure electronic payment mechanism" without
tying the system to one specific provider. This module keeps that
decision out of the views: a view calls ``get_gateway()`` and works
against a small, provider-independent interface.

Provider
--------
paystack: Live Paystack payments (Nigerian NGN). Supply the real API
          keys in the environment, then initialize hosted checkout,
          redirect back to the callback URL, and verify the payment.
"""

import json
import logging
import uuid
from dataclasses import dataclass
from urllib.parse import urlsplit
import urllib.error
import urllib.request


logger = logging.getLogger(__name__)

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

    def charge(self, *, amount, email, reference, callback_url=None) -> PaymentResult:
        """
        Initiate payment.
        For inline gateways: performs the charge immediately.
        For redirect gateways: returns a redirect_url for the user.
        """
        raise NotImplementedError

    def verify(self, provider_reference) -> PaymentResult:
        """Verify a payment reference with the provider."""
        raise NotImplementedError


class PaystackGateway(BasePaymentGateway):
    """
    Live Paystack integration (https://paystack.com).

    How the flow works:
    1. Call charge(): This calls the Paystack Initialize Transaction API
       and returns a redirect_url pointing to Paystack's hosted checkout.
    2. The view redirects the customer to redirect_url.
    3. After the customer pays (or cancels), Paystack redirects back to
       the callback URL for this app, generated from the current request.
    4. The callback view calls verify() with the Paystack reference to
       confirm the payment was actually successful.

    Required environment variables:
        PAYSTACK_SECRET_KEY: Starts with sk_live_... (production)
                             or sk_test_... (testing mode)
        PAYSTACK_PUBLIC_KEY: Starts with pk_live_... or pk_test_...
    """

    provider_name = "paystack"
    _BASE = "https://api.paystack.co"

    def _secret_key(self):
        key = getattr(settings, "PAYSTACK_SECRET_KEY", "")
        if not key:
            raise ValueError(
                "PAYSTACK_SECRET_KEY is not set. Add it to your .env file."
            )
        if not key.startswith(("sk_test_", "sk_live_")):
            raise ValueError("PAYSTACK_SECRET_KEY must be a Paystack test or live secret key.")
        return key
    def _request(self, method, path, body=None):
        """Minimal HTTP helper using standard library urllib."""
        url = f"{self._BASE}{path}"
        if urlsplit(url).scheme.lower() not in {"http", "https"}:
            raise ValueError("Payment gateway URL must use HTTP or HTTPS.")
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self._secret_key()}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "RentPoint/1.0 (+https://rentpoint.example)",
            },
            method=method,
        )
        try:
            opener = urllib.request.build_opener()
            with opener.open(req, timeout=15) as resp:
                raw_body = resp.read()
                return self._decode_response(raw_body, status=getattr(resp, "status", 200))
        except urllib.error.HTTPError as exc:
            raw_body = exc.read()
            decoded = self._decode_response(raw_body, status=exc.code)
            logger.error(
                "Paystack API request failed: method=%s path=%s http_status=%s response_body=%s",
                method,
                path,
                exc.code,
                raw_body.decode("utf-8", errors="replace"),
                exc_info=True,
            )
            decoded.setdefault("http_status", exc.code)
            decoded.setdefault("raw_body", raw_body.decode("utf-8", errors="replace"))
            return decoded
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            reason = getattr(exc, "reason", str(exc))
            message = f"Paystack connection failed: {reason}"
            logger.error(
                "Paystack API connection error: method=%s path=%s error=%s",
                method,
                path,
                exc,
                exc_info=True,
            )
            return {"status": False, "message": message, "http_status": None, "raw_body": str(exc)}

    @staticmethod
    def _decode_response(raw_body, status=200):
        try:
            return json.loads(raw_body)
        except (TypeError, ValueError):
            return {
                "status": False,
                "message": f"Paystack returned an invalid response (HTTP {status}).",
            }

    def charge(self, *, amount, email, reference, callback_url=None):
        """
        Initialize a Paystack transaction.
        amount must be in Naira; this converts to kobo before sending.
        The callback URL is generated from the current request so we do not
        require an extra env var for hosted-checkout redirects.
        """
        if callback_url:
            parsed_callback = urlsplit(callback_url)
            if parsed_callback.scheme.lower() not in {"http", "https"} or not parsed_callback.netloc:
                raise ValueError("callback_url must be an absolute HTTP(S) URL.")
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

        logger.error(
            "Paystack initialization failed for %s: payload=%s response=%s",
            reference,
            payload,
            data,
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

        logger.error(
            "Paystack verification failed for %s: response=%s",
            provider_reference,
            data,
        )
        details = data.get("data") or {}
        message = details.get("gateway_response") or data.get("message") or "Payment not confirmed."
        return PaymentResult(
            success=False,
            provider_reference=provider_reference,
            message=message,
        )


def get_gateway() -> BasePaymentGateway:
    return PaystackGateway()
