import asyncio
import json
import logging
from aiortc import RTCPeerConnection, RTCSessionDescription
import websockets

# Configure logging to see the output clearly
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The URL of our FastAPI server's WebSocket endpoint
SERVER_URL = "ws://localhost:8080/ws"

async def run_test_client():
    """
    Simulates a WebRTC client connecting and performing the signaling handshake.
    """
    logger.info("--- Starting WebRTC Signaling Test Client ---")
    
    try:
        # Connect to the signaling server
        async with websockets.connect(SERVER_URL) as websocket:
            logger.info(f"Successfully connected to WebSocket at {SERVER_URL}")

            # 1. Create a client-side RTCPeerConnection
            pc = RTCPeerConnection()

            @pc.on("iceconnectionstatechange")
            async def on_iceconnectionstatechange():
                logger.info(f"ICE connection state is {pc.iceConnectionState}")

            # 2. Create an SDP offer
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)
            
            logger.info("Created SDP Offer. Sending to server...")

            # 3. Send the offer to the server
            await websocket.send(json.dumps({
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type,
            }))
            
            logger.info("Offer sent. Waiting for an answer...")

            # 4. Wait for the server's answer
            message = await websocket.recv()
            data = json.loads(message)

            if data.get("type") == "answer":
                logger.info("Received SDP Answer from server:")
                # print(data.get("sdp")) # Uncomment for very verbose output
                
                # Create an RTCSessionDescription from the server's answer
                answer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                
                # Set the remote description on our client-side peer connection
                await pc.setRemoteDescription(answer)
                logger.info("Successfully set remote description from server's answer.")
                print("\n✅✅✅ TEST PASSED: Signaling handshake completed successfully! ✅✅✅")
                
            else:
                logger.error(f"Received unexpected message type: {data.get('type')}")
                print("\n❌❌❌ TEST FAILED: Did not receive a valid SDP answer. ❌❌❌")

    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"Connection closed unexpectedly: {e}")
        print("\n❌❌❌ TEST FAILED: WebSocket connection failed. Is the server running? ❌❌❌")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"\n❌❌❌ TEST FAILED: An unexpected error occurred: {e} ❌❌❌")
    finally:
        # Clean up the peer connection if it exists
        if 'pc' in locals() and pc.connectionState != "closed": # type: ignore
            await pc.close() # type: ignore
            logger.info("Peer connection closed.")


if __name__ == "__main__":
    # In Python 3.8+ you can use asyncio.run(run_test_client())
    # For broader compatibility:
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_test_client())
    finally:
        loop.close()