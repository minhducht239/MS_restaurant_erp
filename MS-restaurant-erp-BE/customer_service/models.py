from bson import ObjectId

def customer_helper(customer) -> dict:
    return {
        "id": str(customer["_id"]),
        "name": customer["name"],
        "email": customer["email"],
        "phone": customer.get("phone"),
        "created_at": customer.get("created_at"),
    }