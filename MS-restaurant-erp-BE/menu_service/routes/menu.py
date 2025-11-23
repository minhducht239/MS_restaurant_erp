from fastapi import APIRouter, HTTPException, Query
from schemas import MenuItemCreate, MenuItemUpdate, MenuItemOut
from bson import ObjectId
from database import db
from models import menu_item_helper
from typing import List, Optional
from auth import get_current_user
from fastapi import Depends, File, UploadFile
from datetime import datetime

router = APIRouter()

@router.get("/menu-items", response_model=List[MenuItemOut])
async def list_menu_items(
    category: Optional[str] = Query(None),
    available: Optional[bool] = Query(None)
):
    query = {}
    if category:
        query["category"] = category
    if available is not None:
        query["is_available"] = available
    items = await db.menu_items.find(query).to_list(100)
    return [menu_item_helper(item) for item in items]

@router.post("/menu-items", response_model=MenuItemOut)
async def create_menu_item(item: MenuItemCreate, user=Depends(get_current_user)):
    new_item = item.dict()
    new_item["price"] = float(new_item["price"])
    new_item["created_at"] = datetime.utcnow()
    new_item["updated_at"] = datetime.utcnow()
    result = await db.menu_items.insert_one(new_item)
    created = await db.menu_items.find_one({"_id": result.inserted_id})
    return menu_item_helper(created)

@router.put("/menu-items/{item_id}", response_model=MenuItemOut)
async def update_menu_item(item_id: str, item: MenuItemUpdate, user=Depends(get_current_user)):
    update_data = {k: v for k, v in item.dict().items() if v is not None}
    if "price" in update_data:
        update_data["price"] = float(update_data["price"])
    update_data["updated_at"] = datetime.utcnow()
    result = await db.menu_items.update_one({"_id": ObjectId(item_id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
    updated = await db.menu_items.find_one({"_id": ObjectId(item_id)})
    return menu_item_helper(updated)

@router.delete("/menu-items/{item_id}")
async def delete_menu_item(item_id: str, user=Depends(get_current_user)):
    result = await db.menu_items.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"message": "Deleted"}


@router.patch("/menu-items/{item_id}")
async def upload_menu_image(item_id: str, image: UploadFile = File(...), user=Depends(get_current_user)):
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file ảnh JPG/PNG")
    # Lưu file vào thư mục static hoặc cloud, ví dụ:
    file_location = f"static/menu_images/{item_id}_{image.filename}"
    with open(file_location, "wb") as f:
        f.write(await image.read())
    # Cập nhật đường dẫn ảnh vào DB
    await db.menu_items.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": {"image": file_location, "updated_at": datetime.utcnow()}}
    )
    updated = await db.menu_items.find_one({"_id": ObjectId(item_id)})
    return menu_item_helper(updated)