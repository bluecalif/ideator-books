-- Create test user for development
-- Run this in Supabase Dashboard SQL Editor

-- Step 1: Create auth user (Supabase Auth table)
-- Note: This will fail if you don't have permission to insert into auth.users
-- Use Supabase Auth UI instead or use the following workaround:

-- Workaround: Temporarily remove FK constraint, insert user, then re-add constraint

-- 1. Drop FK constraint
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_id_fkey;

-- 2. Insert test user directly
INSERT INTO users (id, email, name, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'test@ideator-books.dev',
    'Test User',
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- 3. Re-add FK constraint (optional, can skip for development)
-- ALTER TABLE users ADD CONSTRAINT users_id_fkey 
--     FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Verify
SELECT * FROM users WHERE id = '00000000-0000-0000-0000-000000000001';

