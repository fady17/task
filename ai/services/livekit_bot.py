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
# # ai/livekit_bot.py
# import asyncio
# import os
# import json
# import logging
# from livekit import rtc, api

# # Import your existing AI logic and dependencies
# from ai.services.ai_processor import process_chat_request
# from ai.dependencies import get_todo_api_client

# logger = logging.getLogger(__name__)

# LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
# LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
# LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
# BOT_IDENTITY = "ai-assistant-bot"

# class LiveKitBot:
#     def __init__(self):
#         self.room: rtc.Room | None = None
#         self.todo_api_client = get_todo_api_client()
#         logger.info("LiveKitBot initialized")

#     async def connect(self, room_name: str):
#         """Connect the bot to a LiveKit room"""
#         logger.info(f"AI Bot attempting to join LiveKit room: {room_name}")
        
#         if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
#             raise ValueError("LiveKit API key and secret must be configured")
        
#         # Generate token for the bot
#         token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
#             .with_identity(BOT_IDENTITY) \
#             .with_name("AI Assistant") \
#             .with_grants(api.VideoGrants(room_join=True, room=room_name)) \
#             .to_jwt()

#         self.room = rtc.Room()

#         # Set up event handlers
#         @self.room.on("participant_connected")
#         def on_participant_connected(participant: rtc.RemoteParticipant):
#             logger.info(f"Participant connected: {participant.identity}")

#         @self.room.on("participant_disconnected") 
#         def on_participant_disconnected(participant: rtc.RemoteParticipant):
#             logger.info(f"Participant disconnected: {participant.identity}")

#         @self.room.on("data_received")
#         def on_data_received(data: bytes, participant: rtc.RemoteParticipant | None, **kwargs):
#             """Handle incoming data from participants"""
#             if participant and participant.identity != BOT_IDENTITY:
#                 logger.info(f"Bot received data from {participant.identity}")
                
#                 # Process the message asynchronously
#                 asyncio.create_task(self._handle_chat_message(data, participant))

#         # Connect to the room
#         await self.room.connect(LIVEKIT_URL, token)
#         logger.info(f"AI Bot connected successfully to room: {room_name}")

#     async def _handle_chat_message(self, data: bytes, participant: rtc.RemoteParticipant):
#         """Process a chat message using existing AI logic"""
#         try:
#             message_str = data.decode("utf-8")
#             message_data = json.loads(message_str)
            
#             prompt = message_data.get("prompt", "")
#             session_id = message_data.get("sessionId", 1)  # Default session
            
#             logger.info(f"Processing chat request: {prompt} for session {session_id}")
            
#             if not prompt:
#                 await self._send_error("Empty message received")
#                 return
            
#             # Use your existing AI processor - this is the key integration point
#             async for event in process_chat_request(prompt, session_id, self.todo_api_client):
#                 await self._send_event(event)
                
#         except json.JSONDecodeError:
#             logger.error(f"Invalid JSON received: {data.decode('utf-8', errors='ignore')}")
#             await self._send_error("Invalid message format")
#         except Exception as e:
#             logger.error(f"Error in chat processing: {e}", exc_info=True)
#             await self._send_error(f"Processing error: {e}")

#     async def _send_event(self, event: dict):
#         """Send an event back to all participants via data channel"""
#         try:
#             if not self.room:
#                 logger.error("Cannot send event: Room not connected")
#                 return
                
#             message = json.dumps(event)
#             data = message.encode("utf-8")
            
#             # Send to all participants
#             await self.room.local_participant.publish_data(data)
#             logger.info(f"Sent event: {event.get('type', 'unknown')}")
            
#         except Exception as e:
#             logger.error(f"Error sending event: {e}", exc_info=True)

#     async def _send_error(self, error_message: str):
#         """Send an error message to all participants"""
#         error_event = {
#             "type": "error",
#             "content": error_message
#         }
#         await self._send_event(error_event)

#     async def disconnect(self):
#         """Disconnect from the room"""
#         if self.room:
#             await self.room.disconnect()
#             self.room = None
#             logger.info("AI Bot disconnected")

# # Singleton instance
# livekit_bot = LiveKitBot()

# # The room name must be consistent between frontend and backend
# AI_CHAT_ROOM_NAME = "ai-chat-room"

# # Auto-start the bot when this module is imported
# async def start_bot():
#     """Start the bot and connect to the default room"""
#     try:
#         await livekit_bot.connect(AI_CHAT_ROOM_NAME)
#     except Exception as e:
#         logger.error(f"Failed to start LiveKit bot: {e}")
#         raise

# # For manual testing/debugging
# if __name__ == "__main__":
#     import asyncio
#     logging.basicConfig(level=logging.INFO)
    
#     async def main():
#         await start_bot()
#         # Keep the bot running
#         try:
#             while True:
#                 await asyncio.sleep(1)
#         except KeyboardInterrupt:
#             logger.info("Shutting down bot...")
#             await livekit_bot.disconnect()
    
#     asyncio.run(main())
# # import asyncio
# # import os
# # import json
# # from livekit import rtc, api

# # # We need access to our existing AI logic and dependencies
# # from .ai_processor import process_chat_request
# # from ..dependencies import get_todo_api_client

# # LIVEKIT_URL = "ws://localhost:7880"
# # LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
# # LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
# # BOT_IDENTITY = "ai-assistant-bot"

# # class LiveKitBot:
# #     def __init__(self):
# #         self.room: rtc.Room | None = None
# #         # The bot needs its own Todo API client to pass to the processor
# #         self.todo_api_client = get_todo_api_client()

# #     async def connect(self, room_name: str):
# #         print(f"AI Bot attempting to join LiveKit room: {room_name}")
# #         token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
# #             .with_identity(BOT_IDENTITY) \
# #             .with_name("AI Assistant") \
# #             .with_grants(api.VideoGrants(room_join=True, room=room_name)) \
# #             .to_jwt()

# #         self.room = rtc.Room()

# #         # This is the new entry point for user messages
# #         @self.room.on("data_received")
# #         async def on_data_received(data: bytes, participant: rtc.RemoteParticipant, **kwargs):
# #             message_str = data.decode("utf-8")
# #             print(f"Bot received data from {participant.identity}: {message_str}")
# #             try:
# #                 payload = json.loads(message_str)
# #                 # We call the EXACT SAME AI processor as before
# #                 async for response in process_chat_request(
# #                     prompt=payload.get("prompt"),
# #                     session_id=payload.get("sessionId"),
# #                     todo_api=self.todo_api_client
# #                 ):
# #                     # We send the response back via LiveKit instead of WebRTC
# #                     await self.send_data(json.dumps(response))
# #             except Exception as e:
# #                 print(f"Error processing bot message: {e}")
# #                 await self.send_data(json.dumps({"type": "error", "content": str(e)}))

# #         await self.room.connect(LIVEKIT_URL, token)
# #         print(f"AI Bot connected successfully to room: {self.room.name}")

# #     async def send_data(self, payload: str):
# #         if self.room:
# #             await self.room.local_participant.publish_data(payload)

# #     async def disconnect(self):
# #         if self.room:
# #             await self.room.disconnect()
# #             print("AI Bot disconnected.")

# # # A singleton instance to manage our bot's connection
# # livekit_bot = LiveKitBot()
# # # The room name must be consistent between frontend and backend
# # AI_CHAT_ROOM_NAME = "ai-chat-room"