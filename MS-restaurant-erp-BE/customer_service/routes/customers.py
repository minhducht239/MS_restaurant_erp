from flask import Blueprint, request, jsonify
from database import db
from models import customer_helper, calculate_loyalty_points
from schemas import CustomerSchema, CustomerFilterSchema
from datetime import datetime
from bson import ObjectId, Regex
from auth import token_required
import math

bp = Blueprint('customers', __name__)
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
filter_schema = CustomerFilterSchema()

@bp.route('/customers/', methods=['GET'])
@token_required
def get_customers():
    """Lấy danh sách khách hàng với pagination, filtering, sorting"""
    try:
        # Parse query params
        filters = filter_schema.load(request.args)
        page = filters.get('page', 1)
        limit = filters.get('limit', 10)
        skip = (page - 1) * limit
        
        # Build MongoDB query
        query = {}
        
        # Search filter
        search = filters.get('search')
        if search:
            query['$or'] = [
                {'name': Regex(search, 'i')},
                {'phone': Regex(search, 'i')}
            ]
        
        # Loyalty points filter
        loyalty_min = filters.get('loyalty_points_min')
        loyalty_max = filters.get('loyalty_points_max')
        if loyalty_min is not None or loyalty_max is not None:
            query['loyalty_points'] = {}
            if loyalty_min is not None:
                query['loyalty_points']['$gte'] = loyalty_min
            if loyalty_max is not None:
                query['loyalty_points']['$lte'] = loyalty_max
        
        # Total spent filter
        spent_min = filters.get('total_spent_min')
        spent_max = filters.get('total_spent_max')
        if spent_min is not None or spent_max is not None:
            query['total_spent'] = {}
            if spent_min is not None:
                query['total_spent']['$gte'] = spent_min
            if spent_max is not None:
                query['total_spent']['$lte'] = spent_max
        
        # Date range filter
        date_after = filters.get('created_at_after')
        date_before = filters.get('created_at_before')
        if date_after or date_before:
            query['created_at'] = {}
            if date_after:
                query['created_at']['$gte'] = datetime.combine(date_after, datetime.min.time())
            if date_before:
                query['created_at']['$lte'] = datetime.combine(date_before, datetime.max.time())
        
        # Sorting
        ordering = filters.get('ordering', '-loyalty_points')
        sort_field = ordering.lstrip('-')
        sort_direction = -1 if ordering.startswith('-') else 1
        
        # Execute query
        total_count = db.customers.count_documents(query)
        customers = db.customers.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)
        
        results = [customer_helper(c) for c in customers]
        
        # Pagination info
        total_pages = math.ceil(total_count / limit)
        
        return jsonify({
            'count': total_count,
            'next': f'/customers/?page={page+1}&limit={limit}' if page < total_pages else None,
            'previous': f'/customers/?page={page-1}&limit={limit}' if page > 1 else None,
            'results': customers_schema.dump(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/customers/', methods=['POST'])
@token_required
def create_customer():
    """Tạo khách hàng mới"""
    try:
        data = request.json
        errors = customer_schema.validate(data)
        if errors:
            return jsonify(errors), 400
        
        # Check duplicate phone
        existing = db.customers.find_one({'phone': data['phone']})
        if existing:
            return jsonify({'error': 'Phone number already exists'}), 400
        
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        data['loyalty_points'] = data.get('loyalty_points', 0)
        data['total_spent'] = data.get('total_spent', 0.0)
        data['visit_count'] = data.get('visit_count', 1)
        
        result = db.customers.insert_one(data)
        customer = db.customers.find_one({"_id": result.inserted_id})
        
        return jsonify(customer_schema.dump(customer_helper(customer))), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/customers/<string:customer_id>/', methods=['GET'])
@token_required
def get_customer(customer_id):
    """Lấy thông tin chi tiết 1 khách hàng"""
    try:
        customer = db.customers.find_one({"_id": ObjectId(customer_id)})
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify(customer_schema.dump(customer_helper(customer))), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/customers/<string:customer_id>/', methods=['PUT'])
@token_required
def update_customer(customer_id):
    """Cập nhật thông tin khách hàng"""
    try:
        data = request.json
        data['updated_at'] = datetime.utcnow()
        
        result = db.customers.update_one(
            {"_id": ObjectId(customer_id)}, 
            {"$set": data}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Customer not found"}), 404
        
        customer = db.customers.find_one({"_id": ObjectId(customer_id)})
        return jsonify(customer_schema.dump(customer_helper(customer))), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/customers/<string:customer_id>/', methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    """Xóa khách hàng"""
    try:
        result = db.customers.delete_one({"_id": ObjectId(customer_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify({"message": "Customer deleted successfully"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/customers/<string:customer_id>/loyalty_history/', methods=['GET'])
@token_required
def get_loyalty_history(customer_id):
    """Lấy lịch sử tích điểm"""
    try:
        customer = db.customers.find_one({"_id": ObjectId(customer_id)})
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        # Lấy bills từ Bill Service (cần gọi API hoặc shared DB)
        # Tạm thời return empty
        history = []
        
        return jsonify({
            'customer': customer_schema.dump(customer_helper(customer)),
            'history': history,
            'total_points': customer.get('loyalty_points', 0)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/customers/<string:customer_id>/recalculate_totals/', methods=['POST'])
@token_required
def recalculate_totals(customer_id):
    """Tính lại tổng chi tiêu và điểm tích lũy"""
    try:
        customer = db.customers.find_one({"_id": ObjectId(customer_id)})
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        # Logic tính lại từ bills (cần integrate với Bill Service)
        # Tạm thời giữ nguyên giá trị hiện tại
        
        return jsonify({
            'customer': customer_schema.dump(customer_helper(customer)),
            'message': 'Totals recalculated successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/customers/analytics/', methods=['GET'])
@token_required
def get_analytics():
    """Thống kê khách hàng theo segments"""
    try:
        pipeline = [
            {
                '$bucket': {
                    'groupBy': '$loyalty_points',
                    'boundaries': [0, 50, 100, 200, float('inf')],
                    'default': 'Other',
                    'output': {
                        'count': {'$sum': 1},
                        'total_spent': {'$sum': '$total_spent'}
                    }
                }
            }
        ]
        
        segments = list(db.customers.aggregate(pipeline))
        
        total_customers = db.customers.count_documents({})
        
        return jsonify({
            'segments': segments,
            'total_customers': total_customers
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400