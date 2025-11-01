from flask import Blueprint, request, jsonify
from database import db
from models import table_helper
from bson import ObjectId
from datetime import datetime
from models import table_helper, order_helper

bp = Blueprint('tables', __name__, url_prefix='/tables')

@bp.route('/', methods=['GET'])
def list_tables():
    tables = db.tables.find()
    return jsonify([table_helper(t) for t in tables])

@bp.route('/', methods=['POST'])
def create_table():
    data = request.json
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = datetime.utcnow()
    result = db.tables.insert_one(data)
    table = db.tables.find_one({"_id": result.inserted_id})
    return jsonify(table_helper(table)), 201

@bp.route('/<string:table_id>', methods=['PUT'])
def update_table(table_id):
    data = request.json
    data["updated_at"] = datetime.utcnow()
    result = db.tables.update_one({"_id": ObjectId(table_id)}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "Table not found"}), 404
    table = db.tables.find_one({"_id": ObjectId(table_id)})
    return jsonify(table_helper(table))

@bp.route('/<string:table_id>', methods=['DELETE'])
def delete_table(table_id):
    result = db.tables.delete_one({"_id": ObjectId(table_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Table not found"}), 404
    return jsonify({"message": "Table deleted"})
@bp.route('/<string:table_id>/orders', methods=['GET'])
def list_orders(table_id):
    orders = db.orders.find({"table_id": ObjectId(table_id)})
    return jsonify([order_helper(o) for o in orders])

@bp.route('/<string:table_id>/orders', methods=['POST'])
def create_order(table_id):
    data = request.json
    order = {
        "table_id": ObjectId(table_id),
        "items": data.get("items", []),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = db.orders.insert_one(order)
    order["_id"] = result.inserted_id
    return jsonify(order_helper(order)), 201

@bp.route('/orders/<string:order_id>', methods=['GET'])
def get_order(order_id):
    order = db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order_helper(order))

@bp.route('/orders/<string:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.json
    data["updated_at"] = datetime.utcnow()
    result = db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": data})
    if result.matched_count == 0:
        return jsonify({"error": "Order not found"}), 404
    order = db.orders.find_one({"_id": ObjectId(order_id)})
    return jsonify(order_helper(order))

@bp.route('/orders/<string:order_id>', methods=['DELETE'])
def delete_order(order_id):
    result = db.orders.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Order not found"}), 404
    return jsonify({"message": "Order deleted"})