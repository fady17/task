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
