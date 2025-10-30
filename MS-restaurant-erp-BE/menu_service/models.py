from bson import ObjectId

def menu_item_helper(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "description": item.get("description"),
        "price": float(item["price"]),
        "category": item["category"],
        "image": item.get("image"),
        "is_available": item.get("is_available", True),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
    }