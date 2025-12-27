-- NCD INAI Database Schema
-- PostgreSQL 15+ (Neon Compatible)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (Clerk integration)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id TEXT UNIQUE NOT NULL,
    email TEXT,
    name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_clerk_id ON users(clerk_user_id);
CREATE INDEX idx_users_email ON users(email);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    intent TEXT,
    status TEXT NOT NULL DEFAULT 'created',
    domain JSONB,
    questions JSONB DEFAULT '[]'::jsonb,
    answers JSONB DEFAULT '{}'::jsonb,
    blueprint JSONB,
    blueprint_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);

-- Generated files metadata (stored in R2)
CREATE TABLE generated_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL, -- 'html', 'css', 'js', 'image', etc.
    r2_key TEXT NOT NULL, -- R2 object key
    r2_url TEXT NOT NULL, -- Public URL
    size_bytes BIGINT,
    mime_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_files_session_id ON generated_files(session_id);
CREATE INDEX idx_files_file_type ON generated_files(file_type);

-- Chat messages with AI
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'ai', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_chat_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_created_at ON chat_messages(created_at DESC);

-- Theme customizations
CREATE TABLE themes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    primary_color TEXT NOT NULL,
    secondary_color TEXT NOT NULL,
    accent_color TEXT NOT NULL,
    font_family TEXT NOT NULL,
    style TEXT NOT NULL, -- 'modern', 'minimal', 'classic', etc.
    custom_css TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_themes_session_id ON themes(session_id);

-- User uploaded assets metadata
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    asset_name TEXT NOT NULL,
    asset_type TEXT NOT NULL, -- 'image', 'logo', 'icon', etc.
    r2_key TEXT NOT NULL,
    r2_url TEXT NOT NULL,
    size_bytes BIGINT,
    mime_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_assets_session_id ON assets(session_id);
CREATE INDEX idx_assets_user_id ON assets(user_id);

-- Activity logs for analytics
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_logs_session_id ON activity_logs(session_id);
CREATE INDEX idx_logs_created_at ON activity_logs(created_at DESC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for auto-updating updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_themes_updated_at BEFORE UPDATE ON themes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE VIEW session_summary AS
SELECT 
    s.id,
    s.user_id,
    s.status,
    s.intent,
    s.blueprint_confirmed,
    s.created_at,
    s.updated_at,
    COUNT(DISTINCT gf.id) AS file_count,
    COUNT(DISTINCT cm.id) AS message_count,
    u.email AS user_email
FROM sessions s
LEFT JOIN generated_files gf ON s.id = gf.session_id
LEFT JOIN chat_messages cm ON s.id = cm.session_id
LEFT JOIN users u ON s.user_id = u.id
GROUP BY s.id, s.user_id, s.status, s.intent, s.blueprint_confirmed, s.created_at, s.updated_at, u.email;

-- Sample data for testing (optional)
-- Uncomment to insert test data
/*
INSERT INTO users (clerk_user_id, email, name) VALUES
('clerk_test_user_1', 'test@example.com', 'Test User');
*/
