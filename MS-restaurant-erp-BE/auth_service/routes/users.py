from fastapi import APIRouter, HTTPException, Depends, Request, Body
from schemas import UserCreate, UserLogin, UserOut
from auth import hash_password, verify_password, create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM
from database import db
from models import user_helper
from jose import JWTError, jwt
from pydantic import BaseModel

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate):
    if len(user.password) > 72:
        raise HTTPException(status_code=400, detail="Password must be <= 72 characters")
    existing = await db.users.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = hash_password(user.password)
    new_user = {"username": user.username, "email": user.email, "hashed_password": hashed_pw}
    result = await db.users.insert_one(new_user)
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return {"success": True, "user": user_helper(created_user)}

@router.post("/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"username": credentials.username})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": credentials.username})
    refresh_token = create_refresh_token({"sub": credentials.username})
    return {
        "success": True,
        "access": access_token,
        "refresh": refresh_token,
        "user": user_helper(user)
    }

class RefreshTokenRequest(BaseModel):
    refresh: str

@router.post("/token/refresh")
async def refresh_token(data: RefreshTokenRequest):
    try:
        payload = jwt.decode(data.refresh, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        access_token = create_access_token({"sub": username})
        return {"access": access_token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.get("/me")
async def get_me(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        user = await db.users.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user_helper(user)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.put("/change-password")
async def change_password(request: Request, data: ChangePasswordRequest = Body(...)):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        user = await db.users.find_one({"username": username})
        if not user or not verify_password(data.current_password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        if len(data.new_password) < 6 or len(data.new_password) > 72:
            raise HTTPException(status_code=400, detail="New password must be 6-72 characters")
        new_hashed = hash_password(data.new_password)
        await db.users.update_one({"username": username}, {"$set": {"hashed_password": new_hashed}})
        return {"success": True}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/user/{username}")
async def get_user_info(username: str):
    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_helper(user)