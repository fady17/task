# app/routers/todos.py
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db import database, models, schemas

router = APIRouter(
    prefix="/lists",
    tags=["Todo Lists"],
)

DBSession = Annotated[AsyncSession, Depends(database.get_db)]

# Helper function to calculate list statistics from a model instance.
def _calculate_stats(db_list: models.TodoList) -> schemas.TodoListStats:
    """Calculates statistics for a given TodoList model instance."""
    # This is safe now because 'items' will always be eagerly loaded.
    total_items = len(db_list.items)
    if total_items == 0:
        return schemas.TodoListStats(
            total_items=0, completed_items=0, percentage_complete=0
        )

    completed_items = sum(1 for item in db_list.items if item.completed)
    percentage = int(round((completed_items / total_items) * 100))

    return schemas.TodoListStats(
        total_items=total_items,
        completed_items=completed_items,
        percentage_complete=percentage,
    )

# Helper to format a DB model into the full Pydantic response schema with stats.
def _format_list_response(db_list: models.TodoList) -> schemas.TodoList:
    """Formats a TodoList model for API response, including calculated stats."""
    list_data = db_list.__dict__
    list_data["stats"] = _calculate_stats(db_list)
    return schemas.TodoList.model_validate(list_data)


# --- DEFINITIVELY FIXED: Handles post-commit state and relationship loading ---
@router.post("/", response_model=schemas.TodoList, status_code=status.HTTP_201_CREATED)
async def create_todo_list(list_data: schemas.TodoListCreate, db: DBSession):
    """Creates a new todo list and returns it with initial stats."""
    db_list = models.TodoList(title=list_data.title)
    db.add(db_list)
    await db.commit()

    # STEP 1: Refresh the instance to get its database-assigned ID and
    # make it "live" in the session again. This prevents the lazy-load on db_list.id
    await db.refresh(db_list)

    # STEP 2: Now that db_list.id is safely loaded, we still need to
    # eagerly load the `items` relationship before passing it to the format helper.
    query = (
        select(models.TodoList)
        .where(models.TodoList.id == db_list.id)
        .options(selectinload(models.TodoList.items))
    )
    result = await db.execute(query)
    # The result of this query is the fully loaded object we can safely use.
    newly_created_list = result.scalars().first()

    if newly_created_list is None:
        # This case is highly unlikely but handles potential race conditions.
        raise HTTPException(status_code=500, detail="Failed to retrieve created list.")

    return _format_list_response(newly_created_list)


@router.get("/", response_model=list[schemas.TodoList])
async def get_all_todo_lists(db: DBSession):
    """Retrieves all todo lists with their items and stats."""
    query = select(models.TodoList).options(selectinload(models.TodoList.items))
    result = await db.execute(query)
    db_lists = result.scalars().all()

    return [_format_list_response(db_list) for db_list in db_lists]


@router.get("/{list_id}", response_model=schemas.TodoList)
async def get_todo_list_by_id(list_id: int, db: DBSession):
    """Retrieves a single todo list by its ID, including its items and stats."""
    query = (
        select(models.TodoList)
        .where(models.TodoList.id == list_id)
        .options(selectinload(models.TodoList.items))
    )
    result = await db.execute(query)
    db_list = result.scalars().first()

    if db_list is None:
        raise HTTPException(status_code=404, detail="Todo list not found")

    return _format_list_response(db_list)


@router.put("/{list_id}", response_model=schemas.TodoList)
async def update_todo_list(
    list_id: int,
    list_data: schemas.TodoListUpdate,
    db: DBSession,
):
    """Updates a list's title and returns the full updated list with stats."""
    query = (
        select(models.TodoList)
        .where(models.TodoList.id == list_id)
        .options(selectinload(models.TodoList.items))
    )
    result = await db.execute(query)
    db_list = result.scalars().first()

    if db_list is None:
        raise HTTPException(status_code=404, detail="Todo list not found")

    # Only update if the title is provided
    if list_data.title is not None:
        db_list.title = list_data.title
        await db.commit()
        # After updating, we must refresh to get the latest state before returning
        await db.refresh(db_list)

    return _format_list_response(db_list)


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_list(list_id: int, db: DBSession):
    """Deletes a todo list and all of its items."""
    result = await db.execute(select(models.TodoList).where(models.TodoList.id == list_id))
    db_list = result.scalars().first()

    if db_list is None:
        raise HTTPException(status_code=404, detail="Todo list not found")

    await db.delete(db_list)
    await db.commit()
    return None
# # app/routers/todos.py

# from typing import Annotated
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlalchemy.orm import selectinload

# from app.db import database, models, schemas

# router = APIRouter(
#     prefix="/lists",
#     tags=["Todo Lists"],
# )

# DBSession = Annotated[AsyncSession, Depends(database.get_db)]

# # NEW: Helper function to calculate list statistics from a model instance.
# def _calculate_stats(db_list: models.TodoList) -> schemas.TodoListStats:
#     total_items = len(db_list.items)
#     if total_items == 0:
#         return schemas.TodoListStats(
#             total_items=0, completed_items=0, percentage_complete=0
#         )

#     completed_items = sum(1 for item in db_list.items if item.completed)
#     percentage = int(round((completed_items / total_items) * 100))

#     return schemas.TodoListStats(
#         total_items=total_items,
#         completed_items=completed_items,
#         percentage_complete=percentage,
#     )

# # NEW: Helper to format a DB model into the full Pydantic response schema with stats.
# def _format_list_response(db_list: models.TodoList) -> schemas.TodoList:
#     return schemas.TodoList(
#         id=db_list.id,
#         title=db_list.title,
#         items=db_list.items,  # Assumes items are already eager-loaded
#         stats=_calculate_stats(db_list),
#     )

# @router.post("/", response_model=schemas.TodoList, status_code=status.HTTP_201_CREATED)
# async def create_todo_list(list_data: schemas.TodoListCreate, db: DBSession):
#     """Creates a new todo list."""
#     db_list = models.TodoList(title=list_data.title)
#     db.add(db_list)
#     await db.commit()
#     await db.refresh(db_list)
#     return _format_list_response(db_list)
    
#     # FIXED: Query the list again with eager loading to avoid lazy loading issues
#     # query = (
#     #     select(models.TodoList)
#     #     .where(models.TodoList.id == db_list.id)
#     #     .options(selectinload(models.TodoList.items))
#     # )
#     # result = await db.execute(query)
#     # return result.scalars().first()



# @router.get("/", response_model=list[schemas.TodoList])
# async def get_all_todo_lists(db: DBSession):
#     """Retrieves all todo lists."""
#     # FIXED: Use selectinload to eagerly load items relationship
#     query = select(models.TodoList).options(selectinload(models.TodoList.items))
#     result = await db.execute(query)
#     return result.scalars().all()

# @router.get("/{list_id}", response_model=schemas.TodoList)
# async def get_todo_list_by_id(list_id: int, db: DBSession):
#     """Retrieves a single todo list by its ID, including its items."""
#     query = (
#         select(models.TodoList)
#         .where(models.TodoList.id == list_id)
#         .options(selectinload(models.TodoList.items))
#     )
#     result = await db.execute(query)
#     db_lists = result.scalars().first()

#     if db_lists is None:
#         raise HTTPException(status_code=404, detail="Todo list not found")
#     # return db_list
#     return [_format_list_response(db_list) for db_list in db_lists]


# # FIXED: Use proper update schema
# @router.put("/{list_id}", response_model=schemas.TodoList)
# async def update_todo_list(
#     list_id: int,
#     list_data: schemas.TodoListUpdate,  # FIXED: Use update schema
#     db: DBSession,
# ):
#     """Updates the title of an existing todo list."""
#     result = await db.execute(select(models.TodoList).where(models.TodoList.id == list_id))
#     db_list = result.scalars().first()

#     if db_list is None:
#         raise HTTPException(status_code=404, detail="Todo list not found")

#     # Only update if title is provided
#     if list_data.title is not None:
#         db_list.title = list_data.title
        
#     await db.commit()
#     await db.refresh(db_list)
    
#     # FIXED: Query again with eager loading to avoid lazy loading issues
#     query = (
#         select(models.TodoList)
#         .where(models.TodoList.id == list_id)
#         .options(selectinload(models.TodoList.items))
#     )
#     result = await db.execute(query)
#     return result.scalars().first()

# @router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_todo_list(list_id: int, db: DBSession):
#     """Deletes a todo list and all of its items."""
#     result = await db.execute(select(models.TodoList).where(models.TodoList.id == list_id))
#     db_list = result.scalars().first()

#     if db_list is None:
#         raise HTTPException(status_code=404, detail="Todo list not found")

#     await db.delete(db_list)
#     await db.commit()
#     return None
# # # app/routers/todos.py

# # from typing import Annotated
# # from fastapi import APIRouter, Depends, HTTPException, status
# # from sqlalchemy.ext.asyncio import AsyncSession
# # from sqlalchemy.future import select
# # from sqlalchemy.orm import selectinload

# # from app.db import database, models, schemas


# # # This router will handle all top-level list operations.
# # # Everything here will live under the `/lists` path.
# # router = APIRouter(
# #     prefix="/lists",
# #     tags=["Todo Lists"],
# # )

# # # This little alias is a great trick. It cleans up our function signatures
# # # and makes it super clear what 'db' is: it's an AsyncSession that we get
# # # by depending on our get_db function.
# # DBSession = Annotated[AsyncSession, Depends(database.get_db)]


# # # --- Endpoint 1: Create a new list ---
# # # This is the entry point. A simple POST to the collection.
# # @router.post("/", response_model=schemas.TodoList, status_code=status.HTTP_201_CREATED)
# # async def create_todo_list(list_data: schemas.TodoListCreate, db: DBSession):
# #     """Creates a new todo list."""
# #     # This is pretty straightforward: take the title from the request body,
# #     # create a new model instance, and then add/commit/refresh.
# #     db_list = models.TodoList(title=list_data.title)
# #     db.add(db_list)
# #     await db.commit()
# #     await db.refresh(db_list)
# #     return db_list


# # # --- Endpoint 2: Get all lists ---
# # # The "show me everything" endpoint.
# # @router.get("/", response_model=list[schemas.TodoList])
# # async def get_all_todo_lists(db: DBSession):
# #     """Retrieves all todo lists."""
# #     # Just a basic select-all query.
# #     query = select(models.TodoList)
# #     result = await db.execute(query)
# #     return result.scalars().all()


# # # --- Endpoint 3: Get a specific list ---
# # # Here, we need to fetch a single list by its ID.
# # # This one is interesting because we also want to fetch all its child items
# # # at the same time to avoid extra database trips.
# # @router.get("/{list_id}", response_model=schemas.TodoList)
# # async def get_todo_list_by_id(list_id: int, db: DBSession):
# #     """Retrieves a single todo list by its ID, including its items."""
# #     # The key here is `selectinload(models.TodoList.items)`. This tells
# #     # SQLAlchemy: "When you fetch the list, also run a second query to
# #     # grab all its items and load them into the .items attribute." It's
# #     # a classic optimization to solve the N+1 query problem.
# #     query = (
# #         select(models.TodoList)
# #         .where(models.TodoList.id == list_id)
# #         .options(selectinload(models.TodoList.items))
# #     )
# #     result = await db.execute(query)
# #     db_list = result.scalars().first()

# #     # We always have to handle the "what if it doesn't exist?" case.
# #     if db_list is None:
# #         raise HTTPException(status_code=404, detail="Todo list not found")
# #     return db_list


# # # --- Endpoint 4: Update a list ---
# # # A standard PUT operation to change a list's details.
# # @router.put("/{list_id}", response_model=schemas.TodoList)
# # async def update_todo_list(
# #     list_id: int,
# #     list_data: schemas.TodoListCreate, # Reusing the Create schema is fine here.
# #     db: DBSession,
# # ):
# #     """Updates the title of an existing todo list."""
# #     # The standard pattern for an update: fetch, check, modify, commit.
# #     result = await db.execute(select(models.TodoList).where(models.TodoList.id == list_id))
# #     db_list = result.scalars().first()

# #     if db_list is None:
# #         raise HTTPException(status_code=404, detail="Todo list not found")

# #     # We just update the attribute on the model instance. SQLAlchemy's
# #     # session management keeps track of this change.
# #     db_list.title = list_data.title
# #     await db.commit()
# #     await db.refresh(db_list)
# #     return db_list


# # # --- Endpoint 5: Delete a list ---
# # # The destructive action. Needs to be handled carefully.
# # @router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
# # async def delete_todo_list(list_id: int, db: DBSession):
# #     """Deletes a todo list and all of its items."""
# #     # Same fetch-and-check pattern.
# #     result = await db.execute(select(models.TodoList).where(models.TodoList.id == list_id))
# #     db_list = result.scalars().first()

# #     if db_list is None:
# #         raise HTTPException(status_code=404, detail="Todo list not found")

# #     await db.delete(db_list)
# #     await db.commit()

# #     # For a 204 response, we shouldn't return any content, so we just return None.
# #     return None