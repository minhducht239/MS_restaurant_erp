from fastapi import APIRouter, HTTPException, Query, Depends, status
from schemas import StaffCreate, StaffUpdate, StaffOut, StaffFilter
from bson import ObjectId
from database import db
from models import staff_helper
from typing import Optional
from datetime import datetime, date
from auth import get_current_user
import math

router = APIRouter()

@router.get("/staff/", response_model=dict)
async def list_staff(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    ordering: Optional[str] = Query(None),
    hire_date: Optional[date] = Query(None),
    user=Depends(get_current_user)
):
    """Lấy danh sách nhân viên với pagination, filtering, sorting"""
    # Build query
    query = {}
    
    # Filter by role
    if role:
        query["role"] = role
    
    # Filter by hire_date
    if hire_date:
        query["hire_date"] = hire_date.isoformat()
    
    # Search by name or phone
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}}
        ]
    
    # Count total
    total_count = await db.staff.count_documents(query)
    
    # Sorting
    sort_field = "created_at"
    sort_direction = -1
    
    if ordering:
        if ordering.startswith("-"):
            sort_field = ordering[1:]
            sort_direction = -1
        else:
            sort_field = ordering
            sort_direction = 1
    
    # Pagination
    skip = (page - 1) * limit
    
    staffs = await db.staff.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit).to_list(limit)
    
    results = [staff_helper(s) for s in staffs]
    
    # Pagination info
    total_pages = math.ceil(total_count / limit)
    
    return {
        "count": total_count,
        "next": f"/staff/?page={page+1}&limit={limit}" if page < total_pages else None,
        "previous": f"/staff/?page={page-1}&limit={limit}" if page > 1 else None,
        "results": results
    }

@router.get("/staff/{staff_id}/", response_model=StaffOut)
async def get_staff(staff_id: str, user=Depends(get_current_user)):
    """Lấy chi tiết 1 nhân viên"""
    try:
        staff = await db.staff.find_one({"_id": ObjectId(staff_id)})
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        return staff_helper(staff)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/staff/", response_model=StaffOut, status_code=status.HTTP_201_CREATED)
async def create_staff(item: StaffCreate, user=Depends(get_current_user)):
    """Tạo nhân viên mới"""
    try:
        # Check duplicate phone
        existing = await db.staff.find_one({"phone": item.phone})
        if existing:
            raise HTTPException(status_code=400, detail="Phone number already exists")
        
        new_staff = item.dict()
        new_staff["created_at"] = datetime.utcnow()
        new_staff["updated_at"] = datetime.utcnow()
        new_staff["salary"] = float(new_staff["salary"])
        new_staff["hire_date"] = new_staff["hire_date"].isoformat()
        
        result = await db.staff.insert_one(new_staff)
        staff = await db.staff.find_one({"_id": result.inserted_id})
        
        return staff_helper(staff)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/staff/{staff_id}/", response_model=StaffOut)
async def update_staff(staff_id: str, item: StaffUpdate, user=Depends(get_current_user)):
    """Cập nhật nhân viên"""
    try:
        # Check if staff exists
        existing = await db.staff.find_one({"_id": ObjectId(staff_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Staff not found")
        
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        if "salary" in update_data:
            update_data["salary"] = float(update_data["salary"])
        
        if "hire_date" in update_data:
            update_data["hire_date"] = update_data["hire_date"].isoformat()
        
        await db.staff.update_one(
            {"_id": ObjectId(staff_id)}, 
            {"$set": update_data}
        )
        
        staff = await db.staff.find_one({"_id": ObjectId(staff_id)})
        return staff_helper(staff)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/staff/{staff_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(staff_id: str, user=Depends(get_current_user)):
    """Xóa nhân viên"""
    try:
        result = await db.staff.delete_one({"_id": ObjectId(staff_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Staff not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health/")
async def health_check():
    """Health check endpoint"""
    try:
        await db.command('ping')
        return {"status": "healthy", "service": "staff", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")