from bson import ObjectId

STATUS_CHOICES = {
    'available': 'Trống',
    'occupied': 'Đã có khách',
    'reserved': 'Đã đặt trước',
}

FLOOR_CHOICES = {
    0: 'Tầng 1',
    1: 'Tầng 2', 
    2: 'Tầng 3',
}

def table_helper(table) -> dict:
    return {
        "id": str(table["_id"]),
        "name": table["name"],
        "capacity": table.get("capacity", 4),
        "status": table["status"],
        "status_display": STATUS_CHOICES.get(table["status"], table["status"]),
        "floor": table.get("floor", 0),
        "floor_display": FLOOR_CHOICES.get(table.get("floor", 0), "Tầng 1"),
        "current_order": table.get("current_order"),
        "created_at": table.get("created_at"),
        "updated_at": table.get("updated_at"),
    }

def order_helper(order) -> dict:
    return {
        "id": str(order["_id"]),
        "table_id": str(order["table_id"]),
        "items": order.get("items", []),
        "total": float(order.get("total", 0)),
        "is_completed": order.get("is_completed", False),
        "notes": order.get("notes", ""),
        "created_at": order.get("created_at"),
        "created_by": order.get("created_by"),
    }

def order_item_helper(item) -> dict:
    return {
        "id": str(item.get("_id", "")),
        "name": item["name"],
        "quantity": item["quantity"],
        "price": float(item["price"]),
        "notes": item.get("notes", ""),
        "subtotal": float(item["quantity"]) * float(item["price"])
    }