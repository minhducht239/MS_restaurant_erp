from flask import Blueprint, jsonify, request
from auth import token_required
import requests
import os

bp = Blueprint('dashboard', __name__)

BILLING_URL = os.getenv("BILLING_URL", "http://billing_service:8000")
CUSTOMER_URL = os.getenv("CUSTOMER_URL", "http://customer_service:8000")
MENU_URL = os.getenv("MENU_URL", "http://menu_service:8000")
STAFF_URL = os.getenv("STAFF_URL", "http://staff_service:8000")
TABLE_URL = os.getenv("TABLE_URL", "http://table_service:8000")

# Lấy thống kê tổng quan
@bp.route('/dashboard/statistics/', methods=['GET'])
@token_required
def get_statistics():
    try:
        stats = {}
        
        # Lấy tổng doanh thu từ billing service
        try:
            billing_response = requests.get(f"{BILLING_URL}/bills/", timeout=5)
            if billing_response.status_code == 200:
                bills = billing_response.json()
                stats['total_revenue'] = sum(bill.get('total', 0) for bill in bills)
                stats['total_orders'] = len(bills)
            else:
                stats['total_revenue'] = 0
                stats['total_orders'] = 0
        except:
            stats['total_revenue'] = 0
            stats['total_orders'] = 0
        
        # Lấy tổng số khách hàng từ customer service
        try:
            customer_response = requests.get(f"{CUSTOMER_URL}/customers/", timeout=5)
            if customer_response.status_code == 200:
                customers = customer_response.json()
                stats['total_customers'] = len(customers)
            else:
                stats['total_customers'] = 0
        except:
            stats['total_customers'] = 0
        
        # Lấy tổng số món ăn từ menu service
        try:
            menu_response = requests.get(f"{MENU_URL}/menu/", timeout=5)
            if menu_response.status_code == 200:
                menu_items = menu_response.json()
                stats['total_menu_items'] = len(menu_items)
            else:
                stats['total_menu_items'] = 0
        except:
            stats['total_menu_items'] = 0
        
        # Lấy tổng số nhân viên từ staff service
        try:
            staff_response = requests.get(f"{STAFF_URL}/staff/", timeout=5)
            if staff_response.status_code == 200:
                staff = staff_response.json()
                stats['total_staff'] = len(staff)
            else:
                stats['total_staff'] = 0
        except:
            stats['total_staff'] = 0
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Lấy doanh thu theo tuần (7 ngày gần nhất)
@bp.route('/dashboard/weekly-revenue/', methods=['GET'])
@token_required
def get_weekly_revenue():
    try:
        from datetime import datetime, timedelta
        
        # Lấy tất cả bills từ billing service
        billing_response = requests.get(f"{BILLING_URL}/bills/", timeout=5)
        if billing_response.status_code != 200:
            return jsonify([0, 0, 0, 0, 0, 0, 0]), 200
        
        bills = billing_response.json()
        
        # Tính doanh thu 7 ngày gần nhất
        weekly_revenue = [0] * 7
        today = datetime.now().date()
        
        for bill in bills:
            created_at = bill.get('created_at')
            if created_at:
                bill_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
                days_ago = (today - bill_date).days
                if 0 <= days_ago < 7:
                    weekly_revenue[6 - days_ago] += bill.get('total', 0)
        
        return jsonify(weekly_revenue), 200
    except Exception as e:
        return jsonify([0, 0, 0, 0, 0, 0, 0]), 200

# Lấy doanh thu theo tháng (12 tháng)
@bp.route('/dashboard/monthly-revenue/', methods=['GET'])
@token_required
def get_monthly_revenue():
    try:
        from datetime import datetime
        
        # Lấy tất cả bills từ billing service
        billing_response = requests.get(f"{BILLING_URL}/bills/", timeout=5)
        if billing_response.status_code != 200:
            return jsonify([0] * 12), 200
        
        bills = billing_response.json()
        
        # Tính doanh thu 12 tháng
        monthly_revenue = [0] * 12
        current_year = datetime.now().year
        
        for bill in bills:
            created_at = bill.get('created_at')
            if created_at:
                bill_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if bill_date.year == current_year:
                    month_index = bill_date.month - 1
                    monthly_revenue[month_index] += bill.get('total', 0)
        
        return jsonify(monthly_revenue), 200
    except Exception as e:
        return jsonify([0] * 12), 200

# Lấy top món ăn/đồ uống bán chạy
@bp.route('/dashboard/top-selling/', methods=['GET'])
@token_required
def get_top_selling():
    try:
        # Lấy tất cả bills từ billing service
        billing_response = requests.get(f"{BILLING_URL}/bills/", timeout=5)
        if billing_response.status_code != 200:
            return jsonify({"food": [], "drinks": []}), 200
        
        bills = billing_response.json()
        
        # Đếm số lượng món ăn và đồ uống đã bán
        item_count = {}
        for bill in bills:
            items = bill.get('items', [])
            for item in items:
                item_name = item.get('name', 'Unknown')
                quantity = item.get('quantity', 1)
                if item_name in item_count:
                    item_count[item_name] += quantity
                else:
                    item_count[item_name] = quantity
        
        # Sắp xếp theo số lượng bán
        sorted_items = sorted(item_count.items(), key=lambda x: x[1], reverse=True)
        
        # Lấy top 5 món ăn và top 5 đồ uống (giả sử có category trong menu)
        # Nếu không có category, có thể dựa vào tên hoặc logic khác
        top_food = []
        top_drinks = []
        
        for item_name, sold in sorted_items[:10]:
            item_data = {
                "name": item_name,
                "value": sold,
                "sold": sold,
                "trend": "up"  # Có thể tính trend dựa trên dữ liệu lịch sử
            }
            
            # Logic đơn giản: nếu tên chứa từ khóa đồ uống thì xếp vào drinks
            drink_keywords = ['trà', 'cà phê', 'nước', 'sinh tố', 'soda', 'bia']
            if any(keyword in item_name.lower() for keyword in drink_keywords):
                if len(top_drinks) < 5:
                    top_drinks.append(item_data)
            else:
                if len(top_food) < 5:
                    top_food.append(item_data)
        
        return jsonify({"food": top_food, "drinks": top_drinks}), 200
    except Exception as e:
        return jsonify({"food": [], "drinks": []}), 200