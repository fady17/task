-- ai/seed/user.sql

-- AI-related tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL DEFAULT 'New Chat',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Todo-related tables
CREATE TABLE IF NOT EXISTS todo_lists (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE -- <-- ADDED UNIQUE CONSTRAINT
);

CREATE TABLE IF NOT EXISTS todo_items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    list_id INTEGER REFERENCES todo_lists(id) ON DELETE CASCADE
);

-- Insert initial data
INSERT INTO users (id, username) VALUES (1, 'demo_user') ON CONFLICT (id) DO NOTHING;
INSERT INTO todo_lists (title) VALUES ('Shopping List'), ('Work Tasks') ON CONFLICT (title) DO NOTHING;
-- -- ai/seed/user.sql

-- -- AI-related tables
-- CREATE TABLE IF NOT EXISTS users (
--     id SERIAL PRIMARY KEY,
--     username VARCHAR(50) UNIQUE NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- );

-- CREATE TABLE IF NOT EXISTS chat_sessions (
--     id SERIAL PRIMARY KEY,
--     user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     title VARCHAR(100) NOT NULL DEFAULT 'New Chat',
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- );

-- CREATE TABLE IF NOT EXISTS chat_messages (
--     id SERIAL PRIMARY KEY,
--     session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
--     role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
--     content TEXT NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- );

-- -- Todo-related tables
-- CREATE TABLE IF NOT EXISTS todo_lists (
--     id SERIAL PRIMARY KEY,
--     title VARCHAR(255) NOT NULL
-- );

-- -- --- THIS TABLE DEFINITION IS NOW CORRECTED ---
-- CREATE TABLE IF NOT EXISTS todo_items (
--     id SERIAL PRIMARY KEY,
--     title VARCHAR(255) NOT NULL,
--     completed BOOLEAN DEFAULT FALSE, -- Changed 'is_completed' to 'completed'
--     list_id INTEGER REFERENCES todo_lists(id) ON DELETE CASCADE
-- );
-- -- --- END OF CORRECTION ---

-- -- Insert initial data
-- INSERT INTO users (id, username) VALUES (1, 'demo_user') ON CONFLICT (id) DO NOTHING;
-- INSERT INTO todo_lists (title) VALUES ('Shopping List'), ('Work Tasks') ON CONFLICT (title) DO NOTHING;
-- -- -- A simple table for our single demo user
-- -- CREATE TABLE IF NOT EXISTS users (
-- --     id SERIAL PRIMARY KEY,
-- --     username VARCHAR(50) UNIQUE NOT NULL,
-- --     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- -- );

-- -- -- A table to store each distinct chat conversation
-- -- CREATE TABLE IF NOT EXISTS chat_sessions (
-- --     id SERIAL PRIMARY KEY,
-- --     user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
-- --     title VARCHAR(100) NOT NULL DEFAULT 'New Chat',
-- --     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- -- );

-- -- -- A table to store every message within a session
-- -- CREATE TABLE IF NOT EXISTS chat_messages (
-- --     id SERIAL PRIMARY KEY,
-- --     session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
-- --     role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
-- --     content TEXT NOT NULL,
-- --     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- -- );

-- -- INSERT INTO users (id, username) VALUES (1, 'demo_user') ON CONFLICT (id) DO NOTHING;