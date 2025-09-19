import pytest
from todo.auth import get_current_superuser, get_current_user
from fastapi import HTTPException, status

## Dependency Tests

#Auth Dependencies
async def test_get_current_active_user_no_token():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=None)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"

async def test_get_current_superuser_no_token():
    with pytest.raises(HTTPException) as exc_info:
        get_current_superuser(token=None)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token or not a superuser"

