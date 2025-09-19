from pydantic import BaseModel
from typing import Union
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from todo.models import User as UserModel
from todo.crud import auth_crud
from todo.api.auth.schemas import UserCreate, UserInDB
from todo.settings import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    sub: Union[str, None] = None
    is_superuser: bool = False

async def create_user(db, user: UserCreate) -> UserInDB:
    user.password = hash_password(user.password)
    db_user = await auth_crud.create_user(db, user)
    return UserInDB.model_validate(db_user)



async def authenticate_user(username: str, password: str, db) -> Union[UserInDB, bool]:
    user:UserInDB = await auth_crud.get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return UserInDB.model_validate(user)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user: UserInDB, expires_delta: Union[timedelta, None] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.jwt_exp_minutes)
    to_encode = {"sub": user.username, "is_superuser": user.is_superuser, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_alg)
    return encoded_jwt

def decode_access_token(token: str) -> Union[TokenData, None]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
        username: str = payload.get("sub")
        is_superuser: bool = payload.get("is_superuser", False)
        if username is None:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        token_data = TokenData(sub=username, is_superuser=is_superuser)
        return token_data
    except JWTError:
        return None
    except Exception:
        return None
    

def get_current_user(token: str) -> Union[UserInDB, None]:
    token_data = decode_access_token(token)
    if token_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = UserInDB(username=token_data.sub, hashed_password="", is_superuser=token_data.is_superuser)
    return user


def get_current_superuser(token: str) -> Union[UserInDB, None]:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or not a superuser") 
    token_data = decode_access_token(token)
    if token_data is None or not token_data.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or not a superuser")
    user = UserInDB(username=token_data.sub, hashed_password="", is_superuser=token_data.is_superuser)
    return user