from fastapi import APIRouter, HTTPException, Query
from schemas import StaffCreate, StaffUpdate, StaffOut
from bson import ObjectId
from database import db
from models import staff_helper
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.get("/staff", response_model=List[StaffOut])
async def list_staff(role: Optional[str] = Query(None)):
    query = {}
    if role:
        query["role"] = role
    staffs = await db.staff.find(query).to_list(100)
    return [staff_helper(s) for s in staffs]

@router.post("/staff", response_model=StaffOut)
async def create_staff(item: StaffCreate):
    new_staff = item.dict()
    new_staff["created_at"] = datetime.utcnow()
    new_staff["updated_at"] = datetime.utcnow()
    new_staff["salary"] = float(new_staff["salary"])
    result = await db.staff.insert_one(new_staff)
    staff = await db.staff.find_one({"_id": result.inserted_id})
    return staff_helper(staff)

@router.put("/staff/{staff_id}", response_model=StaffOut)
async def update_staff(staff_id: str, item: StaffUpdate):
    update_data = {k: v for k, v in item.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    if "salary" in update_data:
        update_data["salary"] = float(update_data["salary"])
    result = await db.staff.update_one({"_id": ObjectId(staff_id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Staff not found")
    staff = await db.staff.find_one({"_id": ObjectId(staff_id)})
    return staff_helper(staff)

@router.delete("/staff/{staff_id}")
async def delete_staff(staff_id: str):
    result = await db.staff.delete_one({"_id": ObjectId(staff_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"message": "Staff deleted"}