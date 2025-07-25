# ai/db_utils.py
"""
Data Access Layer for chat history persistence.
This module handles all database operations related to chat sessions and messages
using the asyncpg library for direct PostgreSQL communication.
"""
import asyncpg
import os

# --- Database Connection Pool ---
DB_POOL = None

async def get_pool():
    """
    Initializes and returns a singleton asyncpg connection pool.
    """
    global DB_POOL
    if DB_POOL is None:
        DB_POOL = await asyncpg.create_pool(
            user=os.getenv("DB_USER", "appuser"),
            password=os.getenv("DB_PASSWORD", "a-strong-password"),
            database=os.getenv("DB_NAME", "todo_db"),
            host=os.getenv("DB_HOST", "localhost"),
        )
    return DB_POOL

# --- Database Operations ---

async def save_message(session_id: int, role: str, content: str):
    """Saves a single chat message to the database."""
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO chat_messages (session_id, role, content) VALUES ($1, $2, $3)",
        session_id, role, content
    )

async def fetch_session_messages(session_id: int):
    """Fetches all messages for a given session, ordered by creation time."""
    pool = await get_pool()
    return await pool.fetch(
        "SELECT role, content FROM chat_messages WHERE session_id = $1 ORDER BY created_at ASC",
        session_id
    )

async def create_new_session(user_id: int):
    """Creates a new chat session for a user and returns the new session's data."""
    pool = await get_pool()
    return await pool.fetchrow(
        "INSERT INTO chat_sessions (user_id) VALUES ($1) RETURNING id, title, created_at",
        user_id
    )

async def fetch_user_sessions(user_id: int):
    """Fetches all chat sessions for a given user."""
    pool = await get_pool()
    return await pool.fetch(
        "SELECT id, title, created_at FROM chat_sessions WHERE user_id = $1 ORDER BY created_at DESC",
        user_id
    )

async def delete_session(session_id: int) -> bool:
    """
    Deletes a specific chat session. Deleting a session also deletes its messages
    due to the 'ON DELETE CASCADE' constraint in the database schema.
    Returns True if a row was deleted, False otherwise.
    """
    pool = await get_pool()
    result = await pool.execute("DELETE FROM chat_sessions WHERE id = $1", session_id)
    # The result from an execute command is a string like 'DELETE 1' if one row was deleted.
    return "DELETE 1" in result

async def count_user_messages_in_session(session_id: int) -> int:
    """Counts the number of 'user' role messages in a given session."""
    pool = await get_pool()
    count = await pool.fetchval(
        "SELECT COUNT(*) FROM chat_messages WHERE session_id = $1 AND role = 'user'",
        session_id
    )
    return count or 0

async def update_session_title(session_id: int, new_title: str):
    """Updates the title of a specific chat session."""
    pool = await get_pool()
    await pool.execute(
        "UPDATE chat_sessions SET title = $1 WHERE id = $2",
        new_title, session_id
    )
# # db_utils.py
# import asyncpg
# import os

# # --- Database Connection Pool ---
# DB_POOL = None

# async def get_pool():
#     global DB_POOL
#     if DB_POOL is None:
#         DB_POOL = await asyncpg.create_pool(
#             user=os.getenv("DB_USER", "appuser"),
#             password=os.getenv("DB_PASSWORD", "a-strong-password"),
#             database=os.getenv("DB_NAME", "todo_db"),
#             host=os.getenv("DB_HOST", "localhost"),
#         )
#     return DB_POOL

# # --- Database Operations ---
# async def save_message(session_id: int, role: str, content: str):
#     pool = await get_pool()
#     await pool.execute(
#         "INSERT INTO chat_messages (session_id, role, content) VALUES ($1, $2, $3)",
#         session_id, role, content
#     )

# async def fetch_session_messages(session_id: int):
#     pool = await get_pool()
#     return await pool.fetch("SELECT role, content FROM chat_messages WHERE session_id = $1 ORDER BY created_at ASC", session_id)

# async def create_new_session(user_id: int):
#     pool = await get_pool()
#     return await pool.fetchrow("INSERT INTO chat_sessions (user_id) VALUES ($1) RETURNING id, title, created_at", user_id)

# async def fetch_user_sessions(user_id: int):
#     pool = await get_pool()
#     return await pool.fetch("SELECT id, title, created_at FROM chat_sessions WHERE user_id = $1 ORDER BY created_at DESC", user_id)

# async def delete_session(session_id: int):
#     """
#     Deletes a specific chat session.
#     Thanks to "ON DELETE CASCADE" in our table schema, deleting a session
#     will automatically delete all associated messages in the chat_messages table.
#     """
#     pool = await get_pool()
#     result = await pool.execute("DELETE FROM chat_sessions WHERE id = $1", session_id)
#     # The result from an execute command is a string like 'DELETE 1' if one row was deleted.
#     return "DELETE 1" in result

# async def count_user_messages_in_session(session_id: int) -> int:
#     """Counts the number of 'user' role messages in a given session."""
#     pool = await get_pool()
#     count = await pool.fetchval("SELECT COUNT(*) FROM chat_messages WHERE session_id = $1 AND role = 'user'", session_id)
#     return count or 0

# async def update_session_title(session_id: int, new_title: str):
#     """Updates the title of a specific chat session."""
#     pool = await get_pool()
#     await pool.execute("UPDATE chat_sessions SET title = $1 WHERE id = $2", new_title, session_id)
