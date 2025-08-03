# ai/routers/voice.py
"""
API routes for voice bot management.
Provides endpoints to control voice bot connections and status.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

# Try to import voice bot, but handle gracefully if Pipecat isn't installed
try:
    from ..services.voice_pipeline_bot import voice_pipeline_bot
    VOICE_BOT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Voice pipeline bot not available: {e}")
    voice_pipeline_bot = None
    VOICE_BOT_AVAILABLE = False

router = APIRouter(
    prefix="/voice",
    tags=["Voice Bot"],
)

class VoiceBotRequest(BaseModel):
    room_name: str
    user_id: Optional[int] = 1
    session_name: Optional[str] = None

class VoiceBotStatus(BaseModel):
    running: bool
    room_name: Optional[str] = None
    available: bool = VOICE_BOT_AVAILABLE

@router.get("/status")
async def get_voice_bot_status() -> VoiceBotStatus:
    """Get the current status of the voice bot"""
    if not VOICE_BOT_AVAILABLE:
        return VoiceBotStatus(
            running=False,
            room_name=None,
            available=False
        )
    
    return VoiceBotStatus(
        running=voice_pipeline_bot.is_running, # type: ignore
        room_name=voice_pipeline_bot.room_name, # type: ignore
        available=True
    )

@router.post("/connect")
async def connect_voice_bot(request: VoiceBotRequest):
    """Connect the voice bot to a LiveKit room"""
    if not VOICE_BOT_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Voice bot is not available. Please check Pipecat installation and Azure Speech credentials."
        )
    
    try:
        if voice_pipeline_bot.is_running:
            raise HTTPException(
                status_code=400, 
                detail=f"Voice bot is already connected to room: {voice_pipeline_bot.room_name}"
            )
        
        await voice_pipeline_bot.connect(
            room_name=request.room_name, 
            user_id=request.user_id, 
            session_name=request.session_name
        )
        
        return {
            "status": "success",
            "message": f"Voice bot connected to room: {request.room_name}",
            "room_name": request.room_name,
            "user_id": request.user_id,
            "session_name": request.session_name
        }
    except Exception as e:
        logging.error(f"Failed to connect voice bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disconnect")
async def disconnect_voice_bot():
    """Disconnect the voice bot from its current room"""
    if not VOICE_BOT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Voice bot is not available")
    
    try:
        if not voice_pipeline_bot.is_running:
            raise HTTPException(status_code=400, detail="Voice bot is not currently connected")
        
        current_room = voice_pipeline_bot.room_name
        await voice_pipeline_bot.disconnect()
        
        return {
            "status": "success",
            "message": f"Voice bot disconnected from room: {current_room}"
        }
    except Exception as e:
        logging.error(f"Failed to disconnect voice bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restart")
async def restart_voice_bot(request: VoiceBotRequest):
    """Restart the voice bot (disconnect if running, then connect to new room)"""
    if not VOICE_BOT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Voice bot is not available")
    
    try:
        if voice_pipeline_bot.is_running:
            logging.info("Disconnecting voice bot for restart...")
            await voice_pipeline_bot.disconnect()
        
        await voice_pipeline_bot.connect(
            room_name=request.room_name, 
            user_id=request.user_id, 
            session_name=request.session_name
        )
        
        return {
            "status": "success",
            "message": f"Voice bot restarted and connected to room: {request.room_name}",
            "room_name": request.room_name,
            "user_id": request.user_id,
            "session_name": request.session_name
        }
    except Exception as e:
        logging.error(f"Failed to restart voice bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def voice_health_check():
    """Check if voice services are properly configured"""
    import os
    
    checks = {
        "voice_bot_available": VOICE_BOT_AVAILABLE,
        "azure_speech_key": bool(os.getenv("AZURE_SPEECH_KEY")),
        "azure_speech_region": bool(os.getenv("AZURE_SPEECH_REGION")),
        "livekit_configured": bool(os.getenv("LIVEKIT_API_KEY")) and bool(os.getenv("LIVEKIT_API_SECRET"))
    }
    
    all_good = all(checks.values())
    
    return {
        "status": "healthy" if all_good else "unhealthy",
        "checks": checks,
        "message": "All voice services are ready" if all_good else "Some voice services need configuration"
    }