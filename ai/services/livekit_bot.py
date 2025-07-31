# ai/services/livekit_bot.py

import asyncio
import os
import json
import logging
from livekit import rtc, api

# Import your existing AI logic and dependencies
from .ai_processor import process_chat_request
from ..dependencies import get_todo_api_client

logger = logging.getLogger(__name__)

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
BOT_IDENTITY = "ai-assistant-bot"

class LiveKitBot:
    def __init__(self):
        self.room: rtc.Room | None = None
        self.todo_api_client = get_todo_api_client()
        logger.info("LiveKitBot initialized")

    async def _process_incoming_data(self, packet: rtc.DataPacket):
        """This async helper method contains the core AI logic."""
        # Ignore messages from self or server-sent messages without a participant
        if not packet.participant or packet.participant.identity == BOT_IDENTITY:
            return

        message_str = packet.data.decode("utf-8")
        logger.info(f"Bot received data from {packet.participant.identity}: {message_str}")
        try:
            payload = json.loads(message_str)
            async for response in process_chat_request(
                prompt=payload.get("prompt"),
                session_id=payload.get("sessionId"),
                todo_api=self.todo_api_client
            ):
                await self.send_data(json.dumps(response))
        except Exception as e:
            logger.error(f"Error processing bot message: {e}", exc_info=True)
            await self.send_data(json.dumps({"type": "error", "content": str(e)}))

    async def connect(self, room_name: str):
        logger.info(f"AI Bot attempting to join LiveKit room: {room_name}")
        
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(BOT_IDENTITY) \
            .with_name("AI Assistant") \
            .with_grants(api.VideoGrants(room_join=True, room=room_name)) \
            .to_jwt()

        self.room = rtc.Room()

        # --- THIS IS THE FINAL, DOCUMENTATION-CORRECT EVENT HANDLER ---
        # The 'data_received' event provides a SINGLE DataPacket object, which we name 'packet'.
        @self.room.on("data_received")
        def on_data_received(packet: rtc.DataPacket):
            # We launch our async logic in a background task, passing the entire packet.
            asyncio.create_task(self._process_incoming_data(packet))
        # --- END OF CORRECTION ---
        
        @self.room.on("participant_connected")
        def on_participant_connected(participant: rtc.RemoteParticipant):
            logger.info(f"Participant connected: {participant.identity}")
        
        @self.room.on("participant_disconnected") 
        def on_participant_disconnected(participant: rtc.RemoteParticipant):
            logger.info(f"Participant disconnected: {participant.identity}")

        await self.room.connect(LIVEKIT_URL, token)
        logger.info(f"AI Bot connected successfully to room: {room_name}")

    async def send_data(self, payload: str):
        if self.room:
            # await self.room.local_participant.publish_data(payload, kind=rtc.DataPacketKind.RELIABLE) 
            await self.room.local_participant.publish_data(payload, reliable=True)

    async def disconnect(self):
        if self.room:
            await self.room.disconnect()
            logger.info("AI Bot disconnected.")

# Singleton instance
livekit_bot = LiveKitBot()
AI_CHAT_ROOM_NAME = "ai-chat-room"
