# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Import Routers from the CRUD 'app' module ---
from .routers import todos, items

# --- Import Router and Lifecycle Events from the 'ai' module ---
# Use 'as' to create clear aliases and avoid potential name conflicts
from ai.main import api_router as ai_api_router
from ai.main import startup_event as ai_startup_event
from ai.main import shutdown_event as ai_shutdown_event


# --- Main Application Initialization ---
app = FastAPI(
    title="Unified Todo & AI API",
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
app.include_router(todos.router)
app.include_router(items.router)

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
# # app/main.py 

# from fastapi import FastAPI
# from .routers import todos, items
# from fastapi.middleware.cors import CORSMiddleware
# app = FastAPI(
#     title="Simple Todo API",
#     description="A minimalist API for managing todo lists and items.",
#     version="1.0.0",
# )

# # Include the todos router (handles /lists endpoints)
# app.include_router(todos.router)

# # FIXED: Remove the prefix since paths are now defined in the router
# app.include_router(items.router)

# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

# @app.get("/", tags=["Health Check"])
# async def read_root():
#     return {"status": "API is running"}
# # # app/main.py (Modified)

# # from fastapi import FastAPI
# # # REMOVE: from .database import Base, engine # We no longer need these here
# # from .routers import todos, items

# # app = FastAPI(
# #     title="Simple Todo API",
# #     description="A minimalist API for managing todo lists and items.",
# #     version="1.0.0",
# # )

# # # DELETE THE ENTIRE @app.on_event("startup") BLOCK.
# # # Alembic now handles table creation. The application should not
# # # be modifying the database schema on its own.
# # #
# # # @app.on_event("startup")
# # # async def startup_event():
# # #     async with engine.begin() as conn:
# # #         await conn.run_sync(Base.metadata.create_all)

# # # The rest of the file remains the same.
# # app.include_router(todos.router)
# # app.include_router(items.router, prefix="/lists")

# # @app.get("/", tags=["Health Check"])
# # async def read_root():
# #     return {"status": "API is running"}