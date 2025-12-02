from flask import request, jsonify
from flask_restful import Resource
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, date
import os
import requests
from auth import token_required

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "billing_service")
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL", "http://customer-service:8000")

def calculate_loyalty_points(amount):
    """Tính điểm tích lũy: 100.000 VNĐ = 1 điểm"""
    return int(amount / 100000)

def update_customer_loyalty(phone):
    """Cập nhật loyalty points cho customer"""
    if not phone:
        return
    
    try:
        # Tính tổng từ tất cả bills của phone này
        bills = list(db.bills.find({"phone": phone}))
        
        total_spent = sum(float(bill.get("total", 0)) for bill in bills)
        loyalty_points = sum(calculate_loyalty_points(bill.get("total", 0)) for bill in bills)
        visit_count = len(bills)
        
        # Gọi customer service để update
        requests.post(
            f"{CUSTOMER_SERVICE_URL}/customers/update-loyalty",
            json={
                "phone": phone,
                "total_spent": total_spent,
                "loyalty_points": loyalty_points,
                "visit_count": visit_count
            },
            timeout=5
        )
        print(f"✅ Updated customer loyalty: {phone} - {loyalty_points} points")
    except Exception as e:
        print(f"❌ Error updating customer loyalty: {e}")

def bill_helper(bill):
    """Convert MongoDB bill to dict"""
    return {
        "id": str(bill["_id"]),
        "customer": bill.get("customer", ""),
        "phone": bill.get("phone", ""),
        "date": bill.get("date"),
        "total": float(bill.get("total", 0)),
        "staff_username": bill.get("staff_username"),
        "items": bill.get("items", []),
        "created_at": bill.get("created_at").isoformat() if bill.get("created_at") else None,
        "updated_at": bill.get("updated_at").isoformat() if bill.get("updated_at") else None
    }

class BillList(Resource):
    @token_required
    def get(self, current_user):
        """Lấy danh sách hóa đơn với filters"""
        # Get query parameters
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        search = request.args.get('search')
        sort = request.args.get('sort', 'date_desc')
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        query = {}
        
        # Filter by date range
        if from_date or to_date:
            query["date"] = {}
            if from_date:
                query["date"]["$gte"] = from_date
            if to_date:
                query["date"]["$lte"] = to_date
        
        # Search by customer, phone
        if search:
            query["$or"] = [
                {"customer": {"$regex": search, "$options": "i"}},
                {"phone": {"$regex": search, "$options": "i"}}
            ]
            if ObjectId.is_valid(search):
                query["$or"].append({"_id": ObjectId(search)})
        
        # Sorting
        sort_field = "created_at"
        sort_order = -1  # descending
        
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
        
        return [bill_helper(bill) for bill in bills], 200
    
    @token_required
    def post(self, current_user):
        """Tạo hóa đơn mới"""
        data = request.get_json()
        
        if not data or not data.get("items"):
            return {"error": "Items are required"}, 400
        
        # Tính tổng tiền
        total = sum(item.get("subtotal", 0) for item in data["items"])
        
        bill = {
            "customer": data.get("customer", ""),
            "phone": data.get("phone", ""),
            "date": data.get("date", date.today().isoformat()),
            "total": total,
            "staff_username": current_user.get("username"),
            "items": data["items"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.bills.insert_one(bill)
        
        # Update customer loyalty
        if bill.get("phone"):
            update_customer_loyalty(bill["phone"])
        
        created_bill = db.bills.find_one({"_id": result.inserted_id})
        
        return bill_helper(created_bill), 201

class BillDetail(Resource):
    @token_required
    def get(self, current_user, bill_id):
        """Lấy chi tiết hóa đơn"""
        if not ObjectId.is_valid(bill_id):
            return {"error": "Invalid bill ID"}, 400
        
        bill = db.bills.find_one({"_id": ObjectId(bill_id)})
        if not bill:
            return {"error": "Bill not found"}, 404
        
        return bill_helper(bill), 200
    
    @token_required
    def put(self, current_user, bill_id):
        """Cập nhật thông tin hóa đơn"""
        if not ObjectId.is_valid(bill_id):
            return {"error": "Invalid bill ID"}, 400
        
        existing_bill = db.bills.find_one({"_id": ObjectId(bill_id)})
        if not existing_bill:
            return {"error": "Bill not found"}, 404
        
        data = request.get_json()
        old_phone = existing_bill.get("phone")
        
        update_data = {
            "customer": data.get("customer", existing_bill.get("customer")),
            "phone": data.get("phone", existing_bill.get("phone")),
            "updated_at": datetime.utcnow()
        }
        
        db.bills.update_one(
            {"_id": ObjectId(bill_id)},
            {"$set": update_data}
        )
        
        # Update customer loyalty nếu phone thay đổi
        new_phone = update_data.get("phone")
        if old_phone and old_phone != new_phone:
            update_customer_loyalty(old_phone)
        if new_phone:
            update_customer_loyalty(new_phone)
        
        updated_bill = db.bills.find_one({"_id": ObjectId(bill_id)})
        
        return bill_helper(updated_bill), 200
    
    @token_required
    def delete(self, current_user, bill_id):
        """Xóa hóa đơn"""
        if not ObjectId.is_valid(bill_id):
            return {"error": "Invalid bill ID"}, 400
        
        bill = db.bills.find_one({"_id": ObjectId(bill_id)})
        if not bill:
            return {"error": "Bill not found"}, 404
        
        phone = bill.get("phone")
        
        db.bills.delete_one({"_id": ObjectId(bill_id)})
        
        # Update customer loyalty
        if phone:
            update_customer_loyalty(phone)
        
        return {"message": "Bill deleted successfully"}, 200

class BillStats(Resource):
    @token_required
    def get(self, current_user):
        """Lấy thống kê bills"""
        total = db.bills.count_documents({})
        
        # Today's bills
        today = date.today().isoformat()
        today_bills = db.bills.count_documents({"date": today})
        
        # Today's revenue
        pipeline = [
            {"$match": {"date": today}},
            {"$group": {"_id": None, "total": {"$sum": "$total"}}}
        ]
        today_revenue_result = list(db.bills.aggregate(pipeline))
        today_revenue = today_revenue_result[0]["total"] if today_revenue_result else 0
        
        return {
            "total": total,
            "today_bills": today_bills,
            "today_revenue": float(today_revenue)
        }, 200

class MonthlyRevenue(Resource):
    @token_required
    def get(self, current_user):
        """Lấy doanh thu theo tháng"""
        year = int(request.args.get('year', datetime.now().year))
        
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
        
        # Initialize array for all 12 months
        monthly_revenue = [0] * 12
        
        for result in results:
            month_idx = int(result["_id"]) - 1
            monthly_revenue[month_idx] = float(result["revenue"])
        
        return monthly_revenue, 200