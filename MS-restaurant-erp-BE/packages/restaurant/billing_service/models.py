def bill_helper(bill) -> dict:
    return {
        "id": str(bill["_id"]),
        "customer": bill.get("customer", ""),
        "phone": bill.get("phone", ""),
        "date": bill.get("date"),
        "total": float(bill.get("total", 0)),
        "staff_username": bill.get("staff_username"),
        "items": bill.get("items", []),
        "created_at": bill.get("created_at"),
        "updated_at": bill.get("updated_at")
    }

def bill_item_helper(item) -> dict:
    return {
        "item_id": item.get("item_id"),
        "item_name": item.get("item_name"),
        "quantity": item.get("quantity"),
        "price": float(item.get("price", 0)),
        "subtotal": float(item.get("subtotal", 0))
    }