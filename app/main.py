# app/main.py 

from fastapi import FastAPI
from .routers import todos, items
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="Simple Todo API",
    description="A minimalist API for managing todo lists and items.",
    version="1.0.0",
)

# Include the todos router (handles /lists endpoints)
app.include_router(todos.router)

# FIXED: Remove the prefix since paths are now defined in the router
app.include_router(items.router)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "API is running"}
# # app/main.py (Modified)

# from fastapi import FastAPI
# # REMOVE: from .database import Base, engine # We no longer need these here
# from .routers import todos, items

# app = FastAPI(
#     title="Simple Todo API",
#     description="A minimalist API for managing todo lists and items.",
#     version="1.0.0",
# )

# # DELETE THE ENTIRE @app.on_event("startup") BLOCK.
# # Alembic now handles table creation. The application should not
# # be modifying the database schema on its own.
# #
# # @app.on_event("startup")
# # async def startup_event():
# #     async with engine.begin() as conn:
# #         await conn.run_sync(Base.metadata.create_all)

# # The rest of the file remains the same.
# app.include_router(todos.router)
# app.include_router(items.router, prefix="/lists")

# @app.get("/", tags=["Health Check"])
# async def read_root():
#     return {"status": "API is running"}