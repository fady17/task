# ai/routers/sessions.py
"""
API routes for managing chat sessions.
Provides endpoints to create, retrieve, and delete sessions and their messages.
"""

from fastapi import APIRouter, HTTPException
from .. import db_utils

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)
# router = APIRouter(
#     prefix="/ai/sessions",
#     tags=["Sessions"],
# )
# router = APIRouter(prefix="/sessions", tags=["AI Sessions"])

@router.get("/user/{user_id}")
async def get_user_sessions(user_id: int):
    sessions = await db_utils.fetch_user_sessions(user_id)
    return [dict(session) for session in sessions]

@router.post("/user/{user_id}", status_code=201)
async def create_session(user_id: int):
    session = await db_utils.create_new_session(user_id)
    return dict(session)

@router.get("/{session_id}/messages")
async def get_session_messages(session_id: int):
    messages = await db_utils.fetch_session_messages(session_id)
    return [dict(msg) for msg in messages]

@router.delete("/{session_id}")
async def delete_session(session_id: int):
    success = await db_utils.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return {"status": "success", "message": f"Session {session_id} deleted"}