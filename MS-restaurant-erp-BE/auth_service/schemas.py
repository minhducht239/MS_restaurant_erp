from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: constr(min_length=6, max_length=72)

class UserLogin(BaseModel):
    username: str
    password: constr(min_length=6, max_length=72)

class UserOut(BaseModel):
    id: Optional[str]
    username: str
    email: EmailStr
    role: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None