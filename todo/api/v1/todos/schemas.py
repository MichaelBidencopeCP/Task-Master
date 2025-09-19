from pydantic import BaseModel, Field
from typing import Union

class TodoItemCreate(BaseModel):
    title: str = Field(..., description="The task description of the todo item")
    description: str = Field("", description="Additional details about the todo item")

class TodoItemUpdate(BaseModel):
    title: Union[str, None] = Field(None, description="The task description of the todo item")
    description: Union[str, None] = Field(None, description="Additional details about the todo item")
    completed: Union[bool, None] = Field(None, description="Completion status of the todo item")

class TodoItemResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    title: str
    description: str
    completed: bool = Field(False, description="Completion status of the todo item")
    

# Alias
class TodoItem(TodoItemResponse):
    pass