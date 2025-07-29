# app/routers/livekit.py

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from livekit import api

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# --- CHANGE THIS LINE ---
# When running inside Docker, the API needs to connect to the host machine.
LIVEKIT_URL = "http://host.docker.internal:7880" 
# --- END OF CHANGE ---

router = APIRouter(prefix="/livekit", tags=["LiveKit"])

class JoinRequest(BaseModel):
    room_name: str
    identity: str

@router.post("/token")
async def get_join_token(join_request: JoinRequest):
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise HTTPException(status_code=500, detail="LiveKit API keys are not configured.")
    
    # This token generation logic is correct and does not need to change.
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
        .with_identity(join_request.identity) \
        .with_name(join_request.identity) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=join_request.room_name,
        )).to_jwt()
    
    return {"token": token}
# # app/routers/livekit.py

# import os
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from livekit import api # The correct import based on the docs

# # Your environment variable loading is correct
# LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
# LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# router = APIRouter(prefix="/livekit", tags=["LiveKit"])

# class JoinRequest(BaseModel):
#     room_name: str
#     identity: str

# @router.post("/token")
# async def get_join_token(join_request: JoinRequest):
#     if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
#         raise HTTPException(status_code=500, detail="LiveKit API keys are not configured.")

#     # --- THIS IS THE CORRECT IMPLEMENTATION BASED ON THE OFFICIAL DOCS ---
    
#     token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
#         .with_identity(join_request.identity) \
#         .with_name(join_request.identity) \
#         .with_grants(api.VideoGrants(
#             room_join=True,
#             room=join_request.room_name,
#         )).to_jwt()

#     # --- END OF CORRECTION ---
    
#     return {"token": token}