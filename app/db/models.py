# app/db/models.py
"""
This module defines the SQLAlchemy ORM models for a simple, single-user
todo application. All concepts of multiple users and teams have been removed
to meet the core requirement.
"""
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

# ==============================================================================
# CORE TODO MODELS
# ==============================================================================

# Pseudocode Plan for the TodoList Class (Simplified):
# CLASS TodoList: A container for todo items.
#
#   INPUTS (for creation):
#     - title: string
#
#   OUTPUTS (when retrieved):
#     - id: integer (primary key)
#     - title: string
#     - items: a list of TodoItem objects belonging to this list.
#
#   RELATIONS:
#     - One-to-Many with TodoItem: A list contains many items.
class TodoList(Base):
    __tablename__ = "todo_lists"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)

    # The 'cascade' option ensures that when a TodoList is deleted,
    # all its associated TodoItems are also automatically deleted from the database.
    items: Mapped[list["TodoItem"]] = relationship(
        back_populates="todo_list", cascade="all, delete-orphan"
    )

# Pseudocode Plan for the TodoItem Class (Simplified):
# CLASS TodoItem: An individual task.
#
#   INPUTS (for creation):
#     - title: string
#     - list_id: integer (the ID of the list it belongs to)
#
#   OUTPUTS (when retrieved):
#     - id: integer (primary key)
#     - title: string
#     - completed: boolean
#     - list_id: integer
#
#   RELATIONS:
#     - Many-to-One with TodoList: Many items belong to one list.
class TodoItem(Base):
    __tablename__ = "todo_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    completed: Mapped[bool] = mapped_column(default=False)

    # This foreign key is non-nullable, as every item MUST belong to a list.
    list_id: Mapped[int] = mapped_column(ForeignKey("todo_lists.id"))

    # The relationship that allows an item object to access its parent list.
    todo_list: Mapped["TodoList"] = relationship(back_populates="items")
# # app/db/models.py

# """
# This module defines the SQLAlchemy ORM models for a simple, single-user
# todo application. All concepts of multiple users and teams have been removed
# to meet the core requirement.
# """
# from sqlalchemy import (
#     Boolean,
#     ForeignKey,
#     Integer,
#     String,
# )
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from .database import Base

# # ==============================================================================
# # CORE TODO MODELS
# # ==============================================================================

# # Pseudocode Plan for the TodoList Class (Simplified):
# # CLASS TodoList: A container for todo items.
# #
# #   INPUTS (for creation):
# #     - title: string
# #
# #   OUTPUTS (when retrieved):
# #     - id: integer (primary key)
# #     - title: string
# #     - items: a list of TodoItem objects belonging to this list.
# #
# #   RELATIONS:
# #     - One-to-Many with TodoItem: A list contains many items.
# class TodoList(Base):
#     __tablename__ = "todo_lists"
#     id: Mapped[int] = mapped_column(primary_key=True, index=True)
#     title: Mapped[str] = mapped_column(String)

#     # The 'cascade' option ensures that when a TodoList is deleted,
#     # all its associated TodoItems are also automatically deleted from the database.
#     items: Mapped[list["TodoItem"]] = relationship(
#         back_populates="todo_list", cascade="all, delete-orphan"
#     )

# # Pseudocode Plan for the TodoItem Class (Simplified):
# # CLASS TodoItem: An individual task.
# #
# #   INPUTS (for creation):
# #     - title: string
# #     - list_id: integer (the ID of the list it belongs to)
# #
# #   OUTPUTS (when retrieved):
# #     - id: integer (primary key)
# #     - title: string
# #     - completed: boolean
# #     - list_id: integer
# #
# #   RELATIONS:
# #     - Many-to-One with TodoList: Many items belong to one list.
# class TodoItem(Base):
#     __tablename__ = "todo_items"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     title: Mapped[str] = mapped_column(String)
#     completed: Mapped[bool] = mapped_column(default=False)

#     # This foreign key is non-nullable, as every item MUST belong to a list.
#     list_id: Mapped[int] = mapped_column(ForeignKey("todo_lists.id"))

#     # The relationship that allows an item object to access its parent list.
#     todo_list: Mapped["TodoList"] = relationship(back_populates="items")