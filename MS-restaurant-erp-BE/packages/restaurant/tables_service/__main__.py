from models import staff_helper
from database import db
from schemas import StaffCreate, StaffUpdate
from auth import get_user_from_request
import json
from datetime import datetime, date
from bson import ObjectId
import math

def main(args):
    path = args.get("__ow_path", "")
    method = args.get("__ow_method", "get").lower()
    
    # Health check
    if path == "/health":
        try:
            db.command('ping')
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "healthy", "service": "staff", "database": "connected"}),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"status": "unhealthy", "error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Xác thực user (trừ health check)
    user = get_user_from_request(args)
    if not user:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Unauthorized"}),
            "headers": {"Content-Type": "application/json"}
        }

    # GET /staff - Danh sách nhân viên
    if path == "/staff" and method == "get":
        try:
            page = int(args.get("page", 1))
            limit = int(args.get("limit", 10))
            role = args.get("role")
            search = args.get("search")
            ordering = args.get("ordering")
            hire_date = args.get("hire_date")
            
            query = {}
            
            # Filter by role
            if role:
                query["role"] = role
            
            # Filter by hire_date
            if hire_date:
                query["hire_date"] = hire_date
            
            # Search by name or phone
            if search:
                query["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}}
                ]
            
            # Count total
            total_count = db.staff.count_documents(query)
            
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
            
            staffs = list(db.staff.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit))
            results = [staff_helper(s) for s in staffs]
            
            # Pagination info
            total_pages = math.ceil(total_count / limit) if limit > 0 else 0
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "count": total_count,
                    "next": f"/staff?page={page+1}&limit={limit}" if page < total_pages else None,
                    "previous": f"/staff?page={page-1}&limit={limit}" if page > 1 else None,
                    "results": results
                }),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # POST /staff - Tạo nhân viên mới
    if path == "/staff" and method == "post":
        try:
            data = args.get("body")
            if isinstance(data, str):
                data = json.loads(data)
            
            # Check duplicate phone
            existing = db.staff.find_one({"phone": data.get("phone")})
            if existing:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Phone number already exists"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            item = StaffCreate(**data)
            new_staff = item.dict()
            new_staff["created_at"] = datetime.utcnow()
            new_staff["updated_at"] = datetime.utcnow()
            new_staff["salary"] = float(new_staff["salary"])
            new_staff["hire_date"] = new_staff["hire_date"].isoformat()
            
            result = db.staff.insert_one(new_staff)
            staff = db.staff.find_one({"_id": result.inserted_id})
            
            return {
                "statusCode": 201,
                "body": json.dumps(staff_helper(staff)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # GET /staff/<id> - Chi tiết nhân viên
    if path.startswith("/staff/") and method == "get":
        staff_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(staff_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid staff ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            staff = db.staff.find_one({"_id": ObjectId(staff_id)})
            if not staff:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Staff not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            return {
                "statusCode": 200,
                "body": json.dumps(staff_helper(staff)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # PUT /staff/<id> - Cập nhật nhân viên
    if path.startswith("/staff/") and method == "put":
        staff_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(staff_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid staff ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            existing = db.staff.find_one({"_id": ObjectId(staff_id)})
            if not existing:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Staff not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            data = args.get("body")
            if isinstance(data, str):
                data = json.loads(data)
            
            # Check duplicate phone if updating
            if data.get("phone"):
                phone_exists = db.staff.find_one({
                    "phone": data["phone"],
                    "_id": {"$ne": ObjectId(staff_id)}
                })
                if phone_exists:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "Phone number already exists"}),
                        "headers": {"Content-Type": "application/json"}
                    }
            
            update_data = {k: v for k, v in data.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            
            if "salary" in update_data:
                update_data["salary"] = float(update_data["salary"])
            
            if "hire_date" in update_data:
                if isinstance(update_data["hire_date"], str):
                    update_data["hire_date"] = update_data["hire_date"]
                else:
                    update_data["hire_date"] = update_data["hire_date"].isoformat()
            
            db.staff.update_one(
                {"_id": ObjectId(staff_id)},
                {"$set": update_data}
            )
            
            staff = db.staff.find_one({"_id": ObjectId(staff_id)})
            return {
                "statusCode": 200,
                "body": json.dumps(staff_helper(staff)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # DELETE /staff/<id> - Xóa nhân viên
    if path.startswith("/staff/") and method == "delete":
        staff_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(staff_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid staff ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            result = db.staff.delete_one({"_id": ObjectId(staff_id)})
            if result.deleted_count == 0:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Staff not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Staff deleted successfully"}),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Default: 404
    return {
        "statusCode": 404,
        "body": json.dumps({"error": "Not found"}),
        "headers": {"Content-Type": "application/json"}
    }