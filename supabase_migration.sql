-- ============================================================
-- Beat Addicts - Subscription & Add-on Tables
-- Run this in Supabase SQL Editor (Dashboard → SQL Editor → New Query)
-- ============================================================

-- 1. Users table (no email validation required)
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_name    TEXT,
    email           TEXT UNIQUE,              -- stored but NOT validated
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- 2. Subscription tiers (reference table)
CREATE TABLE IF NOT EXISTS subscription_tiers (
    id              TEXT PRIMARY KEY,         -- 'free', 'basic', 'studio'
    name            TEXT NOT NULL,
    price_cents     INTEGER NOT NULL DEFAULT 0,
    monthly_generations INTEGER NOT NULL,
    owns_creations  BOOLEAN NOT NULL DEFAULT FALSE,
    full_tool_access BOOLEAN NOT NULL DEFAULT FALSE,
    description     TEXT
);

INSERT INTO subscription_tiers (id, name, price_cents, monthly_generations, owns_creations, full_tool_access, description) VALUES
    ('free',    'Free',    0,    4,   FALSE, FALSE, 'Try the platform — 4 AI generations/month, no ownership rights'),
    ('starter', 'Starter', 1999, 50,  TRUE,  FALSE, '$19.99/mo — 50 generations, ownership rights, limited tools'),
    ('studio', 'Studio', 5000, 500, TRUE,  TRUE,  '$50/mo — 500 generations, full tool access, ownership rights')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    price_cents = EXCLUDED.price_cents,
    monthly_generations = EXCLUDED.monthly_generations,
    owns_creations = EXCLUDED.owns_creations,
    full_tool_access = EXCLUDED.full_tool_access,
    description = EXCLUDED.description;

-- 3. User subscriptions
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tier_id         TEXT NOT NULL REFERENCES subscription_tiers(id),
    status          TEXT NOT NULL DEFAULT 'active',   -- active | cancelled | past_due
    started_at      TIMESTAMPTZ DEFAULT now(),
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user ON user_subscriptions(user_id);

-- 4. Monthly generation usage tracking
CREATE TABLE IF NOT EXISTS generation_usage (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    period          TEXT NOT NULL,            -- e.g. '2026-02'
    count           INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, period)
);

-- 5. Available add-ons (reference table)
CREATE TABLE IF NOT EXISTS addons (
    id              TEXT PRIMARY KEY,         -- 'voice_clone', 'stem_separation', etc.
    name            TEXT NOT NULL,
    price_cents     INTEGER NOT NULL DEFAULT 0,
    description     TEXT,
    requires_tier   TEXT,                     -- minimum tier: NULL = any, 'basic', 'studio'
    active          BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO addons (id, name, price_cents, description, requires_tier) VALUES
    ('voice_clone',      'Voice Cloning',      999,  '$9.99/mo — Clone and apply vocal styles',          'basic'),
    ('stem_separation',  'Stem Separation',    499,  '$4.99/mo — AI-powered stem isolation',             NULL),
    ('sample_ai',        'AI Sample Pack',     799,  '$7.99/mo — Monthly AI-generated sample packs',     NULL),
    ('mastering',        'Auto-Mastering',     1499, '$14.99/mo — AI mastering for finished tracks',     'basic'),
    ('collab_rooms',     'Collab Rooms',       599,  '$5.99/mo — Real-time collaboration sessions',      'studio')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    price_cents = EXCLUDED.price_cents,
    description = EXCLUDED.description,
    requires_tier = EXCLUDED.requires_tier;

-- 6. User add-on subscriptions
CREATE TABLE IF NOT EXISTS user_addons (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    addon_id        TEXT NOT NULL REFERENCES addons(id),
    status          TEXT NOT NULL DEFAULT 'active',   -- active | cancelled
    started_at      TIMESTAMPTZ DEFAULT now(),
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, addon_id)
);

-- 7. Content ownership ledger
CREATE TABLE IF NOT EXISTS content_ownership (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    generation_id   TEXT NOT NULL,
    tier_at_creation TEXT NOT NULL,
    owns_content    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_content_ownership_user ON content_ownership(user_id);

-- 8. RLS policies (allow service_role full access)
ALTER TABLE users              ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE generation_usage   ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_addons        ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_ownership  ENABLE ROW LEVEL SECURITY;

-- Service role bypass (your backend uses service_role key)
CREATE POLICY "service_role_all" ON users              FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON user_subscriptions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON generation_usage   FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON user_addons        FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON content_ownership  FOR ALL USING (true) WITH CHECK (true);
