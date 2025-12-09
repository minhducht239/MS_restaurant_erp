from models import menu_item_helper
from database import db
from schemas import MenuItemCreate, MenuItemUpdate
from auth import get_user_from_request
import json
from datetime import datetime
from bson import ObjectId
import math
import os
import base64
from pathlib import Path

# Tạo thư mục lưu ảnh
UPLOAD_DIR = Path("static/menu_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def main(args):
    path = args.get("__ow_path", "")
    method = args.get("__ow_method", "get").lower()
    
    # Health check
    if path == "/health":
        try:
            db.command('ping')
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "healthy", "service": "menu", "database": "connected"}),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"status": "unhealthy", "error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # GET /menu-items - Danh sách menu items
    if path == "/menu-items" and method == "get":
        try:
            page = int(args.get("page", 1))
            limit = int(args.get("limit", 12))
            category = args.get("category")
            available = args.get("available")
            search = args.get("search")
            ordering = args.get("ordering")
            
            query = {}
            
            if category:
                query["category"] = category
            
            if available is not None:
                query["is_available"] = available.lower() == "true"
            
            if search:
                query["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}}
                ]
            
            total_count = db.menu_items.count_documents(query)
            
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
            
            skip = (page - 1) * limit
            items = list(db.menu_items.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit))
            results = [menu_item_helper(item) for item in items]
            
            total_pages = math.ceil(total_count / limit) if limit > 0 else 0
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "count": total_count,
                    "next": f"/menu-items?page={page+1}&limit={limit}" if page < total_pages else None,
                    "previous": f"/menu-items?page={page-1}&limit={limit}" if page > 1 else None,
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

    # POST /menu-items - Tạo menu item mới
    if path == "/menu-items" and method == "post":
        user = get_user_from_request(args)
        if not user:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Unauthorized"}),
                "headers": {"Content-Type": "application/json"}
            }
        
        try:
            data = args.get("body")
            if isinstance(data, str):
                data = json.loads(data)
            
            item = MenuItemCreate(**data)
            new_item = item.dict()
            new_item["price"] = float(new_item["price"])
            new_item["created_at"] = datetime.utcnow()
            new_item["updated_at"] = datetime.utcnow()
            
            result = db.menu_items.insert_one(new_item)
            created = db.menu_items.find_one({"_id": result.inserted_id})
            
            return {
                "statusCode": 201,
                "body": json.dumps(menu_item_helper(created)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # GET /menu-items/<id> - Chi tiết menu item
    if path.startswith("/menu-items/") and method == "get":
        item_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(item_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid item ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            item = db.menu_items.find_one({"_id": ObjectId(item_id)})
            if not item:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Menu item not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            return {
                "statusCode": 200,
                "body": json.dumps(menu_item_helper(item)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # PUT /menu-items/<id> - Cập nhật menu item
    if path.startswith("/menu-items/") and method == "put":
        user = get_user_from_request(args)
        if not user:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Unauthorized"}),
                "headers": {"Content-Type": "application/json"}
            }
        
        item_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(item_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid item ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            existing = db.menu_items.find_one({"_id": ObjectId(item_id)})
            if not existing:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Menu item not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            data = args.get("body")
            if isinstance(data, str):
                data = json.loads(data)
            
            update_data = {k: v for k, v in data.items() if v is not None}
            
            if "price" in update_data:
                update_data["price"] = float(update_data["price"])
            
            update_data["updated_at"] = datetime.utcnow()
            
            db.menu_items.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": update_data}
            )
            
            updated = db.menu_items.find_one({"_id": ObjectId(item_id)})
            return {
                "statusCode": 200,
                "body": json.dumps(menu_item_helper(updated)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # PATCH /menu-items/<id> - Upload ảnh hoặc toggle availability
    if path.startswith("/menu-items/") and method == "patch":
        user = get_user_from_request(args)
        if not user:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Unauthorized"}),
                "headers": {"Content-Type": "application/json"}
            }
        
        item_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(item_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid item ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            existing = db.menu_items.find_one({"_id": ObjectId(item_id)})
            if not existing:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Menu item not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            data = args.get("body")
            if isinstance(data, str):
                data = json.loads(data)
            
            update_data = {"updated_at": datetime.utcnow()}
            
            # Handle image upload (base64)
            if data.get("image"):
                # Delete old image if exists
                if existing.get("image"):
                    old_image = Path(existing["image"])
                    if old_image.exists():
                        old_image.unlink()
                
                # Save new image from base64
                image_data = base64.b64decode(data["image"])
                file_name = f"{item_id}_{datetime.utcnow().timestamp()}.jpg"
                file_path = UPLOAD_DIR / file_name
                
                with open(file_path, "wb") as f:
                    f.write(image_data)
                
                update_data["image"] = str(file_path)
            
            # Handle availability toggle
            if "is_available" in data:
                update_data["is_available"] = data["is_available"]
            
            db.menu_items.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": update_data}
            )
            
            updated = db.menu_items.find_one({"_id": ObjectId(item_id)})
            return {
                "statusCode": 200,
                "body": json.dumps(menu_item_helper(updated)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # DELETE /menu-items/<id> - Xóa menu item
    if path.startswith("/menu-items/") and method == "delete":
        user = get_user_from_request(args)
        if not user:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Unauthorized"}),
                "headers": {"Content-Type": "application/json"}
            }
        
        item_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(item_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid item ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            existing = db.menu_items.find_one({"_id": ObjectId(item_id)})
            if not existing:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Menu item not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            # Delete image file if exists
            if existing.get("image"):
                image_path = Path(existing["image"])
                if image_path.exists():
                    image_path.unlink()
            
            db.menu_items.delete_one({"_id": ObjectId(item_id)})
            
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Menu item deleted successfully"}),
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