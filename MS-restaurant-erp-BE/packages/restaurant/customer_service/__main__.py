from models import customer_helper, calculate_loyalty_points
from database import db
from schemas import CustomerCreate, CustomerUpdate
from auth import get_user_from_request
import json
from datetime import datetime, date
from bson import ObjectId
import math

def main(args):
    path = args.get("__ow_path", "")
    method = args.get("__ow_method", "get").lower()
    
    # Xác thực user (trừ endpoint health)
    user = None
    if path != "/health":
        user = get_user_from_request(args)
        if not user:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Unauthorized"}),
                "headers": {"Content-Type": "application/json"}
            }

    # GET /customers - Danh sách khách hàng
    if path == "/customers" and method == "get":
        try:
            page = int(args.get("page", 1))
            limit = int(args.get("limit", 10))
            search = args.get("search")
            loyalty_min = args.get("loyalty_points_min")
            loyalty_max = args.get("loyalty_points_max")
            spent_min = args.get("total_spent_min")
            spent_max = args.get("total_spent_max")
            ordering = args.get("ordering", "-loyalty_points")
            
            skip = (page - 1) * limit
            query = {}
            
            # Search filter
            if search:
                query["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}}
                ]
            
            # Loyalty points filter
            if loyalty_min or loyalty_max:
                query["loyalty_points"] = {}
                if loyalty_min:
                    query["loyalty_points"]["$gte"] = int(loyalty_min)
                if loyalty_max:
                    query["loyalty_points"]["$lte"] = int(loyalty_max)
            
            # Total spent filter
            if spent_min or spent_max:
                query["total_spent"] = {}
                if spent_min:
                    query["total_spent"]["$gte"] = float(spent_min)
                if spent_max:
                    query["total_spent"]["$lte"] = float(spent_max)
            
            # Sorting
            sort_field = ordering.lstrip("-")
            sort_direction = -1 if ordering.startswith("-") else 1
            
            total_count = db.customers.count_documents(query)
            customers = list(db.customers.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit))
            results = [customer_helper(c) for c in customers]
            
            total_pages = math.ceil(total_count / limit) if limit > 0 else 0
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "count": total_count,
                    "next": f"/customers?page={page+1}&limit={limit}" if page < total_pages else None,
                    "previous": f"/customers?page={page-1}&limit={limit}" if page > 1 else None,
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

    # POST /customers - Tạo khách hàng mới
    if path == "/customers" and method == "post":
        try:
            data = args.get("body")
            if isinstance(data, str):
                data = json.loads(data)
            
            # Check duplicate phone
            existing = db.customers.find_one({"phone": data.get("phone")})
            if existing:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Phone number already exists"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            # Check duplicate email if provided
            if data.get("email"):
                existing_email = db.customers.find_one({"email": data["email"]})
                if existing_email:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "Email already exists"}),
                        "headers": {"Content-Type": "application/json"}
                    }
            
            customer_in = CustomerCreate(**data)
            customer_data = customer_in.dict()
            customer_data["created_at"] = datetime.utcnow()
            customer_data["updated_at"] = datetime.utcnow()
            
            result = db.customers.insert_one(customer_data)
            customer = db.customers.find_one({"_id": result.inserted_id})
            
            return {
                "statusCode": 201,
                "body": json.dumps(customer_helper(customer)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # GET /customers/analytics - Thống kê (phải trước GET /customers/<id>)
    if path == "/customers/analytics" and method == "get":
        try:
            pipeline = [
                {
                    "$bucket": {
                        "groupBy": "$loyalty_points",
                        "boundaries": [0, 50, 100, 200, float('inf')],
                        "default": "Other",
                        "output": {
                            "count": {"$sum": 1},
                            "total_spent": {"$sum": "$total_spent"}
                        }
                    }
                }
            ]
            
            segments = list(db.customers.aggregate(pipeline))
            total_customers = db.customers.count_documents({})
            
            # Thống kê thêm
            avg_loyalty = list(db.customers.aggregate([
                {"$group": {"_id": None, "avg": {"$avg": "$loyalty_points"}}}
            ]))
            avg_spent = list(db.customers.aggregate([
                {"$group": {"_id": None, "avg": {"$avg": "$total_spent"}}}
            ]))
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "segments": segments,
                    "total_customers": total_customers,
                    "avg_loyalty_points": avg_loyalty[0]["avg"] if avg_loyalty else 0,
                    "avg_total_spent": avg_spent[0]["avg"] if avg_spent else 0
                }),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # GET /customers/<id> - Chi tiết khách hàng
    if path.startswith("/customers/") and path != "/customers/analytics" and method == "get":
        customer_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(customer_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid customer ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            customer = db.customers.find_one({"_id": ObjectId(customer_id)})
            if not customer:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Customer not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            return {
                "statusCode": 200,
                "body": json.dumps(customer_helper(customer)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # PUT /customers/<id> - Cập nhật khách hàng
    if path.startswith("/customers/") and path != "/customers/analytics" and method == "put":
        customer_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(customer_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid customer ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            data = args.get("body")
            if isinstance(data, str):
                data = json.loads(data)
            
            # Check duplicate phone if updating
            if data.get("phone"):
                existing = db.customers.find_one({
                    "phone": data["phone"],
                    "_id": {"$ne": ObjectId(customer_id)}
                })
                if existing:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "Phone number already exists"}),
                        "headers": {"Content-Type": "application/json"}
                    }
            
            # Check duplicate email if updating
            if data.get("email"):
                existing_email = db.customers.find_one({
                    "email": data["email"],
                    "_id": {"$ne": ObjectId(customer_id)}
                })
                if existing_email:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "Email already exists"}),
                        "headers": {"Content-Type": "application/json"}
                    }
            
            update_data = {k: v for k, v in data.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            
            result = db.customers.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Customer not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            customer = db.customers.find_one({"_id": ObjectId(customer_id)})
            return {
                "statusCode": 200,
                "body": json.dumps(customer_helper(customer)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # DELETE /customers/<id> - Xóa khách hàng
    if path.startswith("/customers/") and path != "/customers/analytics" and method == "delete":
        customer_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(customer_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid customer ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            result = db.customers.delete_one({"_id": ObjectId(customer_id)})
            if result.deleted_count == 0:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Customer not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Customer deleted successfully"}),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Health check
    if path == "/health":
        try:
            db.command('ping')
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "healthy", "service": "customer", "database": "connected"}),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"status": "unhealthy", "error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Default: 404
    return {
        "statusCode": 404,
        "body": json.dumps({"error": "Not found"}),
        "headers": {"Content-Type": "application/json"}
    }