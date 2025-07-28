# ai/routers/websocket.py 
import json
import asyncio
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from aiortc import RTCPeerConnection, RTCSessionDescription

from ..config import logger, PC_CONFIG
from ..services.ai_processor import process_chat_request
from ..services.todo_client import TodoAPIClient
from ..dependencies import get_todo_api_client # <<<--- FIX: Import necessary dependencies

router = APIRouter(
    prefix="/ws", # The prefix is just "/ws"
    tags=["AI WebSocket"]
)

pcs: Set[RTCPeerConnection] = set()

# <<<--- FIX 1: Bring back the lifecycle management function ---<<<
async def close_all_peer_connections():
    """Closes all active WebRTC peer connections gracefully."""
    logger.info(f"Closing {len(pcs)} active peer connections.")
    if pcs:
        await asyncio.gather(*[pc.close() for pc in pcs])
        pcs.clear()

def safe_send(channel, message: str):
    """Safely send message through WebRTC data channel"""
    try:
        if channel and hasattr(channel, 'readyState') and channel.readyState == "open":
            channel.send(message)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    # <<<--- FIX 2: Use Depends for clean dependency injection ---<<<
    todo_api: TodoAPIClient = Depends(get_todo_api_client)
):
    await websocket.accept()
    pc = RTCPeerConnection(configuration=PC_CONFIG)
    pcs.add(pc)

    @pc.on("datachannel")
    def on_datachannel(channel):
        logger.info(f"DataChannel established: {channel.label}")

        @channel.on("message")
        async def on_message(message: str):
            try:
                data = json.loads(message)
                # Keep the generator pattern, but now pass the dependency down
                async for response_data in process_chat_request(
                    prompt=data["prompt"],
                    session_id=data["sessionId"],
                    todo_api=todo_api
                ):
                    safe_send(channel, json.dumps(response_data))

            except Exception as e:
                logger.error(f"Message handling error in websocket: {e}", exc_info=True)
                error_response = {
                    "type": "chat_message",
                    "content": "Error processing your request. Please check the server logs."
                }
                safe_send(channel, json.dumps(error_response))

    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "offer":
                offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                await pc.setRemoteDescription(offer)
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await websocket.send_json({"type": "answer", "sdp": pc.localDescription.sdp})
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    finally:
        if pc in pcs:
            await pc.close()
            pcs.remove(pc)
# # ai/routers/websocket.py
# import json
# from typing import Set
# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from aiortc import RTCPeerConnection, RTCSessionDescription

# from ..config import PC_CONFIG, logger
# from ..services.ai_processor import process_chat_request

# router = APIRouter(tags=["WebRTC Chat"])
# pcs: Set[RTCPeerConnection] = set()

# def safe_send(channel, message: str):
#     """Safely send message through WebRTC data channel"""
#     try:
#         if channel and hasattr(channel, 'readyState') and channel.readyState == "open":
#             channel.send(message)
#     except Exception as e:
#         logger.error(f"Failed to send message: {e}")

# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     pc = RTCPeerConnection(configuration=PC_CONFIG)
#     pcs.add(pc)
    
#     @pc.on("datachannel")
#     def on_datachannel(channel):
#         logger.info(f"DataChannel established: {channel.label}")
        
#         @channel.on("message")
#         async def on_message(message: str):
#             try:
#                 data = json.loads(message)

#                 # --- START OF CRITICAL CODE FIX ---
#                 # The process_chat_request function is now a generator that yields
#                 # dictionaries. We iterate over it and send each yielded piece of
#                 # data through the channel. We no longer pass the channel into the
#                 # AI logic.
#                 async for response_data in process_chat_request(
#                     prompt=data["prompt"],
#                     session_id=data["sessionId"]
#                     # NO 'channel' argument here. This is the fix.
#                 ):
#                     safe_send(channel, json.dumps(response_data))
#                 # --- END OF CRITICAL CODE FIX ---

#             except Exception as e:
#                 logger.error(f"Message handling error in websocket: {e}", exc_info=True)
#                 error_response = {
#                     "type": "chat_message", 
#                     "content": "Error processing your request. Please try again."
#                 }
#                 safe_send(channel, json.dumps(error_response))
    
#     try:
#         while True:
#             data = await websocket.receive_json()
#             if data["type"] == "offer":
#                 offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
#                 await pc.setRemoteDescription(offer)
#                 answer = await pc.createAnswer()
#                 await pc.setLocalDescription(answer)
#                 await websocket.send_json({"type": "answer", "sdp": pc.localDescription.sdp})
#     except WebSocketDisconnect:
#         logger.info("WebSocket disconnected")
#     finally:
#         if pc in pcs:
#             # TODO: Ensure graceful closure of peer connections on disconnect
#             # This is a good place to add more robust cleanup logic if needed.
#             await pc.close()
#             pcs.remove(pc)
# # # ai/routers/websocket.py
# # """
# # WebSocket and WebRTC endpoint for real-time communication.
# # Manages PeerConnection lifecycle and routes incoming messages to the AI processor.
# # """
# # import json
# # import asyncio
# # from typing import Set

# # from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
# # from aiortc import RTCPeerConnection, RTCSessionDescription

# # from ..config import logger, PC_CONFIG
# # from ..services.ai_processor import process_chat_request
# # from ..services.todo_client import TodoAPIClient
# # from ..dependencies import get_todo_api_client

# # router = APIRouter()

# # # This set will hold active peer connections for this server process.
# # pcs: Set[RTCPeerConnection] = set()

# # async def close_all_peer_connections():
# #     """Closes all active WebRTC peer connections gracefully."""
# #     logger.info(f"Closing {len(pcs)} active peer connections.")
# #     if pcs:
# #         await asyncio.gather(*[pc.close() for pc in pcs])
# #         pcs.clear()

# # @router.websocket("/ws")
# # async def websocket_endpoint(
# #     websocket: WebSocket,
# #     todo_api: TodoAPIClient = Depends(get_todo_api_client)
# # ):
# #     await websocket.accept()
# #     pc = RTCPeerConnection(configuration=PC_CONFIG)
# #     pcs.add(pc)

# #     @pc.on("datachannel")
# #     def on_datachannel(channel):
# #         logger.info(f"DataChannel established: {channel.label}")

# #         @channel.on("message")
# #         async def on_message(message: str):
# #             try:
# #                 data = json.loads(message)
# #                 # Pass the dependency-injected todo_api client to the processor
# #                 await process_chat_request(
# #                     prompt=data["prompt"],
# #                     session_id=data["sessionId"],
# #                     channel=channel,
# #                     todo_api=todo_api
# #                 )
# #             except Exception as e:
# #                 logger.error(f"Error handling message on DataChannel: {e}", exc_info=True)
# #                 try:
# #                     channel.send(json.dumps({
# #                         "type": "chat_message",
# #                         "content": "Error processing your request. Please check the server logs."
# #                     }))
# #                 except Exception as send_e:
# #                     logger.error(f"Failed to send error message back to client: {send_e}")

# #     try:
# #         while True:
# #             data = await websocket.receive_json()
# #             if data["type"] == "offer":
# #                 offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
# #                 await pc.setRemoteDescription(offer)
# #                 answer = await pc.createAnswer()
# #                 await pc.setLocalDescription(answer)
# #                 await websocket.send_json({"type": "answer", "sdp": pc.localDescription.sdp})
# #     except WebSocketDisconnect:
# #         logger.info("WebSocket disconnected.")
# #     finally:
# #         if pc in pcs:
# #             await pc.close()
# #             pcs.remove(pc)