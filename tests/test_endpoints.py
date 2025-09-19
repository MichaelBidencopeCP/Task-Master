import pytest

## todo_endpoints Tests
async def test_create_endpoint(client):
    todo_data = {"title": "Test Todo", "description": "This is a test todo item."}
    resp = await client.post("/api/v1/todos", json=todo_data)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert data["title"] == todo_data["title"]
    assert data["description"] == todo_data["description"]
    assert data["completed"] is False

async def test_get_all_endpoint(client):
    # First, create a couple of todo items
    todo_data1 = {"title": "Test Todo 1", "description": "This is the first test todo item."}
    todo_data2 = {"title": "Test Todo 2", "description": "This is the second test todo item."}
    await client.post("/api/v1/todos", json=todo_data1)
    await client.post("/api/v1/todos", json=todo_data2)
    resp = await client.get("/api/v1/todos")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    for item in data:
        assert "id" in item
        assert "title" in item
        assert "description" in item
        assert "completed" in item
        
async def test_get_single_endpoint(client):
    # First, create a todo item
    todo_data = {"title": "Single Todo", "description": "This is a single test todo item."}
    create_resp = await client.post("/api/v1/todos", json=todo_data)
    created_item = create_resp.json()
    todo_id = created_item["id"]
    resp = await client.get(f"/api/v1/todos/{todo_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    item = data[0]
    assert item["id"] == todo_id
    assert item["title"] == todo_data["title"]
    assert item["description"] == todo_data["description"]
    assert item["completed"] is False

async def test_update_endpoint(client):
    # First, create a todo item
    todo_data = {"title": "Update Todo", "description": "This todo will be updated."}
    create_resp = await client.post("/api/v1/todos", json=todo_data)
    created_item = create_resp.json()
    todo_id = created_item["id"]
    update_data = {"title": "Updated Title", "completed": True}
    resp = await client.put(f"/api/v1/todos/{todo_id}", json=update_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == todo_id
    assert data["title"] == update_data["title"]
    assert data["description"] == todo_data["description"]
    assert data["completed"] is True

async def test_delete_endpoint(client):
    # First, create a todo item
    todo_data = {"title": "Delete Todo", "description": "This todo will be deleted.", "completed": False}
    create_resp = await client.post("/api/v1/todos", json=todo_data)
    created_item = create_resp.json()
    todo_id = created_item["id"]
    resp = await client.delete(f"/api/v1/todos/{todo_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == todo_id
    # Verify the item is actually deleted
    get_resp = await client.get(f"/api/v1/todos/{todo_id}")
    assert get_resp.status_code == 404

##Auth Endpoints
async def test_signup_endpoint(client):
    user_data = {"username": "testuser", "password": "testpassword"}
    resp = await client.post("/api/auth/signup", json=user_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == user_data["username"]
    assert "is_superuser" in data
    assert data["is_superuser"] is False

async def test_login_endpoint(client):
    # First, create a user
    user_data = {"username": "loginuser", "password": "loginpassword"}
    await client.post("/api/auth/signup", json=user_data)
    login_data = {"username": "loginuser", "password": "loginpassword"}
    resp = await client.post("/api/auth/login", json=login_data)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"



async def test_login_invalid_credentials(client):
    login_data = {"username": "nonexistentuser", "password": "wrongpassword"}
    resp = await client.post("/api/auth/login", json=login_data)
    assert resp.status_code == 401
    data = resp.json()
    assert data["detail"] == "Incorrect username or password"

async def test_signup_existing_username(client):
    user_data = {"username": "existinguser", "password": "somepassword"}
    await client.post("/api/auth/signup", json=user_data)
    resp = await client.post("/api/auth/signup", json=user_data)
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"] == "Username already registered"

