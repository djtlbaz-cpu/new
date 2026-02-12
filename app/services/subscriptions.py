"""Subscription & tier management backed by Supabase."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException

from ..schemas import (
    AddonInfo,
    TierID,
    TierInfo,
    UsageInfo,
    UserAddon,
    UserSubscription,
)
from .database import get_database_gateway


# ── Tier definitions (in-memory mirror of subscription_tiers table) ──

TIERS: dict[str, TierInfo] = {
    "free": TierInfo(
        id="free",
        name="Free",
        price_cents=0,
        monthly_generations=4,
        owns_creations=False,
        full_tool_access=False,
        description="Try the platform — 4 AI generations/month, no ownership rights",
    ),
    "basic": TierInfo(
        id="basic",
        name="Basic",
        price_cents=2000,
        monthly_generations=50,
        owns_creations=True,
        full_tool_access=False,
        description="$20/mo — 50 generations, ownership rights, limited tools",
    ),
    "studio": TierInfo(
        id="studio",
        name="Studio",
        price_cents=5000,
        monthly_generations=500,
        owns_creations=True,
        full_tool_access=True,
        description="$50/mo — 500 generations, full tool access, ownership rights",
    ),
}

TIER_RANK = {"free": 0, "basic": 1, "studio": 2}

# ── Add-on definitions ──

ADDONS: dict[str, AddonInfo] = {
    "voice_clone": AddonInfo(
        id="voice_clone",
        name="Voice Cloning",
        price_cents=999,
        description="$9.99/mo — Clone and apply vocal styles",
        requires_tier="basic",
    ),
    "stem_separation": AddonInfo(
        id="stem_separation",
        name="Stem Separation",
        price_cents=499,
        description="$4.99/mo — AI-powered stem isolation",
        requires_tier=None,
    ),
    "sample_ai": AddonInfo(
        id="sample_ai",
        name="AI Sample Pack",
        price_cents=799,
        description="$7.99/mo — Monthly AI-generated sample packs",
        requires_tier=None,
    ),
    "mastering": AddonInfo(
        id="mastering",
        name="Auto-Mastering",
        price_cents=1499,
        description="$14.99/mo — AI mastering for finished tracks",
        requires_tier="basic",
    ),
    "collab_rooms": AddonInfo(
        id="collab_rooms",
        name="Collab Rooms",
        price_cents=599,
        description="$5.99/mo — Real-time collaboration sessions",
        requires_tier="studio",
    ),
}


def _current_period() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


# ── User management ─────────────────────────────────────────


def register_user(display_name: Optional[str] = None, email: Optional[str] = None) -> dict:
    """Create a new user and assign the free tier. No email validation."""
    db = get_database_gateway()
    if not db.is_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")

    user_payload = {}
    if display_name:
        user_payload["display_name"] = display_name
    if email:
        user_payload["email"] = email

    try:
        result = db.client.table("users").insert(user_payload).execute()
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Registration failed: {exc}") from exc

    user = result.data[0]
    user_id = user["id"]

    # Auto-assign free tier
    db.client.table("user_subscriptions").insert({
        "user_id": user_id,
        "tier_id": "free",
        "status": "active",
    }).execute()

    return user


# ── Subscription management ─────────────────────────────────


def get_user_tier(user_id: str) -> TierInfo:
    """Get the active tier for a user. Defaults to free if none found."""
    db = get_database_gateway()
    if not db.is_enabled():
        return TIERS["free"]

    result = (
        db.client.table("user_subscriptions")
        .select("tier_id")
        .eq("user_id", user_id)
        .eq("status", "active")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if result.data:
        tier_id = result.data[0]["tier_id"]
        return TIERS.get(tier_id, TIERS["free"])
    return TIERS["free"]


def subscribe_user(user_id: str, tier_id: TierID) -> UserSubscription:
    """Change a user's subscription tier."""
    db = get_database_gateway()
    if not db.is_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")

    # Cancel any existing active subscription
    db.client.table("user_subscriptions").update({
        "status": "cancelled",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("user_id", user_id).eq("status", "active").execute()

    # Create new subscription
    result = db.client.table("user_subscriptions").insert({
        "user_id": user_id,
        "tier_id": tier_id.value,
        "status": "active",
    }).execute()

    row = result.data[0]
    return UserSubscription(
        id=row["id"],
        user_id=row["user_id"],
        tier_id=row["tier_id"],
        status=row["status"],
        started_at=row.get("started_at"),
    )


def get_user_subscription(user_id: str) -> Optional[UserSubscription]:
    """Get the current active subscription record."""
    db = get_database_gateway()
    if not db.is_enabled():
        return None

    result = (
        db.client.table("user_subscriptions")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "active")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if result.data:
        row = result.data[0]
        return UserSubscription(
            id=row["id"],
            user_id=row["user_id"],
            tier_id=row["tier_id"],
            status=row["status"],
            started_at=row.get("started_at"),
            expires_at=row.get("expires_at"),
        )
    return None


# ── Generation usage tracking ───────────────────────────────


def get_usage(user_id: str) -> UsageInfo:
    """Return the user's generation count for the current month."""
    tier = get_user_tier(user_id)
    period = _current_period()

    db = get_database_gateway()
    count = 0
    if db.is_enabled():
        result = (
            db.client.table("generation_usage")
            .select("count")
            .eq("user_id", user_id)
            .eq("period", period)
            .limit(1)
            .execute()
        )
        if result.data:
            count = result.data[0]["count"]

    return UsageInfo(
        user_id=user_id,
        period=period,
        count=count,
        limit=tier.monthly_generations,
        remaining=max(0, tier.monthly_generations - count),
        tier_id=tier.id,
        owns_creations=tier.owns_creations,
    )


def increment_usage(user_id: str) -> UsageInfo:
    """Increment the generation counter and return updated usage."""
    tier = get_user_tier(user_id)
    period = _current_period()

    db = get_database_gateway()
    if not db.is_enabled():
        return UsageInfo(
            user_id=user_id,
            period=period,
            count=0,
            limit=tier.monthly_generations,
            remaining=tier.monthly_generations,
            tier_id=tier.id,
            owns_creations=tier.owns_creations,
        )

    # Upsert: insert or increment
    existing = (
        db.client.table("generation_usage")
        .select("id, count")
        .eq("user_id", user_id)
        .eq("period", period)
        .limit(1)
        .execute()
    )

    if existing.data:
        row = existing.data[0]
        new_count = row["count"] + 1
        db.client.table("generation_usage").update({
            "count": new_count,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", row["id"]).execute()
    else:
        new_count = 1
        db.client.table("generation_usage").insert({
            "user_id": user_id,
            "period": period,
            "count": 1,
        }).execute()

    return UsageInfo(
        user_id=user_id,
        period=period,
        count=new_count,
        limit=tier.monthly_generations,
        remaining=max(0, tier.monthly_generations - new_count),
        tier_id=tier.id,
        owns_creations=tier.owns_creations,
    )


def check_generation_allowed(user_id: str) -> UsageInfo:
    """Raise 429 if the user has exhausted their monthly generations."""
    usage = get_usage(user_id)
    if usage.remaining <= 0:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Monthly generation limit reached ({usage.limit} "
                f"for {usage.tier_id} tier). Upgrade your plan for more."
            ),
        )
    return usage


# ── Content ownership ───────────────────────────────────────


def record_ownership(user_id: str, generation_id: str) -> bool:
    """Log whether the user owns this generated content based on tier."""
    tier = get_user_tier(user_id)
    db = get_database_gateway()
    if not db.is_enabled():
        return tier.owns_creations

    db.client.table("content_ownership").insert({
        "user_id": user_id,
        "generation_id": generation_id,
        "tier_at_creation": tier.id,
        "owns_content": tier.owns_creations,
    }).execute()

    return tier.owns_creations


# ── Add-on management ───────────────────────────────────────


def get_user_addons(user_id: str) -> list[AddonInfo]:
    """Return the list of active add-ons for a user."""
    db = get_database_gateway()
    if not db.is_enabled():
        return []

    result = (
        db.client.table("user_addons")
        .select("addon_id")
        .eq("user_id", user_id)
        .eq("status", "active")
        .execute()
    )

    return [
        ADDONS[row["addon_id"]]
        for row in result.data
        if row["addon_id"] in ADDONS
    ]


def subscribe_addon(user_id: str, addon_id: str) -> UserAddon:
    """Subscribe a user to an add-on. Validates tier requirements."""
    db = get_database_gateway()
    if not db.is_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")

    if addon_id not in ADDONS:
        raise HTTPException(status_code=404, detail=f"Add-on '{addon_id}' not found")

    addon = ADDONS[addon_id]

    # Check tier requirement
    if addon.requires_tier:
        user_tier = get_user_tier(user_id)
        user_rank = TIER_RANK.get(user_tier.id, 0)
        required_rank = TIER_RANK.get(addon.requires_tier, 0)
        if user_rank < required_rank:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Add-on '{addon.name}' requires at least "
                    f"the {addon.requires_tier.title()} plan."
                ),
            )

    # Upsert: reactivate if cancelled, or create new
    existing = (
        db.client.table("user_addons")
        .select("id, status")
        .eq("user_id", user_id)
        .eq("addon_id", addon_id)
        .limit(1)
        .execute()
    )

    if existing.data:
        row = existing.data[0]
        if row["status"] == "active":
            raise HTTPException(status_code=409, detail="Add-on already active")
        db.client.table("user_addons").update({
            "status": "active",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", row["id"]).execute()
        return UserAddon(id=row["id"], user_id=user_id, addon_id=addon_id, status="active")

    result = db.client.table("user_addons").insert({
        "user_id": user_id,
        "addon_id": addon_id,
        "status": "active",
    }).execute()

    r = result.data[0]
    return UserAddon(id=r["id"], user_id=user_id, addon_id=addon_id, status="active")


def cancel_addon(user_id: str, addon_id: str) -> UserAddon:
    """Cancel an active add-on."""
    db = get_database_gateway()
    if not db.is_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")

    result = (
        db.client.table("user_addons")
        .select("id")
        .eq("user_id", user_id)
        .eq("addon_id", addon_id)
        .eq("status", "active")
        .limit(1)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="No active subscription for this add-on")

    row_id = result.data[0]["id"]
    db.client.table("user_addons").update({
        "status": "cancelled",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", row_id).execute()

    return UserAddon(id=row_id, user_id=user_id, addon_id=addon_id, status="cancelled")


def user_has_addon(user_id: str, addon_id: str) -> bool:
    """Check if a user has a specific active add-on."""
    db = get_database_gateway()
    if not db.is_enabled():
        return False

    result = (
        db.client.table("user_addons")
        .select("id")
        .eq("user_id", user_id)
        .eq("addon_id", addon_id)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    return bool(result.data)
