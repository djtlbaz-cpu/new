"""Subscription, tier, usage, and add-on API endpoints."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from ..schemas import (
    AddonInfo,
    AddonResponse,
    AddonSubscribeRequest,
    RegisterRequest,
    SubscribeRequest,
    SubscriptionResponse,
    TierInfo,
    UsageInfo,
    UserProfile,
)
from ..services.subscriptions import (
    ADDONS,
    TIERS,
    cancel_addon,
    get_usage,
    get_user_addons,
    get_user_subscription,
    get_user_tier,
    register_user,
    subscribe_addon,
    subscribe_user,
)

router = APIRouter()


# ── Tiers ────────────────────────────────────────────────────


@router.get("/tiers", response_model=List[TierInfo])
async def list_tiers():
    """List all available subscription tiers."""
    return list(TIERS.values())


@router.get("/tiers/{tier_id}", response_model=TierInfo)
async def get_tier(tier_id: str):
    """Get details for a specific tier."""
    if tier_id not in TIERS:
        raise HTTPException(status_code=404, detail=f"Tier '{tier_id}' not found")
    return TIERS[tier_id]


# ── User registration ───────────────────────────────────────


@router.post("/register", response_model=UserProfile)
async def register(request: RegisterRequest):
    """Register a new user (no email validation). Auto-assigned free tier."""
    user = register_user(request.display_name, request.email)
    tier = TIERS["free"]
    return UserProfile(
        id=user["id"],
        display_name=user.get("display_name"),
        email=user.get("email"),
        tier=tier,
        addons=[],
        usage=UsageInfo(
            user_id=user["id"],
            period="",
            count=0,
            limit=tier.monthly_generations,
            remaining=tier.monthly_generations,
            tier_id=tier.id,
            owns_creations=tier.owns_creations,
        ),
    )


# ── Subscription management ─────────────────────────────────


@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe(request: SubscribeRequest):
    """Subscribe or change a user's plan."""
    sub = subscribe_user(request.user_id, request.tier_id)
    tier = TIERS[sub.tier_id]
    return SubscriptionResponse(subscription=sub, tier=tier)


@router.get("/subscription/{user_id}", response_model=SubscriptionResponse)
async def get_subscription(user_id: str):
    """Get a user's current subscription and tier details."""
    sub = get_user_subscription(user_id)
    if sub is None:
        # Default to free
        tier = TIERS["free"]
        from ..schemas import UserSubscription

        sub = UserSubscription(user_id=user_id, tier_id="free", status="active")
    else:
        tier = TIERS.get(sub.tier_id, TIERS["free"])
    return SubscriptionResponse(subscription=sub, tier=tier)


# ── Usage ────────────────────────────────────────────────────


@router.get("/usage/{user_id}", response_model=UsageInfo)
async def usage(user_id: str):
    """Get the user's generation usage for the current billing period."""
    return get_usage(user_id)


# ── User profile ────────────────────────────────────────────


@router.get("/profile/{user_id}", response_model=UserProfile)
async def profile(user_id: str):
    """Get full user profile: tier, add-ons, and usage."""
    tier = get_user_tier(user_id)
    addons = get_user_addons(user_id)
    usage_info = get_usage(user_id)
    return UserProfile(
        id=user_id,
        tier=tier,
        addons=addons,
        usage=usage_info,
    )


# ── Add-ons ──────────────────────────────────────────────────


@router.get("/addons", response_model=List[AddonInfo])
async def list_addons():
    """List all available add-ons."""
    return [a for a in ADDONS.values() if a.active]


@router.post("/addons/subscribe", response_model=AddonResponse)
async def addon_subscribe(request: AddonSubscribeRequest):
    """Subscribe to an add-on. Validates tier requirements."""
    addon_sub = subscribe_addon(request.user_id, request.addon_id)
    info = ADDONS[request.addon_id]
    return AddonResponse(addon=addon_sub, info=info)


@router.post("/addons/cancel", response_model=AddonResponse)
async def addon_cancel(request: AddonSubscribeRequest):
    """Cancel an active add-on."""
    addon_sub = cancel_addon(request.user_id, request.addon_id)
    info = ADDONS[request.addon_id]
    return AddonResponse(addon=addon_sub, info=info)


@router.get("/addons/{user_id}", response_model=List[AddonInfo])
async def user_addons(user_id: str):
    """List a user's active add-ons."""
    return get_user_addons(user_id)
