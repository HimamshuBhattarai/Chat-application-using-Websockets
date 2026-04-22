from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Literal["admin", "user"] = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None  
    
    class Config:
        orm_mode = True

class MessageResponse(BaseModel):
    id: int
    content: str
    timestamp: datetime
    user_id: int
    room_id: int

    class Config:
        orm_mode = True
        
class RoomCreate(BaseModel):
    name: str
    description: str