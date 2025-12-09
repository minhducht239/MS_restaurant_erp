from models import bill_helper
from database import db
from schemas import BillCreate, BillOut
import json
from datetime import datetime, date
from bson import ObjectId

def main(args):
    path = args.get("__ow_path", "")
    method = args.get("__ow_method", "get").lower()

    # Health check (luôn để đầu)
    if path == "/health":
        try:
            db.command('ping')
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "healthy", "service": "billing", "database": "connected"}),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"status": "unhealthy", "error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Thống kê bills (phải trước /bills/<id>)
    if path == "/bills/stats" and method == "get":
        try:
            total = db.bills.count_documents({})
            today = date.today().isoformat()
            today_bills = db.bills.count_documents({"date": today})
            pipeline = [
                {"$match": {"date": today}},
                {"$group": {"_id": None, "total": {"$sum": "$total"}}}
            ]
            today_revenue_result = list(db.bills.aggregate(pipeline))
            today_revenue = today_revenue_result[0]["total"] if today_revenue_result else 0
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "total": total,
                    "today_bills": today_bills,
                    "today_revenue": float(today_revenue)
                }),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Doanh thu theo tháng (phải trước /bills/<id>)
    if path == "/bills/monthly-revenue" and method == "get":
        try:
            year = int(args.get("year", datetime.now().year))
            pipeline = [
                {
                    "$match": {
                        "date": {
                            "$gte": f"{year}-01-01",
                            "$lte": f"{year}-12-31"
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {"$substr": ["$date", 5, 2]},
                        "revenue": {"$sum": "$total"}
                    }
                },
                {
                    "$sort": {"_id": 1}
                }
            ]
            results = list(db.bills.aggregate(pipeline))
            monthly_revenue = [0] * 12
            for result in results:
                month_idx = int(result["_id"]) - 1
                monthly_revenue[month_idx] = float(result["revenue"])
            return {
                "statusCode": 200,
                "body": json.dumps(monthly_revenue),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Lấy danh sách hóa đơn
    if path == "/bills" and method == "get":
        try:
            from_date = args.get("from_date")
            to_date = args.get("to_date")
            search = args.get("search")
            sort = args.get("sort", "date_desc")
            skip = int(args.get("skip", 0))
            limit = int(args.get("limit", 100))

            query = {}
            if from_date or to_date:
                query["date"] = {}
                if from_date:
                    query["date"]["$gte"] = from_date
                if to_date:
                    query["date"]["$lte"] = to_date
            if search:
                query["$or"] = [
                    {"customer": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}}
                ]
                if ObjectId.is_valid(search):
                    query["$or"].append({"_id": ObjectId(search)})

            sort_field = "created_at"
            sort_order = -1
            if sort == "date_desc":
                sort_field = "date"
                sort_order = -1
            elif sort == "date_asc":
                sort_field = "date"
                sort_order = 1
            elif sort == "total_desc":
                sort_field = "total"
                sort_order = -1
            elif sort == "total_asc":
                sort_field = "total"
                sort_order = 1

            bills = list(db.bills.find(query).sort(sort_field, sort_order).skip(skip).limit(limit))
            results = [bill_helper(b) for b in bills]
            return {
                "statusCode": 200,
                "body": json.dumps(results),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Tạo hóa đơn mới
    if path == "/bills" and method == "post":
        try:
            data = args.get("body")
            if isinstance(data, str):
                data = json.loads(data)
            bill_in = BillCreate(**data)
            result = db.bills.insert_one(bill_in.dict())
            bill = db.bills.find_one({"_id": result.inserted_id})
            return {
                "statusCode": 201,
                "body": json.dumps(bill_helper(bill)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Lấy chi tiết hóa đơn (sau stats và monthly-revenue)
    if path.startswith("/bills/") and path not in ["/bills/stats", "/bills/monthly-revenue"] and method == "get":
        bill_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(bill_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid bill ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            bill = db.bills.find_one({"_id": ObjectId(bill_id)})
            if not bill:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Bill not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            return {
                "statusCode": 200,
                "body": json.dumps(bill_helper(bill)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Cập nhật hóa đơn
    if path.startswith("/bills/") and path not in ["/bills/stats", "/bills/monthly-revenue"] and method == "put":
        bill_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(bill_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid bill ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            existing_bill = db.bills.find_one({"_id": ObjectId(bill_id)})
            if not existing_bill:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Bill not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            data = args.get("body")
            if isinstance(data, str):
                data = json.loads(data)
            update_data = {
                "customer": data.get("customer", existing_bill.get("customer")),
                "phone": data.get("phone", existing_bill.get("phone")),
                "updated_at": datetime.utcnow()
            }
            db.bills.update_one({"_id": ObjectId(bill_id)}, {"$set": update_data})
            updated_bill = db.bills.find_one({"_id": ObjectId(bill_id)})
            return {
                "statusCode": 200,
                "body": json.dumps(bill_helper(updated_bill)),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Xóa hóa đơn
    if path.startswith("/bills/") and path not in ["/bills/stats", "/bills/monthly-revenue"] and method == "delete":
        bill_id = path.split("/")[-1]
        try:
            if not ObjectId.is_valid(bill_id):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid bill ID"}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            bill = db.bills.find_one({"_id": ObjectId(bill_id)})
            if not bill:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Bill not found"}),
                    "headers": {"Content-Type": "application/json"}
                }
            db.bills.delete_one({"_id": ObjectId(bill_id)})
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Bill deleted successfully"}),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # Mặc định: 404
    return {
        "statusCode": 404,
        "body": json.dumps({"error": "Not found"}),
        "headers": {"Content-Type": "application/json"}
    }