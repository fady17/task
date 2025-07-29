# app/db/schemas.py
from pydantic import BaseModel
from typing import Optional
# ==============================================================================
# CORE TODO SCHEMAS
# ==============================================================================

# Base schema with just the title
class TodoItemBase(BaseModel):
    title: str

# Schema for creating a new item - can optionally set completed status
class TodoItemCreate(TodoItemBase):
    completed: bool = False

# Schema for updating an item - all fields optional for partial updates
class TodoItemUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None

# Response schema with all database fields
class TodoItem(TodoItemBase):
    id: int
    completed: bool
    list_id: int

    class Config:
        from_attributes = True

# ==============================================================================
# UPDATED: TODO LIST SCHEMAS WITH ANALYTICS
# ==============================================================================

# NEW: Schema for computed statistics of a list
class TodoListStats(BaseModel):
    total_items: int
    completed_items: int
    percentage_complete: int

# Base schema for todo lists
class TodoListBase(BaseModel):
    title: str

# Schema for creating a new list
class TodoListCreate(TodoListBase):
    pass

# Schema for updating a list
class TodoListUpdate(BaseModel):
    title: Optional[str] = None

# UPDATED: Response schema now includes the 'stats' object
class TodoList(TodoListBase):
    id: int
    items: list[TodoItem] = []
    stats: TodoListStats  # ADDED: Analytics are now part of the list object

    class Config:
        from_attributes = True
