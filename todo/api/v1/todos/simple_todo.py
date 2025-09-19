from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException, status, Response
from todo.api.v1.todos.schemas import TodoItem, TodoItemCreate, TodoItemUpdate
from todo.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
from todo.crud import todo_crud

router = APIRouter()

@router.get("/todos")
@router.get("/todos/{todo_id}")
async def get_todos(todo_id: Union[None, int] = None, db: AsyncSession = Depends(get_db), ) -> list[TodoItem] : 
    try:
        if todo_id is None:
            todos = await todo_crud.get_all(db)
            return todos
        else:
            todo = await todo_crud.get(db, todo_id)
            if todo is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
            return [todo]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

            


@router.post("/todos")
async def create_todo(item: TodoItemCreate, response: Response, db: AsyncSession = Depends(get_db)) -> TodoItem:
    try:
        todo = await todo_crud.create(db, item)
        response.status_code = status.HTTP_201_CREATED
        return todo
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/todos/{todo_id}")
async def update_todo(todo_id: int, item: TodoItemUpdate, db: AsyncSession = Depends(get_db)) -> TodoItem:
    ##may add authentication later
    try:
        existing_todo = await todo_crud.get(db, todo_id)
        if existing_todo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
        updated_todo = await todo_crud.update(db, todo_id, item)
        return updated_todo
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: AsyncSession = Depends(get_db)) -> TodoItem:
    try:
        existing_todo = await todo_crud.get(db, todo_id)
        if existing_todo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
        deleted_todo = await todo_crud.delete(db, todo_id)
        return deleted_todo
    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
