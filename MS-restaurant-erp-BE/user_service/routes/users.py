from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Depends
from schemas import UserOut, UserUpdate, AvatarUploadResponse
from models import user_helper
from database import db
from jose import JWTError, jwt
import os
import shutil
from pathlib import Path
from typing import List

router = APIRouter()

# JWT Configuration (should match auth service)
SECRET_KEY = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"

# File upload configuration
UPLOAD_DIR = Path("uploads/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def get_current_user(request: Request):
    """Dependency to get current user from JWT token"""
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
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.patch("/me", response_model=UserOut)
async def update_my_profile(
    data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    update_data = data.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    # Check email uniqueness if updating email
    if "email" in update_data:
        existing_user = await db.users.find_one({
            "email": update_data["email"],
            "username": {"$ne": current_user["username"]}
        })
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use")
    
    await db.users.update_one(
        {"username": current_user["username"]},
        {"$set": update_data}
    )
    
    updated_user = await db.users.find_one({"username": current_user["username"]})
    return user_helper(updated_user)

@router.post("/upload-avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload user avatar"""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, and GIF are allowed"
        )
    
    # Validate file size (max 5MB)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Seek back to start
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="File too large. Max 5MB allowed")
    
    # Generate unique filename
    file_ext = file.filename.split(".")[-1]
    filename = f"{current_user['username']}_avatar.{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    # Delete old avatar if exists
    old_avatar = current_user.get("avatar")
    if old_avatar and not old_avatar.startswith("http"):
        old_file_path = Path(old_avatar.lstrip("/"))
        if old_file_path.exists():
            old_file_path.unlink()
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    
    # Update user avatar path in database
    avatar_url = f"/uploads/avatars/{filename}"
    await db.users.update_one(
        {"username": current_user["username"]},
        {"$set": {"avatar": avatar_url}}
    )
    
    return AvatarUploadResponse(
        avatar=avatar_url,
        message="Avatar uploaded successfully"
    )

@router.delete("/avatar")
async def delete_avatar(current_user: dict = Depends(get_current_user)):
    """Delete user avatar"""
    if not current_user.get("avatar"):
        raise HTTPException(status_code=404, detail="No avatar to delete")
    
    # Delete file if exists
    avatar_path = current_user["avatar"]
    if avatar_path and not avatar_path.startswith("http"):
        file_path = Path(avatar_path.lstrip("/"))
        if file_path.exists():
            file_path.unlink()
    
    # Remove avatar from database
    await db.users.update_one(
        {"username": current_user["username"]},
        {"$set": {"avatar": None}}
    )
    
    return {"message": "Avatar deleted successfully"}

@router.get("/list", response_model=List[UserOut])
async def list_users(
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get list of users (admin only)"""
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = await db.users.find().skip(skip).limit(limit).to_list(length=limit)
    return [user_helper(user) for user in users]

@router.get("/{username}", response_model=UserOut)
async def get_user_by_username(
    username: str,
    current_user: dict = Depends(get_current_user)
):
    """Get user by username (admin only or own profile)"""
    # Allow users to view their own profile or admin to view any profile
    if current_user["username"] != username and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_helper(user)