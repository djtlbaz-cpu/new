"""Stripe payment endpoints for Beat Addicts subscriptions."""
from __future__ import annotations

import logging
from typing import Optional

import stripe
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..config import settings
from ..services.subscriptions import ADDONS, TIERS

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Initialise Stripe ────────────────────────────────────────

if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key
    logger.info("Stripe SDK initialised")
else:
    logger.warning("STRIPE_SECRET_KEY not set – payment endpoints will fail")


# ── Stripe ↔ tier price mapping (cents) ─────────────────────

TIER_PRICES = {
    "free":   0,
    "basic":  2000,   # $20/mo
    "studio": 5000,   # $50/mo
}

ADDON_PRICES = {
    "voice_clone":    1500,  # $15/mo
    "stem_sep":       1000,  # $10/mo
    "ai_sample_gen":   800,  # $8/mo
    "mastering":      2000,  # $20/mo
    "collab_rooms":   1200,  # $12/mo
}


# ── Request / Response schemas ──────────────────────────────


class CreateCheckoutRequest(BaseModel):
    user_id: str
    tier_id: Optional[str] = None
    addon_id: Optional[str] = None
    success_url: str = "https://beat-addicts.app/success"
    cancel_url: str = "https://beat-addicts.app/cancel"


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class CreateProductsResponse(BaseModel):
    products_created: int
    prices_created: int
    details: list


# ── Endpoints ───────────────────────────────────────────────


@router.get("/status")
async def stripe_status():
    """Check whether Stripe is configured."""
    configured = bool(settings.stripe_secret_key)
    if not configured:
        return {"stripe": False, "message": "STRIPE_SECRET_KEY not set"}
    try:
        acct = stripe.Account.retrieve()
        return {
            "stripe": True,
            "account_id": acct.id,
            "country": acct.get("country"),
            "charges_enabled": acct.get("charges_enabled"),
        }
    except stripe.StripeError as exc:
        return {"stripe": False, "error": str(exc)}


@router.post("/create-checkout", response_model=CheckoutResponse)
async def create_checkout(req: CreateCheckoutRequest):
    """Create a Stripe Checkout Session for a tier upgrade or add‑on."""
    _require_stripe()

    if req.tier_id and req.addon_id:
        raise HTTPException(400, "Specify either tier_id or addon_id, not both")
    if not req.tier_id and not req.addon_id:
        raise HTTPException(400, "Provide tier_id or addon_id")

    # Build line items
    if req.tier_id:
        if req.tier_id not in TIERS:
            raise HTTPException(404, f"Tier '{req.tier_id}' not found")
        if req.tier_id == "free":
            raise HTTPException(400, "Free tier does not require payment")
        tier = TIERS[req.tier_id]
        line_items = [
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": tier.price_cents,
                    "recurring": {"interval": "month"},
                    "product_data": {
                        "name": tier.name,
                        "description": tier.description or "Beat Addicts subscription",
                    },
                },
                "quantity": 1,
            }
        ]
        mode = "subscription"
    else:
        if req.addon_id not in ADDONS:
            raise HTTPException(404, f"Add-on '{req.addon_id}' not found")
        addon = ADDONS[req.addon_id]
        line_items = [
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": addon.price_cents,
                    "recurring": {"interval": "month"},
                    "product_data": {
                        "name": addon.name,
                        "description": addon.description or "Beat Addicts add-on",
                    },
                },
                "quantity": 1,
            }
        ]
        mode = "subscription"

    try:
        session = stripe.checkout.Session.create(
            mode=mode,
            line_items=line_items,
            success_url=req.success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=req.cancel_url,
            client_reference_id=req.user_id,
            metadata={
                "user_id": req.user_id,
                "tier_id": req.tier_id or "",
                "addon_id": req.addon_id or "",
            },
        )
        return CheckoutResponse(checkout_url=session.url, session_id=session.id)
    except stripe.StripeError as exc:
        raise HTTPException(502, f"Stripe error: {exc}")


@router.post("/sync-products", response_model=CreateProductsResponse)
async def sync_stripe_products():
    """Create / sync Beat Addicts tier & add-on products in Stripe."""
    _require_stripe()

    created_products = 0
    created_prices = 0
    details = []

    # Tiers
    for tier_id, tier in TIERS.items():
        if tier_id == "free":
            continue
        prod = stripe.Product.create(
            name=tier.name,
            description=tier.description or f"Beat Addicts {tier.name} tier",
            metadata={"beat_addicts_tier": tier_id},
        )
        created_products += 1
        price = stripe.Price.create(
            product=prod.id,
            unit_amount=tier.price_cents,
            currency="usd",
            recurring={"interval": "month"},
        )
        created_prices += 1
        details.append({"type": "tier", "id": tier_id, "product": prod.id, "price": price.id})

    # Add-ons
    for addon_id, addon in ADDONS.items():
        prod = stripe.Product.create(
            name=addon.name,
            description=addon.description or f"Beat Addicts {addon.name}",
            metadata={"beat_addicts_addon": addon_id},
        )
        created_products += 1
        price = stripe.Price.create(
            product=prod.id,
            unit_amount=addon.price_cents,
            currency="usd",
            recurring={"interval": "month"},
        )
        created_prices += 1
        details.append({"type": "addon", "id": addon_id, "product": prod.id, "price": price.id})

    return CreateProductsResponse(
        products_created=created_products,
        prices_created=created_prices,
        details=details,
    )


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events (checkout.session.completed, etc.)."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if settings.stripe_webhook_secret and sig_header:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
        except (ValueError, stripe.SignatureVerificationError) as exc:
            raise HTTPException(400, f"Webhook signature verification failed: {exc}")
    else:
        import json
        event = json.loads(payload)

    event_type = event.get("type") if isinstance(event, dict) else event.type

    if event_type == "checkout.session.completed":
        session = event.get("data", {}).get("object", {}) if isinstance(event, dict) else event.data.object
        logger.info(
            "Checkout completed: user=%s tier=%s addon=%s",
            session.get("metadata", {}).get("user_id"),
            session.get("metadata", {}).get("tier_id"),
            session.get("metadata", {}).get("addon_id"),
        )
        # TODO: call subscribe_user() / subscribe_addon() to activate in Supabase

    elif event_type == "customer.subscription.deleted":
        logger.info("Subscription cancelled via Stripe")
        # TODO: call cancel logic

    return {"received": True}


# ── Helpers ──────────────────────────────────────────────────


def _require_stripe():
    if not settings.stripe_secret_key:
        raise HTTPException(503, "Stripe is not configured (STRIPE_SECRET_KEY missing)")
