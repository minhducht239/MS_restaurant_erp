from fastapi import APIRouter, HTTPException, Body
from schemas import UserCreate, UserLogin, TokenResponse
from auth import hash_password, verify_password, create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM
from database import db
from jose import JWTError, jwt

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate):
    """Register new user"""
    # Check if username exists
    existing = await db.users.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user_dict = user.dict()
    user_dict["password"] = hash_password(user_dict["password"])
    user_dict["role"] = "staff"  # default role
    
    result = await db.users.insert_one(user_dict)
    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}

@router.post("/login")
async def login(user: UserLogin):
    """Login user"""
    db_user = await db.users.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/token/refresh")
async def refresh_token(refresh: str = Body(..., embed=True)):
    """Refresh access token"""
    try:
        payload = jwt.decode(refresh, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        access_token = create_access_token(data={"sub": username})
        return {"access": access_token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.put("/change-password")
async def change_password(
    current_password: str = Body(...),
    new_password: str = Body(...),
    username: str = Body(...)
):
    """Change user password"""
    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(current_password, user["password"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    hashed_password = hash_password(new_password)
    await db.users.update_one(
        {"username": username},
        {"$set": {"password": hashed_password}}
    )
    
    return {"message": "Password changed successfully"}