from flask import Blueprint, request, jsonify
from database import db
from models import customer_helper
from schemas import CustomerSchema
from datetime import datetime
from bson import ObjectId

bp = Blueprint('customers', __name__)
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

@bp.route('/customers', methods=['GET'])
def get_customers():
    customers = db.customers.find()
    return customers_schema.dump([customer_helper(c) for c in customers]), 200

@bp.route('/customers', methods=['POST'])
def create_customer():
    data = request.json
    errors = customer_schema.validate(data)
    if errors:
        return errors, 400
    data['created_at'] = datetime.utcnow()
    result = db.customers.insert_one(data)
    customer = db.customers.find_one({"_id": result.inserted_id})
    return customer_schema.dump(customer_helper(customer)), 201

@bp.route('/customers/<string:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = db.customers.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        return {"error": "Customer not found"}, 404
    return customer_schema.dump(customer_helper(customer)), 200

@bp.route('/customers/<string:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.json
    db.customers.update_one({"_id": ObjectId(customer_id)}, {"$set": data})
    customer = db.customers.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        return {"error": "Customer not found"}, 404
    return customer_schema.dump(customer_helper(customer)), 200

@bp.route('/customers/<string:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    result = db.customers.delete_one({"_id": ObjectId(customer_id)})
    if result.deleted_count == 0:
        return {"error": "Customer not found"}, 404
    return {"message": "Deleted"}, 200