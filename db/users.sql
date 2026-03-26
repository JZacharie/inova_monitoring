-- Table for users and auth mapping
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    email         TEXT UNIQUE NOT NULL,
    hashed_password TEXT, -- For Basic Auth
    full_name     TEXT,
    picture_url   TEXT,
    provider      TEXT, -- 'basic', 'google', 'github', 'entra'
    provider_id   TEXT, -- ID from the provider
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login    TIMESTAMP WITH TIME ZONE
);

-- Mock user for testing Basic Auth (admin / admin)
-- In a real app, use a proper hashing library like passlib or bcrypt
INSERT INTO users (email, hashed_password, full_name, provider)
VALUES ('admin@inova.local', 'admin', 'Administrator', 'basic')
ON CONFLICT (email) DO NOTHING;
