-- ============================================================
-- Engagement Tracker — Database Schema
-- Reproducible SQL schema for SQLite
-- ============================================================

CREATE TABLE IF NOT EXISTS engagement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    engagement_year INTEGER NOT NULL,
    organization_name TEXT NOT NULL,
    description TEXT,
    website TEXT,
    industry TEXT,
    hq_region TEXT,
    hq_geography TEXT
);

-- ------------------------------------------------------------
-- Indexes to improve filtering and search performance
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_engagement_year
    ON engagement (engagement_year);

CREATE INDEX IF NOT EXISTS idx_industry
    ON engagement (industry);

CREATE INDEX IF NOT EXISTS idx_hq_region
    ON engagement (hq_region);

CREATE INDEX IF NOT EXISTS idx_hq_geography
    ON engagement (hq_geography);