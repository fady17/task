# app/main.py


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Import Routers from the CRUD 'app' module ---
from .routers import todos, items, config

# --- Import Router and Lifecycle Events from the 'ai' module ---
# Use 'as' to create clear aliases and avoid potential name conflicts
from ai.main import api_router as ai_api_router
from ai.main import startup_event as ai_startup_event
from ai.main import shutdown_event as ai_shutdown_event


# --- Main Application Initialization ---
app = FastAPI(
    title="Todo & AI API",
    description="A single API service for managing todo lists and interacting with an AI chat assistant.",
    version="1.0.0",
)

# --- Register Lifecycle Events ---
# The main app's startup event will trigger the ai module's startup.
@app.on_event("startup")
async def startup():
    await ai_startup_event()

# The main app's shutdown event will trigger the ai module's shutdown.
@app.on_event("shutdown")
async def shutdown():
    await ai_shutdown_event()


# --- Add Middleware ---
# This middleware will apply to all routes, including those from the 'ai' module.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Include Routers ---
# Include the CRUD routers at the root level
app.include_router(config.router)
app.include_router(todos.router)
app.include_router(items.router)
# app.include_router(ai_api_router, prefix="/ai")

# Mount the entire AI application under the /ai prefix
app.include_router(
    ai_api_router,
    prefix="/ai",
    tags=["AI Chat Assistant"]  # Group AI routes in the docs
)


# --- Root Health Check ---
@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "Unified API is running. See /docs for details."}
