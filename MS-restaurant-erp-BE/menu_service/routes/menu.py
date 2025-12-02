from fastapi import APIRouter, HTTPException, Query, Depends, File, UploadFile, status
from schemas import MenuItemCreate, MenuItemUpdate, MenuItemOut
from bson import ObjectId
from database import db
from models import menu_item_helper
from typing import List, Optional
from auth import get_current_user
from datetime import datetime
import os
import shutil
from pathlib import Path
import math

router = APIRouter()

# Tạo thư mục lưu ảnh nếu chưa có
UPLOAD_DIR = Path("static/menu_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/menu-items/", response_model=dict)
async def list_menu_items(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    category: Optional[str] = Query(None),
    available: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    ordering: Optional[str] = Query(None)
):
    """Lấy danh sách menu items với pagination, filtering, sorting"""
    # Build query
    query = {}
    
    if category:
        query["category"] = category
    
    if available is not None:
        query["is_available"] = available
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Count total
    total_count = await db.menu_items.count_documents(query)
    
    # Sorting
    sort_field = "name"
    sort_direction = 1
    
    if ordering:
        if ordering.startswith("-"):
            sort_field = ordering[1:]
            sort_direction = -1
        else:
            sort_field = ordering
            sort_direction = 1
    
    # Pagination
    skip = (page - 1) * limit
    
    items = await db.menu_items.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit).to_list(limit)
    
    results = [menu_item_helper(item) for item in items]
    
    # Pagination info
    total_pages = math.ceil(total_count / limit)
    
    return {
        "count": total_count,
        "next": f"/menu-items/?page={page+1}&limit={limit}" if page < total_pages else None,
        "previous": f"/menu-items/?page={page-1}&limit={limit}" if page > 1 else None,
        "results": results
    }

@router.get("/menu-items/{item_id}/", response_model=MenuItemOut)
async def get_menu_item(item_id: str):
    """Lấy chi tiết 1 menu item"""
    try:
        item = await db.menu_items.find_one({"_id": ObjectId(item_id)})
        if not item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return menu_item_helper(item)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/menu-items/", response_model=MenuItemOut, status_code=status.HTTP_201_CREATED)
async def create_menu_item(item: MenuItemCreate, user=Depends(get_current_user)):
    """Tạo menu item mới"""
    try:
        new_item = item.dict()
        new_item["price"] = float(new_item["price"])
        new_item["created_at"] = datetime.utcnow()
        new_item["updated_at"] = datetime.utcnow()
        
        result = await db.menu_items.insert_one(new_item)
        created = await db.menu_items.find_one({"_id": result.inserted_id})
        
        return menu_item_helper(created)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/menu-items/{item_id}/", response_model=MenuItemOut)
async def update_menu_item(item_id: str, item: MenuItemUpdate, user=Depends(get_current_user)):
    """Cập nhật menu item"""
    try:
        # Check if item exists
        existing = await db.menu_items.find_one({"_id": ObjectId(item_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Menu item not found")
        
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        
        if "price" in update_data:
            update_data["price"] = float(update_data["price"])
        
        update_data["updated_at"] = datetime.utcnow()
        
        await db.menu_items.update_one(
            {"_id": ObjectId(item_id)}, 
            {"$set": update_data}
        )
        
        updated = await db.menu_items.find_one({"_id": ObjectId(item_id)})
        return menu_item_helper(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/menu-items/{item_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(item_id: str, user=Depends(get_current_user)):
    """Xóa menu item"""
    try:
        # Check if item exists
        existing = await db.menu_items.find_one({"_id": ObjectId(item_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Menu item not found")
        
        # Delete image file if exists
        if existing.get("image"):
            image_path = Path(existing["image"])
            if image_path.exists():
                image_path.unlink()
        
        result = await db.menu_items.delete_one({"_id": ObjectId(item_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Menu item not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/menu-items/{item_id}/", response_model=MenuItemOut)
async def upload_or_update_menu_item(
    item_id: str,
    image: Optional[UploadFile] = File(None),
    is_available: Optional[bool] = None,
    user=Depends(get_current_user)
):
    """Upload ảnh hoặc toggle availability cho menu item"""
    try:
        # Check if item exists
        existing = await db.menu_items.find_one({"_id": ObjectId(item_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Menu item not found")
        
        update_data = {"updated_at": datetime.utcnow()}
        
        # Handle image upload
        if image:
            if image.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
                raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file ảnh JPG/PNG")
            
            # Delete old image if exists
            if existing.get("image"):
                old_image = Path(existing["image"])
                if old_image.exists():
                    old_image.unlink()
            
            # Save new image
            file_extension = os.path.splitext(image.filename)[1]
            file_name = f"{item_id}_{datetime.utcnow().timestamp()}{file_extension}"
            file_path = UPLOAD_DIR / file_name
            
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            update_data["image"] = str(file_path)
        
        # Handle availability toggle
        if is_available is not None:
            update_data["is_available"] = is_available
        
        await db.menu_items.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": update_data}
        )
        
        updated = await db.menu_items.find_one({"_id": ObjectId(item_id)})
        return menu_item_helper(updated)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health/")
async def health_check():
    """Health check endpoint"""
    try:
        await db.command('ping')
        return {"status": "healthy", "service": "menu", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")