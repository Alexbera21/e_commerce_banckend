from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserInDB(BaseModel):
    id: Optional[str]
    name: str
    email: EmailStr
    hashed_password: str
    role: str = "customer"
    created_at: datetime