from fastapi import APIRouter, HTTPException, Depends
from schemas import UserCreate, UserLogin, UserOut
from auth import hash_password, verify_password, create_access_token
from database import db
from models import user_helper

router = APIRouter()

@router.post("/register", response_model=UserOut)
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
    return user_helper(created_user)

@router.post("/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"username": credentials.username})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": credentials.username})
    return {"access_token": token, "token_type": "bearer"}
