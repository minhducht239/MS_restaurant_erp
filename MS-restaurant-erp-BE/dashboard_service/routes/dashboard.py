from flask import Blueprint, jsonify, request
import requests
import os
from auth import token_required  # Thêm dòng này

bp = Blueprint('dashboard', __name__)

BILLING_URL = os.getenv("BILLING_URL", "http://billing_service:8000")
CUSTOMER_URL = os.getenv("CUSTOMER_URL", "http://customer_service:8000")
MENU_URL = os.getenv("MENU_URL", "http://menu_service:8000")
STAFF_URL = os.getenv("STAFF_URL", "http://staff_service:8000")

@bp.route('/dashboard/statistics', methods=['GET'])
@token_required
def dashboard_statistics():
    token = request.headers.get("Authorization")
    headers = {"Authorization": token} if token else {}

    try:
        billing_stats = requests.get(f"{BILLING_URL}/bills/statistics", headers=headers).json()
        customer_count = requests.get(f"{CUSTOMER_URL}/customers/count", headers=headers).json()
        menu_count = requests.get(f"{MENU_URL}/menu-items/count", headers=headers).json()
        staff_count = requests.get(f"{STAFF_URL}/staff/count", headers=headers).json()

        result = {
            "totalOrders": billing_stats.get("totalOrders"),
            "totalRevenue": billing_stats.get("totalRevenue"),
            "averageOrderValue": billing_stats.get("averageOrderValue"),
            "totalSalaries": staff_count.get("totalSalaries"),
            "customerCount": customer_count.get("count"),
            "menuCount": menu_count.get("count"),
            "staffCount": staff_count.get("count"),
            "monthlyData": billing_stats.get("monthlyData"),
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500