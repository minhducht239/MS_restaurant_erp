from flask import Blueprint, request, jsonify
from database import db
from models import table_helper, order_helper, order_item_helper
from bson import ObjectId
from datetime import datetime
from auth import token_required
import requests
import os

bp = Blueprint('tables', __name__)

BILL_SERVICE_URL = os.getenv("BILL_SERVICE_URL", "http://localhost:8003")

@bp.route('/tables/', methods=['GET'])
@token_required
def list_tables():
    """Lấy danh sách bàn với filtering"""
    floor = request.args.get('floor', type=int)
    status = request.args.get('status')
    
    query = {}
    if floor is not None:
        query['floor'] = floor
    if status:
        query['status'] = status
    
    tables = list(db.tables.find(query).sort('floor', 1).sort('name', 1))
    
    results = []
    for table in tables:
        table_data = table_helper(table)
        
        active_order = db.orders.find_one({
            "table_id": table["_id"],
            "is_completed": False
        })
        
        if active_order:
            items = active_order.get("items", [])
            table_data["current_order"] = {
                "id": str(active_order["_id"]),
                "items": [order_item_helper(item) for item in items],
                "total": sum(item["quantity"] * item["price"] for item in items),
                "created_at": active_order.get("created_at"),
                "notes": active_order.get("notes", "")
            }
        else:
            table_data["current_order"] = None
        
        results.append(table_data)
    
    return jsonify(results), 200

@bp.route('/tables/<string:table_id>/', methods=['GET'])
@token_required
def get_table(table_id):
    """Lấy chi tiết bàn"""
    try:
        table = db.tables.find_one({"_id": ObjectId(table_id)})
        if not table:
            return jsonify({"error": "Table not found"}), 404
        
        table_data = table_helper(table)
        
        active_order = db.orders.find_one({
            "table_id": ObjectId(table_id),
            "is_completed": False
        })
        
        if active_order:
            items = active_order.get("items", [])
            table_data["current_order"] = {
                "id": str(active_order["_id"]),
                "items": [order_item_helper(item) for item in items],
                "total": sum(item["quantity"] * item["price"] for item in items),
                "created_at": active_order.get("created_at"),
                "notes": active_order.get("notes", "")
            }
        else:
            table_data["current_order"] = None
        
        return jsonify(table_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/tables/', methods=['POST'])
@token_required
def create_table():
    """Tạo bàn mới"""
    try:
        data = request.json
        
        if not data.get("name"):
            return jsonify({"error": "Table name is required"}), 400
        
        existing = db.tables.find_one({"name": data["name"]})
        if existing:
            return jsonify({"error": "Table name already exists"}), 400
        
        new_table = {
            "name": data["name"],
            "capacity": data.get("capacity", 4),
            "status": data.get("status", "available"),
            "floor": data.get("floor", 0),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.tables.insert_one(new_table)
        table = db.tables.find_one({"_id": result.inserted_id})
        
        return jsonify(table_helper(table)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/tables/<string:table_id>/', methods=['PATCH'])
@token_required
def update_table_status(table_id):
    """Cập nhật trạng thái bàn"""
    try:
        data = request.json
        
        if "status" not in data:
            return jsonify({"error": "Status is required"}), 400
        
        update_data = {
            "status": data["status"],
            "updated_at": datetime.utcnow()
        }
        
        result = db.tables.update_one(
            {"_id": ObjectId(table_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Table not found"}), 404
        
        table = db.tables.find_one({"_id": ObjectId(table_id)})
        return jsonify(table_helper(table)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/tables/<string:table_id>/', methods=['DELETE'])
@token_required
def delete_table(table_id):
    """Xóa bàn"""
    try:
        table = db.tables.find_one({"_id": ObjectId(table_id)})
        if not table:
            return jsonify({"error": "Table not found"}), 404
        
        if table["status"] == "occupied":
            return jsonify({"error": "Không thể xóa bàn đang có khách"}), 403
        
        active_order = db.orders.find_one({
            "table_id": ObjectId(table_id),
            "is_completed": False
        })
        
        if active_order:
            return jsonify({"error": "Không thể xóa bàn đang có order"}), 403
        
        db.tables.delete_one({"_id": ObjectId(table_id)})
        
        return jsonify({"message": "Table deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/tables/<string:table_id>/orders/', methods=['GET'])
@token_required
def get_table_orders(table_id):
    """Lấy danh sách order của bàn"""
    try:
        orders = list(db.orders.find({"table_id": ObjectId(table_id)}).sort("created_at", -1))
        
        results = []
        for order in orders:
            order_data = order_helper(order)
            items = order.get("items", [])
            order_data["items"] = [order_item_helper(item) for item in items]
            order_data["total"] = sum(item["quantity"] * item["price"] for item in items)
            results.append(order_data)
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/tables/<string:table_id>/add_order/', methods=['POST'])
@token_required
def add_order_to_table(table_id):
    """Thêm món vào bàn"""
    try:
        data = request.json
        items = data.get("items", [])
        
        if not items:
            return jsonify({"error": "Items are required"}), 400
        
        table = db.tables.find_one({"_id": ObjectId(table_id)})
        if not table:
            return jsonify({"error": "Table not found"}), 404
        
        active_order = db.orders.find_one({
            "table_id": ObjectId(table_id),
            "is_completed": False
        })
        
        if active_order:
            existing_items = active_order.get("items", [])
            
            for new_item in items:
                found = False
                for existing_item in existing_items:
                    if existing_item["name"] == new_item["name"]:
                        existing_item["quantity"] += new_item["quantity"]
                        found = True
                        break
                
                if not found:
                    existing_items.append(new_item)
            
            db.orders.update_one(
                {"_id": active_order["_id"]},
                {"$set": {
                    "items": existing_items,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            order_id = active_order["_id"]
        else:
            new_order = {
                "table_id": ObjectId(table_id),
                "items": items,
                "is_completed": False,
                "notes": data.get("notes", ""),
                "created_at": datetime.utcnow(),
                "created_by": request.user
            }
            
            result = db.orders.insert_one(new_order)
            order_id = result.inserted_id
            
            db.tables.update_one(
                {"_id": ObjectId(table_id)},
                {"$set": {"status": "occupied"}}
            )
        
        order = db.orders.find_one({"_id": order_id})
        return jsonify(order_helper(order)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/tables/<string:table_id>/create_bill/', methods=['POST'])
@token_required
def create_bill_from_table(table_id):
    """Tạo hóa đơn từ bàn"""
    try:
        table = db.tables.find_one({"_id": ObjectId(table_id)})
        if not table:
            return jsonify({"error": "Table not found"}), 404
        
        active_order = db.orders.find_one({
            "table_id": ObjectId(table_id),
            "is_completed": False
        })
        
        if not active_order:
            return jsonify({"error": "No active order for this table"}), 400
        
        items = active_order.get("items", [])
        if not items:
            return jsonify({"error": "Order has no items"}), 400
        
        bill_data = {
            "table_id": table_id,
            "table_name": table["name"],
            "items": items,
            "date": request.json.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
            "created_by": request.user
        }
        
        try:
            bill_response = requests.post(
                f"{BILL_SERVICE_URL}/bills/",
                json=bill_data,
                headers={"Authorization": request.headers.get("Authorization")},
                timeout=5
            )
            
            if bill_response.status_code not in [200, 201]:
                return jsonify({"error": "Failed to create bill"}), 500
            
            bill = bill_response.json()
        except requests.exceptions.RequestException:
            bill = {
                "id": str(active_order["_id"]),
                "items": items,
                "total": sum(item["quantity"] * item["price"] for item in items)
            }
        
        db.orders.update_one(
            {"_id": active_order["_id"]},
            {"$set": {"is_completed": True}}
        )
        
        db.tables.update_one(
            {"_id": ObjectId(table_id)},
            {"$set": {"status": "available"}}
        )
        
        return jsonify(bill), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/health/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db.command('ping')
        return jsonify({
            "status": "healthy",
            "service": "tables",
            "database": "connected"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500