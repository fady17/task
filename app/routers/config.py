from fastapi import APIRouter, Request
import os

router = APIRouter(
    prefix="/config",
    tags=["Application Configuration"],
)

@router.get("/")
async def get_app_config(request: Request):
    """
    Provides the frontend with dynamic configuration details,
    including the server's reachable hostname and TURN server info.
    """
    # 'request.base_url.hostname' is the most reliable way to get the
    # hostname that the client used to connect to the server.
    # This could be 'localhost', '192.168.1.15', or a real domain name.
    server_host = request.base_url.hostname

    return {
        "api_host": server_host,
        "api_port": os.getenv("API_PORT", 8000),
        "voice_api_port": os.getenv("VOICE_API_PORT", 8001),
        "turn_server": {
            "urls": [
                f"stun:{server_host}:3478",
                f"turn:{server_host}:3478"
            ],
            "username": "demo",
            "credential": "password"
        }
    }