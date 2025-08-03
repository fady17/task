
# ai/main.py
import asyncio
from fastapi import APIRouter

from ai.routers import voice, sessions
from . import db_utils 
from ai.config import logger

from .dependencies import get_todo_api_client
from .services.livekit_bot import livekit_bot, AI_CHAT_ROOM_NAME


api_router = APIRouter()

api_router.include_router(sessions.router)
# api_router.include_router(voice.router)
# api_router.include_router(websocket.router)

async def startup_event():
    logger.info("Executing AI module startup...")
    await db_utils.get_pool()
    logger.info("Database pool initialized.")
    print("Connecting AI Bot to LiveKit...")
    # Start the bot connection in the background
    asyncio.create_task(livekit_bot.connect(AI_CHAT_ROOM_NAME))


async def shutdown_event():
    logger.info("Executing AI module shutdown...")
    # await websocket.close_all_peer_connections()
    await livekit_bot.disconnect()
    todo_client = get_todo_api_client()
    await todo_client.close()
    logger.info("Todo API client closed.")
    pool = await db_utils.get_pool()
    if pool:
        await pool.close()
        logger.info("Database pool closed.")
# # ai/main.py
# """
# Main entry point for the 'ai' sub-application.
# This module aggregates all routers and defines application lifecycle events
# (startup and shutdown) to be used by the main FastAPI app.
# """
# import asyncio
# from fastapi import APIRouter
# from . import db_utils 

# from .config import logger
# from .routers import sessions, websocket
# from .dependencies import get_todo_api_client
# # from fastapi.middleware.cors import CORSMiddleware
# # This is the main router for the entire 'ai' application.
# # The parent FastAPI app will mount this router.
# # api_router = APIRouter(prefix="/ai")
# api_router = APIRouter()


# # Include all the sub-routers
# api_router.include_router(sessions.router)
# api_router.include_router(websocket.router)

# @api_router.get("/health-check")
# async def ai_health_check():
#     return {"status": "AI module is alive!"}
# # --- Application Lifecycle Events ---

# async def startup_event():
#     """
#     Handles application startup logic.
#     - Initializes the database connection pool.
#     """
#     logger.info("Executing AI module startup...")
#     await db_utils.get_pool()
#     logger.info("Database pool initialized.")

# async def shutdown_event():
#     """
#     Handles application shutdown logic.
#     - Closes all active WebRTC connections.
#     - Closes the HTTP client in the Todo API service.
#     - Closes the database connection pool.
#     """
#     logger.info("Executing AI module shutdown...")
#     await websocket.close_all_peer_connections()
    
#     todo_client = get_todo_api_client()
#     await todo_client.close()
#     logger.info("Todo API client closed.")

#     pool = await db_utils.get_pool()
#     if pool:
#         await pool.close()
#         logger.info("Database pool closed.")


# @api_router.get("/")
# async def root():
#     """A health check endpoint for the AI module."""
#     return {"status": "AI module is running"}