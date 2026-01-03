from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from django.utils import timezone
from datetime import timedelta


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


@api_view(['GET'])
@permission_classes([AllowAny])
def statistics(request):
    """Get overall dashboard statistics"""
    with connection.cursor() as cursor:
        # Total orders
        cursor.execute("SELECT COUNT(*) as count FROM billing_bill")
        total_orders = cursor.fetchone()[0]
        
        # Total revenue
        cursor.execute("SELECT COALESCE(SUM(total), 0) as total FROM billing_bill")
        total_revenue = float(cursor.fetchone()[0])
        
        # Average order value
        cursor.execute("SELECT COALESCE(AVG(total), 0) as avg FROM billing_bill")
        avg_order = float(cursor.fetchone()[0])
        
        # Total staff salary
        cursor.execute("SELECT COALESCE(SUM(salary), 0) as total FROM staff_staff WHERE is_active = 1")
        total_salaries = float(cursor.fetchone()[0])
        
        # Monthly revenue data
        current_year = timezone.now().year
        cursor.execute("""
            SELECT MONTH(date) as month, COALESCE(SUM(total), 0) as total 
            FROM billing_bill 
            WHERE YEAR(date) = %s 
            GROUP BY MONTH(date)
        """, [current_year])
        monthly_result = dictfetchall(cursor)
        
        monthly_data = [0] * 12
        for row in monthly_result:
            monthly_data[row['month'] - 1] = float(row['total'])
    
    return Response({
        'totalOrders': total_orders,
        'totalRevenue': total_revenue,
        'averageOrderValue': round(avg_order),
        'totalSalaries': total_salaries,
        'monthlyData': monthly_data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def weekly_revenue(request):
    """Get daily revenue for current week"""
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    result = [0] * 7
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT date, COALESCE(SUM(total), 0) as total 
            FROM billing_bill 
            WHERE date >= %s AND date <= %s 
            GROUP BY date
        """, [start_of_week, today])
        
        for row in cursor.fetchall():
            day_index = row[0].weekday()
            result[day_index] = float(row[1])
    
    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def monthly_revenue(request):
    """Get monthly revenue for current year"""
    current_year = timezone.now().year
    result = [0] * 12
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT MONTH(date) as month, COALESCE(SUM(total), 0) as total 
            FROM billing_bill 
            WHERE YEAR(date) = %s 
            GROUP BY MONTH(date)
        """, [current_year])
        
        for row in cursor.fetchall():
            result[row[0] - 1] = float(row[1])
    
    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def top_items(request):
    """Get top selling menu items grouped by category"""
    limit = int(request.query_params.get('limit', 5))
    
    food_items = []
    drink_items = []
    
    with connection.cursor() as cursor:
        # Get food items (category = 'food')
        cursor.execute("""
            SELECT bi.item_name, SUM(bi.quantity) as total_qty, SUM(bi.quantity * bi.price) as total_revenue
            FROM billing_billitem bi
            LEFT JOIN menu_menuitem mi ON bi.item_name = mi.name
            WHERE mi.category = 'food' OR mi.category IS NULL
            GROUP BY bi.item_name
            ORDER BY total_qty DESC
            LIMIT %s
        """, [limit])
        
        food_result = cursor.fetchall()
        total_food = sum(row[1] for row in food_result) if food_result else 0
        
        for row in food_result:
            food_items.append({
                'name': row[0],
                'sold': int(row[1]),
                'value': round(row[1] / total_food * 100) if total_food > 0 else 0,
                'trend': 'up'
            })
        
        # Get drink items (category = 'drink')
        cursor.execute("""
            SELECT bi.item_name, SUM(bi.quantity) as total_qty, SUM(bi.quantity * bi.price) as total_revenue
            FROM billing_billitem bi
            LEFT JOIN menu_menuitem mi ON bi.item_name = mi.name
            WHERE mi.category = 'drink'
            GROUP BY bi.item_name
            ORDER BY total_qty DESC
            LIMIT %s
        """, [limit])
        
        drink_result = cursor.fetchall()
        total_drink = sum(row[1] for row in drink_result) if drink_result else 0
        
        for row in drink_result:
            drink_items.append({
                'name': row[0],
                'sold': int(row[1]),
                'value': round(row[1] / total_drink * 100) if total_drink > 0 else 0,
                'trend': 'up'
            })
    
    return Response({
        'food': food_items,
        'drinks': drink_items
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def customer_stats(request):
    """Get customer statistics"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM customers_customer")
        total_customers = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN loyalty_points >= 500 THEN 1 ELSE 0 END) as platinum,
                SUM(CASE WHEN loyalty_points >= 200 AND loyalty_points < 500 THEN 1 ELSE 0 END) as gold,
                SUM(CASE WHEN loyalty_points >= 100 AND loyalty_points < 200 THEN 1 ELSE 0 END) as silver,
                SUM(CASE WHEN loyalty_points >= 50 AND loyalty_points < 100 THEN 1 ELSE 0 END) as bronze,
                SUM(CASE WHEN loyalty_points < 50 THEN 1 ELSE 0 END) as standard
            FROM customers_customer
        """)
        tiers = cursor.fetchone()
    
    return Response({
        'total_customers': total_customers,
        'tiers': {
            'platinum': tiers[0] or 0,
            'gold': tiers[1] or 0,
            'silver': tiers[2] or 0,
            'bronze': tiers[3] or 0,
            'standard': tiers[4] or 0
        }
    })
