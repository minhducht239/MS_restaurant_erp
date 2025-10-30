from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: constr(min_length=6, max_length=72)  # Giới hạn tối đa 72 ký tự

class UserLogin(BaseModel):
    username: str
    password: constr(min_length=6, max_length=72)

class UserOut(BaseModel):
    username: str
    email: EmailStr