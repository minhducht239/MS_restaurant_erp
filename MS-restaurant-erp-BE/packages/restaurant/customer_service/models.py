from bson import ObjectId
from datetime import datetime

def customer_helper(customer) -> dict:
    return {
        "id": str(customer["_id"]),
        "name": customer["name"],
        "email": customer.get("email"),
        "phone": customer["phone"],
        "loyalty_points": customer.get("loyalty_points", 0),
        "total_spent": float(customer.get("total_spent", 0)),
        "last_visit": customer.get("last_visit"),
        "visit_count": customer.get("visit_count", 1),
        "created_at": customer.get("created_at"),
        "updated_at": customer.get("updated_at"),
    }

def calculate_loyalty_points(bill_amount):
    """Tính điểm tích lũy: 100,000 VNĐ = 1 điểm"""
    try:
        amount = float(bill_amount) if bill_amount else 0
        points_per_amount = 100000
        points = int(amount / points_per_amount)
        return points
    except (ValueError, TypeError):
        return 0