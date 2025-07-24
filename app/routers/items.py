# app/routers/items.py
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import database, models, schemas

router = APIRouter(
    tags=["Todo Items"],
)

DBSession = Annotated[AsyncSession, Depends(database.get_db)]

async def get_list_or_404(list_id: int, db: DBSession) -> models.TodoList:
    """Helper to get a list or raise a 404, keeping endpoints clean."""
    result = await db.execute(select(models.TodoList).where(models.TodoList.id == list_id))
    db_list = result.scalars().first()
    if not db_list:
        raise HTTPException(status_code=404, detail=f"Todo list with id {list_id} not found")
    return db_list

@router.post("/{list_id}/items/", response_model=schemas.TodoItem, status_code=status.HTTP_201_CREATED)
async def create_todo_item(
    list_id: int,
    item_data: schemas.TodoItemCreate,
    db: DBSession,
):
    """Creates a new todo item within a specific list."""
    await get_list_or_404(list_id, db)

    db_item = models.TodoItem(
        title=item_data.title,
        list_id=list_id,
        completed=item_data.completed
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

# --- UPDATED TO HANDLE PARTIAL UPDATES ---
@router.put("/{list_id}/items/{item_id}", response_model=schemas.TodoItem)
async def update_todo_item(
    list_id: int,
    item_id: int,
    item_data: schemas.TodoItemUpdate,  # CHANGED: Use partial update schema
    db: DBSession,
):
    """Updates the title or completed status of a todo item."""
    query = select(models.TodoItem).where(
        models.TodoItem.id == item_id,
        models.TodoItem.list_id == list_id
    )
    result = await db.execute(query)
    db_item = result.scalars().first()

    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found in list {list_id}")

    # CHANGED: Get a dictionary of provided fields from the Pydantic model
    update_data = item_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided",
        )

    # Iterate over the provided fields and update the database model
    for key, value in update_data.items():
        setattr(db_item, key, value)

    await db.commit()
    await db.refresh(db_item)
    return db_item

@router.delete("/{list_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_item(
    list_id: int,
    item_id: int,
    db: DBSession,
):
    """Deletes a specific todo item from a list."""
    query = select(models.TodoItem).where(
        models.TodoItem.id == item_id,
        models.TodoItem.list_id == list_id
    )
    result = await db.execute(query)
    db_item = result.scalars().first()

    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found in list {list_id}")

    await db.delete(db_item)
    await db.commit()
    return None
# # app/routers/items.py

# from typing import Annotated
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select

# from app.db import database, models, schemas

# # Fixed router with proper nested paths
# router = APIRouter(
#     tags=["Todo Items"],
# )

# DBSession = Annotated[AsyncSession, Depends(database.get_db)] 

# async def get_list_or_404(list_id: int, db: DBSession) -> models.TodoList:
#     """Helper to get a list or raise a 404, keeping endpoints clean."""
#     result = await db.execute(select(models.TodoList).where(models.TodoList.id == list_id))
#     db_list = result.scalars().first()
#     if not db_list:
#         raise HTTPException(status_code=404, detail=f"Todo list with id {list_id} not found")
#     return db_list


# @router.post("/{list_id}/items/", response_model=schemas.TodoItem, status_code=status.HTTP_201_CREATED)
# async def create_todo_item(
#     list_id: int,
#     item_data: schemas.TodoItemCreate,
#     db: DBSession,
# ):
#     """Creates a new todo item within a specific list."""
#     await get_list_or_404(list_id, db)
    
#     db_item = models.TodoItem(title=item_data.title, list_id=list_id)
#     db.add(db_item)
#     await db.commit()
#     await db.refresh(db_item)
#     return db_item

# # FIXED: Handle full item update as expected by tests
# @router.put("/{list_id}/items/{item_id}", response_model=schemas.TodoItem)
# async def update_todo_item(
#     list_id: int,
#     item_id: int,
#     item_data: schemas.TodoItemUpdate,  # FIXED: Tests expect full TodoItem schema
#     db: DBSession,
# ):
#     """Updates the title or completed status of a todo item."""
#     query = select(models.TodoItem).where(
#         models.TodoItem.id == item_id,
#         models.TodoItem.list_id == list_id
#     )
#     result = await db.execute(query)
#     db_item = result.scalars().first()

#     if db_item is None:
#         raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found in list {list_id}")

#     # Update all provided fields
#     update_data = item_data.model_dump(exclude_unset=True)
#     if not update_data:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="No update data provided",
#         )

#     for key, value in update_data.items():
#         setattr(db_item, key, value)

#     await db.commit()
#     await db.refresh(db_item)
#     return db_item


# # FIXED: Match expected URL pattern
# @router.delete("/{list_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_todo_item(
#     list_id: int,
#     item_id: int,
#     db: DBSession,
# ):
#     """Deletes a specific todo item from a list."""
#     query = select(models.TodoItem).where(
#         models.TodoItem.id == item_id,
#         models.TodoItem.list_id == list_id
#     )
#     result = await db.execute(query)
#     db_item = result.scalars().first()

#     if db_item is None:
#         raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found in list {list_id}")

#     await db.delete(db_item)
#     await db.commit()
#     return None
# # # app/routers/items.py

# # from typing import Annotated
# # from fastapi import APIRouter, Depends, HTTPException, status
# # from sqlalchemy.ext.asyncio import AsyncSession
# # from sqlalchemy.future import select

# # from app.db import database, models, schemas

# # # Fixed router with proper nested paths
# # router = APIRouter(
# #     tags=["Todo Items"],
# # )

# # DBSession = Annotated[AsyncSession, Depends(database.get_db)] 

# # async def get_list_or_404(list_id: int, db: DBSession) -> models.TodoList:
# #     """Helper to get a list or raise a 404, keeping endpoints clean."""
# #     result = await db.execute(select(models.TodoList).where(models.TodoList.id == list_id))
# #     db_list = result.scalars().first()
# #     if not db_list:
# #         raise HTTPException(status_code=404, detail=f"Todo list with id {list_id} not found")
# #     return db_list

# # # FIXED: Added {list_id} to the path
# # @router.post("/{list_id}/items", response_model=schemas.TodoItem, status_code=status.HTTP_201_CREATED)
# # async def create_todo_item(
# #     list_id: int,
# #     item_data: schemas.TodoItemCreate,
# #     db: DBSession,
# # ):
# #     """Creates a new todo item within a specific list."""
# #     await get_list_or_404(list_id, db)
    
# #     db_item = models.TodoItem(title=item_data.title, list_id=list_id)
# #     db.add(db_item)
# #     await db.commit()
# #     await db.refresh(db_item)
# #     return db_item

# # # FIXED: Added {list_id} to the path and use proper update schema
# # @router.put("/{list_id}/items/{item_id}", response_model=schemas.TodoItem)
# # async def update_todo_item(
# #     list_id: int,
# #     item_id: int,
# #     item_data: schemas.TodoItemUpdate,  # FIXED: Use proper update schema
# #     db: DBSession,
# # ):
# #     """Updates the title or completed status of a todo item."""
# #     query = select(models.TodoItem).where(
# #         models.TodoItem.id == item_id,
# #         models.TodoItem.list_id == list_id
# #     )
# #     result = await db.execute(query)
# #     db_item = result.scalars().first()

# #     if db_item is None:
# #         raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found in list {list_id}")

# #     # Update only provided fields (partial update)
# #     if item_data.title is not None:
# #         db_item.title = item_data.title
# #     if item_data.completed is not None:
# #         db_item.completed = item_data.completed
        
# #     await db.commit()
# #     await db.refresh(db_item)
# #     return db_item

# # # FIXED: Added {list_id} to the path
# # @router.delete("/{list_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
# # async def delete_todo_item(
# #     list_id: int,
# #     item_id: int,
# #     db: DBSession,
# # ):
# #     """Deletes a specific todo item from a list."""
# #     query = select(models.TodoItem).where(
# #         models.TodoItem.id == item_id,
# #         models.TodoItem.list_id == list_id
# #     )
# #     result = await db.execute(query)
# #     db_item = result.scalars().first()

# #     if db_item is None:
# #         raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found in list {list_id}")

# #     await db.delete(db_item)
# #     await db.commit()
# #     return None
# # # # app/routers/items.py

# # # # This router handles the items within a list. It's a classic example
# # # # of a nested resource in a RESTful API.
# # # from typing import Annotated
# # # from fastapi import APIRouter, Depends, HTTPException, status
# # # from sqlalchemy.ext.asyncio import AsyncSession
# # # from sqlalchemy.future import select

# # # from app.db import database, models, schemas


# # # # We'll define the router, but the prefix will be applied in main.py.
# # # # This keeps this file decoupled from the parent resource's path.
# # # router = APIRouter(
# # #     tags=["Todo Items"],
# # # )

# # # # We'll use the same clean dependency alias here.
# # # DBSession = Annotated[AsyncSession, Depends(database.get_db)] 


# # # # --- A Helper Function ---
# # # # It feels like we're going to be checking if a list exists a lot.
# # # # Let's pull that logic out into a helper so we don't repeat ourselves.
# # # async def get_list_or_404(list_id: int, db: DBSession) -> models.TodoList:
# # #     """Helper to get a list or raise a 404, keeping endpoints clean."""
# # #     result = await db.execute(select(models.TodoList).where(models.TodoList.id == list_id))
# # #     db_list = result.scalars().first()
# # #     if not db_list:
# # #         raise HTTPException(status_code=404, detail=f"Todo list with id {list_id} not found")
# # #     return db_list


# # # # --- Endpoint 1: Create an item in a list ---
# # # # This is the main way to add a task. Note the path will be something like
# # # # POST /lists/{list_id}/items
# # # @router.post("/", response_model=schemas.TodoItem, status_code=status.HTTP_201_CREATED)
# # # async def create_todo_item(
# # #     list_id: int, # This comes from the URL path
# # #     item_data: schemas.TodoItemCreate,
# # #     db: DBSession,
# # # ):
# # #     """Creates a new todo item within a specific list."""
# # #     # First, let's make sure the list we're adding to actually exists.
# # #     await get_list_or_404(list_id, db)

# # #     # Now we can safely create the item, making sure to link it with the list_id.
# # #     db_item = models.TodoItem(title=item_data.title, list_id=list_id)
# # #     db.add(db_item)
# # #     await db.commit()
# # #     await db.refresh(db_item)
# # #     return db_item


# # # # --- Endpoint 2: Update an item ---
# # # # For toggling 'completed' or editing the title.
# # # @router.put("/{item_id}", response_model=schemas.TodoItem)
# # # async def update_todo_item(
# # #     list_id: int,
# # #     item_id: int,
# # #     item_data: schemas.TodoItem, # We expect the full item shape for a PUT
# # #     db: DBSession,
# # # ):
# # #     """Updates the title or completed status of a todo item."""
# # #     # When updating a nested resource, it's crucial to make sure we're
# # #     # fetching the item from within the correct parent list. This prevents
# # #     # a user from, say, editing /lists/1/items/100 when item 100 actually
# # #     # belongs to list 2.
# # #     query = select(models.TodoItem).where(
# # #         models.TodoItem.id == item_id,
# # #         models.TodoItem.list_id == list_id  # This is the key security check
# # #     )
# # #     result = await db.execute(query)
# # #     db_item = result.scalars().first()

# # #     if db_item is None:
# # #         raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found in list {list_id}")

# # #     # Update the model attributes from the request body.
# # #     db_item.title = item_data.title
# # #     db_item.completed = item_data.completed
# # #     await db.commit()
# # #     await db.refresh(db_item)
# # #     return db_item


# # # # --- Endpoint 3: Delete an item ---
# # # @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
# # # async def delete_todo_item(
# # #     list_id: int,
# # #     item_id: int,
# # #     db: DBSession,
# # # ):
# # #     """Deletes a specific todo item from a list."""
# # #     # Same logic as the update: find the specific item within the specific list.
# # #     query = select(models.TodoItem).where(
# # #         models.TodoItem.id == item_id,
# # #         models.TodoItem.list_id == list_id
# # #     )
# # #     result = await db.execute(query)
# # #     db_item = result.scalars().first()

# # #     if db_item is None:
# # #         raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found in list {list_id}")

# # #     await db.delete(db_item)
# # #     await db.commit()
# # #     return None