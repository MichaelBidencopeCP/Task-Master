from todo.models import User as UserModel
from todo.api.auth.schemas import UserCreate, UserInDB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_user(db:AsyncSession, username: str) -> UserInDB | None:
    
    db_user = await db.execute(
        select(UserModel).where(UserModel.username == username)
    )
    db_user = db_user.scalars().first()

    if db_user:
        return UserInDB.model_validate(db_user)
    return None

async def create_user(db:AsyncSession, user: UserCreate) -> UserInDB:
    db_user = UserModel(
        username=user.username,
        hashed_password=user.password,
        is_superuser=user.is_superuser
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserInDB.model_validate(db_user)