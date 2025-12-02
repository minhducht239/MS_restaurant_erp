from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: constr(min_length=6, max_length=72)
    first_name: str = None
    last_name: str = None
    phone: str = None
    date_of_birth: str = None
    address: str = None

class UserLogin(BaseModel):
    username: str
    password: constr(min_length=6, max_length=72)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str