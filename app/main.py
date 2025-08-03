# app/main.py - 

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Import All Routers ---
from app.routers import todos, items, config, livekit
from ai.main import api_router as ai_api_router
from ai.main import startup_event, shutdown_event

app = FastAPI(title="Todo & AI API")

@app.on_event("startup")
async def startup(): await startup_event()
@app.on_event("shutdown")
async def shutdown():
     await shutdown_event()

# This CORS Middleware is correct for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- THE LAST GOOD, WORKING ROUTING CONFIGURATION ---

# Includes routers at the root, creating paths like /lists, /items
app.include_router(config.router)
app.include_router(todos.router)
app.include_router(items.router)

# Includes the AI router at /ai, creating paths like /ai/sessions, /ai/ws
app.include_router(ai_api_router, prefix="/ai")

# --- THE SURGICAL ADDITION FOR LIVEKIT ---
# This adds the LiveKit token endpoint at /api/livekit/token,
# matching the hardcoded URL in the ConferenceRoom component.
app.include_router(livekit.router, prefix="/api")

@app.get("/")
def read_root(): return {"status": "API is running."}

# # app/main.py

# from dotenv import load_dotenv
# load_dotenv()

# from fastapi import APIRouter, FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# # --- Import SPECIFIC Routers ---
# from app.routers import todos, items, config, livekit
# from ai.main import api_router as ai_api_router
# from ai.routers.sessions import router as sessions_router
# from ai.routers.websocket import router as websocket_router

# from ai.main import startup_event as ai_startup_event, shutdown_event as ai_shutdown_event

# app = FastAPI(title="Todo & AI API")

# @app.on_event("startup")
# async def startup(): await ai_startup_event()
# @app.on_event("shutdown")
# async def shutdown(): await ai_shutdown_event()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# api_router = APIRouter(prefix="/api")

# # --- Include All Routers with a Unified "/api" Prefix ---
# app.include_router(todos.router, prefix="/api")
# app.include_router(items.router, prefix="/api")
# app.include_router(config.router, prefix="/api")
# app.include_router(livekit.router, prefix="/api")

# # 3. Create a sub-router for the /ai prefix
# ai_router = APIRouter(prefix="/ai", tags=["AI Chat Assistant"])
# ai_router.include_router(sessions_router)  # Will create /ai/sessions
# ai_router.include_router(websocket_router) # Will create /ai/ws

# # 4. Add the AI sub-router to the main API router
# api_router.include_router(ai_router)

# # 5. Mount the single, unified API router to the main app
# app.include_router(api_router)


# @app.get("/")
# def read_root(): return {"status": "Server is running"}
# # # app/main.py

# # from fastapi import FastAPI
# # from fastapi.middleware.cors import CORSMiddleware

# # # --- Import Routers from all modules ---
# # from app.routers import todos, items, config, livekit
# # from ai.main import api_router as ai_api_router
# # from ai.main import startup_event as ai_startup_event, shutdown_event as ai_shutdown_event

# # # --- Main Application Initialization ---
# # app = FastAPI(
# #     title="Todo & AI API",
# #     description="A single API service for managing todo lists and interacting with an AI chat assistant.",
# #     version="1.0.0",
# # )

# # # --- Register Lifecycle Events ---
# # @app.on_event("startup")
# # async def startup():
# #     await ai_startup_event()

# # @app.on_event("shutdown")
# # async def shutdown():
# #     await ai_shutdown_event()

# # # --- Add CORS Middleware ---
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # # --- Include All Routers with a Unified "/api" Prefix ---

# # # Mount the CRUD routers directly under /api
# # app.include_router(config.router, prefix="/api")
# # app.include_router(todos.router, prefix="/api") # Serves -> /api/lists
# # app.include_router(items.router, prefix="/api")
# # app.include_router(livekit.router, prefix="/api") # Serves -> /api/livekit/token

# # # Mount the entire AI application's router under /api/ai
# # # This is the key change to match the frontend's expectations.
# # app.include_router(
# #     ai_api_router,
# #     prefix="/api/ai", # Serves -> /api/ai/sessions and /api/ai/ws
# #     tags=["AI Chat Assistant"]
# # )

# # # --- Root Health Check ---
# # @app.get("/", tags=["Health Check"])
# # async def read_root():
# #     return {"status": "Server is running. API is at /api"}
# # # # app/main.py


# # # from fastapi import FastAPI
# # # from fastapi.middleware.cors import CORSMiddleware

# # # from app.routers import livekit

# # # # --- Import Routers from the CRUD 'app' module ---
# # # from app.routers import todos, items, config

# # # # --- Import Router and Lifecycle Events from the 'ai' module ---
# # # # Use 'as' to create clear aliases and avoid potential name conflicts
# # # from ai.main import api_router as ai_api_router
# # # from ai.main import startup_event as ai_startup_event
# # # from ai.main import shutdown_event as ai_shutdown_event


# # # # --- Main Application Initialization ---
# # # app = FastAPI(
# # #     title="Todo & AI API",
# # #     description="A single API service for managing todo lists and interacting with an AI chat assistant.",
# # #     version="1.0.0",
# # # )

# # # # --- Register Lifecycle Events ---
# # # # The main app's startup event will trigger the ai module's startup.
# # # @app.on_event("startup")
# # # async def startup():
# # #     await ai_startup_event()

# # # # The main app's shutdown event will trigger the ai module's shutdown.
# # # @app.on_event("shutdown")
# # # async def shutdown():
# # #     await ai_shutdown_event()


# # # # --- Add Middleware ---
# # # # This middleware will apply to all routes, including those from the 'ai' module.
# # # # app.add_middleware(
# # # #     CORSMiddleware,
# # # #     allow_origins=["*"],
# # # #     allow_credentials=True,
# # # #     allow_methods=["*"],
# # # #     allow_headers=["*"],
# # # # )
# # # app.add_middleware(
# # #     CORSMiddleware,
# # #     allow_origins=["*"], # Allows all origins
# # #     allow_credentials=True,
# # #     allow_methods=["*"], # Allows all methods
# # #     allow_headers=["*"], # Allows all headers
# # # )

# # # # --- Include Routers ---
# # # # Include the CRUD routers at the root level
# # # app.include_router(config.router)
# # # app.include_router(todos.router)
# # # app.include_router(items.router)
# # # # app.include_router(ai_api_router, prefix="/ai")

# # # # Mount the entire AI application under the /ai prefix
# # # app.include_router(
# # #     ai_api_router,
# # #     prefix="/ai",
# # #     tags=["AI Chat Assistant"]  # Group AI routes in the docs
# # # )

# # # app.include_router(livekit.router, prefix="/api")
# # # # --- Root Health Check ---
# # # @app.get("/", tags=["Health Check"])
# # # async def read_root():
# # #     return {"status": "Unified API is running. See /docs for details."}
