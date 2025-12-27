-- Dashboard Schema Migration
-- Version: 002
-- Date: 2025-12-25
-- Description: Add storage quota and project metadata for user dashboard

-- ============================================
-- USER TABLE: Add storage quota tracking
-- ============================================

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS storage_used_bytes BIGINT DEFAULT 0 NOT NULL,
ADD COLUMN IF NOT EXISTS storage_limit_bytes BIGINT DEFAULT 209715200 NOT NULL;  -- 200MB

COMMENT ON COLUMN users.storage_used_bytes IS 'Total R2 storage used by user in bytes';
COMMENT ON COLUMN users.storage_limit_bytes IS 'R2 storage limit in bytes (default 200MB)';


-- ============================================
-- SESSIONS TABLE: Add project metadata
-- ============================================

ALTER TABLE sessions
ADD COLUMN IF NOT EXISTS project_title VARCHAR(255),
ADD COLUMN IF NOT EXISTS project_description TEXT,
ADD COLUMN IF NOT EXISTS thumbnail_r2_key VARCHAR(500),
ADD COLUMN IF NOT EXISTS thumbnail_r2_url VARCHAR(1000),
ADD COLUMN IF NOT EXISTS total_size_bytes BIGINT DEFAULT 0;

COMMENT ON COLUMN sessions.project_title IS 'User-friendly project name for dashboard';
COMMENT ON COLUMN sessions.project_description IS 'Optional project description';
COMMENT ON COLUMN sessions.thumbnail_r2_key IS 'R2 key for project thumbnail image';
COMMENT ON COLUMN sessions.thumbnail_r2_url IS 'Public URL for project thumbnail';
COMMENT ON COLUMN sessions.total_size_bytes IS 'Cached total size of all session files';


-- ============================================
-- STORAGE USAGE LOG: Track uploads/deletes
-- ============================================

CREATE TABLE IF NOT EXISTS storage_usage_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    operation VARCHAR(50) NOT NULL,  -- 'upload', 'delete'
    file_name VARCHAR(255),
    size_bytes BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE storage_usage_log IS 'Audit log for storage operations';


-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX IF NOT EXISTS idx_storage_usage_user 
ON storage_usage_log(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_storage_usage_session 
ON storage_usage_log(session_id);

CREATE INDEX IF NOT EXISTS idx_sessions_user_created 
ON sessions(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_sessions_project_title 
ON sessions(project_title);

CREATE INDEX IF NOT EXISTS idx_users_storage 
ON users(storage_used_bytes);


-- ============================================
-- MIGRATION: Calculate existing storage usage
-- ============================================

-- Update storage_used_bytes for existing users
UPDATE users u
SET storage_used_bytes = COALESCE((
    SELECT SUM(gf.size_bytes)
    FROM sessions s
    JOIN generated_files gf ON gf.session_id = s.id
    WHERE s.user_id = u.id
), 0);

-- Update total_size_bytes for existing sessions
UPDATE sessions s
SET total_size_bytes = COALESCE((
    SELECT SUM(gf.size_bytes)
    FROM generated_files gf
    WHERE gf.session_id = s.id
), 0);

-- Generate project titles for sessions without them (from intent)
UPDATE sessions
SET project_title = 
    CASE 
        WHEN intent IS NOT NULL AND intent != '' THEN 
            CONCAT(UPPER(SUBSTRING(intent, 1, 1)), SUBSTRING(intent, 2, 50))
        ELSE 
            CONCAT('Project ', SUBSTRING(id::text, 1, 8))
    END
WHERE project_title IS NULL;
