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
# # app/db/schemas.py

# """
# This module defines the Pydantic schemas for a simple, single-user todo API.
# All user- and team-related schemas have been removed.
# """
# from pydantic import BaseModel
# from typing import Optional

# # ==============================================================================
# # CORE TODO SCHEMAS
# # ==============================================================================

# # Base schema with just the title
# class TodoItemBase(BaseModel):
#     title: str

# # Schema for creating a new item - can optionally set completed status
# class TodoItemCreate(TodoItemBase):
#     completed: bool = False  # FIXED: Added completed field with default

# # Schema for updating an item - all fields optional for partial updates
# class TodoItemUpdate(BaseModel):
#     title: Optional[str] = None
#     completed: Optional[bool] = None

# # Response schema with all database fields
# class TodoItem(TodoItemBase):
#     id: int
#     completed: bool
#     list_id: int  # FIXED: Added list_id field that exists in the model

#     class Config:
#         from_attributes = True


# # NEW: Schema for computed statistics of a list
# class TodoListStats(BaseModel):
#     total_items: int
#     completed_items: int
#     percentage_complete: int


# # Base schema for todo lists
# class TodoListBase(BaseModel):
#     title: str

# # Schema for creating a new list
# class TodoListCreate(TodoListBase):
#     pass

# # Schema for updating a list
# class TodoListUpdate(BaseModel):
#     title: Optional[str] = None

# # Response schema with all database fields and nested items
# class TodoList(TodoListBase):
#     id: int
#     items: list[TodoItem] = []
#     stats: TodoListStats

#     class Config:
#         from_attributes = True
# # # app/db/schemas.py

# # """
# # This module defines the Pydantic schemas for a simple, single-user todo API.
# # All user- and team-related schemas have been removed.
# # """
# # from pydantic import BaseModel

# # # ==============================================================================
# # # CORE TODO SCHEMAS
# # # ==============================================================================

# # # Pseudocode Plan for TodoItem Schemas:
# # # SCHEMA TodoItemBase:
# # #   - Core attribute: title (string)
# # class TodoItemBase(BaseModel):
# #     title: str

# # # SCHEMA TodoItemCreate:
# # #   - Used for creating a new item. Inherits from Base.
# # class TodoItemCreate(TodoItemBase):
# #     pass

# # # SCHEMA TodoItem (for response):
# # #   - Includes database-generated fields 'id' and 'completed'.
# # class TodoItem(TodoItemBase):
# #     id: int
# #     completed: bool

# #     class Config:
# #         from_attributes = True

# # # Pseudocode Plan for TodoList Schemas:
# # # SCHEMA TodoListBase:
# # #   - Core attribute: title (string)
# # class TodoListBase(BaseModel):
# #     title: str

# # # SCHEMA TodoListCreate:
# # #   - Used for creating a new list.
# # class TodoListCreate(TodoListBase):
# #     pass

# # # SCHEMA TodoList (for response):
# # #   - Includes 'id' and a nested list of its 'items'.
# # class TodoList(TodoListBase):
# #     id: int
# #     items: list[TodoItem] = [] # A list of TodoItem response schemas

# #     class Config:
# #         from_attributes = True