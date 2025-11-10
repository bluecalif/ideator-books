-- ideator-books Database Schema
-- PostgreSQL + Supabase
-- 8 Tables: users, libraries, books, kb_items, runs, artifacts, reminders, audits

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. Users Table (extends Supabase Auth)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE users IS 'User profiles extending Supabase Auth';

-- ============================================
-- 2. Libraries Table (CSV collections)
-- ============================================
CREATE TABLE IF NOT EXISTS libraries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_user_library UNIQUE (user_id, name)
);

COMMENT ON TABLE libraries IS 'Uploaded CSV book collections';

-- ============================================
-- 3. Books Table (individual books)
-- ============================================
CREATE TABLE IF NOT EXISTS books (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    library_id UUID NOT NULL REFERENCES libraries(id) ON DELETE CASCADE,
    meta_json JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE books IS 'Individual books from uploaded CSVs';
COMMENT ON COLUMN books.meta_json IS 'Book metadata: {title, author, year, domain, topic, summary}';

-- ============================================
-- 4. KB Items Table (knowledge base)
-- ============================================
CREATE TABLE IF NOT EXISTS kb_items (
    kb_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain TEXT NOT NULL CHECK (domain IN ('경제경영', '과학기술', '역사사회', '인문자기계발')),
    type TEXT NOT NULL,
    anchor_id TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    is_fusion BOOLEAN DEFAULT FALSE,
    is_integrated_knowledge BOOLEAN DEFAULT FALSE,
    reference_books TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE kb_items IS 'Knowledge base items from 4 domain markdown files';
COMMENT ON COLUMN kb_items.is_fusion IS 'True if marked as (융합형)';
COMMENT ON COLUMN kb_items.is_integrated_knowledge IS 'True if from 통합지식 section';

-- ============================================
-- 5. Runs Table (1p generation jobs)
-- ============================================
CREATE TABLE IF NOT EXISTS runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    params_json JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    progress_json JSONB DEFAULT '{}'::JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

COMMENT ON TABLE runs IS '1-pager generation job tracking';
COMMENT ON COLUMN runs.params_json IS 'Job parameters: {book_ids, mode, format, remind_enabled}';
COMMENT ON COLUMN runs.progress_json IS 'Progress tracking: {current_node, percent, timestamp}';

-- ============================================
-- 6. Artifacts Table (generated 1p files)
-- ============================================
CREATE TABLE IF NOT EXISTS artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    kind TEXT NOT NULL DEFAULT 'onepager' CHECK (kind IN ('onepager')),
    format TEXT NOT NULL CHECK (format IN ('md', 'pdf')),
    url TEXT NOT NULL,
    metadata_json JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE artifacts IS 'Generated 1-pager output files';
COMMENT ON COLUMN artifacts.url IS 'Supabase Storage URL or direct content';

-- ============================================
-- 7. Reminders Table (review queue)
-- ============================================
CREATE TABLE IF NOT EXISTS reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    artifact_id UUID NOT NULL REFERENCES artifacts(id) ON DELETE CASCADE,
    schedule TIMESTAMPTZ,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_user_artifact_reminder UNIQUE (user_id, artifact_id)
);

COMMENT ON TABLE reminders IS 'User reminder queue for reviewing generated 1-pagers';

-- ============================================
-- 8. Audits Table (validation logs)
-- ============================================
CREATE TABLE IF NOT EXISTS audits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    anchored_by_ok BOOLEAN NOT NULL,
    unique3_ok BOOLEAN NOT NULL,
    external0_ok BOOLEAN NOT NULL,
    details_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE audits IS 'Validation audit logs for 1-pager quality checks';
COMMENT ON COLUMN audits.anchored_by_ok IS 'All sentences anchored to KB (100%)';
COMMENT ON COLUMN audits.unique3_ok IS 'At least 3 unique sentences';
COMMENT ON COLUMN audits.external0_ok IS 'No external frameworks (0 external references)';

-- ============================================
-- Indexes for Performance
-- ============================================

-- Libraries
CREATE INDEX IF NOT EXISTS idx_libraries_user ON libraries(user_id);

-- Books
CREATE INDEX IF NOT EXISTS idx_books_library ON books(library_id);
CREATE INDEX IF NOT EXISTS idx_books_meta_domain ON books USING GIN(meta_json);

-- KB Items
CREATE INDEX IF NOT EXISTS idx_kb_items_domain ON kb_items(domain);
CREATE INDEX IF NOT EXISTS idx_kb_items_anchor ON kb_items(anchor_id);
CREATE INDEX IF NOT EXISTS idx_kb_items_fusion ON kb_items(is_fusion);
CREATE INDEX IF NOT EXISTS idx_kb_items_integrated ON kb_items(is_integrated_knowledge);

-- Runs
CREATE INDEX IF NOT EXISTS idx_runs_user ON runs(user_id);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_created ON runs(created_at DESC);

-- Artifacts
CREATE INDEX IF NOT EXISTS idx_artifacts_run ON artifacts(run_id);

-- Reminders
CREATE INDEX IF NOT EXISTS idx_reminders_user_active ON reminders(user_id, active);
CREATE INDEX IF NOT EXISTS idx_reminders_schedule ON reminders(schedule) WHERE active = TRUE;

-- Audits
CREATE INDEX IF NOT EXISTS idx_audits_run ON audits(run_id);

-- ============================================
-- Row Level Security (RLS)
-- ============================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE libraries ENABLE ROW LEVEL SECURITY;
ALTER TABLE books ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE audits ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS Policies: KB Items (Public Read-Only)
-- ============================================
CREATE POLICY "KB items are viewable by everyone"
    ON kb_items FOR SELECT
    USING (TRUE);

-- ============================================
-- RLS Policies: Users
-- ============================================
CREATE POLICY "Users can view own profile"
    ON users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON users FOR UPDATE
    USING (auth.uid() = id);

-- ============================================
-- RLS Policies: Libraries
-- ============================================
CREATE POLICY "Users can view own libraries"
    ON libraries FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own libraries"
    ON libraries FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own libraries"
    ON libraries FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- RLS Policies: Books
-- ============================================
CREATE POLICY "Users can view own books"
    ON books FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM libraries
            WHERE libraries.id = books.library_id
            AND libraries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert books to own libraries"
    ON books FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM libraries
            WHERE libraries.id = books.library_id
            AND libraries.user_id = auth.uid()
        )
    );

-- ============================================
-- RLS Policies: Runs
-- ============================================
CREATE POLICY "Users can view own runs"
    ON runs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own runs"
    ON runs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own runs"
    ON runs FOR UPDATE
    USING (auth.uid() = user_id);

-- ============================================
-- RLS Policies: Artifacts
-- ============================================
CREATE POLICY "Users can view own artifacts"
    ON artifacts FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM runs
            WHERE runs.id = artifacts.run_id
            AND runs.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert artifacts for own runs"
    ON artifacts FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM runs
            WHERE runs.id = artifacts.run_id
            AND runs.user_id = auth.uid()
        )
    );

-- ============================================
-- RLS Policies: Reminders
-- ============================================
CREATE POLICY "Users can view own reminders"
    ON reminders FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own reminders"
    ON reminders FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own reminders"
    ON reminders FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own reminders"
    ON reminders FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- RLS Policies: Audits
-- ============================================
CREATE POLICY "Users can view audits for own runs"
    ON audits FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM runs
            WHERE runs.id = audits.run_id
            AND runs.user_id = auth.uid()
        )
    );

-- ============================================
-- End of Schema
-- ============================================

