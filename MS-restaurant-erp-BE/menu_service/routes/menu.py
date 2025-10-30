from fastapi import APIRouter, HTTPException, Query
from schemas import MenuItemCreate, MenuItemUpdate, MenuItemOut
from database import db
from models import menu_item_helper
from typing import List, Optional

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
async def create_menu_item(item: MenuItemCreate):
    new_item = item.dict()
    result = await db.menu_items.insert_one(new_item)
    created = await db.menu_items.find_one({"_id": result.inserted_id})
    return menu_item_helper(created)

@router.put("/menu-items/{item_id}", response_model=MenuItemOut)
async def update_menu_item(item_id: str, item: MenuItemUpdate):
    update_data = {k: v for k, v in item.dict().items() if v is not None}
    result = await db.menu_items.update_one({"_id": ObjectId(item_id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
    updated = await db.menu_items.find_one({"_id": ObjectId(item_id)})
    return menu_item_helper(updated)

@router.delete("/menu-items/{item_id}")
async def delete_menu_item(item_id: str):
    result = await db.menu_items.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"message": "Deleted"}