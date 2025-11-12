from flask import Blueprint, request, jsonify
from database import db
from models import bill_helper
from schemas import BillSchema
from datetime import datetime
from bson import ObjectId
from auth import token_required

bp = Blueprint('billing', __name__)
bill_schema = BillSchema()
bills_schema = BillSchema(many=True)

@bp.route('/bills', methods=['GET'])
@token_required
def get_bills():
    bills = db.bills.find()
    return bills_schema.dump([bill_helper(b) for b in bills]), 200

@bp.route('/bills', methods=['POST'])
@token_required
def create_bill():
    data = request.json
    errors = bill_schema.validate(data)
    if errors:
        return errors, 400
    data['created_at'] = datetime.utcnow()
    result = db.bills.insert_one(data)
    bill = db.bills.find_one({"_id": result.inserted_id})
    return bill_schema.dump(bill_helper(bill)), 201

@bp.route('/bills/<string:bill_id>', methods=['GET'])
@token_required
def get_bill(bill_id):
    bill = db.bills.find_one({"_id": ObjectId(bill_id)})
    if not bill:
        return {"error": "Bill not found"}, 404
    return bill_schema.dump(bill_helper(bill)), 200

@bp.route('/bills/<string:bill_id>', methods=['PUT'])
@token_required
def update_bill(bill_id):
    data = request.json
    db.bills.update_one({"_id": ObjectId(bill_id)}, {"$set": data})
    bill = db.bills.find_one({"_id": ObjectId(bill_id)})
    if not bill:
        return {"error": "Bill not found"}, 404
    return bill_schema.dump(bill_helper(bill)), 200

@bp.route('/bills/<string:bill_id>', methods=['DELETE'])
@token_required
def delete_bill(bill_id):
    result = db.bills.delete_one({"_id": ObjectId(bill_id)})
    if result.deleted_count == 0:
        return {"error": "Bill not found"}, 404
    return {"message": "Deleted"}, 200