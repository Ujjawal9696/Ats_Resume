-- =============================================
-- ATS Resume Scorer - Supabase SQL Schema
-- Run this in Supabase SQL Editor
-- =============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── 1. USERS (extends Supabase auth.users) ─────────────────────────────────
CREATE TABLE IF NOT EXISTS public.profiles (
    id           UUID PRIMARY KEY,
    email        TEXT NOT NULL,
    full_name    TEXT,
    avatar_url   TEXT,
    plan         TEXT DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'enterprise')),
    analyses_count INT DEFAULT 0,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ── 2. RESUMES ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.resumes (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id        UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    file_name      TEXT NOT NULL,
    file_url       TEXT,
    raw_text       TEXT,
    parsed_data    JSONB DEFAULT '{}',   -- skills, experience, education, etc.
    word_count     INT DEFAULT 0,
    page_count     INT DEFAULT 1,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ── 3. ANALYSES ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.analyses (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id              UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    resume_id            UUID REFERENCES public.resumes(id) ON DELETE SET NULL,
    job_title            TEXT,
    company_name         TEXT,
    job_description      TEXT NOT NULL,

    -- Scores
    ats_score            FLOAT DEFAULT 0,
    keyword_match_pct    FLOAT DEFAULT 0,
    semantic_similarity  FLOAT DEFAULT 0,
    skill_overlap_pct    FLOAT DEFAULT 0,
    formatting_score     FLOAT DEFAULT 0,
    section_completeness FLOAT DEFAULT 0,
    resume_quality_score FLOAT DEFAULT 0,

    -- Extracted data
    matched_skills       JSONB DEFAULT '[]',
    missing_skills       JSONB DEFAULT '[]',
    matched_keywords     JSONB DEFAULT '[]',
    missing_keywords     JSONB DEFAULT '[]',
    jd_required_skills   JSONB DEFAULT '[]',
    resume_skills        JSONB DEFAULT '[]',

    -- AI Suggestions
    ai_suggestions       JSONB DEFAULT '{}',

    -- Status
    status               TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message        TEXT,

    created_at           TIMESTAMPTZ DEFAULT NOW(),
    updated_at           TIMESTAMPTZ DEFAULT NOW()
);

-- ── 4. REPORTS ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.reports (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id  UUID REFERENCES public.analyses(id) ON DELETE CASCADE,
    user_id      UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    file_url     TEXT,
    file_name    TEXT,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ── INDEXES ────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_resumes_user_id  ON public.resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_user_id  ON public.reports(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created ON public.analyses(created_at DESC);

-- ── ROW LEVEL SECURITY ─────────────────────────────────────────────────────
ALTER TABLE public.profiles  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports   ENABLE ROW LEVEL SECURITY;

-- Profiles: users see only their own
CREATE POLICY "profiles_own" ON public.profiles
    FOR ALL USING (auth.uid() = id);

-- Resumes: users see only their own
CREATE POLICY "resumes_own" ON public.resumes
    FOR ALL USING (auth.uid() = user_id);

-- Analyses: users see only their own
CREATE POLICY "analyses_own" ON public.analyses
    FOR ALL USING (auth.uid() = user_id);

-- Reports: users see only their own
CREATE POLICY "reports_own" ON public.reports
    FOR ALL USING (auth.uid() = user_id);

-- ── AUTO-UPDATE TIMESTAMPS ─────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER analyses_updated_at
    BEFORE UPDATE ON public.analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

