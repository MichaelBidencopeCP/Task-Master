from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from todo.auth import authenticate_user, create_access_token, TokenData, create_user
from todo.database import get_db
from todo.api.auth.schemas import UserCreate, UserInDB
from todo.models import User as UserModel
from todo.crud import auth_crud



router = APIRouter()

@router.post("/auth/login")
async def login(form_data: dict, db = Depends(get_db)):
    username = form_data.get("username")
    password = form_data.get("password")
    user = await authenticate_user(username, password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/signup")
async def signup(user_data: UserCreate, db:AsyncSession = Depends(get_db)):
    exiting_user = await auth_crud.get_user(db, user_data.username)
    if exiting_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    new_user: UserInDB = await create_user(db, user_data)

    return {"username": new_user.username, "is_superuser": new_user.is_superuser}
