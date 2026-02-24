from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    email: str
    name: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    remind_at: Optional[datetime] = None
    action_url: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    remind_at: Optional[datetime] = None
    is_done: Optional[bool] = None
    action_url: Optional[str] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    remind_at: Optional[datetime]
    is_done: bool
    swiped_count: int
    action_url: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    user_id: int
    class Config:
        from_attributes = True
