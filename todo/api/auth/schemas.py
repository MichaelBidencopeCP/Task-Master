from pydantic import BaseModel
from typing import Union
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    is_superuser: bool = False

class UserInDB(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    username: str
    hashed_password: str
    is_superuser: bool = False

