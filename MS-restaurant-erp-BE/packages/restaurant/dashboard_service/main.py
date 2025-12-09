from auth import get_user_from_request
import json
import requests
import os
from datetime import datetime, timedelta

# Service URLs
BILLING_URL = os.getenv("BILLING_URL", "https://your-billing-service.com")
CUSTOMER_URL = os.getenv("CUSTOMER_URL", "https://your-customer-service.com")
MENU_URL = os.getenv("MENU_URL", "https://your-menu-service.com")
STAFF_URL = os.getenv("STAFF_URL", "https://your-staff-service.com")
TABLE_URL = os.getenv("TABLE_URL", "https://your-table-service.com")

def get_service_data(url, headers=None, timeout=5):
    """Helper function to call other services"""
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def main(args):
    path = args.get("__ow_path", "")
    method = args.get("__ow_method", "get").lower()
    
    # Health check
    if path == "/health":
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "healthy", "service": "dashboard"}),
            "headers": {"Content-Type": "application/json"}
        }

    # Xác thực user
    user = get_user_from_request(args)
    if not user:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Unauthorized"}),
            "headers": {"Content-Type": "application/json"}
        }

    # Prepare headers for service calls
    auth_header = args.get("__ow_headers", {}).get("authorization", "")
    headers = {"Authorization": auth_header} if auth_header else {}

    # GET /dashboard/statistics - Thống kê tổng quan
    if path == "/dashboard/statistics" and method == "get":
        try:
            stats = {}
            
            # Lấy thống kê từ billing service
            billing_stats = get_service_data(f"{BILLING_URL}/bills/stats", headers)
            if billing_stats:
                stats['total_revenue'] = billing_stats.get('today_revenue', 0)
                stats['total_orders'] = billing_stats.get('total', 0)
                stats['today_orders'] = billing_stats.get('today_bills', 0)
            else:
                stats['total_revenue'] = 0
                stats['total_orders'] = 0
                stats['today_orders'] = 0
            
            # Lấy thống kê từ customer service
            customer_stats = get_service_data(f"{CUSTOMER_URL}/customers/analytics", headers)
            if customer_stats:
                stats['total_customers'] = customer_stats.get('total_customers', 0)
                stats['avg_loyalty_points'] = customer_stats.get('avg_loyalty_points', 0)
            else:
                stats['total_customers'] = 0
                stats['avg_loyalty_points'] = 0
            
            # Lấy danh sách menu items
            menu_data = get_service_data(f"{MENU_URL}/menu-items?limit=1000", headers)
            if menu_data:
                results = menu_data.get('results', [])
                stats['total_menu_items'] = len(results)
                stats['available_items'] = sum(1 for item in results if item.get('is_available'))
            else:
                stats['total_menu_items'] = 0
                stats['available_items'] = 0
            
            # Lấy danh sách staff
            staff_data = get_service_data(f"{STAFF_URL}/staff?limit=1000", headers)
            if staff_data:
                results = staff_data.get('results', [])
                stats['total_staff'] = len(results)
            else:
                stats['total_staff'] = 0
            
            # Lấy danh sách tables
            tables_data = get_service_data(f"{TABLE_URL}/tables", headers)
            if tables_data:
                stats['total_tables'] = len(tables_data)
                stats['occupied_tables'] = sum(1 for t in tables_data if t.get('status') == 'occupied')
            else:
                stats['total_tables'] = 0
                stats['occupied_tables'] = 0
            
            return {
                "statusCode": 200,
                "body": json.dumps(stats),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)}),
                "headers": {"Content-Type": "application/json"}
            }

    # GET /dashboard/weekly-revenue - Doanh thu 7 ngày gần nhất
    if path == "/dashboard/weekly-revenue" and method == "get":
        try:
            # Lấy bills từ 7 ngày gần nhất
            today = datetime.now().date()
            from_date = (today - timedelta(days=6)).isoformat()
            to_date = today.isoformat()
            
            bills = get_service_data(
                f"{BILLING_URL}/bills?from_date={from_date}&to_date={to_date}&limit=10000",
                headers
            )
            
            if not bills:
                return {
                    "statusCode": 200,
                    "body": json.dumps([0] * 7),
                    "headers": {"Content-Type": "application/json"}
                }
            
            # Tính doanh thu theo từng ngày
            weekly_revenue = [0] * 7
            
            for bill in bills:
                bill_date_str = bill.get('date')
                if bill_date_str:
                    try:
                        bill_date = datetime.fromisoformat(bill_date_str).date()
                        days_ago = (today - bill_date).days
                        if 0 <= days_ago < 7:
                            weekly_revenue[6 - days_ago] += bill.get('total', 0)
                    except:
                        continue
            
            return {
                "statusCode": 200,
                "body": json.dumps(weekly_revenue),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 200,
                "body": json.dumps([0] * 7),
                "headers": {"Content-Type": "application/json"}
            }

    # GET /dashboard/monthly-revenue - Doanh thu 12 tháng
    if path == "/dashboard/monthly-revenue" and method == "get":
        try:
            year = args.get("year", datetime.now().year)
            
            # Gọi endpoint monthly-revenue của billing service
            monthly_data = get_service_data(
                f"{BILLING_URL}/bills/monthly-revenue?year={year}",
                headers
            )
            
            if not monthly_data:
                return {
                    "statusCode": 200,
                    "body": json.dumps([0] * 12),
                    "headers": {"Content-Type": "application/json"}
                }
            
            return {
                "statusCode": 200,
                "body": json.dumps(monthly_data),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 200,
                "body": json.dumps([0] * 12),
                "headers": {"Content-Type": "application/json"}
            }

    # GET /dashboard/top-selling - Top món bán chạy
    if path == "/dashboard/top-selling" and method == "get":
        try:
            # Lấy tất cả bills
            bills = get_service_data(f"{BILLING_URL}/bills?limit=10000", headers)
            
            if not bills:
                return {
                    "statusCode": 200,
                    "body": json.dumps({"food": [], "drinks": []}),
                    "headers": {"Content-Type": "application/json"}
                }
            
            # Đếm số lượng từng món
            item_count = {}
            item_revenue = {}
            
            for bill in bills:
                items = bill.get('items', [])
                for item in items:
                    item_name = item.get('name', 'Unknown')
                    quantity = item.get('quantity', 1)
                    price = item.get('price', 0)
                    revenue = quantity * price
                    
                    if item_name in item_count:
                        item_count[item_name] += quantity
                        item_revenue[item_name] += revenue
                    else:
                        item_count[item_name] = quantity
                        item_revenue[item_name] = revenue
            
            # Sắp xếp theo số lượng bán
            sorted_items = sorted(item_count.items(), key=lambda x: x[1], reverse=True)
            
            # Phân loại food và drinks
            top_food = []
            top_drinks = []
            
            drink_keywords = ['trà', 'cà phê', 'nước', 'sinh tố', 'soda', 'bia', 'rượu', 'juice', 'cola', 'pepsi']
            
            for item_name, sold in sorted_items:
                revenue = item_revenue.get(item_name, 0)
                item_data = {
                    "name": item_name,
                    "value": sold,
                    "sold": sold,
                    "revenue": revenue,
                    "trend": "up"
                }
                
                # Phân loại
                is_drink = any(keyword in item_name.lower() for keyword in drink_keywords)
                
                if is_drink and len(top_drinks) < 5:
                    top_drinks.append(item_data)
                elif not is_drink and len(top_food) < 5:
                    top_food.append(item_data)
                
                # Dừng khi đã đủ cả 2 loại
                if len(top_food) >= 5 and len(top_drinks) >= 5:
                    break
            
            return {
                "statusCode": 200,
                "body": json.dumps({"food": top_food, "drinks": top_drinks}),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 200,
                "body": json.dumps({"food": [], "drinks": []}),
                "headers": {"Content-Type": "application/json"}
            }

    # GET /dashboard/customer-segments - Phân khúc khách hàng
    if path == "/dashboard/customer-segments" and method == "get":
        try:
            customer_analytics = get_service_data(f"{CUSTOMER_URL}/customers/analytics", headers)
            
            if not customer_analytics:
                return {
                    "statusCode": 200,
                    "body": json.dumps([]),
                    "headers": {"Content-Type": "application/json"}
                }
            
            segments = customer_analytics.get('segments', [])
            
            return {
                "statusCode": 200,
                "body": json.dumps(segments),
                "headers": {"Content-Type": "application/json"}
            }
        except Exception as e:
            return {
                "statusCode": 200,
                "body": json.dumps([]),
                "headers": {"Content-Type": "application/json"}
            }

    # Default: 404
    return {
        "statusCode": 404,
        "body": json.dumps({"error": "Not found"}),
        "headers": {"Content-Type": "application/json"}
    }