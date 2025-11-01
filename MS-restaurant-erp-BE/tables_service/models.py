from bson import ObjectId

def table_helper(table) -> dict:
    return {
        "id": str(table["_id"]),
        "number": table["number"],
        "status": table["status"],
        "location": table.get("location"),
        "created_at": table.get("created_at"),
        "updated_at": table.get("updated_at"),
    }
def order_helper(order) -> dict:
    return {
        "id": str(order["_id"]),
        "table_id": str(order["table_id"]),
        "items": order.get("items", []),
        "created_at": order.get("created_at"),
        "updated_at": order.get("updated_at"),
    }