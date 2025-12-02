def user_helper(user) -> dict:
    """Convert MongoDB user document to dict"""
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "role": user.get("role"),
        "avatar": user.get("avatar"),
        "phone": user.get("phone"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "date_of_birth": user.get("date_of_birth"),
        "address": user.get("address"),
    }