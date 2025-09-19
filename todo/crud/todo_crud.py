from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sql_update, delete as sql_delete
from todo import models
from todo.api.v1.todos.schemas import TodoItemResponse, TodoItemCreate, TodoItemUpdate


async def create(db: AsyncSession, todo: TodoItemCreate):
    db_item = models.TodoItem(title=todo.title, description=todo.description)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.TodoItem).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def get(db: AsyncSession, item_id: int):
    result = await db.execute(
        select(models.TodoItem).where(models.TodoItem.id == item_id)
    )
    return result.scalars().first()

async def update(db: AsyncSession, item_id: int, update_data: TodoItemUpdate) -> TodoItemResponse:
    update_dict = update_data.model_dump(exclude_unset=True)
    if not update_dict:
        return await get(db, item_id)
    
    result = await db.execute(
        sql_update(models.TodoItem)
        .where(models.TodoItem.id == item_id)
        .values(**update_dict)
        .returning(models.TodoItem)
    )
    await db.commit()
    return result.scalars().first()


async def delete(db: AsyncSession, item_id: int):
    item = await get(db, item_id)
    if item is None:
        return None
    await db.execute(
        sql_delete(models.TodoItem).where(models.TodoItem.id == item_id)
    )
    await db.commit()
    return item


    
    
