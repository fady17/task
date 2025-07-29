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


app.include_router(items.router)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "API is running"}
