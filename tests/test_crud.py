import pytest
from todo.crud import todo_crud
from todo.api.v1.todos.schemas import TodoItemCreate, TodoItemUpdate, TodoItemResponse
from todo.crud import auth_crud
from todo.api.auth.schemas import UserCreate, UserInDB


## todo_crud Tests
async def test_create_todo(db_session):
    todo_data : TodoItemCreate = TodoItemCreate(title="Test Todo", description="This is a test todo item.")
    db = db_session
    todo_item = await todo_crud.create(db, todo_data)
    assert todo_item.id is not None
    assert todo_item.title == todo_data.title
    assert todo_item.description == todo_data.description
    assert todo_item.completed is False
    
async def test_get_all_todos(db_session):
    db = db_session
    todos = await todo_crud.get_all(db)
    assert isinstance(todos, list)
    for todo in todos:
        assert hasattr(todo, "id")
        assert hasattr(todo, "title")
        assert hasattr(todo, "description")
        assert hasattr(todo, "completed")

async def test_update_todo(db_session):
    db = db_session
    todo_data = TodoItemCreate(title="Initial Title", description="Initial Description")
    todo_item = await todo_crud.create(db, todo_data)

    update_data = TodoItemUpdate(title="Updated Title", completed=True)
    updated_todo = await todo_crud.update(db, todo_item.id, update_data)

    assert updated_todo.id == todo_item.id
    assert updated_todo.title == update_data.title
    assert updated_todo.description == todo_data.description
    assert updated_todo.completed is True
    
async def test_delete_todo(db_session):
    db = db_session
    todo_data = TodoItemCreate(title="To be deleted", description="This todo will be deleted.")
    todo_item = await todo_crud.create(db, todo_data)
    deleted_todo = await todo_crud.delete(db, todo_item.id)
    assert deleted_todo.id == todo_item.id
    assert await todo_crud.get(db, todo_item.id) is None

async def test_fail_delete_todo(db_session):
    db = db_session
    deleted_todo = await todo_crud.delete(db, 9999)
    assert deleted_todo is None

async def test_get_todo_not_found(db_session):
    db = db_session
    todo = await todo_crud.get(db, 9999)
    assert todo is None
    
async def test_update_todo_not_found(db_session):
    db = db_session
    update_data = TodoItemCreate(title="Non-existent", description="This todo does not exist.")
    updated_todo = await todo_crud.update(db, 9999, update_data)
    assert updated_todo is None

## auth_crud Tests
async def test_create_user(db_session):
    db = db_session
    user_data : UserCreate = UserCreate(username="testuser1", password="testpassword", is_superuser=False)
    new_user: UserInDB = await auth_crud.create_user(db, user_data)
    assert new_user.username == user_data.username
    assert new_user.is_superuser == user_data.is_superuser
    assert new_user.id is not None

async def test_fail_create_user_duplicate_username(db_session):
    db = db_session
    user_data : UserCreate = UserCreate(username="duplicateuser", password="password1", is_superuser=False)
    await auth_crud.create_user(db, user_data)
    with pytest.raises(Exception):
        await auth_crud.create_user(db, user_data)

async def test_get_user(db_session):
    db = db_session
    user_data : UserCreate = UserCreate(username="anotheruser", password="anotherpassword", is_superuser=True)
    created_user: UserInDB = await auth_crud.create_user(db, user_data)
    fetched_user = await auth_crud.get_user(db, user_data.username)
    assert fetched_user is not None
    assert fetched_user.username == created_user.username
    assert fetched_user.is_superuser == created_user.is_superuser
    assert fetched_user.id == created_user.id

async def test_get_nonexistent_user(db_session):
    db = db_session
    user = await auth_crud.get_user(db, "nonexistentuser")
    assert user is None
