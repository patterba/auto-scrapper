-- Supabase migration: Create the signing_events table
-- Run this in the Supabase SQL Editor (Dashboard -> SQL Editor -> New query)

CREATE TABLE IF NOT EXISTS signing_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    signer_name TEXT NOT NULL,
    team_or_franchise TEXT,
    date_time TEXT,
    location TEXT,
    business_name TEXT,
    price TEXT,
    image_url TEXT,
    contact_info TEXT,
    source_url TEXT NOT NULL,
    source_site TEXT NOT NULL,
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Deduplication: same signer + date + source = same event
    UNIQUE (signer_name, date_time, source_site)
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_signing_events_scraped_at
    ON signing_events (scraped_at DESC);

CREATE INDEX IF NOT EXISTS idx_signing_events_source_site
    ON signing_events (source_site);

CREATE INDEX IF NOT EXISTS idx_signing_events_signer_name
    ON signing_events (signer_name);

-- Enable Row Level Security (optional, recommended)
ALTER TABLE signing_events ENABLE ROW LEVEL SECURITY;

-- Allow read access for authenticated users
CREATE POLICY "Allow read access"
    ON signing_events
    FOR SELECT
    TO authenticated
    USING (true);

-- Allow full access for service role (used by the scraper)
CREATE POLICY "Allow service role full access"
    ON signing_events
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
