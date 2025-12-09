from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserOut(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    role: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None

class AvatarUploadResponse(BaseModel):
    avatar: str
    message: str